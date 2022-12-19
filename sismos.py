import streamlit as st
from datetime import datetime
import numpy as np
import pandas as pd
import os
import plotly.express as px

st.title('Sismos registrados en el Perú 1960 - 2021')
st.write("Grupo 1")
st.write("Tema : CATALOGO SISMICO 1960-2021 (IGP)")
st.write("Integrantes:")
st.write("* Marin Zúñiga, Antony")
st.write("* Serquén Yparraguirre, Oscar Alex")
st.write("* Cardenas Sanchez, Nestor Raul")
st.write("* Deza Quinteros, Victor Junior's")
st.write("* Ancajima Arrospide, Pedro")

st.write("Fuente: https://www.datosabiertos.gob.pe/sites/default/files/Catalogo1960_2021.xlsx")
# Ruta de la Data de Movimientos sismicos

#url = "https://www.datosabiertos.gob.pe/sites/default/files/Catalogo1960_2021.xlsx"
#url = "https://github.com/aserquen/sismos/blob/main/Catalogo1960_2021.xlsx"
url = "Catalogo1960_2021.xlsx"
#Importar datos de Temblores
df = pd.read_excel(url)
st.subheader('Explorando el conjunto de datos del Catalogo Sismico')
num = st.slider("MOSTRAR FILAS", 1,50, step=1) # -----
df.shape, df.head(num)

df.FECHA_UTC = df.FECHA_UTC.astype('string').str[:4].astype('int64') #Convertir año de string a tipo numerico
df['UBICACION'] = df.LATITUD.astype('string').str.cat(df.LONGITUD.astype('string'), sep=',')

# Tabla que contiene la informacion de todos los movimientos sismicos con su respectivo punto poligonal(geometry) y su departamento al que pertenece(LUGAR).
# Categorizar las variables Magnitud y Latitud
df['MAGNITUD_CAT'] = pd.cut(df['MAGNITUD'],
                                bins=[3,4,6,np.inf], # Rangos de los intervalos
                                labels=['Leve','Moderado','Fuerte'], # Nombre de los intervalos
                                right = False,  # contenedores incluyen el borde de la derecha o no.
                                ordered=True)   # 3<= x <4 , 4<= x <6 , 6<= x <=8
df['MAGNITUD_CAT2'] = pd.cut(df['MAGNITUD'],
                                bins=[3,4,5,6,7,np.inf], # Rangos de los intervalos
                                labels=['[3 - 4>','[4 - 5>','[5 - 6>','[6 - 7>','[7 - 8]'], # Nombre de los intervalos
                                right = False,  # contenedores incluyen el borde de la derecha o no.
                                ordered=True
                             )   # 3<= x <4 , 4<= x <5 , 5<= x <=6 , 6<= x <7 , 7<= x <=8
df['PROFUNDIDAD_CAT'] = pd.cut(df['PROFUNDIDAD'],
                                bins=[0,60,300,np.inf], # Rangos de los intervalos
                                labels=['Superficial','Intermedia','Profundo'], # Nombre de los intervalos
                                right = False,  # contenedores incluyen el borde de la derecha o no.
                                ordered=True)   # x <60 , 60<= x <350 , x > 300

st.subheader('Transformación de las columnas del Catalogo Sismico')
df.shape, df.head()

#Obteniendo la cantidad total de sismos por año
dftotal = df.groupby(['FECHA_UTC']).count()['ID'].reset_index(name='Total')
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
    st.plotly_chart(fig, theme="streamlit", use_conatiner_width=True)
with tab2:
    st.plotly_chart(fig, theme=None, use_conatiner_width=True)


st.subheader('Sismos en el Perú (2010 - 2021)')
magnitud = st.slider("MAGNITUD MAYOR O IGUAL A: ", 3,7, step=1) #
year = st.slider("AÑO MAYOR O IGUAL A ", 3,7, step=1) #
df2 = df[df['MAGNITUD'] >= magnitud]
df2 = df2[df2['FECHA_UTC'] >= year]
dfLatLon = df2[['LATITUD','LONGITUD']]
dfLatLon.columns= ['LAT','LON']
st.map(dfLatLon)

st.subheader("Cantidad de Sismos registrados según su magnitud en el intervalo 1960-2021")
df_csis = df.groupby('MAGNITUD_CAT2').agg({'FECHA_CORTE':'count'})
df_csis.reset_index(inplace=True)
df_csis.columns = ['RANGO MAGNITUD','CANTIDAD SISMOS']

yaxis=['3-4   ','4-5   ','5-6   ','6-7   ','7-8   ']
fig2 = px.bar(df_csis,x='CANTIDAD SISMOS',y=yaxis,text='CANTIDAD SISMOS')
fig2.update_yaxes(title="Rango magnitud de sismos (ML)")
fig2.update_xaxes(title="Cantidad de sismos",showticklabels=False)

tab1, tab2 = st.tabs(["Tema Streamlit (default)", "Plotly native theme"])
with tab1:
    st.plotly_chart(fig2, theme="streamlit", use_conatiner_width=True)
with tab2:
    st.plotly_chart(fig2, theme=None, use_conatiner_width=True)
