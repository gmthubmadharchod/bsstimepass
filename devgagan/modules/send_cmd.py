from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, ChatAdminRequired
import asyncio

DEFAULT_DELAY = 3
MAX_RETRY = 2


def extract_chat(link):
    if "t.me/c/" in link:
        parts = link.split("/")
        return int("-100" + parts[-2])
    elif "t.me/" in link:
        return link.split("/")[-2]
    return None


def extract_range(link):
    last_part = link.split("/")[-1]

    if "-" in last_part:
        start, end = last_part.split("-")
        return int(start), int(end)
    else:
        return int(last_part), int(last_part)


@app.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_cmd(client, message):
    try:
        _, user_id, link = message.text.split()
        user_id = int(user_id)
    except:
        return await message.reply("Usage:\n/send user_id link")

    chat = extract_chat(link)
    start, end = extract_range(link)

    if not chat:
        return await message.reply("Invalid link")

    sent = 0
    skipped = 0

    status = await message.reply("🚀 Sending started...")

    for msg_id in range(start, end + 1):

        retry = 0
        while retry <= MAX_RETRY:
            try:
                await client.copy_message(
                    chat_id=user_id,
                    from_chat_id=chat,
                    message_id=msg_id
                )

                sent += 1
                await asyncio.sleep(DEFAULT_DELAY)
                break  # success → exit retry loop

            # ⏳ FloodWait → wait + retry
            except FloodWait as fw:
                wait_time = fw.value + 2
                await status.edit(f"⏳ FloodWait: Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)

            # ❌ User blocked → stop completely
            except UserIsBlocked:
                await status.edit("❌ User has blocked the bot. Stopping...")
                return

            # ❌ Bot not admin → stop completely
            except (PeerIdInvalid, ChatAdminRequired):
                await status.edit("❌ Bot is not admin in that channel or invalid link.")
                return

            # 🔁 Other errors → retry
            except Exception:
                retry += 1
                if retry > MAX_RETRY:
                    skipped += 1
                    break
                await asyncio.sleep(1)

        # 📊 progress update
        if (sent + skipped) % 5 == 0:
            await status.edit(f"📤 Sent: {sent} | ⏭ Skipped: {skipped}")

    await status.edit(
        f"""✅ Done

📤 Sent: {sent}
⏭ Skipped: {skipped}
📊 Total: {end-start+1}"""
                                  )
