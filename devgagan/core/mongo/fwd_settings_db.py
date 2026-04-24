from motor.motor_asyncio import AsyncIOMotorClient
from config import APNA_DB

# 🔗 Mongo connection
mongo = AsyncIOMotorClient(APNA_DB)

# 📂 DB + Collection
db = mongo.fwd_settings
col = db.users


# 📥 GET USER SETTINGS
async def get_settings(user_id):
    data = await col.find_one({"_id": user_id})
    return data if data else {}


# 💾 SET / UPDATE SINGLE FIELD
async def set_setting(user_id, key, value):
    await col.update_one(
        {"_id": user_id},
        {"$set": {key: value}},
        upsert=True
    )


# ❌ REMOVE SINGLE FIELD
async def remove_setting(user_id, key):
    await col.update_one(
        {"_id": user_id},
        {"$unset": {key: ""}}
    )


# 🔥 RESET ALL SETTINGS
async def reset_all(user_id):
    await col.delete_one({"_id": user_id})
