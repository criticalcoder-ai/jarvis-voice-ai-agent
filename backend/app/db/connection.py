import asyncpg
from contextlib import asynccontextmanager
from app.config import DATABASE_URL


@asynccontextmanager
async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()
