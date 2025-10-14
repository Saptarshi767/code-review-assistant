import os
import sqlite3

# Security issue: hardcoded credentials
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

def get_user_data(user_id):
    # Security issue: SQL injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()

def process_file(filename):
    # Performance issue: file not closed properly
    file = open(filename, 'r')
    data = file.read()
    return data.upper()

# Style issue: unused import, poor naming
def calc(x, y):
    return x + y