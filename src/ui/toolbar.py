
import customtkinter as ctk

from src.utils.icons import IconFactory
from src.ui.tooltip import ToolTip
from src.utils.i18n import I18N

class ToolbarFrame(ctk.CTkFrame):
    def __init__(self, master, command_compile=None, **kwargs):
        super().__init__(master, height=50, **kwargs)
        
        self.command_compile = command_compile

        # Layout
        self.grid_columnconfigure(0, weight=0) # Left spacer
        # We'll just pack buttons left to right

        # Bold
        self.btn_bold = ctk.CTkButton(self, text="B", width=40, font=("Arial", 12, "bold"), command=lambda: self.master.master.editor.insert_at_cursor("**bold**"))
        # self.btn_bold = ctk.CTkButton(self, text="", image=IconFactory.get_icon("bold"), width=30, command=...)
        # Keeping text for now ensuring icons work, actually let's try direct replace if possible or hybrid
        self.btn_bold.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(self.btn_bold, f"{I18N.t('bold')} (Ctrl+B)")

        self.btn_italic = ctk.CTkButton(self, text="I", width=40, font=("Arial", 12, "italic"), command=lambda: self.master.master.editor.insert_at_cursor("_italic_"))
        self.btn_italic.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(self.btn_italic, f"{I18N.t('italic')} (Ctrl+I)")
        
        self.btn_math = ctk.CTkButton(self, text="Math", width=50, command=lambda: self.master.master.editor.insert_at_cursor("$E=mc^2$"))
        self.btn_math.grid(row=0, column=2, padx=5, pady=5)

        self.btn_img = ctk.CTkButton(self, text="Img", width=50, fg_color="gray", command=self.on_image_click)
        self.btn_img.grid(row=0, column=3, padx=5, pady=5)

        # Formatting Group 2
        self.btn_h1 = ctk.CTkButton(self, text="H1", width=30, command=lambda: self.insert_md("# "))
        self.btn_h1.grid(row=0, column=4, padx=2)
        
        self.btn_h2 = ctk.CTkButton(self, text="H2", width=30, command=lambda: self.insert_md("## "))
        self.btn_h2.grid(row=0, column=5, padx=2)
        
        self.btn_list = ctk.CTkButton(self, text="", image=IconFactory.get_icon("list"), width=40, command=lambda: self.insert_md("- "))
        self.btn_list.grid(row=0, column=6, padx=2)
        ToolTip(self.btn_list, I18N.t("list"))
        
        self.btn_quote = ctk.CTkButton(self, text='""', width=30, command=lambda: self.insert_md("> "))
        self.btn_quote.grid(row=0, column=7, padx=2)

        # Spacer
        self.spacer = ctk.CTkLabel(self, text="", width=20)
        self.spacer.grid(row=0, column=9)
        
        # Theme Toggle
        self.btn_theme = ctk.CTkButton(self, text="", image=IconFactory.get_icon("list", color="yellow"), width=30, command=self.toggle_theme)
        # Using 'list' as placeholder for Sun/Moon if 'sun' not defined, lets assume generic icon
        self.btn_theme.grid(row=0, column=10, padx=5)
        ToolTip(self.btn_theme, I18N.t("change_theme"))

        # Compile Button (Right aligned? Or just next)
        self.btn_compile = ctk.CTkButton(self, text=I18N.t("compile"), fg_color="green", hover_color="darkgreen", command=self.command_compile)
        self.btn_compile.grid(row=0, column=11, padx=20, pady=5)
        
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        
    def insert_md(self, text):
        self.master.master.editor.insert_at_cursor(text)

    def on_image_click(self):
        from customtkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            # We need to call the app to handle the file copy via ProjectManager
            app = self.master.master
            # Assuming app has a method to add asset, or we access app.pm directly?
            # Better to have key methods on App.
            try:
                # Need to convert to Path
                from pathlib import Path
                p = Path(path)
                rel_path = app.pm.add_asset(p)
                app.editor.insert_image(rel_path)
            except Exception as e:
                print(f"Error adding image: {e}")
