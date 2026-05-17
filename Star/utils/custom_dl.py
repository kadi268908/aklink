import math
import asyncio
import logging
from config import Var
from typing import Dict, Union
from Star.bot import work_loads
from pyrogram import Client, utils, raw
from Star.utils.file_properties import get_file_ids
from pyrogram.session import Session, Auth
from pyrogram.errors import AuthBytesInvalid
from Star.server.exceptions import FIleNotFound
from pyrogram.file_id import FileId, FileType, ThumbnailSource


class ByteStreamer:
    def __init__(self, client: Client):
        self.clean_timer = 30 * 60
        self.client: Client = client
        self.cached_file_ids: Dict[int, FileId] = {}
        self.max_cache_size = 1000  # Maximum 1000 file entries in cache
        asyncio.create_task(self.clean_cache())

    async def get_file_properties(self, id: int) -> FileId:
        if id not in self.cached_file_ids:
            await self.generate_file_properties(id)
        return self.cached_file_ids[id]

    async def generate_file_properties(self, id: int) -> FileId:
        file_id = await get_file_ids(self.client, Var.BIN_CHANNEL, id)
        if not file_id:
            raise FIleNotFound
        
        # Add to cache with LRU eviction if needed
        if len(self.cached_file_ids) >= self.max_cache_size:
            # Remove oldest entry (first one added)
            oldest_id = next(iter(self.cached_file_ids))
            del self.cached_file_ids[oldest_id]
            logging.info(f"Cache evicted oldest file {oldest_id}, size={len(self.cached_file_ids)}")
        
        self.cached_file_ids[id] = file_id
        return self.cached_file_ids[id]

    async def generate_media_session(self, client: Client, file_id: FileId) -> Session:
        media_session = client.media_sessions.get(file_id.dc_id)

        if media_session and media_session.is_connected:
            return media_session

        if media_session:
            await media_session.stop()
            client.media_sessions.pop(file_id.dc_id, None)

        if file_id.dc_id != await client.storage.dc_id():
            media_session = Session(
                client,
                file_id.dc_id,
                await Auth(client, file_id.dc_id, await client.storage.test_mode()).create(),
                await client.storage.test_mode(),
                is_media=True,
            )
            await media_session.start()

            auth_success = False
            for attempt in range(6):
                try:
                    exported_auth = await client.invoke(raw.functions.auth.ExportAuthorization(dc_id=file_id.dc_id))
                    await media_session.send(raw.functions.auth.ImportAuthorization(id=exported_auth.id, bytes=exported_auth.bytes))
                    auth_success = True
                    break
                except AuthBytesInvalid:
                    logging.warning(f"Auth attempt {attempt+1}/6 failed for dc_id {file_id.dc_id}")
                    continue
                except Exception as e:
                    logging.error(f"Unexpected error in auth setup: {e}", exc_info=True)
                    break
            
            if not auth_success:
                await media_session.stop()
                logging.error(f"Failed to setup auth for dc_id {file_id.dc_id}")
                raise AuthBytesInvalid("Failed to establish auth after 6 attempts")
        else:
            media_session = Session(
                client,
                file_id.dc_id,
                await client.storage.auth_key(),
                await client.storage.test_mode(),
                is_media=True,
            )
            await media_session.start()

        client.media_sessions[file_id.dc_id] = media_session
        return media_session

    @staticmethod
    async def get_location(file_id: FileId) -> Union[
        raw.types.InputPhotoFileLocation,
        raw.types.InputDocumentFileLocation,
        raw.types.InputPeerPhotoFileLocation,
    ]:
        if file_id.file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(user_id=file_id.chat_id, access_hash=file_id.chat_access_hash)
            else:
                if file_id.chat_access_hash == 0:
                    peer = raw.types.InputPeerChat(chat_id=-file_id.chat_id)
                else:
                    peer = raw.types.InputPeerChannel(channel_id=utils.get_channel_id(file_id.chat_id), access_hash=file_id.chat_access_hash)

            return raw.types.InputPeerPhotoFileLocation(peer=peer, volume_id=file_id.volume_id, local_id=file_id.local_id, big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG)

        if file_id.file_type == FileType.PHOTO:
            return raw.types.InputPhotoFileLocation(id=file_id.media_id, access_hash=file_id.access_hash, file_reference=file_id.file_reference, thumb_size=file_id.thumbnail_size)

        return raw.types.InputDocumentFileLocation(id=file_id.media_id, access_hash=file_id.access_hash, file_reference=file_id.file_reference, thumb_size=file_id.thumbnail_size)

    async def yield_file(self, file_id: FileId, index: int, offset: int,
                         first_part_cut: int, last_part_cut: int,
                         part_count: int, chunk_size: int):

        try:
            work_loads[index] += 1
            media_session = await self.generate_media_session(self.client, file_id)
            location = await self.get_location(file_id)
            current_part = 1

            r = await media_session.send(raw.functions.upload.GetFile(location=location, offset=offset, limit=chunk_size))

            while isinstance(r, raw.types.upload.File):
                if asyncio.current_task().cancelled():
                    return

                chunk = r.bytes
                if not chunk:
                    break

                if part_count == 1:
                    yield chunk[first_part_cut:last_part_cut]
                    return
                elif current_part == 1:
                    yield chunk[first_part_cut:]
                elif current_part == part_count:
                    yield chunk[:last_part_cut]
                else:
                    yield chunk

                current_part += 1
                if current_part > part_count:
                    return

                offset += chunk_size
                r = await media_session.send(raw.functions.upload.GetFile(location=location, offset=offset, limit=chunk_size))

        except Exception:
            if file_id.dc_id in self.client.media_sessions:
                s = self.client.media_sessions.pop(file_id.dc_id)
                await s.stop()
            return
        finally:
            work_loads[index] -= 1

    async def clean_cache(self):
        while True:
            try:
                await asyncio.sleep(self.clean_timer)
                self.cached_file_ids.clear()
                logging.info(f"Cache cleared. Previous size: {len(self.cached_file_ids)} files")
            except asyncio.CancelledError:
                logging.info("Cache cleaner task cancelled")
                break
            except Exception as e:
                logging.error(f"Error in cache cleaner: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait before retrying
