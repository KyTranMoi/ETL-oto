import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import json
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Định nghĩa các trạng thái của ConversationHandler
PASSWORD = 0

# Định nghĩa mật khẩu đúng cần nhập
CORRECT_PASSWORD = "192.168.1.1"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bắt đầu cuộc hội thoại và yêu cầu người dùng nhập mật khẩu."""
    await update.message.reply_text(
        "Vui lòng nhập mật khẩu:"
    )
    return PASSWORD

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Kiểm tra mật khẩu người dùng nhập."""
    password = update.message.text
    if password == CORRECT_PASSWORD:
        await update.message.reply_text(
            f"Mật khẩu chính xác! Group ID là: {update.message.chat_id}"   
        )
        with open('groupid.json', 'r+') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

            data.append({"group_id": str(update.message.chat_id)})

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Mật khẩu sai. Vui lòng thử lại."
        )
        return PASSWORD

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7305659457:AAH7iMjozC4D5msQJGKLq3N9FU-Fc8njvds").build()

    # Add conversation handler with the states PASSWORD
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
