import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import PREMIUM_DB_URL

mongo = AsyncIOMotorClient(PREMIUM_DB_URL)
db = mongo.settings_premium
col = db.users

# ADD PREMIUM
async def add_settings_premium(user_id, days):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=days)

    data = await col.find_one({"_id": user_id})

    if data:
        await col.update_one({"_id": user_id}, {"$set": {"expire_date": expiry}})
    else:
        await col.insert_one({"_id": user_id, "expire_date": expiry})


# CHECK PREMIUM
async def is_settings_premium(user_id):
    data = await col.find_one({"_id": user_id})

    if not data:
        return False

    expire = data.get("expire_date")

    if expire and expire > datetime.datetime.utcnow():
        return True
    else:
        await col.delete_one({"_id": user_id})
        return False


# REMOVE
async def remove_settings_premium(user_id):
    await col.delete_one({"_id": user_id})


# AUTO CLEAN
async def clean_expired_users():
    current_time = datetime.datetime.utcnow()

    async for data in col.find():
        expire = data.get("expire_date")

        if expire and expire < current_time:
            await col.delete_one({"_id": data["_id"]})
