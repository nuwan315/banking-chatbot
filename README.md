# NOVA AI Banking chatbot

Follow these step by steps to setup NOVA bot on your envioronment.

<b>Step 1</b><br>
Run: pip install Flask tensorflow-cpu numpy deep-translator spacy pyspellchecker scikit-learn<br>
python3 -m spacy download en_core_web_sm<br>
<br>
Step 2

To create database, run:
python3 create_db.py

Success message: Database and accounts table created.

Step 3

To train chatbot model<br>
python3 preprocess.py<br>
python3 train_model.py<br>
Success message: ✅ Model trained and saved.
