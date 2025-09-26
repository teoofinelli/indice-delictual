import folium
from streamlit_folium import folium_static



def mapa_delitos(df):

    m = folium.Map(location=[-31.4, -64.2], zoom_start=12)
    muestra = df.sample(min(1000, len(df)))  # limitar puntos para performance
    for _, row in muestra.iterrows():
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=2,
            color="red",
            fill=True,
            fill_opacity=0.6
        ).add_to(m)
    return m._repr_html_()

