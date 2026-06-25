import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.title('Python para Ciencia de Datos')
st.title('Sismos registrados en el Perú 1960 - 2021')
st.write("**Tema:** CATALOGO SISMICO 1960-2021 (IGP)")
st.write("**Integrantes:**")
st.write("** Serquén Yparraguirre, Oscar Alex\n*)

st.write("**Fuente:** [Datos Abiertos de Perú](https://www.datosabiertos.gob.pe/sites/default/files/Catalogo1960_2021.xlsx)")

@st.cache_data
def load_data():
    url = "Catalogo1960_2021.xlsx"
    df_raw = pd.read_excel(url)
    return df_raw

df = load_data()

st.subheader('Explorando el conjunto de datos del Catálogo Sísmico')
num = st.slider("MOSTRAR FILAS", 1, 50, step=1)

st.write(f"Dimensiones del dataset: {df.shape}")
st.dataframe(df.head(num))

try:
    df['FECHA_UTC'] = pd.to_datetime(df['FECHA_UTC'], format='%Y%m%d', errors='coerce').dt.year
except:
    df['FECHA_UTC'] = df['FECHA_UTC'].astype(str).str[:4].astype(int)

df['UBICACION'] = df['LATITUD'].astype(str) + ',' + df['LONGITUD'].astype(str)

df['MAGNITUD_CAT'] = pd.cut(df['MAGNITUD'],
                            bins=[3, 4, 6, np.inf],
                            labels=['Leve', 'Moderado', 'Fuerte'],
                            right=False,
                            ordered=True)

df['MAGNITUD_CAT2'] = pd.cut(df['MAGNITUD'],
                             bins=[3, 4, 5, 6, 7, np.inf],
                             labels=['[3 - 4>', '[4 - 5>', '[5 - 6>', '[6 - 7>', '[7 - 8]'],
                             right=False,
                             ordered=True)

df['PROFUNDIDAD_CAT'] = pd.cut(df['PROFUNDIDAD'],
                               bins=[0, 60, 300, np.inf],
                               labels=['Superficial', 'Intermedia', 'Profundo'],
                               right=False,
                               ordered=True)

st.subheader('Transformación de las columnas del Catálogo Sísmico')
st.write(f"Nuevas dimensiones: {df.shape}")
st.dataframe(df.head())

# --- GRÁFICO 1: Sismos por año ---
dftotal = df.groupby(['FECHA_UTC'])['ID'].count().reset_index(name='Total')

st.subheader("Cantidad de Sismos registrados cada año (1960 - 2021)")
fig = px.scatter(
    dftotal,
    x="FECHA_UTC",
    y="Total",
    color="Total",
    color_continuous_scale="reds",
)

tab1, tab2 = st.tabs(["Tema Streamlit (default)", "Plotly native theme"])
with tab1:
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(fig, theme=None, use_container_width=True)

# --- MAPA INTERACTIVO ---
st.subheader('Sismos en el Perú (2010 - 2021)')

# 1. Creamos columnas para organizar mejor los filtros visualmente
col1, col2 = st.columns(2)

with col1:
    magnitud = st.slider("MAGNITUD MAYOR O IGUAL A: ", 3, 7, step=1)
with col2:
    year = st.slider("AÑO MAYOR O IGUAL A: ", 2010, 2021, step=1)

# 2. NUEVO: Filtro múltiple para la profundidad
# Obtenemos las categorías únicas limpiando los valores nulos (por si acaso)
opciones_profundidad = ['Superficial', 'Intermedia', 'Profundo']
profundidades_seleccionadas = st.multiselect(
    "SELECCIONE EL TIPO DE PROFUNDIDAD:",
    options=opciones_profundidad,
    default=opciones_profundidad # Por defecto, mostramos todas
)

# 3. NUEVO: Actualizamos el filtro del DataFrame para incluir la profundidad elegida
df2 = df[
    (df['MAGNITUD'] >= magnitud) & 
    (df['FECHA_UTC'] >= year) &
    (df['PROFUNDIDAD_CAT'].isin(profundidades_seleccionadas))
]

# Mostramos un mensaje si el usuario desmarca todas las opciones de profundidad
if df2.empty:
    st.warning("No hay sismos que coincidan con estos filtros. Intenta ajustar la búsqueda.")
else:
    dfLatLon = df2[['LATITUD', 'LONGITUD']]
    dfLatLon.columns = ['lat', 'lon'] 
    st.map(dfLatLon)

# --- GRÁFICO 2: Sismos por magnitud ---
st.subheader("Cantidad de Sismos registrados según su magnitud (1960-2021)")

df_csis = df['MAGNITUD_CAT2'].value_counts().reset_index()
df_csis.columns = ['RANGO MAGNITUD', 'CANTIDAD SISMOS']
df_csis = df_csis.sort_values(by='RANGO MAGNITUD')

fig2 = px.bar(df_csis, 
              x='CANTIDAD SISMOS', 
              y='RANGO MAGNITUD', 
              text='CANTIDAD SISMOS',
              orientation='h') 
fig2.update_yaxes(title="Rango magnitud de sismos (ML)")
fig2.update_xaxes(title="Cantidad de sismos", showticklabels=False)

tab3, tab4 = st.tabs(["Tema Streamlit (default)", "Plotly native theme"])
with tab3:
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)
with tab4:
    st.plotly_chart(fig2, theme=None, use_container_width=True)
