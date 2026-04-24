from telethon import events, Button
from devgagan import gf
from devgagan.core.mongo.fwd_settings_db import (
    set_setting, remove_setting, reset_all
)
from devgagan.core.mongo.fwd_db import is_premium

SET_PIC = "settings.jpg"
MESS = "⚙️ Customize your FWD settings"

# 🔥 pending user states
pending = {}


# 🔁 replace parser
def parse_replace(text):
    lines = text.split("\n")
    rep = {}

    for line in lines:
        if "," in line:
            old, new = line.split(",", 1)
            rep[old.strip()] = new.strip()

    return rep


# 🚫 remove parser
def parse_remove(text):
    return [w.strip() for w in text.split("\n") if w.strip()]


# 📩 command
@gf.on(events.NewMessage(pattern="/fwdsettings"))
async def settings(event):
    user_id = event.sender_id

    buttons = [
        [Button.inline("✏️ Rename Tag", b'setrename'), Button.inline("❌ Reset", b'remove_rename')],
        [Button.inline("📝 Caption", b'setcaption'), Button.inline("❌ Reset", b'remove_caption')],
        [Button.inline("📌 Chat ID", b'setchat'), Button.inline("❌ Reset", b'remove_target')],
        [Button.inline("🔁 Replace Words", b'setreplacement'), Button.inline("❌ Reset", b'remove_replace')],
        [Button.inline("🚫 Remove Words", b'delete'), Button.inline("❌ Reset", b'clear_words')],
        [Button.url("💎✨ BUY PREMIUM ✨💎", "https://t.me/sonuporsa")],
        [Button.inline("♻️ RESET ALL SETTINGS", b'resetall')]
    ]

    await gf.send_file(event.chat_id, file=SET_PIC, caption=MESS, buttons=buttons)


# 🔘 button handler
@gf.on(events.CallbackQuery)
async def callbacks(event):
    user_id = event.sender_id
    is_prem = await is_premium(user_id)

    # 🔒 non-premium
    if not is_prem:
        await event.respond(
            "🔒 FWD Premium Required\n\n💎 Buy Premium 👇",
            buttons=[[Button.url("💎 BUY PREMIUM 💎", "https://t.me/sonuporsa")]]
        )
        return await event.answer()

    data = event.data

    try:
        # 🔹 set rename
        if data == b'setrename':
            pending[user_id] = "rename"
            await event.respond("Send rename tag (example: _Sonu)")
            await event.answer()

        # 🔹 set caption
        elif data == b'setcaption':
            pending[user_id] = "caption"
            await event.respond("Send caption to append")
            await event.answer()

        # 🔹 set chat id
        elif data == b'setchat':
            pending[user_id] = "target"
            await event.respond("Send chat id (example: -100xxxx)")
            await event.answer()

        # 🔹 set replace
        elif data == b'setreplacement':
            pending[user_id] = "replace"
            await event.respond("Send in format:\nold,new\nabc,xyz")
            await event.answer()

        # 🔹 remove words
        elif data == b'delete':
            pending[user_id] = "remove"
            await event.respond("Send words line by line to remove")
            await event.answer()

        # 🔹 resets
        elif data == b'remove_rename':
            await remove_setting(user_id, "rename")
            await event.answer("Rename removed", alert=True)

        elif data == b'remove_caption':
            await remove_setting(user_id, "caption")
            await event.answer("Caption removed", alert=True)

        elif data == b'remove_target':
            await remove_setting(user_id, "target")
            await event.answer("Target removed", alert=True)

        elif data == b'remove_replace':
            await set_setting(user_id, "replace", {})
            await event.answer("Replace cleared", alert=True)

        elif data == b'clear_words':
            await set_setting(user_id, "remove", [])
            await event.answer("Words cleared", alert=True)

        elif data == b'resetall':
            await reset_all(user_id)
            await event.answer("All settings reset", alert=True)

    except:
        await event.answer("Error", alert=True)


# 📥 user input handler
@gf.on(events.NewMessage)
async def input_handler(event):
    user_id = event.sender_id

    if user_id not in pending:
        return

    key = pending[user_id]
    text = event.text.strip()

    try:
        if key == "rename":
            await set_setting(user_id, "rename", text)

        elif key == "caption":
            await set_setting(user_id, "caption", text)

        elif key == "target":
            await set_setting(user_id, "target", int(text))

        elif key == "replace":
            rep = parse_replace(text)
            await set_setting(user_id, "replace", rep)

        elif key == "remove":
            rem = parse_remove(text)
            await set_setting(user_id, "remove", rem)

        await event.reply("✅ Saved")

    except:
        await event.reply("❌ Invalid input")

    del pending[user_id]
