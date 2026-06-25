import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.title('Python para Ciencia de Datos')
st.title('Sismos registrados en el Perú 1960 - 2021')
st.write("### Grupo 1")
st.write("**Tema:** CATALOGO SISMICO 1960-2021 (IGP)")
st.write("**Integrantes:**")
st.write("* Marin Zúñiga, Antony\n* Serquén Yparraguirre, Oscar Alex\n* Cardenas Sanchez, Nestor Raul\n* Deza Quinteros, Victor Junior's\n* Ancajima Arrospide, Pedro")

st.write("**Fuente:** [Datos Abiertos de Perú](https://www.datosabiertos.gob.pe/sites/default/files/Catalogo1960_2021.xlsx)")

# 1. OPTIMIZACIÓN: Cargar datos usando caché para que no se lea el Excel en cada interacción
@st.cache_data
def load_data():
    # url = "https://www.datosabiertos.gob.pe/sites/default/files/Catalogo1960_2021.xlsx"
    url = "Catalogo1960_2021.xlsx"
    df_raw = pd.read_excel(url)
    return df_raw

df = load_data()

st.subheader('Explorando el conjunto de datos del Catálogo Sísmico')
num = st.slider("MOSTRAR FILAS", 1, 50, step=1)

# Mostrar dimensiones y las primeras n filas
st.write(f"Dimensiones del dataset: {df.shape}")
st.dataframe(df.head(num))

# 2. MEJORA: Usar .dt.year de pandas para extraer el año de manera más robusta
# Si FECHA_UTC ya es año en formato int en tu Excel, puedes omitir esta línea o manejar excepciones.
try:
    df['FECHA_UTC'] = pd.to_datetime(df['FECHA_UTC'], format='%Y%m%d', errors='coerce').dt.year
except:
    # Si ya son solo números de 4 dígitos o strings de años
    df['FECHA_UTC'] = df['FECHA_UTC'].astype(str).str[:4].astype(int)

df['UBICACION'] = df['LATITUD'].astype(str) + ',' + df['LONGITUD'].astype(str)

# Categorizar las variables Magnitud y Profundidad
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

# Obteniendo la cantidad total de sismos por año
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
    # CORRECCIÓN: use_container_width en lugar de use_conatiner_width
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(fig, theme=None, use_container_width=True)

st.subheader('Sismos en el Perú (2010 - 2021)')
magnitud = st.slider("MAGNITUD MAYOR O IGUAL A: ", 3, 7, step=1)
year = st.slider("AÑO MAYOR O IGUAL A: ", 2010, 2021, step=1)

df2 = df[(df['MAGNITUD'] >= magnitud) & (df['FECHA_UTC'] >= year)]
dfLatLon = df2[['LATITUD', 'LONGITUD']]
# MEJORA: st.map prefiere columnas en minúsculas
dfLatLon.columns = ['lat', 'lon'] 
st.map(dfLatLon)

st.subheader("Cantidad de Sismos registrados según su magnitud (1960-2021)")

# Conteo según rango de magnitud
df_csis = df['MAGNITUD_CAT2'].value_counts().reset_index()
df_csis.columns = ['RANGO MAGNITUD', 'CANTIDAD SISMOS']
# Ordenamos para asegurar que el gráfico de barras siga el orden correcto
df_csis = df_csis.sort_values(by='RANGO MAGNITUD')

fig2 = px.bar(df_csis, 
              x='CANTIDAD SISMOS', 
              y='RANGO MAGNITUD', 
              text='CANTIDAD SISMOS',
              orientation='h') # Gráfico de barras horizontales
fig2.update_yaxes(title="Rango magnitud de sismos (ML)")
fig2.update_xaxes(title="Cantidad de sismos", showticklabels=False)

tab3, tab4 = st.tabs(["Tema Streamlit (default)", "Plotly native theme"])
with tab3:
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)
with tab4:
    st.plotly_chart(fig2, theme=None, use_container_width=True)
