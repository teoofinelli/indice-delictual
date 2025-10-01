import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from pyproj import Transformer

def page_mapa(df):
    st.title("Exploración de Mapas")

    opcion = st.radio(
        "Selecciona el tipo de mapa:",
        ["Folium interactivo", "Plotly XY", "GeoPandas estático"]
    )

    if opcion == "Folium interactivo":
        m = folium.Map(location=[-31.4, -64.2], zoom_start=12)

        # ---------------------
        # 1️⃣ Delitos como puntos
        # ---------------------
        muestra = df[["latitud", "longitud"]].dropna()
        if len(muestra) > 1000:
            muestra = muestra.sample(1000, random_state=42)
        for _, row in muestra.iterrows():
            folium.CircleMarker(
                location=[row["latitud"], row["longitud"]],
                radius=2,
                color="red",
                fill=True,
                fill_opacity=0.6
            ).add_to(m)

        # ---------------------
        # 2️⃣ Distritos con etiquetas
        # ---------------------
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        shp_path = os.path.join(BASE_DIR, "../data", "distritos_policiales.geojson")
        

        gdf = gpd.read_file(shp_path)  # geojson
        folium.GeoJson(
            gdf,
            name="Distritos",
            style_function=lambda feature: {
                "fillColor": "blue",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.2
            },
            # etiquetas y popups
            tooltip=folium.features.GeoJsonTooltip(fields=["nombre"], aliases=["Distrito:"]),
            popup=folium.GeoJsonPopup(fields=["nombre", "sup_km2", "pob_est_20"],
                                    aliases=["Distrito", "Superficie km²", "Población estimada 2020"])
        ).add_to(m)


        geojson_path = os.path.join(BASE_DIR, "../data", "distritos_policiales_monbre.geojson")
        gdf = gpd.read_file(geojson_path)

        # Transformar las coordenadas a WGS84
        transformer = Transformer.from_crs("EPSG:22174", "EPSG:4326", always_xy=True)
        gdf["lon"], gdf["lat"] = transformer.transform(gdf.geometry.x.values, gdf.geometry.y.values)

        # Agregar los puntos de distrito al mapa
        for _, row in gdf.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                icon=folium.DivIcon(
                    html = f'<div style="font-size:10pt; font-weight:bold; color:blue; white-space:nowrap">{row["nombre"]}</div>'
                )
            ).add_to(m)

        # Mostrar capas
        folium.LayerControl().add_to(m)

        st_folium(m, use_container_width=True)

    elif opcion == "Plotly XY":
        import plotly.express as px
        fig = px.scatter(df, x="X", y="Y", title="Delitos en coordenadas X/Y")
        st.plotly_chart(fig, use_container_width=True)

    elif opcion == "GeoPandas estático":
        import matplotlib.pyplot as plt
        gdf_delitos = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df["X"], df["Y"]), crs="EPSG:22195"
        )
        fig, ax = plt.subplots(figsize=(8, 8))
        gdf_delitos.plot(ax=ax, color="red", markersize=5)
        st.pyplot(fig)
