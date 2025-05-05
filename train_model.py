import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from preprocess import preprocess_data

# Load processed data
X_train, y_train, output_dim, _, _ = preprocess_data()

model = Sequential()
model.add(Embedding(input_dim=1000, output_dim=16, input_length=10))
model.add(GlobalAveragePooling1D())
model.add(Dense(16, activation='relu'))
model.add(Dense(output_dim, activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

model.fit(X_train, np.array(y_train), epochs=200)

model.save("chat_model.h5")
print("Model trained and saved.")
