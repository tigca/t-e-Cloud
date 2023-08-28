from typing import Any

class database:
    def __init__(self, db) -> None:
        self.db = db

    async def find(self, user: int):
        return await self.db.find_one({'_id': user})

    async def edit(self, user: int, key: str, value: Any):
        return await self.db.update_one({'_id': user}, {'$set': {
            key: value
        }})

    async def insert(self, value: dict):
        return await self.db.insert_one(value)