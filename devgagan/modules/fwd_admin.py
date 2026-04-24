from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.fwd_db import premium_col


@app.on_message(filters.command("remfwd") & filters.user(OWNER_ID))
async def remove_fwd(client, message):
    try:
        _, user_id = message.text.split()
        user_id = int(user_id)
    except:
        return await message.reply("Usage:\n/remfwd user_id")

    result = await premium_col.delete_one({"_id": user_id})

    if result.deleted_count == 0:
        await message.reply("⚠️ User already not premium")
    else:
        await message.reply("❌ FWD Premium Removed")
