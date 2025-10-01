# app/utils/preprocess.py
#!/usr/bin/env python3
"""
Limpia y guarda un dataset optimizado (parquet / csv.gz) desde el CSV consolidado.
Ejecutar: python app/utils/preprocess.py
"""

import pandas as pd 
from pathlib import Path 
import json 

INPUT = Path("data/delitos_cordoba_2019_2023.csv") 
OUT_PARQUET = Path("data/delitos_cordoba_2019_2023_clean.parquet") 
OUT_CSV_GZ = Path("data/delitos_cordoba_2019_2023_clean.csv.gz") 
MAPPING_JSON = Path("data/delitos_mapping.json")
MAPPING_JSON_COMISARIA = Path("data/comisarias_mapping.json")
MAPPING_JSON_DISTRITO = Path("data/distritos_mapping.json")

def normalize_text(s):
    if pd.isna(s):
        return None
    s = str(s).strip()
    if s in ["", "s/d", "SIN DATOS", "-"]:
        return None
    return s.upper()

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"No existe {INPUT}. Coloca el CSV en data/ y vuelve a intentar.")

    print("Leyendo CSV (low_memory=False)...")
    df = pd.read_csv(INPUT, low_memory=False, dtype=str)  # todo string primero
    print("Filas leídas:", len(df))

    # Convertir columnas numéricas clave
    for c in ["latitud", "longitud", "X", "Y"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Normalizar fecha/hora
    if "fecha_hora" in df.columns:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    else:
        if "fecha_hech" in df.columns and "hora_hecho" in df.columns:
            df["fecha_hora"] = pd.to_datetime(
                df["fecha_hech"].fillna("") + " " + df["hora_hecho"].fillna(""),
                errors="coerce"
            )

    # Normalizar el distrito (algunos tienen "DISTRITO X")
    if "distrito" in df.columns:
        # cambiar "DISTRITO (numeros romanos)" por valor numérico
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO XIII", "DISTRITO 13", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO XII", "DISTRITO 12", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO XI", "DISTRITO 11", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO X", "DISTRITO 10", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO IX", "DISTRITO 9", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO VIII", "DISTRITO 8", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO VII", "DISTRITO 7", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO VI", "DISTRITO 6", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO V", "DISTRITO 5", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO IV", "DISTRITO 4", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO III", "DISTRITO 3", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO II", "DISTRITO 2", case=False, regex=True)
        df["distrito"] = df["distrito"].str.replace(r"DISTRITO I", "DISTRITO 1", case=False, regex=True)
        

    # Extraer componentes temporales
    df["año"] = df["fecha_hora"].dt.year
    df["mes"] = df["fecha_hora"].dt.month
    df["dia"] = df["fecha_hora"].dt.day
    df["hora"] = df["fecha_hora"].dt.hour
    df["weekday"] = df["fecha_hora"].dt.dayofweek  # 0 = lunes

    # Normalizar texto
    for col in ["barrio", "comisaria", "prevenible", "distrito", "zona", "calle", "cuadrantes"]:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    # IDs únicos por año
    if "id" in df.columns and "año" in df.columns:
        df["id"] = df["año"].astype(str) + "_" + df["id"].astype(str)

    # --- 🔹 LIMPIEZA DE COLUMNAS ---
    # Eliminar duplicadas (Latitud/Longitud en string, ya tenemos numéricas)
    df = df.drop(columns=["Latitud", "Longitud"], errors="ignore")

    # Eliminar columnas totalmente nulas
    nunique_valid = df.notna().sum()
    to_drop_nulls = nunique_valid[nunique_valid == 0].index.tolist()
    df = df.drop(columns=to_drop_nulls, errors="ignore")

    # Eliminar columnas redundantes
    redundantes = ["fecha", "fecha_hech", "hora_hecho"]  # ya tenemos fecha_hora
    df = df.drop(columns=redundantes, errors="ignore")

    # Contar coordenadas faltantes
    total = len(df)
    faltan_coords = df[["latitud", "longitud"]].isna().any(axis=1).sum()
    print(f"Registros totales: {total}; sin coordenadas: {faltan_coords}")

    # limpieza de delitos
    df = aplicar_mapping(df, MAPPING_JSON, column="prevenible")

    # Completar comisaria/distrito/zona desde barrio
    df = aplicar_mapping_lugar(df, MAPPING_JSON_COMISARIA)

    # Completar zona desde distrito
    df = fill_zona_from_distrito(df, MAPPING_JSON_DISTRITO)

    # Guardar dataset limpio
    print("Guardando dataset limpio...")
    try:
        df.to_parquet(OUT_PARQUET, index=False)
        print("✅ Parquet guardado en:", OUT_PARQUET)
    except Exception as e:
        print("⚠️ No se pudo guardar parquet:", e)
        print("Guardando CSV comprimido en:", OUT_CSV_GZ)
        df.to_csv(OUT_CSV_GZ, index=False, compression="gzip")
        print("✅ CSV comprimido guardado.")

    print("Preprocesamiento finalizado.")
    print(df.info())
    print("Valores nulos por columna:\n", df.isna().sum())
    print("Columnas finales:", df.columns.tolist())



def aplicar_mapping(df, mapping_path, column="prevenible"):
    """
    Aplica un diccionario de reemplazo desde archivo JSON sobre una columna del DataFrame.
    Si la clave existe en el mapping, se reemplaza por el valor.
    """
    mapping = {}
    if not mapping_path.exists():
        print(f"⚠️ No se encontró mapping en {mapping_path}, no se aplican reemplazos.")
        return df

    # 1) Cargar mapping
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    print(f"✅ Mapping cargado con {len(mapping)} claves desde {mapping_path}")

    # 2) Asegurar columna
    if column not in df.columns:
        df[column] = None

    # 3) Mostrar valores únicos antes
    originales = set(df[column].dropna().unique())
    print(f"🔎 Valores únicos en '{column}' antes de reemplazo: {len(originales)}")

    # 4) Aplicar mapping
    df[column] = df[column].replace(mapping)

    # 5) Mostrar valores no mapeados
    restantes = set(df[column].dropna().unique())
    no_mapeados = originales.intersection(mapping.keys())
    print(f"📌 Claves en mapping que sí están en df: {len(no_mapeados)}")
    print(f"📌 Valores únicos después de mapping: {len(restantes)}")

    # 6) Reporte de nulos
    nulos = df[column].isna().sum()
    total = len(df)
    print(f"📊 Columna '{column}': {nulos}/{total} registros nulos después de aplicar mapping")

    return df

def aplicar_mapping_lugar(df, mapping_path):
    mapping = {}
    if not mapping_path.exists():
        print(f"⚠️ No se encontró mapping en {mapping_path}, no se aplican reemplazos.")
        return df

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    print(f"✅ Mapping cargado con {len(mapping)} claves desde {mapping_path}")

    cols = ["comisaria", "distrito", "zona"]

    def fill_row(row):
        barrio = row.get("barrio")
        if not barrio or barrio not in mapping:
            return row  # no hay mapping, devuelve igual
        for col in cols:
            if pd.isna(row[col]) and col in mapping[barrio]:
                row[col] = mapping[barrio][col]
        return row

    df = df.apply(fill_row, axis=1)
    return df

def fill_zona_from_distrito(df, mapping_path):
    """
    Completa los valores nulos de la columna 'zona' en base al 'distrito'.
    
    distritos_mapping: dict con estructura
        { "DISTRITO X": {"zona": "ZONA Y"} }
    """
    mapping = {}
    if not mapping_path.exists():
        print(f"⚠️ No se encontró mapping en {mapping_path}, no se aplican reemplazos.")
        return df

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    print(f"✅ Mapping cargado con {len(mapping)} claves desde {mapping_path}")


    def get_zona(row):
        if pd.isna(row["zona"]) and row["distrito"] in mapping:
            return mapping[row["distrito"]]["zona"]
        return row["zona"]

    df["zona"] = df.apply(get_zona, axis=1)
    return df





if __name__ == "__main__":
    main()

