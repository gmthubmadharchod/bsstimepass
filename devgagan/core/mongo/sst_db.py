from motor.motor_asyncio import AsyncIOMotorClient
from config import SST_DB

client = AsyncIOMotorClient(SST_DB)
db = client["SST_DB"]

collection = db["chats"]


# 💾 SAVE CHAT
async def save_chat(chat_id, title, chat_type):
    await collection.update_one(
        {"_id": chat_id},
        {"$set": {
            "title": title,
            "type": chat_type
        }},
        upsert=True
    )


# 📥 GET ALL
async def get_all_chats():
    chats = []
    async for chat in collection.find():
        chats.append(chat)
    return chats


# ❌ DELETE CHAT
async def delete_chat(chat_id):
    await collection.delete_one({"_id": chat_id})
