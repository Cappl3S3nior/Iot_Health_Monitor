from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from app.config import settings

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("DB connected successfully!")
