from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, Application, ContextTypes
from typing import Final
import requests
import random
from fuzzywuzzy import fuzz
import pinyin
from data.wordlist import data

 

TOKEN: Final = ""
BOT_USERNAME: Final = "@ChineseSmartSysBot"



###########################################################################
# COMMANDS (these take the command given by user and adds the functionality)
###########################################################################
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('instructions here')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('instructions here')
    

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question_number' not in context.user_data: 
        context.user_data['current_question_number'] = 0
        context.user_data['current_quiz_score'] = 0 
        
    while context.user_data['current_question_number'] < 5:
        word_to_quiz = random.choice(data)
        chinese_word = word_to_quiz['simplified']
        correct_answer = word_to_quiz['definitions']
        pinyin = word_to_quiz["pinyin"]
        context.user_data['correct_translation'] = correct_answer
        context.user_data['has_quizzed'] = True 
        context.user_data['current_question_number'] += 1
        await update.message.reply_text(f"Translate this word to English: {chinese_word} ({pinyin})")
        return
        

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args)  # Get the text to translate from the user's message
    if text:
        translated_text = translate(text) 
        await update.message.reply_text(translated_text)  
    else:
        await update.message.reply_text("Please provide some text to translate.")
                
                
                
###########################################################################
#MESSAGE (This function runs when normal message is sent)
###########################################################################
async def check_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        answer_is_true = False
        if 'has_quizzed' in context.user_data and context.user_data['has_quizzed']:
            user_answer = update.message.text.strip().lower()
            
            # Retrieve the correct translation from user data
            correct_translation = context.user_data.get('correct_translation')
            
            for i in range(0, len(correct_translation)):
                fuzzy_ratio = fuzz.ratio(correct_translation[i], user_answer)
                if fuzzy_ratio > 80:
                    answer_is_true = True
                
            # Check if the answer is correct
            if answer_is_true:
                context.user_data['current_quiz_score'] += 1
                await update.message.reply_text(f"Correct! ✅ The correct answer was:  {', '.join(correct_translation)}.")
            else:
                await update.message.reply_text(f"❌ The correct translation was:  {', '.join(correct_translation)}.")
            context.user_data['has_quizzed'] = False
            
            if context.user_data['current_question_number'] == 5:
                context.user_data['current_question_number'] = 0
                await update.message.reply_text(f"You have completed your quiz! 🎉 You scored {context.user_data['current_quiz_score']}/5.")
                context.user_data['current_quiz_score'] = 0 
                return
            await quiz_command(update, context)
        else:
            await update.message.reply_text(f"You have no ongoing quizzes. Use '/help' to get instructions for the bots use")
   




###########################################################################
#HELPERS (helper functions can be transferred to other .py file later)
###########################################################################

#Function that uses google translate API to return the translation
def translate(text: str) -> str:
    processed: str = text.lower()
    
    payload = {
	"from": "auto",
	"to": "zh",
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
    translation_string = f"{translation} ( {pinyin.get(translation, delimiter=' ')})"
    return translation_string



#Error function prints error to terminal 
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print (f"Update {update} caused error {context.error}")

    





#Starts the bot and defines the rules for the bot
if __name__ == "__main__":
    print("starting bot")
    app = Application.builder().token(TOKEN).build()

    #commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quizme", quiz_command))
    app.add_handler(CommandHandler("translate", translate_command))

    

    # #messages
    app.add_handler(MessageHandler(filters.TEXT, check_translation))

    #errors
    app.add_error_handler(error)

    print("polling")
    app.run_polling(poll_interval=3)




