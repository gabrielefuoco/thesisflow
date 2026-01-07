import json
import locale
from pathlib import Path
import os

class TranslationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationManager, cls).__new__(cls)
            cls._instance.translations = {}
            cls._instance.current_locale = "it" # Default
            cls._instance.load_translations()
        return cls._instance

    def load_translations(self):
        # Determine locale
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang and sys_lang.startswith("en"):
            self.current_locale = "en"
        else:
            self.current_locale = "it"
            
        # Generic path finding
        root = Path(__file__).parent.parent.parent
        locale_dir = root / "locales"
        
        # Load IT
        try:
            with open(locale_dir / "it.json", "r", encoding="utf-8") as f:
                self.translations["it"] = json.load(f)
        except Exception as e:
            print(f"Failed to load it.json: {e}")
            self.translations["it"] = {}

        # Load EN
        try:
            with open(locale_dir / "en.json", "r", encoding="utf-8") as f:
                self.translations["en"] = json.load(f)
        except:
             self.translations["en"] = {}

    def t(self, key: str, default: str = None) -> str:
        # Check current locale
        val = self.translations.get(self.current_locale, {}).get(key)
        if val: return val
        
        # Fallback to IT if EN missing (or vice versa, let's fallback to IT)
        val = self.translations.get("it", {}).get(key)
        if val: return val
        
        return default if default is not None else key

I18N = TranslationManager()
