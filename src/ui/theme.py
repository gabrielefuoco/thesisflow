import customtkinter as ctk


# Helper for class properties
class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget(owner)

class Theme:
    MODE_DARK = "Dark"
    MODE_LIGHT = "Light"
    
    _current_mode = MODE_DARK
    
    # Base HSL values for the Slate palette
    # Slate 500: H=215, S=16, L=47
    _PALETTE_HSL = {
        MODE_DARK: {
            "BG": (222, 47, 11),           # Slate 950 equivalents
            "PANEL": (222, 47, 15),        # Slate 900
            "PANEL_HOVER": (217, 33, 17),  # Slate 850
            "BORDER": (217, 32, 20),       # Slate 800
            "TEXT_MAIN": (210, 40, 98),    # Slate 50
            "TEXT_DIM": (215, 16, 70),     # Slate 400
            "ACCENT": (173, 80, 40),       # Teal 500
            "ACCENT_HOVER": (173, 80, 35), # Teal 600
            "EDITOR_BG": (222, 47, 11),
            "EDITOR_TEXT": (214, 32, 91)   # Slate 200
        },
        MODE_LIGHT: {
            "BG": (210, 40, 98),           # Slate 50
            "PANEL": (0, 0, 100),          # White
            "PANEL_HOVER": (210, 40, 96),  # Slate 100
            "BORDER": (214, 32, 91),       # Slate 200
            "TEXT_MAIN": (222, 47, 11),    # Slate 950
            "TEXT_DIM": (215, 16, 47),     # Slate 500
            "ACCENT": (173, 80, 35),       # Teal 600
            "ACCENT_HOVER": (173, 80, 30), # Teal 700
            "EDITOR_BG": (0, 0, 100),
            "EDITOR_TEXT": (222, 47, 11)   # Slate 950
        }
    }

    # Functional (Common)
    COLOR_ERROR = "#ef4444"
    COLOR_SUCCESS = "#22c55e"
    COLOR_WARNING = "#f59e0b"
    
    # Fonts
    import platform
    FONT_FAMILY = "Inter" if platform.system() == "Windows" else "Inter, Segoe UI, Arial"
    
    FONT_SIZE_MAIN = 16
    FONT_SIZE_H1 = 24
    FONT_SIZE_H2 = 20
    FONT_SIZE_H3 = 18

    @classmethod
    def hsl_to_hex(cls, h, s, l):
        """Standard HSL to Hex conversion."""
        h /= 360
        s /= 100
        l /= 100
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

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
        hsl = cls._PALETTE_HSL[cls._current_mode].get(key)
        if hsl:
            return cls.hsl_to_hex(*hsl)
        return "#ff00ff"

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

