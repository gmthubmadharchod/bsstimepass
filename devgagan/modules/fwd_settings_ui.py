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


def buy_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")]
    ])


# ⚙️ SETTINGS PANEL
@app.on_message(filters.command("fwdsettings") & filters.private)
async def settings(client, message):
    user_id = message.from_user.id

    if not await is_premium(user_id):
        return await message.reply("🚫 FWD Settings Locked", reply_markup=buy_btn())

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Rename", callback_data="fwd_setrename"),
         InlineKeyboardButton("❌ Reset", callback_data="fwd_remove_rename")],

        [InlineKeyboardButton("📝 Caption", callback_data="fwd_setcaption"),
         InlineKeyboardButton("❌ Reset", callback_data="fwd_remove_caption")],

        [InlineKeyboardButton("📌 Chat ID", callback_data="fwd_setchat"),
         InlineKeyboardButton("❌ Reset", callback_data="fwd_remove_target")],

        [InlineKeyboardButton("🔁 Replace", callback_data="fwd_setreplace"),
         InlineKeyboardButton("❌ Reset", callback_data="fwd_remove_replace")],

        [InlineKeyboardButton("🚫 Remove Words", callback_data="fwd_setremove"),
         InlineKeyboardButton("❌ Reset", callback_data="fwd_clear_words")],

        [InlineKeyboardButton("♻️ RESET ALL", callback_data="fwd_resetall")]
    ])

    await message.reply("⚙️ FWD Settings Panel", reply_markup=buttons)


# 🔘 CALLBACK HANDLER (PREFIX FIX)
@app.on_callback_query(filters.regex("^fwd_"))
async def callbacks(client, cq):
    user_id = cq.from_user.id
    data = cq.data.replace("fwd_", "")

    if not await is_premium(user_id):
        await cq.message.reply("🚫 Premium Required", reply_markup=buy_btn())
        return await cq.answer()

    try:
        if data in ("setrename", "setcaption", "setchat", "setreplace", "setremove"):
            pending[user_id] = {"type": data, "time": time.time()}

            await cq.message.reply("✏️ Send value (use /fcancel to cancel)")

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

        await cq.answer("✅ Done")

    except Exception as e:
        print(e)
        await cq.answer("Error")


# ❌ CANCEL
@app.on_message(filters.command("fcancel"))
async def cancel_cmd(client, message):
    pending.pop(message.from_user.id, None)
    await message.reply("❌ Cancelled")


# 📩 INPUT
@app.on_message(filters.private & filters.text)
async def input_handler(client, message):
    if message.text.startswith("/"):
        return

    user_id = message.from_user.id

    if user_id not in pending:
        return

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
            await set_setting(user_id, "replace", {})

        elif key == "setremove":
            await set_setting(user_id, "remove", [text])

        await message.reply("✅ Saved")

    except:
        await message.reply("❌ Invalid input")

    pending.pop(user_id, None)
