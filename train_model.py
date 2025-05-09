import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D, Dropout
from preprocess import preprocess_data

# Load processed data
X_train, y_train, output_dim, _, _ = preprocess_data()

model = Sequential()
model.add(Embedding(input_dim=2000, output_dim=32, input_length=20))
model.add(GlobalAveragePooling1D())
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(16, activation='relu'))
model.add(Dense(output_dim, activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

model.fit(X_train, np.array(y_train), epochs=300, batch_size=8, verbose=1)

model.save("chat_model.h5")
print("✅ Model trained and saved.")
