import customtkinter as ctk
from src.ui.theme import Theme

class CitationPopup(ctk.CTkToplevel):
    def __init__(self, master, keys, on_select, bbox):
        super().__init__(master)
        self.on_select = on_select
        
        self.overrideredirect(True)
        self.withdraw() 
        
        x = master.winfo_rootx() + bbox[0]
        y = master.winfo_rooty() + bbox[1] + bbox[3]
        
        self.geometry(f"200x150+{x}+{y}")
        self.deiconify()
        
        scroll = ctk.CTkScrollableFrame(self, fg_color=Theme.COLOR_PANEL)
        scroll.pack(fill="both", expand=True)
        
        for key in keys:
             btn = ctk.CTkButton(scroll, text=key, anchor="w", fg_color="transparent", 
                                 text_color=Theme.TEXT_MAIN, hover_color=Theme.COLOR_PANEL_HOVER,
                                 command=lambda k=key: self.on_item_click(k))
             btn.pack(fill="x")
        
        self.bind("<FocusOut>", lambda e: self.destroy())
        
    def on_item_click(self, key):
        self.on_select(key)
        self.destroy()
