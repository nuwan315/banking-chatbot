import sqlite3

# Connect to database (creates it if not exists)
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

# Create table for account types
cursor.execute('''
    CREATE TABLE IF NOT EXISTS account_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')

# Create table for feedback
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT NOT NULL,
        correct_tag TEXT NOT NULL,
        used_for_training INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')


# Insert some sample account types
cursor.executemany('''
    INSERT INTO account_types (name) VALUES (?)
''', [
    ('Savings Account',),
    ('Current Account',),
    ('Fixed Deposit Account',)
])

# Commit and close
conn.commit()
conn.close()

print("Database and tables created with sample data.")
