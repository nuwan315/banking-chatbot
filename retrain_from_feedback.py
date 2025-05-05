import sqlite3
import json
import numpy as np
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

# Parameters
vocab_size = 1000
max_len = 10
oov_token = "<OOV>"

# --- Step 1: Load data from intents.json ---
with open('intents.json', encoding='utf-8') as file:
    data = json.load(file)

sentences = []
labels = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        sentences.append(pattern)
        labels.append(intent['tag'])

# --- Step 2: Load data from feedback table ---
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, user_message, correct_tag FROM feedback 
    WHERE correct_tag IS NOT NULL AND correct_tag != '' AND used_for_training = 0
""")
feedback_data = cursor.fetchall()

feedback_ids = []
for row in feedback_data:
    feedback_ids.append(row[0])
    sentences.append(row[1])
    labels.append(row[2])

# --- Step 3: Prepare tokenizer and label encoder ---
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(sentences)
sequences = tokenizer.texts_to_sequences(sentences)
X = pad_sequences(sequences, truncating='post', padding='post', maxlen=max_len)

lbl_encoder = LabelEncoder()
y = lbl_encoder.fit_transform(labels)

# Save tokenizer and label encoder
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('label_encoder.pickle', 'wb') as ecn_file:
    pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)

# --- Step 4: Build and train the model ---
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=16, input_length=max_len))
model.add(GlobalAveragePooling1D())
model.add(Dense(16, activation='relu'))
model.add(Dense(len(lbl_encoder.classes_), activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()
model.fit(X, np.array(y), epochs=100)

model.save("chat_model.h5")
print("✅ Model retrained and saved using both original and feedback data.")

# --- Step 5: Mark used feedback entries as trained ---
if feedback_ids:
    cursor.executemany("""
        UPDATE feedback SET used_for_training = 1 WHERE id = ?
    """, [(i,) for i in feedback_ids])
    conn.commit()
    print(f"✅ Marked {len(feedback_ids)} feedback entries as used.")
else:
    print("ℹ️ No new feedback entries were used.")

conn.close()
