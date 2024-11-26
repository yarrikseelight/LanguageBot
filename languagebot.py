from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, Application, ContextTypes
from typing import Final
import requests

TOKEN: Final = "TOKEN"
BOT_USERNAME: Final = "@ChineseSmartSysBot"



#COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('instructions here')

async def translate_string(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(translate)

                


#MESSAGES

def translate(text: str) -> str:
    processed: str = text.lower()
    
    payload = {
	"from": "auto",
	"to": "et",
	"text": processed
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "1511cd1ddcmsha1f889405c199c3p137bbfjsn0b8b188e6801",
        "X-RapidAPI-Host": "google-translate113.p.rapidapi.com"
    }
    url = "https://google-translate113.p.rapidapi.com/api/v1/translator/text"
    response = requests.post(url, data=payload, headers=headers)
    translation = response.json().get('trans', 'Translation not found')
    return translation



def handle_answer(text: str):
    return
    


def handle_response(text: str) -> str:
    print("message sent")
    return
    

    


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    print(f"user ({update.message.chat.id}) in {message_type}: '{text}'")

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print("Bot:", response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print (f"Update {update} caused error {context.error}")




if __name__ == "__main__":
    print("starting bot")
    app = Application.builder().token(TOKEN).build()

    #commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quizme", quiz_command))
    app.add_handler(CommandHandler("translate", translate_string))

    

    # #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #errors
    app.add_error_handler(error)

    print("polling")
    app.run_polling(poll_interval=3)




