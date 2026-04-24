from pyrogram import filters
from devgagan import app
from devgagan.core.mongo.fwd_db import is_premium, is_protected
from pyrogram.errors import FloodWait
import asyncio

MAX_RANGE = 500
DELAY = 3


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


@app.on_message(filters.command("fwd"))
async def fwd(client, message):
    user_id = message.from_user.id

    if not await is_premium(user_id):
        return await message.reply(
            """🔒 FWD LOCKED

💎 ₹50 / 10 Days  
📦 500 files limit  

👉 https://t.me/sonuporsa"""
        )

    source, target, rng = parse(message.text)

    if source is None:
        return await message.reply(
            "/fwd -100xxx/1-50\n/fwd -100xxx -100yyy/1-50"
        )

    if await is_protected(source):
        return await message.reply("❌ Protected channel")

    if "-" in rng:
        start, end = map(int, rng.split("-"))
    else:
        start = end = int(rng)

    if end - start + 1 > MAX_RANGE:
        return await message.reply("❌ Max 500")

    send_to = target if target else user_id

    sent = 0
    skipped = 0

    msg = await message.reply("🚀 Forwarding...")

    for i in range(start, end + 1):
        try:
            await client.forward_messages(send_to, source, i)
            sent += 1
            await asyncio.sleep(DELAY)

        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)

        except:
            skipped += 1

    await msg.edit(f"✅ Done\n📤 {sent}\n⏭ {skipped}")
