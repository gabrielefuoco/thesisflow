
import customtkinter as ctk
from src.utils.icons import IconFactory
from src.ui.tooltip import ToolTip
from src.utils.i18n import I18N
from src.ui.theme import Theme

class ToolbarFrame(ctk.CTkFrame):
    def __init__(self, master, command_compile=None, **kwargs):
        super().__init__(master, height=40, fg_color="transparent", corner_radius=0, **kwargs)
        
        # command_compile is deprecated here as it moves to global header, but kept for compat if needed
        
        self.grid_columnconfigure(99, weight=1) # Spacer usually
        
        # Helper to create styled buttons
        def btn(icon, cmd, tip, col=0):
            b = ctk.CTkButton(self, text="", image=IconFactory.get_icon(icon, size=(16,16)), 
                              width=32, height=32,
                              fg_color="transparent", hover_color=Theme.COLOR_PANEL_HOVER,
                              command=cmd)
            b.pack(side="left", padx=2)
            ToolTip(b, tip)
            return b
            
        def sep():
            s = ctk.CTkFrame(self, width=2, height=20, fg_color=Theme.COLOR_BORDER)
            s.pack(side="left", padx=5, pady=10)

        # Undo/Redo (Placeholders or future)
        # btn("undo", None, "Undo")
        # btn("redo", None, "Redo")
        # sep()
        
        # Format
        btn("bold", lambda: self.insert("**", "**"), I18N.t("bold"))
        btn("italic", lambda: self.insert("_", "_"), I18N.t("italic"))
        # Strikethrough?
        
        sep()
        
        # Headers
        ctk.CTkButton(self, text="H1", width=32, fg_color="transparent", font=("Segoe UI", 12, "bold"), 
                      hover_color=Theme.COLOR_PANEL_HOVER, command=lambda: self.insert_prefix("# ")).pack(side="left")
        ctk.CTkButton(self, text="H2", width=32, fg_color="transparent", font=("Segoe UI", 11, "bold"), 
                      hover_color=Theme.COLOR_PANEL_HOVER, command=lambda: self.insert_prefix("## ")).pack(side="left")
        
        sep()
        
        # Lists & Quotes
        btn("list", lambda: self.insert_prefix("- "), I18N.t("list"))
        btn("quote", lambda: self.insert_prefix("> "), "Citazione") # Quote icon missing? Use text or generic
        
        sep()
        
        # Inserts
        btn("image", self.on_image_click, "Inserisci Immagine")
        # btn("code", lambda: self.insert("```\n", "\n```"), "Codice")
        # btn("math", lambda: self.insert("$", "$"), "Matematica")
        
    def insert(self, prefix, suffix=""):
        try:
            self.master.master.editor.insert_around_cursor(prefix, suffix)
        except:
             # Fallback
             self.master.master.editor.insert_at_cursor(prefix + suffix)

    def insert_prefix(self, prefix):
        self.master.master.editor.insert_at_cursor(prefix)

    def on_image_click(self):
        from customtkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            app = self.master.master
            try:
                from pathlib import Path
                p = Path(path)
                rel_path = app.pm.add_asset(p)
                app.editor.insert_image(rel_path)
            except Exception as e:
                print(f"Error adding image: {e}")
