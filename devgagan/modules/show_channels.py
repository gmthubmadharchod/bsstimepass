from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.mongo.sst_db import save_chat, get_all_chats, delete_chat


# 🔄 AUTO SAVE (ONLY ADMIN CHATS)
# ✅ FIX: group add kiya + commands untouched
@app.on_message(filters.group | filters.channel, group=10)
async def auto_store(client, message):
    chat = message.chat

    # ❌ commands ko ignore (safe check)
    if message.text and message.text.startswith("/"):
        return

    try:
        member = await client.get_chat_member(chat.id, "me")

        # ✅ only admin chats
        if member.status not in ["administrator", "creator"]:
            return

        await save_chat(
            chat.id,
            chat.title or "Unknown",
            chat.type
        )

    except Exception as e:
        print("AUTO STORE ERROR:", e)


# 📂 SHOW + AUTO CLEAN
@app.on_message(filters.command("showchnls") & filters.user(OWNER_ID))
async def show_channels(client, message):

    chats = await get_all_chats()

    if not chats:
        return await message.reply("❌ No chats stored yet")

    channels = []
    groups = []

    for chat in chats:
        cid = chat.get("_id")
        name = chat.get("title")
        ctype = str(chat.get("type")).lower()

        try:
            member = await client.get_chat_member(cid, "me")

            # ❌ remove if not admin
            if member.status not in ["administrator", "creator"]:
                await delete_chat(cid)
                continue

        except:
            await delete_chat(cid)
            continue

        if "channel" in ctype:
            channels.append((name, cid))
        elif "group" in ctype:
            groups.append((name, cid))

    text = "📢 CHANNELS\n\n"

    for name, cid in channels:
        text += f"{name}\n{cid}\n\n"

    text += "\n👥 GROUPS\n\n"

    for name, cid in groups:
        text += f"{name}\n{cid}\n\n"

    file_name = "channels_groups.txt"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(text)

    await message.reply_document(file_name, caption="📂 Admin Chats List")
