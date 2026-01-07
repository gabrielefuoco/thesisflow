
import customtkinter as ctk

class EditorFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self, width=400, corner_radius=10, font=("Consolas", 14), wrap="word")
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def get_text(self):
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)

    def insert_at_cursor(self, text):
        self.textbox.insert("insert", text)

    def insert_image(self, relative_path):
        """Inserts markdown image syntax."""
        text = f"\n![Alt Text]({relative_path})\n"
        self.insert_at_cursor(text)
