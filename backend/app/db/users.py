from typing import Optional, Dict, Any
import asyncpg


async def get_user_by_id(conn: asyncpg.Connection, user_id: str) -> Optional[dict]:
    row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    return dict(row) if row else None


async def get_user_by_email(conn: asyncpg.Connection, email: str) -> Optional[dict]:
    row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    return dict(row) if row else None


async def create_user(conn: asyncpg.Connection, user_data: Dict[str, Any]) -> dict:
    row = await conn.fetchrow(
        """
        INSERT INTO users (id, email, name, profile_pic, tier_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
    """,
        user_data["id"],
        user_data["email"],
        user_data["name"],
        user_data.get("profile_pic"),
        user_data.get("tier_id", "free"),
    )
    return dict(row)



async def get_or_create_user(
    conn: asyncpg.Connection, email: str, name: str, picture: str
) -> dict:
    user = await get_user_by_email(conn, email)
    if user:
        return user

    import uuid

    user_id = str(uuid.uuid4())
    return await create_user(
        conn,
        {
            "id": user_id,
            "email": email,
            "name": name,
            "profile_pic": picture,
            "tier_id": "free",
        },
    )
