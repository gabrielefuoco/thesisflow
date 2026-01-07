import customtkinter as ctk
from PIL import Image
from pathlib import Path
import os

class IconFactory:
    _icons = {}
    _base_path = Path(__file__).parent.parent.parent / "assets" / "icons"

    @classmethod
    def get_icon(cls, name: str, size: tuple = (20, 20), color: str = None) -> ctk.CTkImage:
        # Note: color argument is currently ignored for PNGs unless we tint them.
        # For now, we assume the PNGs are pre-colored or neutral.
        # Future improvement: Use color to tint the image if needed.
        
        key = f"{name}_{size}"
        if key in cls._icons:
            return cls._icons[key]
            
        icon_path = cls._base_path / f"{name}.png"
        
        if not icon_path.exists():
            # Fallback for missing icons
            print(f"Warning: Icon {name} not found at {icon_path}")
            return None # Or return a default empty image
            
        try:
            img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            cls._icons[key] = ctk_img
            return ctk_img
        except Exception as e:
            print(f"Error loading icon {name}: {e}")
            return None
