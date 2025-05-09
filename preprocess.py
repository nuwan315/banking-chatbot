import json
import numpy as np
import pickle
import spacy
import sqlite3
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

nlp = spacy.load("en_core_web_sm")

def lemmatize_text(text):
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_punct and not token.is_space])

def preprocess_data():
    with open('intents.json') as file:
        data = json.load(file)

    sentences = []
    labels = []

    # Load from intents.json
    for intent in data['intents']:
        for pattern in intent['patterns']:
            lemma_pattern = lemmatize_text(pattern)
            sentences.append(lemma_pattern)
            labels.append(intent['tag'])

    # Load from feedback.db
    try:
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_input, correct_intent FROM feedback WHERE correct_intent IS NOT NULL")
        feedback_rows = cursor.fetchall()
        conn.commit()
        conn.close()

        for user_input, correct_intent in feedback_rows:
            if user_input and correct_intent:
                sentences.append(lemmatize_text(user_input))
                labels.append(correct_intent)

        print(f"[INFO] Loaded {len(feedback_rows)} feedback samples.")
    except Exception as e:
        print(f"[WARNING] Could not load feedback from database: {e}")

    # Encode labels
    lbl_encoder = LabelEncoder()
    y_train = lbl_encoder.fit_transform(labels)

    # Tokenizer setup
    vocab_size = 2000
    oov_token = "<OOV>"
    max_len = 20

    tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
    tokenizer.fit_on_texts(sentences)
    sequences = tokenizer.texts_to_sequences(sentences)
    padded_sequences = pad_sequences(sequences, truncating='post', padding='post', maxlen=max_len)

    # Save assets
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('label_encoder.pickle', 'wb') as ecn_file:
        pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)

    # Save model config
    config = {
        "vocab_size": vocab_size,
        "max_len": max_len,
        "oov_token": oov_token
    }
    with open('model_config.json', 'w') as f:
        json.dump(config, f)

    return padded_sequences, y_train, len(lbl_encoder.classes_), tokenizer, lbl_encoder
