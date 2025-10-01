import streamlit as st
from app.utils.loader import load_data
from app.utils import maps

st.title("🗺️ Mapa de Delitos en Córdoba")

# Cargar datos
df = load_data()

# --- Filtros ---
st.sidebar.header("Filtros de Comparación")
años = st.sidebar.multiselect("Año", sorted(df["año"].unique()), default=df["año"].unique())
filtro = df[df["año"].isin(años)]

# Mostrar página de mapa
maps.page_mapa(filtro)
