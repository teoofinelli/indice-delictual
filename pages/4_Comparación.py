# pages/1_Comparacion.py
import streamlit as st
import pandas as pd
from app.utils.loader import load_data
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    if "prevenible" in filtro.columns:
        prevenible_counts = filtro.groupby("prevenible")["id"].count().reset_index().sort_values("id", ascending=True)
        fig_prevenible = px.pie(prevenible_counts, names="prevenible", values="id", hole=0.4, hover_data=["id"])
        st.plotly_chart(fig_prevenible, use_container_width=True)

    # --- Comparación temporal ---
    st.subheader("Comparación Temporal de Delitos")

    # años únicos en el dataset filtrado
    años = sorted(filtro["año"].unique())

    # calculamos las filas y columnas para los subplots (ejemplo: 3 columnas)
    cols = 3
    rows = (len(años) + cols - 1) // cols  # redondeo hacia arriba

    # crear figura con subplots
    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=[f"Año {a}" for a in años],
        specs=[[{'type': 'domain'} for _ in range(cols)] for _ in range(rows)]
    )

    # agregar un pie chart por año
    for i, año in enumerate(años):
        row = i // cols + 1
        col = i % cols + 1
        
        año_data = filtro[filtro["año"] == año]
        prevenible_counts = (
            año_data.groupby("prevenible")["id"]
            .count()
            .reset_index()
            .sort_values("id", ascending=False)
        )
        
        fig.add_trace(
            go.Pie(labels=prevenible_counts["prevenible"], values=prevenible_counts["id"], name=str(año)),
            row=row, col=col
        )

    # ajustar layout
    fig.update_layout(
        title_text="Comparación de Delitos por Año",
        showlegend=False,
        height=400 * rows,  # escala el alto según cantidad de filas
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    run()
