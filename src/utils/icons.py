import customtkinter as ctk
from PIL import Image
from pathlib import Path
import os

class IconFactory:
    _icons = {}
    _base_path = Path(__file__).parent.parent.parent / "assets" / "icons"

    @classmethod
    def get_base_path(cls):
        import sys
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / "assets" / "icons"
        return Path(__file__).parent.parent.parent / "assets" / "icons"

    @classmethod
    def get_icon(cls, name: str, size: tuple = (20, 20), color: str = None) -> ctk.CTkImage:
        key = f"{name}_{size}"
        if key in cls._icons:
            return cls._icons[key]
            
        icon_path = cls.get_base_path() / f"{name}.png"
        
        if not icon_path.exists():
            print(f"Warning: Icon {name} not found at {icon_path}")
            # Return empty transparent image
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            cls._icons[key] = ctk_img
            return ctk_img
            
        try:
            img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            cls._icons[key] = ctk_img
            return ctk_img
        except Exception as e:
            print(f"Error loading icon {name}: {e}")
            # Fallback
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
