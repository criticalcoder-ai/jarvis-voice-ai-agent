import json
import os
import logging
from datetime import timedelta
from contextlib import asynccontextmanager
from livekit import api
import app.config as config

logger = logging.getLogger(__name__)


class LiveKitService:
    def __init__(self):
        self.api_key = config.LIVEKIT_API_KEY
        self.api_secret = config.LIVEKIT_API_SECRET
        self.livekit_url = config.LIVEKIT_URL

        if not self.api_key or not self.api_secret or not self.livekit_url:
            logger.error("LiveKit configuration is incomplete.")
        else:
            logger.info(f"LiveKit service initialized with URL: {self.livekit_url}")

    @asynccontextmanager
    async def get_api_client(self):
        """Async context manager for LiveKit API client"""
        client = api.LiveKitAPI(
            url=self.livekit_url, api_key=self.api_key, api_secret=self.api_secret
        )
        try:
            yield client
        finally:
            if hasattr(client, "aclose"):
                await client.aclose()

    def generate_token(
        self, room_name: str, participant_id: str, ttl_minutes: int = 60,
    ) -> str:
        """
        Generate LiveKit access token for a participant.
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_id)
        token.with_name(participant_id)
        token.with_grants(
            api.VideoGrants(
                room_join=True, room=room_name, can_publish=True, can_subscribe=True
            )
        )
        token.with_ttl(timedelta(minutes=ttl_minutes))

        return token.to_jwt()

    async def create_room(
        self, room_name: str, agent_config: str, max_participants: int = 2, empty_timeout: int = 300
    ):
        """Create a LiveKit room"""
        async with self.get_api_client() as client:
            req = api.CreateRoomRequest(
                name=room_name,
                metadata=agent_config,
                max_participants=max_participants,
                empty_timeout=empty_timeout,
            )
            await client.room.create_room(req)
            logger.info(f"Room created: {room_name}")

    async def delete_room(self, room_name: str):
        """Delete a specific room"""
        async with self.get_api_client() as client:
            await client.room.delete_room(api.DeleteRoomRequest(room=room_name))
            logger.info(f"Room deleted: {room_name}")

    async def list_rooms(self):
        """List all rooms"""
        async with self.get_api_client() as client:
            res = await client.room.list_rooms(api.ListRoomsRequest())
            return [
                {"name": r.name, "participants": r.num_participants} for r in res.rooms
            ]


livekit_service = LiveKitService()
