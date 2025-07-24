import sqlite3
import os

class DatabaseManager:
    """Manages all database operations for the application."""

    def __init__(self, db_name="epub_swift.db"):
        """Initializes the database connection and creates tables if they don't exist."""
        # Place the database in the project's root directory
        self.db_path = os.path.join(os.path.dirname(__file__), '..', db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Creates the necessary tables if they don't exist."""
        # General settings table (key-value store)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # Book progress tracking table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                book_path TEXT PRIMARY KEY,
                last_chapter INTEGER
            )
        """)
        self.conn.commit()

    def get_setting(self, key, default=None):
        """Gets a value from the settings table."""
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default

    def set_setting(self, key, value):
        """Sets a value in the settings table."""
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def get_progress(self, book_path):
        """Gets the last saved chapter index for a book."""
        self.cursor.execute("SELECT last_chapter FROM progress WHERE book_path = ?", (book_path,))
        result = self.cursor.fetchone()
        return int(result[0]) if result else 0  # Default to the first chapter

    def set_progress(self, book_path, chapter_index):
        """Saves the reading progress for a book."""
        self.cursor.execute("INSERT OR REPLACE INTO progress (book_path, last_chapter) VALUES (?, ?)",
                            (book_path, chapter_index))
        self.conn.commit()
    
    def close(self):
        """Closes the database connection."""
        self.conn.close()
