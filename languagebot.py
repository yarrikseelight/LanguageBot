from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, Application, ContextTypes
from typing import Final
from openai import OpenAI
import random
import copy
import datetime
from data.wordlist import wordlist
from helper_functions import translate, initialize_to_study, add_new_word, check_answer, get_example_sentences




 

TOKEN: Final = ""
client = OpenAI(api_key="")
BOT_USERNAME: Final = "@ChineseSmartSysBot"
data = copy.deepcopy(wordlist)


###########################################################################
# COMMANDS (these take the command given by user and adds the functionality)
###########################################################################
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Use '/quizme' to start quizzing!📚"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('instructions here')
    

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'to_study' not in context.user_data:
        context.user_data['to_study'] = []
        initialize_to_study(context, data)
        context.user_data['to_revise'] = []
        
    if 'current_question_number' not in context.user_data: 
        context.user_data['current_question_number'] = 0
        context.user_data['current_quiz_score'] = 0 
        
    while context.user_data['current_question_number'] < 5:
        word_to_quiz = random.choice(context.user_data['to_study'])
        print(f"Currently quizzing: {word_to_quiz}")
        chinese_word = word_to_quiz['simplified']
        pinyin = word_to_quiz["pinyin"]
        context.user_data['word_last_quizzed'] = word_to_quiz
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
        await update.message.reply_text("Please provide some text to translate eg. '/translate My name is John")
                
                
                
###########################################################################
#MESSAGE (This function runs when normal message is sent)
###########################################################################
async def check_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        answer_is_true = False
        if 'has_quizzed' in context.user_data and context.user_data['has_quizzed']: #checks that we have ongoing quiz
            user_answer = update.message.text.strip().lower()
            
            # Retrieve the correct translation from user data
            word_last_quizzed = context.user_data.get('word_last_quizzed')
            correct_translation = word_last_quizzed['definitions']
        
            #check answer
            answer_is_true = check_answer(correct_translation, user_answer)
                
            # Check if the answer is correct
            if answer_is_true:
                context.user_data['current_quiz_score'] += 1
                if word_last_quizzed['correct_last_time'] != str(datetime.date.today()):  #Allows only to add one to the score per day
                    word_last_quizzed['score'] += 1
                word_last_quizzed['correct_last_time'] = str(datetime.date.today())
                
                if word_last_quizzed['score'] >= 3: 
                    context.user_data['to_revise'].append(word_last_quizzed)
                    context.user_data['to_study'].remove(word_last_quizzed)
                    await update.message.reply_text(f"Great!✨ You have mastered the word: {word_last_quizzed['simplified']}.")
                    add_new_word(context, data)
                    print(f"now in revision list: {context.user_data['to_revise']} and in study: {context.user_data['to_study']}")
                else:
                    await update.message.reply_text(f"Correct! ✅ The correct answer was:  {', '.join(correct_translation)}.")
            else:
                if word_last_quizzed['score'] > 0:
                    word_last_quizzed['score'] -= 1
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




