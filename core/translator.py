import json
import os

class Translator:
    """A simple JSON-based translator."""
    def __init__(self, lang_code='en'):
        self.lang_code = lang_code
        self.translations = {}
        self.load_language(lang_code)

    def load_language(self, lang_code):
        """Loads a new language file."""
        self.lang_code = lang_code
        # Construct the path relative to this file's location
        locale_path = os.path.join(os.path.dirname(__file__), '..', 'locale', f'{lang_code}.json')
        try:
            with open(locale_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"Translation file for '{lang_code}' not found. Defaulting to English.")
            if self.lang_code != 'en':
                self.load_language('en')

    def get_text(self, key):
        """Returns the translated string for a given key."""
        return self.translations.get(key, key) # Return the key itself if not found
