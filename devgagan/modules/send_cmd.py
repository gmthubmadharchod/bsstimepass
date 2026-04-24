from pyrogram import filters
from devgagan import app
from config import OWNER_ID

@app.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_cmd(client, message):
    try:
        _, target, source, msg_id = message.text.split()

        target = int(target)
        source = int(source)
        msg_id = int(msg_id)

    except:
        return await message.reply(
            "Usage:\n/send target source msg_id"
        )

    try:
        await client.copy_message(
            chat_id=target,
            from_chat_id=source,
            message_id=msg_id
        )

        await message.reply("✅ Sent")

    except Exception as e:
        await message.reply(f"❌ {e}")
