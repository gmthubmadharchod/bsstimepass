from pyrogram import filters
from devgagan import app
from devgagan.core.mongo.fwd_db import is_premium, is_protected
from pyrogram.errors import FloodWait
import asyncio

MAX_RANGE = 500
DELAY = 1
MAX_RETRY = 2


def parse(text):
    parts = text.split()[1:]

    if len(parts) == 1:
        # /fwd -100xxx/1-25
        source, rng = parts[0].split("/")
        return int(source), None, rng

    elif len(parts) == 2:
        # /fwd -100xxx -100yyy/1-25
        source = int(parts[0])
        target, rng = parts[1].split("/")
        return source, int(target), rng

    return None, None, None


@app.on_message(filters.command("fwd"))
async def fwd(client, message):
    user_id = message.from_user.id

    # 🔒 premium check
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
            "Usage:\n"
            "/fwd -100xxx/1-50\n"
            "/fwd -100xxx -100yyy/1-50"
        )

    # 🔒 protected check
    if await is_protected(source):
        return await message.reply("❌ This channel is protected")

    # 📊 range
    if "-" in rng:
        start, end = map(int, rng.split("-"))
    else:
        start = end = int(rng)

    if end - start + 1 > MAX_RANGE:
        return await message.reply("❌ Max 500 messages allowed")

    send_to = target if target else user_id

    sent = 0
    skipped = 0

    status = await message.reply("🚀 Processing...")

    for msg_id in range(start, end + 1):

        retry = 0
        while retry <= MAX_RETRY:
            try:
                # 🔥 STEALTH MODE (NO FORWARD TAG)
                await client.copy_message(
                    chat_id=send_to,
                    from_chat_id=source,
                    message_id=msg_id
                )

                sent += 1
                await asyncio.sleep(DELAY)
                break

            except FloodWait as fw:
                wait = fw.value + 2
                await status.edit(f"⏳ FloodWait: {wait}s...")
                await asyncio.sleep(wait)

            except Exception:
                retry += 1
                if retry > MAX_RETRY:
                    skipped += 1
                    break
                await asyncio.sleep(1)

        # 📊 progress update
        if (sent + skipped) % 10 == 0:
            await status.edit(f"📤 {sent} | ⏭ {skipped}")

    await status.edit(
        f"""✅ Done

📤 Sent: {sent}
⏭ Skipped: {skipped}
📊 Total: {end-start+1}"""
  )
