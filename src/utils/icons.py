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
        key = f"{name}_{size}_{color}" # Added color to key
        if key in cls._icons:
            return cls._icons[key]
            
        icon_path = cls.get_base_path() / f"{name}.png"
        
        if not icon_path.exists():
            print(f"Warning: Icon {name} not found at {icon_path}")
            # Return visible placeholder (Red square with X)
            img = Image.new("RGBA", size, (255, 0, 0, 100))
            d = ImageDraw.Draw(img)
            d.line((0, 0, size[0], size[1]), fill="white", width=2)
            d.line((0, size[1], size[0], 0), fill="white", width=2)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            cls._icons[key] = ctk_img
            return ctk_img
            
        try:
            img = Image.open(icon_path)
            # Apply color if specified (simple tint for PNGs)
            if color:
                # This is a very simple tinting, better would be to use Image.composite or similar
                # but for simplicity we'll just use the icons as generated for now
                pass
                
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            cls._icons[key] = ctk_img
            return ctk_img
        except Exception as e:
            print(f"Error loading icon {name}: {e}")
            # Fallback placeholder
            img = Image.new("RGBA", size, (255, 0, 0, 100))
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)

from PIL import ImageDraw # Added import for placeholder drawing
