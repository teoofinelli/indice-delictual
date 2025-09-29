# app/utils/loader.py
from pathlib import Path
import pandas as pd
import streamlit as st
from functools import lru_cache

CLEAN_PARQUET = Path("data/delitos_cordoba_2019_2023_clean.parquet")
CLEAN_CSV_GZ = Path("data/delitos_cordoba_2019_2023_clean.csv.gz")
RAW_CSV = Path("data/delitos_cordoba_2019_2023.csv")

@st.cache_data
def load_data(path: str = None):
    """
    Carga el dataset limpio (parquet preferido). Devuelve un DataFrame listo para usar.
    """
    # elegir archivo
    if path:
        p = Path(path)
    else:
        if CLEAN_PARQUET.exists():
            p = CLEAN_PARQUET
        elif CLEAN_CSV_GZ.exists():
            p = CLEAN_CSV_GZ
        else:
            p = RAW_CSV

    print(f"Cargando datos desde {p} ...")
    if p.suffix == ".parquet":
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p, low_memory=False)

    # Asegurar tipos
    for c in ["latitud", "longitud", "X", "Y"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "fecha_hora" in df.columns:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    else:
        if "fecha_hech" in df.columns and "hora_hecho" in df.columns:
            df["fecha_hora"] = pd.to_datetime(
                df["fecha_hech"].fillna("") + " " + df["hora_hecho"].fillna(""),
                errors="coerce"
            )

    if "año" not in df.columns:
        df["año"] = df["fecha_hora"].dt.year

    return df
