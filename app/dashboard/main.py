import streamlit as st
from app.utils.loader import load_data
from app.dashboard import sidebar, metrics, charts, map

def run():
    st.set_page_config(
        page_title="Dashboard Delitos Córdoba",
        page_icon="🚔",
        layout="wide"
    )

    st.title("🚔 Dashboard de Delitos en Córdoba (2019 - 2023)")

    # --- Carga de datos ---
    df = load_data()

    # --- Sidebar / Filtros ---
    filtro, años, barrios = sidebar.render(df)

    # --- KPIs / Métricas ---
    metrics.render(filtro, años, barrios)

    # --- Gráficos ---
    st.subheader("📊 Distribución por barrios")
    charts.plot_barrios_chart(filtro)

    st.subheader("📈 Evolución temporal")
    charts.plot_evolucion_chart(filtro)

    # --- Mapa ---
    st.subheader("🗺️ Mapa de delitos")
    map.render(filtro)
