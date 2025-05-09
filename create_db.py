import sqlite3

# Connect and create table
conn = sqlite3.connect('bank.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS account_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)''')

# Insert sample account types
account_types = [
    ('Savings Account',),
    ('Current Account',),
    ('Fixed Deposit Account',)
]

c.executemany('INSERT INTO account_types (name) VALUES (?)', account_types)

c.execute('''CREATE TABLE IF NOT EXISTS accounts (
    account_no INTEGER PRIMARY KEY,
    name TEXT,
    balance REAL
)''')

# Sample data
accounts = [
    ('111', 'Savings Account', 10000.00),
    ('222', 'Current Account', 5000.00),
    ('333', 'Fixed Deposit Account', 25000.00),
    ('444', 'Current Account', 1500.00),
    ('555', 'Savings Account', 7000.00)
]

c.executemany('INSERT OR REPLACE INTO accounts VALUES (?, ?, ?)', accounts)


c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            correct_intent TEXT,
            timestamp TEXT
)''')

conn.commit()
conn.close()

print("Database and accounts table created.")
