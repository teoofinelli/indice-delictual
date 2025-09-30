# app/utils/loader.py
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL no está definida en .env")

# Normaliza postgres:// -> postgresql+psycopg2://
if url.startswith("postgres://"):
    url = "postgresql+psycopg2://" + url[len("postgres://"):]

engine = create_engine(url, pool_pre_ping=True)

@st.cache_data(ttl=15)  # TTL corto, porque el usuario mueve el mapa
def map_points(years=None, barrios=None, bbox=None, limit=5000):
    from sqlalchemy import text
    q = """
    SELECT latitud AS lat, longitud AS lon
    FROM delitos
    WHERE latitud IS NOT NULL AND longitud IS NOT NULL
    """
    p = {}
    if years:
        q += " AND año = ANY(:years)"
        p["years"] = years
    if barrios:
        q += " AND barrio = ANY(:barrios)"
        p["barrios"] = barrios
    if bbox:
        q += " AND longitud BETWEEN :minlon AND :maxlon AND latitud BETWEEN :minlat AND :maxlat"
        p.update({"minlon":bbox[0], "minlat":bbox[1], "maxlon":bbox[2], "maxlat":bbox[3]})

    q += " ORDER BY fecha_hora DESC NULLS LAST LIMIT :lim"
    p["lim"] = int(limit)

    import pandas as pd
    df = pd.read_sql(text(q), engine, params=p)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna()
    df = df[(df["lat"].between(-90, 90)) & (df["lon"].between(-180, 180))]
    return df

@st.cache_data(ttl=600)
def get_filter_values():
    with engine.connect() as c:
        years = [r[0] for r in c.execute(text("SELECT DISTINCT año FROM delitos ORDER BY año;"))]
        barrios = [r[0] for r in c.execute(text("""
            SELECT DISTINCT barrio FROM delitos
            WHERE barrio IS NOT NULL
            ORDER BY barrio;
        """))]
    return years, barrios

@st.cache_data(ttl=600)
def load_data(years=None, barrios=None, limit=None):
    q = "SELECT * FROM delitos WHERE 1=1"
    params = {}
    if years:
        q += " AND año = ANY(:years)"
        params["years"] = years
    if barrios:
        q += " AND barrio = ANY(:barrios)"
        params["barrios"] = barrios
    if limit:
        q += f" LIMIT {limit}"
    df = pd.read_sql(text(q), engine, params=params)
    df.reset_index(drop=True, inplace=True)
    if "fecha_hora" in df.columns:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    return df