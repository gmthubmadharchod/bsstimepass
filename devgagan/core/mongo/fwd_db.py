from motor.motor_asyncio import AsyncIOMotorClient
from config import APNA_DB
import datetime

mongo = AsyncIOMotorClient(APNA_DB)
db = mongo.fwd_system

premium_col = db.premium
protect_col = db.protected


async def add_premium(user_id, days):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    await premium_col.update_one(
        {"_id": user_id},
        {"$set": {"expire": expire}},
        upsert=True
    )


async def is_premium(user_id):
    data = await premium_col.find_one({"_id": user_id})
    if not data:
        return False

    if data["expire"] > datetime.datetime.utcnow():
        return True
    else:
        await premium_col.delete_one({"_id": user_id})
        return False


async def add_protect(chat_id):
    await protect_col.update_one({"_id": chat_id}, {"$set": {}}, upsert=True)


async def remove_protect(chat_id):
    await protect_col.delete_one({"_id": chat_id})


async def is_protected(chat_id):
    return await protect_col.find_one({"_id": chat_id}) is not None


async def get_all_protect():
    return protect_col.find({})
