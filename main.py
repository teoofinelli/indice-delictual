import streamlit as st
from app.utils.loader import load_data, get_filter_values
from app.utils.charts import plot_barrios, plot_evolucion
from app.utils.maps import mapa_delitos_dinamico

def run():
    st.set_page_config(page_title="Dashboard Delitos Córdoba", page_icon="🚔", layout="wide")
    st.title("🚔 Dashboard de Delitos en Córdoba (2019 - 2023)")

    st.sidebar.header("Filtros")
    years_all, barrios_all = get_filter_values()
    años = st.sidebar.multiselect("Año", years_all, default=years_all)
    barrios = st.sidebar.multiselect("Barrio", barrios_all)

    df = load_data(years=años, barrios=barrios)
    if df.empty:
        st.info("No hay datos para los filtros seleccionados.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de hechos", f"{len(df):,}")
    c2.metric("Años seleccionados", len(años))
    c3.metric("Barrios seleccionados", len(barrios) if barrios else "Todos")

    st.subheader("📊 Distribución por barrios")
    st.plotly_chart(plot_barrios(df), use_container_width=True)

    st.subheader("📈 Evolución temporal")
    st.plotly_chart(plot_evolucion(df), use_container_width=True)

    # ---------- Mapa dinámico por viewport ----------
    st.subheader("🗺️ Mapa de delitos (dinámico)")
    mapa_delitos_dinamico(years=años, barrios=barrios)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar CSV filtrado", csv, "delitos_filtrado.csv", "text/csv")

if __name__ == "__main__":
    run()
