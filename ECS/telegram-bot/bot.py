import google.generativeai as genai
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import json
import os

API_KEY = os.environ.get('G_TOKEN')
token = os.environ.get('T_TOKEN')

def chat_gpt(user_data):
    genai.configure(api_key=API_KEY)

    model = genai.GenerativeModel(model_name="gemini-1.0-pro-latest")
    response = model.generate_content(user_data)
        
    try:
        msg = response.text
    except:
        for candidate in response.candidates:
            msg = [part.text for part in candidate.content.parts]
            msg = " ".join(msg)
        
    return(msg)

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    text_start = "Hello there. Provide any topic to learn."
    await update.message.reply_text(text_start)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    text_help = "This bot is designed to assist you in looking up and understanding any topic."
    await update.message.reply_text(text_help)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_response_r = chat_gpt(update.message.text)
    await update.message.reply_text(text_response_r, parse_mode="markdown")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    while True:
        main()