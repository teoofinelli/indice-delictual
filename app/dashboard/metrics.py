import streamlit as st

def render(filtro, años, barrios):
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de hechos", f"{len(filtro):,}")
    col2.metric("Años analizados", len(años))
    col3.metric("Barrios seleccionados", len(barrios) if barrios else "Todos")
