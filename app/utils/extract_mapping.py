# app/utils/extract_mapping.py
#!/usr/bin/env python3
"""
Extrae y construye diccionarios para normalizar columnas y
completar datos faltantes usando relaciones jerárquicas:
barrio -> comisaria -> distrito -> zona
"""

import pandas as pd
import json
from pathlib import Path

INPUT = Path("data/delitos_cordoba_2019_2023.csv")
OUT_PREVENIBLE = Path("data/delitos_mapping.json")
OUT_COMISARIA = Path("data/comisarias_mapping.json")

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

    print("Leyendo CSV...")
    df = pd.read_csv(INPUT, low_memory=False, dtype=str)

    # Normalizar columnas clave
    for col in ["prevenible", "delito", "comisaria", "distrito", "barrio", "zona"]:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    # --------------------------
    # 1️⃣ Diccionario de delitos/prevenible
    # --------------------------
    """   if "prevenible" in df.columns:
        prevenibles = set(df["prevenible"].dropna().unique())
        mapping_prevenible = {v: v for v in prevenibles}

        with open(OUT_PREVENIBLE, "w", encoding="utf-8") as f:
            json.dump(mapping_prevenible, f, ensure_ascii=False, indent=2)
        print(f"✅ Diccionario prevenible generado con {len(mapping_prevenible)} entradas.")
    """
    # --------------------------
    # 2️⃣ Diccionario jerárquico comisarias -> distritos -> zonas
    # --------------------------
    hier_cols = ["barrio", "comisaria", "distrito", "zona"]
    mapping_comisaria = {}

    if all(c in df.columns for c in hier_cols):
        # crear un DataFrame único sin duplicados
        df_hier = df[hier_cols].dropna(subset=["barrio", "comisaria", "distrito", "zona"]).drop_duplicates()

        # construir mapping jerárquico
        for _, row in df_hier.iterrows():
            mapping_comisaria[row["barrio"]] = {
                "comisaria": row["comisaria"],
                "distrito": row["distrito"],
                "zona": row["zona"]
            }

        with open(OUT_COMISARIA, "w", encoding="utf-8") as f:
            json.dump(mapping_comisaria, f, ensure_ascii=False, indent=2)
        print(f"✅ Diccionario jerárquico generado con {len(mapping_comisaria)} barrios.")

    # --------------------------
    # 3️⃣ Reporte de nulos
    # --------------------------
    nulos = df[hier_cols].isna().sum()
    print("❗ Valores nulos por columna:\n", nulos)

if __name__ == "__main__":
    main()
