# pages/1_Comparacion.py
import streamlit as st
import pandas as pd
from app.utils.loader import load_data
import plotly.express as px

def run():
    st.title("📊 Comparación de Delitos")

    # --- Cargar datos ---
    df = load_data()

    # --- Filtros ---
    st.sidebar.header("Filtros de Comparación")
    años = st.sidebar.multiselect("Año", sorted(df["año"].unique()), default=df["año"].unique())
    filtro = df[df["año"].isin(años)]

    # --- Agrupación por zona ---
    st.subheader("Delitos por Zona")
    if "zona" in filtro.columns:
        zona_counts = filtro.groupby("zona")["id"].count().reset_index().sort_values("id", ascending=False)
        fig_zona = px.bar(zona_counts, x="zona", y="id", text="id", labels={"id": "Cantidad de hechos"})
        st.plotly_chart(fig_zona, use_container_width=True)

    # --- Agrupación por distrito ---
    st.subheader("Delitos por Distrito")
    if "distrito" in filtro.columns:
        distrito_counts = filtro.groupby("distrito")["id"].count().reset_index().sort_values("id", ascending=False)
        fig_distrito = px.bar(distrito_counts, x="distrito", y="id", text="id", labels={"id": "Cantidad de hechos"})
        st.plotly_chart(fig_distrito, use_container_width=True)

    # --- Agrupación por tipo de hecho ---
    st.subheader("Delitos por Tipo de Hecho")
    if "delito" in filtro.columns:
        delito_counts = filtro.groupby("delito")["id"].count().reset_index().sort_values("id", ascending=True)
        fig_delito = px.pie(delito_counts, names="delito", values="id", hole=0.4)
        st.plotly_chart(fig_delito, use_container_width=True)


if __name__ == "__main__":
    run()
