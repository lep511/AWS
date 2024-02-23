import google.generativeai as genai
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import json
import requests
from pathlib import Path
import os
import logging
import random

msg = ""
start_text = "Hola, soy Marcel, tu asistente virtual en el mundo de Artistes Pintes. Estoy aquí para ayudarte a descubrir las cervezas artesanales únicas y de calidad que tenemos para ofrecer."

resp_error = [
    "Lo siento, pero no puedo ayudarte con eso ahora mismo.",
    "No tengo la información que necesitas en este momento.",
    "No puedo ayudarte con eso.",
    "Lo siento, pero no tengo los recursos para ayudarte con eso.",
    "No puedo ayudarte con eso.",
    "Lo siento, pero no puedo ayudarte con eso.",
    "No puedo ayudarte con eso."
]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

API_KEY = os.environ.get('G_TOKEN')
token = os.environ.get('T_TOKEN')

with open('text_assist.txt', 'r') as f:
    text_assist = f.read()

history_chat = [
    {
        "role": "user",
        "parts": [text_assist]
    },
    {
        "role": "model",
        "parts": [start_text]
    }
]


def fix_text(text):
    # .replace("*", "\\*")
    return text.replace("* **", "\n\n**").replace("_", "\\_").replace("[", "\\[").replace("`", "\\`")
    

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(start_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    text_help = "This bot is designed to assist you in looking up and understanding any topic."
    await update.message.reply_text(text_help)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    genai.configure(api_key=API_KEY)
    
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 2048,
    }
    
    model = genai.GenerativeModel(model_name="gemini-1.0-pro-latest",
                generation_config=generation_config
    )
    
    chat = model.start_chat(history=history_chat)
    response = chat.send_message(update.message.text, stream=True)
    rest_text = ""
       
    for chunk in response:
        try:
            if len(chunk.text) > 10:
                if "\n" in chunk.text:
                    text_part = chunk.text.split("\n")
                    full_response = fix_text(rest_text + text_part[0])
                    await update.message.reply_text(full_response, parse_mode="markdown")
                    rest_text = ""
                    for part in text_part[1:]:
                        rest_text += "\n" + part
                else:
                    rest_text += chunk.text
            else:
                rest_text += chunk.text
        except:
            for candidate in chunk.candidates:
                msg = [part.text for part in candidate.content.parts]
                msg = " ".join(msg)
                rest_text += msg
    
    if len(rest_text) > 10:
        rest_text = fix_text("\n\n" + rest_text)
        await update.message.reply_text(rest_text, parse_mode="markdown")       
    
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest")
    
    user = update.message.from_user
    photo_name = "telegram-bot-image.jpeg"
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(photo_name)
    logger.info("Photo of %s: %s", user.first_name, photo_name)
    
    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": Path(photo_name).read_bytes()
        }
    ]
    
    prompt_parts = [
        "Extrae el nombre y tipo de cerveza y compara con nuestros productos.\n",
        text_assist,
        image_parts[0]
    ]
    
    response = model.generate_content(prompt_parts)    
    
    try:
        msg = response.text
    except:
        for candidate in response.candidates:
            msg = [part.text for part in candidate.content.parts]
            msg = " ".join(msg)
        
    if not msg:
        text_response_r = random.choice(resp_error)
    
    await update.message.reply_text(msg, parse_mode="markdown")
  
    
def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    application.add_handler(MessageHandler(filters.PHOTO, image_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    while True:
        main()
