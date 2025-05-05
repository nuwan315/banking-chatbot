
import json
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Globals to allow reuse after import
tokenizer = None
lbl_encoder = None

def preprocess_data():
    global tokenizer, lbl_encoder

    with open('intents.json', encoding='utf-8') as file:
        data = json.load(file)

    sentences = []
    labels = []
    responses = []
    tags = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            sentences.append(pattern)
            labels.append(intent['tag'])
        responses.append(intent['responses'])
        tags.append(intent['tag'])

    lbl_encoder = LabelEncoder()
    labels_encoded = lbl_encoder.fit_transform(labels)

    vocab_size = 1000
    oov_token = "<OOV>"
    tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
    tokenizer.fit_on_texts(sentences)
    sequences = tokenizer.texts_to_sequences(sentences)
    padded_sequences = pad_sequences(sequences, truncating='post', padding='post', maxlen=10)

    # Save encoder and tokenizer
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('label_encoder.pickle', 'wb') as ecn_file:
        pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)

    return padded_sequences, labels_encoded, len(set(labels)), tokenizer, lbl_encoder
