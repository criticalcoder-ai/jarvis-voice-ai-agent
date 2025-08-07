from typing import Optional
import asyncpg


async def get_tier_by_id(conn: asyncpg.Connection, tier_id: str) -> Optional[dict]:
    row = await conn.fetchrow("SELECT * FROM tiers WHERE id = $1", tier_id)
    return dict(row) if row else None


async def create_tier(
    conn: asyncpg.Connection,
    tier_id: str,
    name: str,
    max_concurrent_sessions: int,
    daily_minutes: int,
) -> dict:
    row = await conn.fetchrow(
        """
        INSERT INTO tiers (id, name, max_concurrent_sessions, daily_minutes)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """,
        tier_id,
        name,
        max_concurrent_sessions,
        daily_minutes,
    )
    return dict(row)
