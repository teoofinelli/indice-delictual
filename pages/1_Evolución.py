import streamlit as st
from app.utils.loader import load_data
from app.dashboard import charts

st.title("📊 Evolución Temporal de Delitos")

# Cargar datos
df = load_data()

# Filtros
años = st.sidebar.multiselect("Año", sorted(df["año"].unique()), default=df["año"].unique())
barrios = st.sidebar.multiselect("Barrio", df["barrio"].unique())

# Filtrado
filtro = df[df["año"].isin(años)]
if barrios:
    filtro = filtro[filtro["barrio"].isin(barrios)]

# Gráfico
charts.plot_evolucion_chart(filtro)