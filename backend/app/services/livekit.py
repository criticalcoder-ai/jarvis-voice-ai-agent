import json
import os
import logging
from datetime import timedelta
from contextlib import asynccontextmanager
from livekit import api
from livekit.api import TwirpError
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
        self, room_name: str, participant_id: str, ttl_minutes: int = 30,
    ) -> str:
        """
        Generate LiveKit access token for a participant.
        """
        try:
            if not room_name or not participant_id:
                raise ValueError("Room name and participant ID are required")
            
            token = api.AccessToken(self.api_key, self.api_secret)
            token.with_identity(participant_id)
            token.with_name(participant_id)
            token.with_grants(
                api.VideoGrants(
                    room_join=True, room=room_name, can_publish=True, can_subscribe=True
                )
            )
            token.with_ttl(timedelta(minutes=ttl_minutes)) # TODO enforce dynamic ttl with tiers etc

            return token.to_jwt()
        except ValueError as e:
            logger.error(f"Invalid parameters for token generation: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error generating token for room '{room_name}', participant '{participant_id}': {e}")
            raise e

    async def create_room(
        self, room_name: str, agent_config: str, max_participants: int = 2, empty_timeout: int = 300
    ):
        """Create a LiveKit room"""
        try:
            if not room_name:
                raise ValueError("Room name is required")
            
            async with self.get_api_client() as client:
                req = api.CreateRoomRequest(
                    name=room_name,
                    metadata=agent_config,
                    max_participants=max_participants,
                    empty_timeout=empty_timeout,
                )
                await client.room.create_room(req)
                logger.info(f"Room created successfully: {room_name}")
        except TwirpError as e:
            if e.code == "already_exists":
                logger.warning(f"Room '{room_name}' already exists")
                # Room already exists, this might be acceptable depending on use case
                return
            else:
                logger.error(f"LiveKit API error creating room '{room_name}': {e.code} - {e.message}")
                raise e
        except ValueError as e:
            logger.error(f"Invalid parameters for room creation: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error creating room '{room_name}': {e}")
            raise e

    async def delete_room(self, room_name: str):
        """Delete a specific room"""
        try:
            if not room_name:
                raise ValueError("Room name is required")
            
            async with self.get_api_client() as client:
                await client.room.delete_room(api.DeleteRoomRequest(room=room_name))
                logger.info(f"Room deleted successfully: {room_name}")
        except TwirpError as e:
            if e.code == "not_found":
                logger.warning(f"Room '{room_name}' does not exist or was already deleted")
                # Room doesn't exist, which might be the desired state anyway
                return
            else:
                logger.error(f"LiveKit API error deleting room '{room_name}': {e.code} - {e.message}")
                raise e
        except ValueError as e:
            logger.error(f"Invalid parameters for room deletion: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error deleting room '{room_name}': {e}")
            raise e

    async def list_rooms(self):
        """List all rooms"""
        try:
            async with self.get_api_client() as client:
                res = await client.room.list_rooms(api.ListRoomsRequest())
                rooms = [
                    {"name": r.name, "participants": r.num_participants} for r in res.rooms
                ]
                logger.debug(f"Listed {len(rooms)} rooms")
                return rooms
        except TwirpError as e:
            logger.error(f"LiveKit API error listing rooms: {e.code} - {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error listing rooms: {e}")
            raise e


livekit_service = LiveKitService()
