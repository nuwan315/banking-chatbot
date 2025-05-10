# NOVA AI Banking chatbot

Follow these step by steps to setup NOVA bot on your envioronment.

<b>Step 1</b><br>
Run: pip install Flask tensorflow-cpu numpy deep-translator spacy pyspellchecker scikit-learn
python -m spacy download en_core_web_sm

Step 2

To create database, run:
python create_db.py

Success message: Database and accounts table created.

Step 3

To train chatbot model
python train_model.py
Success message: 
