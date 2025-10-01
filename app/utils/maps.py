import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from pyproj import Transformer
from folium.plugins import HeatMap, HeatMapWithTime, MarkerCluster
import pandas as pd


def page_mapa(df):
    st.title("Exploración de Mapas")

    opcion = st.radio(
        "Selecciona el tipo de mapa:",
        ["Folium interactivo", "Plotly XY", "GeoPandas estático"]
    )

    # Normalizar columnas
    if "latitud" in df.columns and "longitud" in df.columns:
        df = df.rename(columns={"latitud": "lat", "longitud": "lon"})
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    # ----------------------
    # FOLIUM INTERACTIVO
    # ----------------------
    if opcion == "Folium interactivo":
        subopcion = st.selectbox(
            "Modo de visualización",
            ["Puntos", "Clúster", "Mapa de calor", "Mapa de calor temporal"]
        )

        m = folium.Map(location=[-31.4, -64.2], zoom_start=12)

        muestra = df[["lat", "lon"]].dropna()
        if len(muestra) > 3000:
            muestra = muestra.sample(3000, random_state=42)

        if subopcion == "Puntos":
            for _, row in muestra.iterrows():
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=2,
                    color="red",
                    fill=True,
                    fill_opacity=0.6
                ).add_to(m)

        elif subopcion == "Clúster":
            cluster = MarkerCluster().add_to(m)
            for _, row in muestra.iterrows():
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    popup=f"{row.get('delito', '')} - {row.get('fecha', '')}"
                ).add_to(cluster)

        elif subopcion == "Mapa de calor":
            heat_data = muestra[["lat", "lon"]].values.tolist()
            HeatMap(heat_data, radius=10, blur=8).add_to(m)

        elif subopcion == "Mapa de calor temporal":
            if "fecha" in df.columns:
                df["dia"] = df["fecha"].dt.date
                heat_data = [
                    datos[["lat", "lon"]].dropna().values.tolist()
                    for _, datos in df.groupby("dia")
                ]
                HeatMapWithTime(
                    heat_data,
                    radius=10,
                    auto_play=True,
                    max_opacity=0.8
                ).add_to(m)
            else:
                st.warning("No hay columna 'fecha' disponible para mapa temporal.")

        # Cargar distritos (GeoJSON)
        shp_path = os.path.join(BASE_DIR, "../data", "distritos_policiales.geojson")
        if os.path.exists(shp_path):
            gdf = gpd.read_file(shp_path)
            folium.GeoJson(
                gdf,
                name="Distritos",
                style_function=lambda feature: {
                    "fillColor": "blue",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.2
                },
                tooltip=folium.features.GeoJsonTooltip(fields=["nombre"], aliases=["Distrito:"]),
                popup=folium.GeoJsonPopup(
                    fields=["nombre", "sup_km2", "pob_est_20"],
                    aliases=["Distrito", "Superficie km²", "Población estimada 2020"]
                )
            ).add_to(m)

        # Cargar etiquetas de distritos
        geojson_path = os.path.join(BASE_DIR, "../data", "distritos_policiales_monbre.geojson")
        if os.path.exists(geojson_path):
            gdf_labels = gpd.read_file(geojson_path)
            transformer = Transformer.from_crs("EPSG:22174", "EPSG:4326", always_xy=True)
            gdf_labels["lon"], gdf_labels["lat"] = transformer.transform(
                gdf_labels.geometry.x.values, gdf_labels.geometry.y.values
            )
            for _, row in gdf_labels.iterrows():
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:10pt; font-weight:bold; color:blue; white-space:nowrap">{row["nombre"]}</div>'
                    )
                ).add_to(m)

        folium.LayerControl().add_to(m)
        st_folium(m, use_container_width=True, height=600)

    # ----------------------
    # PLOTLY
    # ----------------------
    elif opcion == "Plotly XY":
        import plotly.express as px
        subopcion = st.selectbox("Modo de visualización", ["Scatter", "Mapa de densidad"])

        if subopcion == "Scatter":
            fig = px.scatter_mapbox(
                df,
                lat="lat", lon="lon",
                color="delito" if "delito" in df.columns else None,
                hover_data=["fecha"] if "fecha" in df.columns else None,
                zoom=11,
                height=600
            )
            fig.update_layout(mapbox_style="carto-positron")
            st.plotly_chart(fig, use_container_width=True)

        elif subopcion == "Mapa de densidad":
            fig = px.density_mapbox(
                df,
                lat="lat", lon="lon",
                z=None,
                radius=15,
                hover_data=["fecha", "delito"] if "delito" in df.columns else None,
                zoom=11,
                height=600
            )
            fig.update_layout(mapbox_style="stamen-terrain")
            st.plotly_chart(fig, use_container_width=True)

    # ----------------------
    # GEOPANDAS
    # ----------------------
    elif opcion == "GeoPandas estático":
        import matplotlib.pyplot as plt
        st.subheader("Delitos por distrito (estático)")

        if "distrito" in df.columns:
            conteo = df.groupby("distrito")["id"].count().reset_index()
            shp_path = os.path.join(BASE_DIR, "../data", "distritos_policiales.geojson")
            if os.path.exists(shp_path):
                gdf = gpd.read_file(shp_path)
                gdf = gdf.merge(conteo, on="distrito", how="left").fillna(0)

                fig, ax = plt.subplots(figsize=(8, 8))
                gdf.plot(
                    column="id",
                    cmap="OrRd",
                    linewidth=0.8,
                    edgecolor="0.8",
                    legend=True,
                    ax=ax
                )
                plt.title("Cantidad de hechos por distrito")
                st.pyplot(fig)
            else:
                st.error("Archivo de distritos no encontrado.")
