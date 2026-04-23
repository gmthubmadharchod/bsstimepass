from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from datetime import datetime, timedelta
import pytz

from devgagan.core.mongo.settings_premium_db import (
    add_settings_premium,
    remove_settings_premium,
    col
)

# ADD PREMIUM
@app.on_message(filters.command("add_premium") & filters.user(OWNER_ID))
async def add_premium_cmd(client, message):
    user_id = int(message.command[1])
    days = int(message.command[2])

    await add_settings_premium(user_id, days)

    await message.reply(f"✅ Settings Premium Added for {days} days")

    # user ko message
    try:
        await client.send_message(
            user_id,
            f"""🎉 **Premium Activated!**

⚙️ Settings Premium Enabled  
⏳ Valid for: {days} days  

Enjoy 🚀"""
        )
    except:
        pass


# REMOVE
@app.on_message(filters.command("remove_premium") & filters.user(OWNER_ID))
async def remove_premium_cmd(client, message):
    user_id = int(message.command[1])

    await remove_settings_premium(user_id)
    await message.reply("❌ Settings Premium Removed")


# MY PLAN
@app.on_message(filters.command("my_settings_plan"))
async def my_settings_plan(client, message):
    user_id = message.from_user.id

    data = await col.find_one({"_id": user_id})

    if not data:
        return await message.reply("❌ No active settings premium")

    expiry = data.get("expire_date")

    if not expiry:
        return await message.reply("❌ No expiry found")

    now = datetime.utcnow()
    time_left = expiry - now

    if time_left.total_seconds() <= 0:
        await message.reply("❌ Premium expired")
        return

    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    await message.reply(
        f"""⚙️ **Your Settings Premium**

⏳ Remaining:
{days} days, {hours} hours, {minutes} minutes

📅 Expiry:
{expiry.strftime("%d-%m-%Y %H:%M:%S")}"""
)
