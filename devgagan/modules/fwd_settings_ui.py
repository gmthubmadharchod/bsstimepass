from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from devgagan import app
from devgagan.core.mongo.fwd_settings_db import (
    set_setting, remove_setting, reset_all
)
from devgagan.core.mongo.fwd_db import is_premium
import time

pending = {}
TIMEOUT = 60  # seconds


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


# 🎯 SETTINGS PANEL
@app.on_message(filters.command("fwdsettings"))
async def settings(client, message):
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

        [InlineKeyboardButton("💎✨ BUY PREMIUM ✨💎", url="https://t.me/sonuporsa")],
        [InlineKeyboardButton("♻️ RESET ALL", callback_data="resetall")]
    ])

    await message.reply_text("⚙️ FWD Settings Panel", reply_markup=buttons)


# 🔘 CALLBACK HANDLER
@app.on_callback_query()
async def callbacks(client, cq):
    user_id = cq.from_user.id
    data = cq.data

    # 🔒 premium check
    if not await is_premium(user_id):
        return await cq.message.reply(
            "🔒 FWD Premium Required\n\n💎 Buy 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")]
            ])
        )

    try:
        # 🔹 set actions
        if data in ["setrename", "setcaption", "setchat", "setreplace", "setremove"]:
            pending[user_id] = {
                "type": data,
                "time": time.time()
            }

            cancel_btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])

            if data == "setrename":
                await cq.message.reply("Send rename tag\n\nUse /fcancel to cancel", reply_markup=cancel_btn)

            elif data == "setcaption":
                await cq.message.reply("Send caption\n\nUse /fcancel to cancel", reply_markup=cancel_btn)

            elif data == "setchat":
                await cq.message.reply("Send chat id (-100...)\n\nUse /fcancel to cancel", reply_markup=cancel_btn)

            elif data == "setreplace":
                await cq.message.reply("Send:\nold,new\nabc,xyz\n\nUse /fcancel to cancel", reply_markup=cancel_btn)

            elif data == "setremove":
                await cq.message.reply("Send words line by line\n\nUse /fcancel to cancel", reply_markup=cancel_btn)

        # 🔥 cancel button
        elif data == "cancel":
            if user_id in pending:
                del pending[user_id]
            await cq.answer("Cancelled", show_alert=True)

        # 🔹 reset options
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


# ❌ MANUAL CANCEL COMMAND
@app.on_message(filters.command("fcancel"))
async def cancel_cmd(client, message):
    user_id = message.from_user.id

    if user_id in pending:
        del pending[user_id]
        await message.reply("❌ FWD Cancelled")
    else:
        await message.reply("Nothing to cancel")


# 📩 INPUT HANDLER
@app.on_message(filters.text & ~filters.command(["fwd", "fwdsettings", "fcancel"]))
async def input_handler(client, message):
    user_id = message.from_user.id

    if user_id not in pending:
        return

    # ⏱ timeout check
    if time.time() - pending[user_id]["time"] > TIMEOUT:
        del pending[user_id]
        return await message.reply("⌛ Timeout. Try again")

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

    del pending[user_id]
