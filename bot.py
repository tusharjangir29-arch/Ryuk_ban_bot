import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application, ChatMemberHandler, ContextTypes
)

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ⚠️ REPLACE THE TEXT BELOW WITH YOUR ACTUAL BOT TOKEN (keep the quotes!)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# ✅ THE CORRECT CHANNEL ID
CHANNEL_ID = -1003950807710

# --- Telegram Bot Logic ---
async def on_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bans users when they leave or are kicked from the channel."""
    result = update.chat_member
    if not result or result.chat.id != CHANNEL_ID:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    # If the user was a member and is now left/kicked, ban them.
    if new_status in ("left", "kicked") and old_status in ("member", "administrator", "creator"):
        try:
            await context.bot.ban_chat_member(
                chat_id=CHANNEL_ID,
                user_id=user.id,
                revoke_messages=True  # Deletes their past messages
            )
            logger.info(f"✅ Banned user {user.id} ({user.full_name}) for leaving.")
        except Exception as e:
            logger.error(f"❌ Failed to ban user {user.id}: {e}")

def run_bot():
    """Starts the Telegram bot in polling mode."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(ChatMemberHandler(on_chat_member, ChatMemberHandler.CHAT_MEMBER))
    logger.info("🤖 Bot is starting polling...")
    application.run_polling()

# --- Flask Server (For Render Health Checks) ---
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def health():
    return "Bot is running!", 200

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start the web server (Render requires this to keep the service alive)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
