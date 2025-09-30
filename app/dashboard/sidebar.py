import streamlit as st

def render(df):
    st.sidebar.header("Filtros")
    años = st.sidebar.multiselect("Año", sorted(df["año"].unique()), default=df["año"].unique())
    barrios = st.sidebar.multiselect("Barrio", df["barrio"].unique())

    # Filtrado
    filtro = df[df["año"].isin(años)]
    if barrios:
        filtro = filtro[filtro["barrio"].isin(barrios)]

    return filtro, años, barrios
