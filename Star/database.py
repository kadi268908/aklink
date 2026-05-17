from config import Var
import motor.motor_asyncio


class Database:
    def __init__(self, uri: str, database_name: str):
        # Create client with connection timeout and pool settings
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second connection timeout
            socketTimeoutMS=30000,  # 30 second socket timeout
            maxPoolSize=50,  # Connection pool size
            retryWrites=True
        )
        self.prest = self._client[database_name]

        self.user = self.prest.users
        self.words = self.prest.words
        self.sudo = self.prest.sudo
        self.remsudo = self.prest.remsudo

        self.channel = self.prest.channel
        self.remchannel = self.prest.remchannel

        self.channel_ids = []

    async def close(self):
        """Properly close database connection"""
        try:
            self._client.close()
        except Exception as e:
            import logging
            logging.error(f"Error closing database connection: {e}")

    def new_user(self, user_id: int):
        return {"_id": user_id, "words": [], "sudo": False}

    async def add_user(self, user_id: int):
        if not await self.is_user_exist(user_id):
            await self.user.insert_one(self.new_user(user_id))

    async def is_user_exist(self, user_id: int):
        found = await self.user.find_one({"_id": int(user_id)})
        return bool(found)

    async def present_user(self, user_id: int):
        return await self.is_user_exist(user_id)

    async def full_userbase(self):
        return [doc["_id"] async for doc in self.user.find({})]

    async def del_user(self, user_id: int):
        await self.user.delete_many({"_id": int(user_id)})

    async def add_word(self, user_id: int, word: str):
        await self.user.update_one(
            {"_id": int(user_id)},
            {"$addToSet": {"words": word}},
            upsert=True,
        )

    async def remove_word(self, user_id: int, word: str):
        await self.user.update_one(
            {"_id": int(user_id)},
            {"$pull": {"words": word}},
        )

    async def get_words(self, user_id: int):
        user = await self.user.find_one({"_id": int(user_id)})
        if user and "words" in user:
            return user["words"]
        return []

    async def clear_words(self, user_id: int):
        await self.user.update_one(
            {"_id": int(user_id)},
            {"$set": {"words": []}},
            upsert=True,
        )

    async def add_sudo(self, user_id: int):
        await self.user.update_one(
            {"_id": int(user_id)},
            {"$set": {"sudo": True}},
            upsert=True,
        )
        await self.sudo.update_one(
            {"_id": int(user_id)},
            {"$set": {"sudo": True}},
            upsert=True,
        )
        await self.remsudo.delete_many({"_id": int(user_id)})

    async def remove_sudo(self, user_id: int):
        await self.user.update_one(
            {"_id": int(user_id)},
            {"$set": {"sudo": False}},
        )
        await self.remsudo.update_one(
            {"_id": int(user_id)},
            {"$set": {"sudo": False}},
            upsert=True,
        )
        await self.sudo.delete_many({"_id": int(user_id)})

    async def get_sudo_users(self):
        users = self.user.find({"sudo": True})
        return [u["_id"] async for u in users]

    async def add_channel(self, channel_id: int):
        channel_id = int(channel_id)
        await self.channel.update_one(
            {"_id": channel_id},
            {"$set": {"channel": True}},
            upsert=True,
        )
        await self.remchannel.delete_many({"_id": channel_id})
        if channel_id not in self.channel_ids:
            self.channel_ids.append(channel_id)

    async def remove_channel(self, channel_id: int):
        channel_id = int(channel_id)
        await self.remchannel.update_one(
            {"_id": channel_id},
            {"$set": {"channel": False}},
            upsert=True,
        )
        await self.channel.delete_many({"_id": channel_id})
        if channel_id in self.channel_ids:
            self.channel_ids.remove(channel_id)

    async def get_channels(self, refresh: bool = True):
        if not refresh and self.channel_ids:
            return self.channel_ids
        cursor = self.channel.find({"channel": True})
        self.channel_ids = [c["_id"] async for c in cursor]
        return self.channel_ids

    async def get_db_size(self):
        stats = await self.prest.command("dbstats")
        return stats["dataSize"]


db1 = Database(Var.DATABASE_URI, Var.DATABASE_NAME)
