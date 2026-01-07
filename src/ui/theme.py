class Theme:
    # Slate / Monochrome Palette
    COLOR_BG = "#0f172a"          # Very dark slate (Main Background)
    COLOR_PANEL = "#1e293b"       # Dark slate (Sidebar, Cards)
    COLOR_PANEL_HOVER = "#334155" # Lighter slate
    COLOR_BORDER = "#334155"      # Borders
    
    # Text
    TEXT_MAIN = "#f8fafc"         # White-ish
    TEXT_DIM = "#94a3b8"          # Dimmed gray
    
    # Accents (Teal)
    COLOR_ACCENT = "#14b8a6"      # Teal 500
    COLOR_ACCENT_HOVER = "#0d9488" # Teal 600
    
    # Functional
    COLOR_ERROR = "#ef4444"
    COLOR_SUCCESS = "#22c55e"
    COLOR_WARNING = "#f59e0b"
    
    # Editor
    EDITOR_BG = "#0f172a" # Match main BG for seamless look
    EDITOR_TEXT = "#e2e8f0"
    
    # Fonts
    FONT_FAMILY = "Segoe UI" if "Windows" else "Arial" # Fallback
    
    @classmethod
    def apply_to(cls, widget, type="panel"):
        if type == "panel":
            widget.configure(fg_color=cls.COLOR_PANEL)
        elif type == "main":
            widget.configure(fg_color=cls.COLOR_BG)
        elif type == "transparent":
            widget.configure(fg_color="transparent")
