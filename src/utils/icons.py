import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

class IconFactory:
    _icons = {}

    @classmethod
    def get_icon(cls, name: str, size: tuple = (20, 20), color: str = "white") -> ctk.CTkImage:
        key = f"{name}_{size}_{color}"
        if key in cls._icons:
            return cls._icons[key]
            
        # Draw fallback icon using PIL
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simple shapes based on name
        w, h = size
        padding = 2
        
        if name == "bold":
            draw.text((padding, 0), "B", fill=color, font_size=16) # Fallback to text if font issues, but try drawing
        elif name == "italic":
            draw.text((padding+2, 0), "I", fill=color)
        elif name == "plus":
            draw.line((w/2, padding, w/2, h-padding), fill=color, width=3)
            draw.line((padding, h/2, w-padding, h/2), fill=color, width=3)
        elif name == "up":
            draw.polygon([(w/2, padding), (padding, h-padding), (w-padding, h-padding)], fill=color)
        elif name == "down":
            draw.polygon([(padding, padding), (w-padding, padding), (w/2, h-padding)], fill=color)
        elif name == "close":
             draw.line((padding, padding, w-padding, h-padding), fill=color, width=2)
             draw.line((w-padding, padding, padding, h-padding), fill=color, width=2)
        elif name == "list":
             # 3 lines with dots
             for i in range(3):
                 y = padding + i * (h-2*padding)/2.5
                 draw.ellipse((padding, y, padding+2, y+2), fill=color)
                 draw.line((padding+5, y+1, w-padding, y+1), fill=color, width=2)
        elif name == "play":
             draw.polygon([(padding, padding), (padding, h-padding), (w-padding, h/2)], fill=color)
        else:
            # Default Box
            draw.rectangle((padding, padding, w-padding, h-padding), outline=color, width=2)
            
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
        cls._icons[key] = ctk_img
        return ctk_img
