# models.py
import sqlite3

DB_NAME = "images.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_name TEXT,
        modified_name TEXT,
        operation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def insert_image(original_name, modified_name, operation):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO images (original_name, modified_name, operation) VALUES (?, ?, ?)",
              (original_name, modified_name, operation))
    conn.commit()
    inserted_id = c.lastrowid  # get the new row's id
    conn.close()
    return inserted_id

def get_image(image_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT original_name, modified_name FROM images WHERE id=?", (image_id,))
    row = c.fetchone()
    conn.close()
    return row
