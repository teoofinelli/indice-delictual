import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS

# Valor de prueba
df_test = pd.DataFrame({
    "X": [4388820.499441358],
    "Y": [6529273.500675989],
    "latitud": [None],
    "longitud": [None]
})

# Crear GeoDataFrame con CRS original (POSGAR94 / Gauss-Krüger Faja 5)
gdf = gpd.GeoDataFrame(
    df_test,
    geometry=gpd.points_from_xy(df_test["X"].astype('float64'), df_test["Y"].astype('float64')),
    crs=CRS.from_epsg(22194)
)

# Transformar a WGS84
gdf = gdf.to_crs(CRS.from_epsg(4326))

# Asignar lat/lon al DataFrame original
df_test["latitud"] = gdf.geometry.y.values
df_test["longitud"] = gdf.geometry.x.values

# Mostrar con máxima precisión
pd.set_option("display.precision", 12)
print(df_test)
