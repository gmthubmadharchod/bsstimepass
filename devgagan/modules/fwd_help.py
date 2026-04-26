from pyrogram import filters
from devgagan import app


@app.on_message(filters.command("fwdhelp") & filters.private)
async def fwd_help(client, message):

    text = """
🚀 **FORWARD SYSTEM GUIDE**

━━━━━━━━━━━━━━━━━━

📤 **/fwd — Forward Messages**

Format:
/fwd source_chat_id/start-end

Example:
/fwd -1001234567890/1-50

👉 Source channel → ID
👉 Range → messages

━━━━━━━━━━━━━━━━━━

🎯 **Target कहाँ जाएगा?**

✔ Default → DM में आएगा  
✔ Custom → `/fwdsettings` में set करो  

━━━━━━━━━━━━━━━━━━

⚙️ **/fwdsettings — Customize**

✏️ Rename → file name बदलो  
📝 Caption → custom caption जोड़ो  
📌 Chat ID → target set करो  
🔁 Replace → words बदलो  
🚫 Remove → words हटाओ  

━━━━━━━━━━━━━━━━━━

⚡ **Rules**

• Max: 500 messages  
• One process per user  
• Stop → /fwdcancel  

━━━━━━━━━━━━━━━━━━

💎 **Pro Tip**
एक बार settings कर लो  
फिर direct /fwd use करो 😎
"""

    await message.reply(text)
