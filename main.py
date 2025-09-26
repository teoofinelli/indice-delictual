import streamlit as st
import pandas as pd
from app.utils.loader import load_data
from app.utils.charts import plot_barrios, plot_evolucion
from app.utils.maps import mapa_delitos

def run():
    # --- Configuración de la página ---
    st.set_page_config(
        page_title="Dashboard Delitos Córdoba",
        page_icon="🚔",
        layout="wide"
    )

    # --- Título principal ---
    st.title("🚔 Dashboard de Delitos en Córdoba (2019 - 2023)")

    # --- Carga de datos ---
    df = load_data()

    # --- Sidebar (filtros) ---
    st.sidebar.header("Filtros")
    años = st.sidebar.multiselect("Año", sorted(df["año"].unique()), default=df["año"].unique())
    barrios = st.sidebar.multiselect("Barrio", df["barrio"].unique())

    # Filtrado dinámico
    filtro = df[df["año"].isin(años)]
    if barrios:
        filtro = filtro[filtro["barrio"].isin(barrios)]

    # --- Métricas rápidas ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de hechos", f"{len(filtro):,}")
    col2.metric("Años analizados", len(años))
    col3.metric("Barrios seleccionados", len(barrios) if barrios else "Todos")

    # --- Sección de gráficos ---
    st.subheader("📊 Distribución por barrios")
    st.plotly_chart(plot_barrios(filtro), use_container_width=True)

    st.subheader("📈 Evolución temporal")
    st.plotly_chart(plot_evolucion(filtro), use_container_width=True)

    # --- Sección de mapa ---
    st.subheader("🗺️ Mapa de delitos")

    # Renombrar columnas y filtrar nulos
    df_mapa = filtro.rename(columns={"latitud": "latitude", "longitud": "longitude"})
    df_mapa = df_mapa.dropna(subset=["latitude", "longitude"])

    # Mostrar mapa
    st.map(df_mapa[["latitude", "longitude"]])


if __name__ == "__main__":
    run()