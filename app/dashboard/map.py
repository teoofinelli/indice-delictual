import streamlit as st

def render(filtro):
    # Renombrar columnas y filtrar nulos
    df_mapa = filtro.rename(columns={"latitud": "latitude", "longitud": "longitude"})
    df_mapa = df_mapa.dropna(subset=["latitude", "longitude"])

    # Mostrar mapa con puntos pequeños y color azul
    st.map(df_mapa[["latitude", "longitude"]], size=10, color="#0044ff")
