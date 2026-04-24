from pyrogram import filters
from devgagan import app
from devgagan.core.mongo.fwd_db import is_premium, is_protected
from devgagan.core.mongo.fwd_settings_db import get_settings
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import asyncio
import os

MAX_RANGE = 500
DELAY = 5

# 🔥 Forward control
fwd_users = {}


def parse(text):
    parts = text.split()[1:]

    if len(parts) == 1:
        source, rng = parts[0].split("/")
        return int(source), None, rng

    elif len(parts) == 2:
        source = int(parts[0])
        target, rng = parts[1].split("/")
        return source, int(target), rng

    return None, None, None


def apply_caption(caption, settings):
    if not caption:
        caption = ""

    if settings.get("replace"):
        for k, v in settings["replace"].items():
            caption = caption.replace(k, v)

    if settings.get("remove"):
        for w in settings["remove"]:
            caption = caption.replace(w, "")

    if settings.get("caption"):
        caption += "\n\n" + settings["caption"]

    return caption


def apply_rename(original_name, tag):
    if not original_name or not tag:
        return original_name

    name, ext = os.path.splitext(original_name)
    return f"{name}{tag}{ext}"


@app.on_message(filters.command("fwd"))
async def fwd(client, message):
    user_id = message.from_user.id

    # 🔥 already running check
    if fwd_users.get(user_id):
        return await message.reply(
            "⚠️ One process is already running\n\n"
            "Please wait to complete it\n"
            "OR use /fwdcancel to stop and start new"
        )

    # 🔒 premium check
    if not await is_premium(user_id):
        return await message.reply(
            "🚫 FWD Locked\n\n💎 Upgrade to Premium 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")]
            ])
        )

    source, target, rng = parse(message.text)

    if source is None:
        return await message.reply("Invalid format\nUse: /fwd -100xxx/1-10")

    if await is_protected(source):
        return await message.reply("❌ Source Channel is Protected")

    settings = await get_settings(user_id)

    if target and await is_protected(target):
        return await message.reply("❌ Target Channel is Protected")

    if not target and settings.get("target"):
        if await is_protected(settings["target"]):
            return await message.reply("❌ Saved Target is Protected")

    # 🎯 target
    if target:
        send_to = target
    elif settings.get("target"):
        send_to = settings["target"]
    else:
        send_to = user_id

    # 🔢 range
    if "-" in rng:
        start, end = map(int, rng.split("-"))
    else:
        start = end = int(rng)

    if end - start + 1 > MAX_RANGE:
        return await message.reply("Max 500")

    # 🔥 mark active
    fwd_users[user_id] = True

    status = await message.reply("🚀 Forwarding Started...\nUse /fwdcancel to stop")

    for i in range(start, end + 1):

        # ❌ stop check
        if not fwd_users.get(user_id):
            await status.edit("❌ Forwarding Cancelled")
            fwd_users.pop(user_id, None)
            return

        try:
            msg = await client.get_messages(source, i)

            caption = apply_caption(msg.caption, settings)

            file_name = None
            if msg.document:
                file_name = apply_rename(msg.document.file_name, settings.get("rename"))
            elif msg.video:
                file_name = apply_rename(msg.video.file_name or "video.mp4", settings.get("rename"))

            try:
                if msg.video:
                    await client.send_video(send_to, msg.video.file_id, caption=caption, file_name=file_name)

                elif msg.document:
                    await client.send_document(send_to, msg.document.file_id, caption=caption, file_name=file_name)

                elif msg.photo:
                    await client.send_photo(send_to, msg.photo.file_id, caption=caption)

                else:
                    await client.send_message(send_to, caption)

            except:
                if send_to != user_id:
                    if msg.video:
                        await client.send_video(user_id, msg.video.file_id, caption=caption, file_name=file_name)
                    elif msg.document:
                        await client.send_document(user_id, msg.document.file_id, caption=caption, file_name=file_name)
                    elif msg.photo:
                        await client.send_photo(user_id, msg.photo.file_id, caption=caption)
                    else:
                        await client.send_message(user_id, caption)

            await asyncio.sleep(DELAY)

        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)

        except:
            continue

    await status.edit("✅ Done")
    fwd_users.pop(user_id, None)


# 🔥 STOP COMMAND
@app.on_message(filters.command("fwdcancel"))
async def stop_fwd(client, message):
    user_id = message.from_user.id

    if fwd_users.get(user_id):
        fwd_users[user_id] = False
        await message.reply("❌ Forwarding Stopped Successfully")
    else:
        await message.reply("⚠️ No active forwarding process")
