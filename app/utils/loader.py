import pandas as pd
from functools import lru_cache

@lru_cache
def load_data():
    df = pd.read_csv("data/delitos_cordoba_2019_2023.csv",
        low_memory=False,       # evita el warning
        dtype=str               # fuerza todo a texto, luego convertimos columnas necesarias
    )
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    df["año"] = df["fecha_hora"].dt.year
    df["mes"] = df["fecha_hora"].dt.month
    df["hora"] = df["fecha_hora"].dt.hour

    # Convertir columnas numéricas que nos interesen
    for col in ["latitud", "longitud"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
