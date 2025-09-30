from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL no está definida")
if url.startswith("postgres://"):
    url = "postgresql+psycopg2://" + url[len("postgres://"):]

engine = create_engine(url, pool_pre_ping=True)

SQL = """
CREATE INDEX IF NOT EXISTS idx_delitos_anio        ON delitos(año);
CREATE INDEX IF NOT EXISTS idx_delitos_barrio      ON delitos(barrio);
CREATE INDEX IF NOT EXISTS idx_delitos_fecha_hora  ON delitos(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_delitos_coords      ON delitos(latitud, longitud);
"""

CHECK = """
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = 'delitos'
ORDER BY indexname;
"""

with engine.begin() as conn:
    conn.execute(text(SQL))
    rows = conn.execute(text(CHECK)).fetchall()

print("✅ Índices en 'delitos':")
for name, defn in rows:
    print("-", name)
