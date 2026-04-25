from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from devgagan import app
from devgagan.core.mongo.fwd_settings_db import (
    set_setting, remove_setting, reset_all
)
from devgagan.core.mongo.fwd_db import is_premium
import time

pending = {}
TIMEOUT = 60


# 🔁 replace parser
def parse_replace(text):
    rep = {}
    for line in text.split("\n"):
        if "," in line:
            old, new = line.split(",", 1)
            rep[old.strip()] = new.strip()
    return rep


# 🚫 remove parser
def parse_remove(text):
    return [w.strip() for w in text.split("\n") if w.strip()]


# ⚙️ SETTINGS PANEL (🔒 PREMIUM ONLY)
@app.on_message(filters.command("fwdsettings") & filters.private)
async def settings(client, message):
    user_id = message.from_user.id

    # 🔥 ENTRY LEVEL PREMIUM CHECK
    if not await is_premium(user_id):
        return await message.reply(
            "🚫 FWD Settings Locked\n\n💎 Upgrade to Premium 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")]
            ])
        )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Rename Tag", callback_data="setrename"),
         InlineKeyboardButton("❌ Reset", callback_data="remove_rename")],

        [InlineKeyboardButton("📝 Caption", callback_data="setcaption"),
         InlineKeyboardButton("❌ Reset", callback_data="remove_caption")],

        [InlineKeyboardButton("📌 Chat ID", callback_data="setchat"),
         InlineKeyboardButton("❌ Reset", callback_data="remove_target")],

        [InlineKeyboardButton("🔁 Replace", callback_data="setreplace"),
         InlineKeyboardButton("❌ Reset", callback_data="remove_replace")],

        [InlineKeyboardButton("🚫 Remove Words", callback_data="setremove"),
         InlineKeyboardButton("❌ Reset", callback_data="clear_words")],

        [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")],
        [InlineKeyboardButton("♻️ RESET ALL", callback_data="resetall")]
    ])

    await message.reply_text("⚙️ FWD Settings Panel", reply_markup=buttons)


# 🔘 CALLBACK HANDLER
@app.on_callback_query(filters.regex(
    "^(setrename|setcaption|setchat|setreplace|setremove|remove_rename|remove_caption|remove_target|remove_replace|clear_words|resetall|cancel)$"
))
async def callbacks(client, cq):
    user_id = cq.from_user.id
    data = cq.data

    # 🔒 SAFETY PREMIUM CHECK
    if not await is_premium(user_id):
        await cq.message.reply(
            "🔒 Premium Required",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")]
            ])
        )
        return await cq.answer()

    try:
        if data in ("setrename", "setcaption", "setchat", "setreplace", "setremove"):
            pending[user_id] = {"type": data, "time": time.time()}

            cancel_btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])

            msg = {
                "setrename": "Send rename tag (e.g. _Sonu)",
                "setcaption": "Send caption",
                "setchat": "Send chat id (-100...)",
                "setreplace": "Send:\nold,new",
                "setremove": "Send words line by line"
            }

            await cq.message.reply(
                f"{msg[data]}\n\nUse /fcancel to cancel",
                reply_markup=cancel_btn
            )

        elif data == "cancel":
            pending.pop(user_id, None)
            await cq.answer("Cancelled", show_alert=True)
            return

        elif data == "remove_rename":
            await remove_setting(user_id, "rename")

        elif data == "remove_caption":
            await remove_setting(user_id, "caption")

        elif data == "remove_target":
            await remove_setting(user_id, "target")

        elif data == "remove_replace":
            await set_setting(user_id, "replace", {})

        elif data == "clear_words":
            await set_setting(user_id, "remove", [])

        elif data == "resetall":
            await reset_all(user_id)

        await cq.answer("Done")

    except:
        await cq.answer("Error")


# ❌ CANCEL CMD
@app.on_message(filters.command("fcancel") & filters.private)
async def cancel_cmd(client, message):
    user_id = message.from_user.id
    if user_id in pending:
        pending.pop(user_id)
        await message.reply("❌ Cancelled")
    else:
        await message.reply("Nothing to cancel")


# 📩 INPUT HANDLER (SAFE)
@app.on_message(filters.private & filters.text & ~filters.regex(r"^/"))
async def input_handler(client, message):
    if not message.from_user:
        return

    if message.text.startswith("/"):
        return

    user_id = message.from_user.id

    if user_id not in pending:
        return

    if time.time() - pending[user_id]["time"] > TIMEOUT:
        pending.pop(user_id, None)
        return await message.reply("⌛ Timeout")

    key = pending[user_id]["type"]
    text = message.text.strip()

    try:
        if key == "setrename":
            await set_setting(user_id, "rename", text)

        elif key == "setcaption":
            await set_setting(user_id, "caption", text)

        elif key == "setchat":
            await set_setting(user_id, "target", int(text))

        elif key == "setreplace":
            await set_setting(user_id, "replace", parse_replace(text))

        elif key == "setremove":
            await set_setting(user_id, "remove", parse_remove(text))

        await message.reply("✅ Saved")

    except:
        await message.reply("❌ Invalid input")

    finally:
        pending.pop(user_id, None)
