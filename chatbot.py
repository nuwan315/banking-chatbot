import json
import random
import pickle
import numpy as np
import sqlite3
import spacy
from deep_translator import GoogleTranslator
from spellchecker import SpellChecker
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Load SpellChecker
spell = SpellChecker()

def correct_spelling(sentence):
    words = sentence.split()
    corrected = [spell.correction(word) if spell.unknown([word]) else word for word in words]
    return ' '.join(corrected)

# Load data
model = load_model('chat_model.h5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
with open('label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)
with open('intents.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# NLP function with lemmatization
def get_response(user_input):

    # Detect and translate to English
    user_input = GoogleTranslator(source='auto', target='en').translate(user_input)

    # SpellChecker the user input
    user_input = correct_spelling(user_input)

    # Lemmatize the user input
    doc = nlp(user_input)
    lemmatized_input = " ".join([token.lemma_ for token in doc])
    
    # Continue with your existing model prediction
    seq = tokenizer.texts_to_sequences([lemmatized_input])
    padded = pad_sequences(seq, truncating='post', maxlen=10)
    pred = model.predict(padded, verbose=0)
    tag = lbl_encoder.inverse_transform([np.argmax(pred)])

    for intent in data['intents']:
        if intent['tag'] == tag[0]:
            if "__get_account_types__" in intent['responses']:
                return get_account_types_from_db()
            else:
                return random.choice(intent['responses'])
            
            # Translate response back to original user language
            translated_response = GoogleTranslator(source='en', target=user_language).translate(response)
            return translated_response

    return GoogleTranslator(source='en', target=user_language).translate("Sorry, I didn't understand that.")

# Helper function to get account types from DB
def get_account_types_from_db():
    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM account_types")
        accounts = cursor.fetchall()
        conn.close()

        if not accounts:
            return "Sorry, no account types are available right now."

        account_list = ", ".join([acc[0] for acc in accounts])
        return f"We offer the following types of accounts: {account_list}."

    except Exception as e:
        return f"Error accessing database: {str(e)}"
