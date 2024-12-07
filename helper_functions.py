import requests
import pinyin
import random
from telegram.ext import ContextTypes
from fuzzywuzzy import fuzz




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



#fills the to_study list with first 25 words
def initialize_to_study(context: ContextTypes.DEFAULT_TYPE, data):
    for item in data[:25]:
        context.user_data['to_study'].append({
                'simplified': item['simplified'],
                'definitions': item['definitions'],
                'pinyin': item['pinyin'],
                'score': 0,
                'correct_last_time': ""
            })
    del data[:25]
    
    
#adds new word to the "to_study" pool   
def add_new_word(context: ContextTypes.DEFAULT_TYPE, data):
    try:
        new_word = random.choice(data)
        new_word_entry = {
                    'simplified': new_word['simplified'],
                    'definitions': new_word['definitions'],
                    'pinyin': new_word['pinyin'],
                    'score': 0,
                    'correct_last_time': ""
                }
        context.user_data['to_study'].append(new_word_entry)
        data.remove(new_word)
    except:
        print("we have run out of words I guess.")
        

def check_answer(correct_translation, user_answer):
    answer_is_correct = False
    for i in correct_translation:
                fuzzy_ratio = fuzz.ratio(i, user_answer)
                if fuzzy_ratio > 80:
                    answer_is_correct = True
    return answer_is_correct
    
    

#generates example sentences with OpenAI API and builds the message to introduce new word with. 
        # Usage in main.py:
            # example_sentences = get_example_sentences(client, word_to_quiz)
            # await update.message.reply_text(example_sentences) 
            # But pls implement it in a way that it just skips this step if there's no API key provided       
def get_example_sentences(client, word):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"Write me 3 simple example sentences using word {word} in Chinese. Include pinyin and English translation. Nothing else. Just the sentences."
        }
    ]
    )
    message = completion.choices[0].message
    output = f"Here's a new word for you: {word['simplified']} ( {word['pinyin']}) = {word['definitions'][0]}. Here is few example sentences on how to use it:\n\n{message.content}"
    return output
    

   