
import customtkinter as ctk

class EditorFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self, width=400, corner_radius=10, font=("Consolas", 14), wrap="word")
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5) # Kept grid as it aligns with grid_columnconfigure/rowconfigure
        
        # Syntax Highlighting Tags
        self.textbox._textbox.tag_config("header", foreground="#ffaa00", font=("Consolas", 14, "bold")) # Orange headers
        self.textbox._textbox.tag_config("bold", font=("Consolas", 12, "bold"))
        self.textbox._textbox.tag_config("italic", font=("Consolas", 12, "italic"))
        self.textbox._textbox.tag_config("code", foreground="#00ff00", font=("Consolas", 12)) # Green code

        self.textbox.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event=None):
        self.highlight_syntax()

    def highlight_syntax(self):
        text_widget = self.textbox._textbox
        content = text_widget.get("1.0", "end")
        
        # Remove old tags
        for tag in ["header", "bold", "italic", "code"]:
            text_widget.tag_remove(tag, "1.0", "end")
        
        # Simple Regex-based highlighting
        import re
        
        # Headers (# ...)
        for match in re.finditer(r"(^|\n)(#{1,6}\s.*)", content):
            start = f"1.0 + {match.start(2)} chars"
            end = f"1.0 + {match.end(2)} chars"
            text_widget.tag_add("header", start, end)

        # Bold (**...**)
        for match in re.finditer(r"(\*\*.+?\*\*)", content):
             start = f"1.0 + {match.start(1)} chars"
             end = f"1.0 + {match.end(1)} chars"
             text_widget.tag_add("bold", start, end)
             
        # Italic (*...*)
        for match in re.finditer(r"(\*[^\*]+?\*)", content):
             start = f"1.0 + {match.start(1)} chars"
             end = f"1.0 + {match.end(1)} chars"
             text_widget.tag_add("italic", start, end)

    def get_text(self):
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.highlight_syntax() # Apply on load

    def insert_at_cursor(self, text):
        self.textbox.insert("insert", text)

    def insert_image(self, relative_path):
        """Inserts markdown image syntax."""
        text = f"\n![Alt Text]({relative_path})\n"
        self.insert_at_cursor(text)
