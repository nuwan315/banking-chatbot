import random
import json
import pickle
import numpy as np
import spacy
import sqlite3
import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from deep_translator import GoogleTranslator
from spellchecker import SpellChecker

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

spell = SpellChecker()

def correct_spelling(text):
    words = text.split()
    corrected = [spell.correction(w) if w not in spell else w for w in words]
    return " ".join(corrected)

# Load trained model and encoders
model = load_model("chat_model.h5")
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
with open('label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)
with open('intents.json') as file:
    data = json.load(file)

# Globals
max_len = 10
CONFIDENCE_THRESHOLD = 0.7

# Track user state
user_context = {
    "expecting_balance_account": False,
    "expecting_transfer": False,
}

# Lemmatization function
def lemmatize_text(text):
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_punct and not token.is_space])

# Save user feedback to DB
def save_feedback_to_db(user_input, correct_intent):
    try:
        conn = sqlite3.connect('bank.db', timeout=10)
        c = conn.cursor()
        c.execute("INSERT INTO feedback (user_input, correct_intent, timestamp) VALUES (?, ?, ?)",
                  (user_input, correct_intent, datetime.datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to save feedback: {e}")

# Main chatbot response function
def get_response(user_input, user_lang='auto'):
    # Special case: Welcome
    if user_input == "__welcome__":
        return "Hello! I’m NOVA, your banking assistant ❤️. How can I help you?"

    # ✅ Handle balance account input directly
    if user_context["expecting_balance_account"]:
        user_context["expecting_balance_account"] = False
        account_no = user_input.strip()
        try:
            conn = sqlite3.connect('bank.db')
            c = conn.cursor()
            c.execute("SELECT balance FROM accounts WHERE account_no = ?", (account_no,))
            result = c.fetchone()
            conn.commit()
            conn.close()
            if result:
                return f"Your current balance is Rs. {result[0]:,.2f}"
            else:
                return "Account number not found. Please try again."
        except:
            return "Sorry, I couldn’t check your balance right now."

    # ✅ Handle fund transfer input directly
    if user_context["expecting_transfer"]:
        user_context["expecting_transfer"] = False
        try:
            sender, receiver, amount = [x.strip() for x in user_input.split(",")]
            amount = float(amount)
            conn = sqlite3.connect('bank.db')
            c = conn.cursor()
            c.execute("SELECT balance FROM accounts WHERE account_no = ?", (sender,))
            sender_result = c.fetchone()
            c.execute("SELECT balance FROM accounts WHERE account_no = ?", (receiver,))
            receiver_result = c.fetchone()

            if not sender_result:
                return "Sender account not found."
            elif not receiver_result:
                return "Receiver account not found."
            elif sender_result[0] < amount:
                return "Insufficient funds."
            else:
                c.execute("UPDATE accounts SET balance = balance - ? WHERE account_no = ?", (amount, sender))
                c.execute("UPDATE accounts SET balance = balance + ? WHERE account_no = ?", (amount, receiver))
                conn.commit()
                conn.close()
                return f"Transfer successful. Rs. {amount:,.2f} sent from {sender} to {receiver}."
        except:
            return "Invalid input. Please use format: sender,receiver,amount"

    # Translate to English if needed
    try:
        translated_input = GoogleTranslator(source='auto', target='en').translate(user_input)
    except:
        translated_input = user_input

    # Preprocess
    
    # Preprocess: Spell correction → Lemmatization
    spelling_corrected = correct_spelling(translated_input)
    lemmatized_input = lemmatize_text(spelling_corrected)
    input_seq = tokenizer.texts_to_sequences([lemmatized_input])
    padded_input = pad_sequences(input_seq, truncating='post', padding='post', maxlen=max_len)
    prediction = model.predict(padded_input)[0]
    confidence = np.max(prediction)
    predicted_tag = lbl_encoder.inverse_transform([np.argmax(prediction)])[0]

    # Debug output
    print(f"[DEBUG] User input: {user_input}")
    print(f"[DEBUG] Translated: {translated_input}")
    print(f"[DEBUG] Lemmatized: {lemmatized_input}")
    print(f"[DEBUG] Predicted tag: {predicted_tag} with confidence {confidence:.4f}")

    # Low confidence fallback
    if confidence < CONFIDENCE_THRESHOLD:
        response = "Sorry, I didn't understand that. Could you please rephrase?"
    else:
        tag = predicted_tag
        response = "Hmm..."

        for intent in data['intents']:
            if intent['tag'] == tag:
                # Special: Show account types from DB
                if tag == "account_types":
                    try:
                        conn = sqlite3.connect('bank.db')
                        c = conn.cursor()
                        c.execute("SELECT name FROM account_types")
                        rows = c.fetchall()
                        conn.commit()
                        conn.close()
                        response = "Here are the available account types:\n" + "\n".join(f"• {r[0]}" for r in rows)
                    except:
                        response = "Sorry, I couldn’t fetch account types right now."

                # Special: Ask for balance account number
                elif tag == "balance":
                    user_context["expecting_balance_account"] = True
                    response = "Please enter your account number to check your balance."

                # Special: Ask for transfer details
                elif tag == "transfer":
                    user_context["expecting_transfer"] = True
                    response = "Please enter: sender_account, receiver_account, amount"

                else:
                    response = random.choice(intent['responses'])
                break

    # Translate back if needed
    if user_lang != 'en' and user_lang != 'auto':
        try:
            response = GoogleTranslator(source='en', target=user_lang).translate(response)
        except:
            pass

    return response
