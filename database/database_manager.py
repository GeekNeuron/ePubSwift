# database/database_manager.py
import sqlite3
import os
from utils.helpers import get_base_path

class DatabaseManager:
    def __init__(self, db_name="epub_swift.db"):
        # Use the helper to ensure the db is created in the correct location
        base_path = os.path.dirname(get_base_path())
        self.db_path = os.path.join(base_path, db_name)
        self._setup_database()

    def _setup_database(self):
        """Creates the database and tables if they don't exist."""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                path TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                chapter_count INTEGER,
                last_read_pos INTEGER DEFAULT 0
            )
        """)
        con.commit()
        con.close()
    
    def load_library(self):
        """Loads the book library from the SQLite database."""
        library = []
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT path, title, chapter_count, last_read_pos FROM books")
            for row in cur.fetchall():
                library.append({
                    'path': row[0], 'title': row[1], 'pages': row[2], 'last_read_pos': row[3]
                })
            con.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        return library

    def add_or_update_book(self, book_data):
        """Adds a new book or updates an existing one in the database."""
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            # Use INSERT OR IGNORE to avoid overwriting existing progress
            cur.execute("INSERT OR IGNORE INTO books (path, title, chapter_count) VALUES (?, ?, ?)",
                        (book_data['path'], book_data['title'], book_data['pages']))
            con.commit()
            con.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        
    def save_progress(self, path, position):
        """Saves the current reading position to the database."""
        if not path: return
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("UPDATE books SET last_read_pos = ? WHERE path = ?", (position, path))
            con.commit()
            con.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
