import customtkinter as ctk


# Helper for class properties
class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget(owner)

class Theme:
    MODE_DARK = "Dark"
    MODE_LIGHT = "Light"
    
    _current_mode = MODE_DARK
    
    # Palette Definitions
    _PALETTE = {
        MODE_DARK: {
            "BG": "#0f172a",          # Very dark slate
            "PANEL": "#1e293b",       # Dark slate
            "PANEL_HOVER": "#334155", # Lighter slate
            "BORDER": "#334155",
            "TEXT_MAIN": "#f8fafc",   # White-ish
            "TEXT_DIM": "#94a3b8",    # Dimmed gray
            "ACCENT": "#14b8a6",      # Teal 500
            "ACCENT_HOVER": "#0d9488",# Teal 600
            "EDITOR_BG": "#0f172a",
            "EDITOR_TEXT": "#e2e8f0"
        },
        MODE_LIGHT: {
            "BG": "#f1f5f9",          # Slate 100
            "PANEL": "#ffffff",       # White
            "PANEL_HOVER": "#e2e8f0", # Slate 200
            "BORDER": "#cbd5e1",      # Slate 300
            "TEXT_MAIN": "#0f172a",   # Slate 900
            "TEXT_DIM": "#64748b",    # Slate 500
            "ACCENT": "#0d9488",      # Teal 600
            "ACCENT_HOVER": "#0f766e",# Teal 700
            "EDITOR_BG": "#ffffff",
            "EDITOR_TEXT": "#0f172a"
        }
    }

    # Functional (Common)
    COLOR_ERROR = "#ef4444"
    COLOR_SUCCESS = "#22c55e"
    COLOR_WARNING = "#f59e0b"
    
    # Fonts
    import platform
    FONT_FAMILY = "Segoe UI" if platform.system() == "Windows" else "Arial"

    @classmethod
    def set_mode(cls, mode):
        if mode in [cls.MODE_DARK, cls.MODE_LIGHT]:
            cls._current_mode = mode
            ctk.set_appearance_mode(mode)

    @classmethod
    def toggle_mode(cls):
        new_mode = cls.MODE_LIGHT if cls._current_mode == cls.MODE_DARK else cls.MODE_DARK
        cls.set_mode(new_mode)
        return new_mode

    @classmethod
    def get_color(cls, key):
        return cls._PALETTE[cls._current_mode].get(key, "#ff00ff")

    # Dynamic Properties for easy access (getters)
    @classproperty
    def COLOR_BG(cls): return cls.get_color("BG")
    @classproperty
    def COLOR_PANEL(cls): return cls.get_color("PANEL")
    @classproperty
    def COLOR_PANEL_HOVER(cls): return cls.get_color("PANEL_HOVER")
    @classproperty
    def COLOR_BORDER(cls): return cls.get_color("BORDER")
    @classproperty
    def TEXT_MAIN(cls): return cls.get_color("TEXT_MAIN")
    @classproperty
    def TEXT_DIM(cls): return cls.get_color("TEXT_DIM")
    @classproperty
    def COLOR_ACCENT(cls): return cls.get_color("ACCENT")
    @classproperty
    def COLOR_ACCENT_HOVER(cls): return cls.get_color("ACCENT_HOVER")
    @classproperty
    def EDITOR_BG(cls): return cls.get_color("EDITOR_BG")
    @classproperty
    def EDITOR_TEXT(cls): return cls.get_color("EDITOR_TEXT")

