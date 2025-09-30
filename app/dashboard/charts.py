import streamlit as st
from app.utils.charts import plot_barrios, plot_evolucion

def plot_barrios_chart(filtro):
    st.plotly_chart(plot_barrios(filtro), use_container_width=True)

def plot_evolucion_chart(filtro):
    st.plotly_chart(plot_evolucion(filtro), use_container_width=True)
