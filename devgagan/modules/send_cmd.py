from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from pyrogram.errors import FloodWait
import asyncio

DELAY = 1
MAX_RETRY = 2


@app.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_cmd(client, message):
    try:
        parts = message.text.split()

        if len(parts) != 4:
            return await message.reply(
                "Usage:\n"
                "/send target_chat source_chat msg_id\n"
                "/send target_chat source_chat 1-25"
            )

        _, target, source, msg_input = parts

        target = int(target)
        source = int(source)

        # 🔥 FIXED LOGIC
        if "-" in msg_input:
            start, end = map(int, msg_input.split("-"))
        else:
            start = end = int(msg_input)

    except:
        return await message.reply("❌ Invalid format")

    sent = 0
    skipped = 0

    status = await message.reply("🚀 Sending...")

    for msg_id in range(start, end + 1):

        retry = 0
        while retry <= MAX_RETRY:
            try:
                await client.copy_message(
                    chat_id=target,
                    from_chat_id=source,
                    message_id=msg_id
                )

                sent += 1
                await asyncio.sleep(DELAY)
                break

            except FloodWait as fw:
                await asyncio.sleep(fw.value + 2)

            except Exception:
                retry += 1
                if retry > MAX_RETRY:
                    skipped += 1
                    break
                await asyncio.sleep(1)

        # progress
        if (sent + skipped) % 5 == 0:
            await status.edit(f"📤 {sent} | ⏭ {skipped}")

    await status.edit(
        f"""✅ Done

📤 Sent: {sent}
⏭ Skipped: {skipped}
📊 Total: {end-start+1}"""
    )
