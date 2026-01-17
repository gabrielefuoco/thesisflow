import customtkinter as ctk
from src.utils.icons import IconFactory
from src.ui.tooltip import ToolTip
from src.utils.i18n import I18N
from src.ui.theme import Theme

class ToolbarFrame(ctk.CTkFrame):
    def __init__(self, master, command_compile=None, command_focus=None, **kwargs):
        super().__init__(master, height=40, fg_color="transparent", corner_radius=0, **kwargs)
        
        self.editor = None # To be set by App
        
        self.grid_columnconfigure(99, weight=1) # Spacer usually
        
        # Helper to create styled buttons
        def btn(icon, cmd, tip, col=0):
            # Safe icon fallback or try catch? 
            # We assume IconFactory has these standard names or handling.
            image = IconFactory.get_icon(icon, size=(16,16))
            if not image: image = IconFactory.get_icon("file", size=(16,16)) # Fallback

            b = ctk.CTkButton(self, text="", image=image, 
                              width=32, height=32,
                              fg_color="transparent", hover_color=Theme.COLOR_PANEL_HOVER,
                              command=cmd)
            b.pack(side="left", padx=2)
            ToolTip(b, tip)
            return b
            
        def sep():
            s = ctk.CTkFrame(self, width=2, height=20, fg_color=Theme.COLOR_BORDER)
            s.pack(side="left", padx=5, pady=10)

        # Undo/Redo
        btn("undo", self.on_undo, "Undo")
        btn("redo", self.on_redo, "Redo")
        sep()
        
        # Format
        btn("bold", lambda: self.insert("**", "**"), I18N.t("bold"))
        btn("italic", lambda: self.insert("_", "_"), I18N.t("italic"))
        
        sep()
        
        # Headers
        h1 = ctk.CTkButton(self, text="H1", width=32, fg_color="transparent", font=(Theme.FONT_FAMILY, 12, "bold"), 
                      hover_color=Theme.COLOR_PANEL_HOVER, command=lambda: self.insert_prefix("# "))
        h1.pack(side="left")
        ToolTip(h1, "Titolo 1")
        
        h2 = ctk.CTkButton(self, text="H2", width=32, fg_color="transparent", font=(Theme.FONT_FAMILY, 11, "bold"), 
                      hover_color=Theme.COLOR_PANEL_HOVER, command=lambda: self.insert_prefix("## "))
        h2.pack(side="left")
        ToolTip(h2, "Titolo 2")
        
        sep()
        
        # Lists & Quotes
        btn("list", lambda: self.insert_prefix("- "), I18N.t("list"))
        btn("quote", lambda: self.insert_prefix("> "), "Citazione") 
        
        sep()
        
        # Inserts
        btn("image", self.on_image_click, "Inserisci Immagine")
        btn("code", lambda: self.insert("```\n", "\n```"), "Codice")
        
        sep()
        
        # Actions
        btn("eye", self.on_toggle_preview, "Attiva/Disattiva Anteprima") 
        
        if command_focus:
            # Use 'maximize' or generic icon for Focus
            btn("maximize", command_focus, "Focus Mode (Distraction Free)")
        
    def on_undo(self): 
        if self.editor:
            try: self.editor.textbox.edit_undo()
            except: pass
        
    def on_redo(self):
        if self.editor:
            try: self.editor.textbox.edit_redo()
            except: pass
        
    def insert(self, prefix, suffix=""):
        if not self.editor: return
        try:
            self.editor.insert_around_cursor(prefix, suffix)
        except:
             # Fallback
             self.editor.insert_at_cursor(prefix + suffix)

    def insert_prefix(self, prefix):
        if self.editor:
            self.editor.insert_at_cursor(prefix)

    def on_image_click(self):
        from customtkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path and self.editor:
            app = self.master.master.master
            try:
                from pathlib import Path
                p = Path(path)
                rel_path = app.pm.add_asset(p)
                self.editor.insert_image(rel_path)
            except Exception as e:
                print(f"Error adding image: {e}")

    def on_toggle_preview(self):
        if self.editor:
            self.editor.toggle_preview()
