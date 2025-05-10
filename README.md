# NOVA AI Banking chatbot

Follow these step by steps to setup NOVA bot on your envioronment.

<h3>Step 1: Install dependacies</h3>
pip install Flask tensorflow-cpu numpy deep-translator spacy pyspellchecker scikit-learn<br>
python3 -m spacy download en_core_web_sm<br>

<h3>Step 2: Create database</h3>
python3 create_db.py<br><br>
Success message: Database and accounts table created.

<h3>Step 3: Train chatbot model</h3>

python3 preprocess.py<br>
python3 train_model.py<br><br>
Success message: ✅ Model trained and saved.

<h3>Step 4: Run App</h3>

python3 app.py<br>

<h3>Step 5: Access</h3>

Use port 5000<br>
To check user feedback dashboard :5000/dashboard<br>
