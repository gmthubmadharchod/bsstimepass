from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from devgagan import app
from devgagan.core.mongo.fwd_settings_db import (
    set_setting, remove_setting, reset_all
)
from devgagan.core.mongo.fwd_db import is_premium

# 🔥 pending state
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


# 🎯 SETTINGS CMD
@app.on_message(filters.command("fwdsettings"))
async def settings(client, message):
    user_id = message.from_user.id

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Rename Tag", callback_data="setrename"),
            InlineKeyboardButton("❌ Reset", callback_data="remove_rename")
        ],
        [
            InlineKeyboardButton("📝 Caption", callback_data="setcaption"),
            InlineKeyboardButton("❌ Reset", callback_data="remove_caption")
        ],
        [
            InlineKeyboardButton("📌 Chat ID", callback_data="setchat"),
            InlineKeyboardButton("❌ Reset", callback_data="remove_target")
        ],
        [
            InlineKeyboardButton("🔁 Replace", callback_data="setreplace"),
            InlineKeyboardButton("❌ Reset", callback_data="remove_replace")
        ],
        [
            InlineKeyboardButton("🚫 Remove Words", callback_data="setremove"),
            InlineKeyboardButton("❌ Reset", callback_data="clear_words")
        ],
        [
            InlineKeyboardButton("💎✨ BUY PREMIUM ✨💎", url="https://t.me/sonuporsa")
        ],
        [
            InlineKeyboardButton("♻️ RESET ALL", callback_data="resetall")
        ]
    ])

    await message.reply_text("⚙️ FWD Settings Panel", reply_markup=buttons)


# 🔘 CALLBACK HANDLER
@app.on_callback_query()
async def callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    # 🔒 premium check
    if not await is_premium(user_id):
        return await callback_query.message.reply(
            "🔒 FWD Premium Required\n\n💎 Buy 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 BUY PREMIUM", url="https://t.me/sonuporsa")]
            ])
        )

    try:
        # 🔹 set rename
        if data == "setrename":
            pending[user_id] = "rename"
            await callback_query.message.reply("Send rename tag (example: _Sonu)")

        elif data == "setcaption":
            pending[user_id] = "caption"
            await callback_query.message.reply("Send caption")

        elif data == "setchat":
            pending[user_id] = "target"
            await callback_query.message.reply("Send chat id (-100xxxx)")

        elif data == "setreplace":
            pending[user_id] = "replace"
            await callback_query.message.reply("Send:\nold,new\nabc,xyz")

        elif data == "setremove":
            pending[user_id] = "remove"
            await callback_query.message.reply("Send words line by line")

        # 🔹 RESET
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

        await callback_query.answer("Done")

    except:
        await callback_query.answer("Error")


# 📩 INPUT HANDLER
@app.on_message(filters.text & ~filters.command(["fwd", "fwdsettings"]))
async def input_handler(client, message):
    user_id = message.from_user.id

    if user_id not in pending:
        return

    key = pending[user_id]
    text = message.text.strip()

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

        await message.reply("✅ Saved")

    except:
        await message.reply("❌ Invalid input")

    del pending[user_id]
