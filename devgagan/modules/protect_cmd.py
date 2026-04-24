from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.fwd_db import add_protect, remove_protect, get_all_protect


@app.on_message(filters.command("pt") & filters.user(OWNER_ID))
async def pt(client, message):
    try:
        chat_id = int(message.command[1])
        await add_protect(chat_id)
        await message.reply("✅ Protected")
    except:
        await message.reply("Usage: /pt -100xxx")


@app.on_message(filters.command("rpt") & filters.user(OWNER_ID))
async def rpt(client, message):
    try:
        chat_id = int(message.command[1])
        await remove_protect(chat_id)
        await message.reply("❌ Removed")
    except:
        await message.reply("Usage: /rpt -100xxx")


@app.on_message(filters.command("showpt") & filters.user(OWNER_ID))
async def showpt(client, message):
    data = await get_all_protect().to_list(None)

    if not data:
        return await message.reply("No protected channels")

    text = "🔒 Protected Channels:\n\n"
    for d in data:
        text += f"{d['_id']}\n"

    await message.reply(text)
