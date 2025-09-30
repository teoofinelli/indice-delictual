import time
import streamlit as st
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium
from app.utils.loader import map_points

CORDOBA_CENTER = [-31.4167, -64.1833]

def _as_xy(center):
    if center is None:
        return CORDOBA_CENTER
    if isinstance(center, (list, tuple)) and len(center) == 2:
        return [float(center[0]), float(center[1])]
    if isinstance(center, dict) and "lat" in center and ("lng" in center or "lon" in center):
        lng = center.get("lng", center.get("lon"))
        return [float(center["lat"]), float(lng)]
    return CORDOBA_CENTER

def _bbox_dict_to_tuple(bounds):
    sw = bounds["_southWest"]; ne = bounds["_northEast"]
    return (sw["lng"], sw["lat"], ne["lng"], ne["lat"])

def _round_bounds(b, ndigits=4):
    return None if not b else tuple(round(float(x), ndigits) for x in b)

def _default_bbox(center, delta=0.20):
    lat, lon = center[0], center[1]
    return (lon - delta, lat - delta, lon + delta, lat + delta)

def _limit_for_zoom(zoom: int) -> int:
    if zoom is None: return 1000
    if zoom >= 14: return 4000
    if zoom >= 12: return 2500
    if zoom >= 10: return 1500
    return 800

def mapa_delitos_dinamico(years=None, barrios=None, height=540, key="mapa_dinamico"):
    # ---- Estado ----
    center = _as_xy(st.session_state.get(f"{key}_center", CORDOBA_CENTER))
    zoom   = st.session_state.get(f"{key}_zoom", 12)
    bbox   = st.session_state.get(f"{key}_bbox") or _default_bbox(center)
    st.session_state[f"{key}_bbox"] = bbox

    last_move_ts = st.session_state.get(f"{key}_last_move_ts", 0.0)
    stable_bbox  = st.session_state.get(f"{key}_stable_bbox") or _round_bounds(bbox)
    debounce_s   = 0.60

    # ---- Placeholder ÚNICO para evitar doble mapa ----
    ph_key = f"{key}_ph"
    if ph_key not in st.session_state:
        st.session_state[ph_key] = st.empty()
    ph = st.session_state[ph_key]   # <-- SIEMPRE asignamos 'ph'

    # 1) Render liviano SOLO para leer viewport (sin puntos), dentro del placeholder
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron", control_scale=True)
    with ph.container():
        data = st_folium(m, height=height, width=None, key=key)

    if not data:
        return

    new_zoom   = data.get("zoom", zoom)
    new_center = _as_xy(data.get("center", center))
    new_bounds = data.get("bounds")
    new_bbox   = _round_bounds(_bbox_dict_to_tuple(new_bounds)) if new_bounds else _round_bounds(bbox)

    changed = False
    if new_bbox and new_bbox != _round_bounds(st.session_state.get(f"{key}_bbox")):
        st.session_state[f"{key}_bbox"] = new_bbox
        changed = True
    if new_zoom != st.session_state.get(f"{key}_zoom", zoom):
        st.session_state[f"{key}_zoom"] = new_zoom
        changed = True
    if new_center != _as_xy(st.session_state.get(f"{key}_center")):
        st.session_state[f"{key}_center"] = new_center
        changed = True

    now = time.time()
    if changed:
        st.session_state[f"{key}_last_move_ts"] = now
        # Opcional UX: mostrar aviso mientras se mueve
        # with ph.container(): st.info("🗺️ Soltá el mapa para actualizar puntos…")
        return

    # 2) Si el viewport quedó estable (sin cambios recientes), reemplazamos el mapa por el de puntos
    if now - last_move_ts < debounce_s:
        return

    if new_bbox != stable_bbox:
        st.session_state[f"{key}_stable_bbox"] = new_bbox
        stable_bbox = new_bbox

    limit = _limit_for_zoom(new_zoom)
    pts = map_points(years=years, barrios=barrios, bbox=stable_bbox, limit=limit)

    m2 = folium.Map(location=new_center, zoom_start=new_zoom, tiles="CartoDB positron", control_scale=True)
    if not pts.empty:
        FastMarkerCluster(pts[["lat", "lon"]].values.tolist(), maxClusterRadius=60).add_to(m2)

    # Reemplazo del contenido del placeholder: ahora sí, mapa con puntos (queda solo uno en pantalla)
    ph.empty()
    with ph.container():
        st_folium(m2, height=height, width=None, key=key)