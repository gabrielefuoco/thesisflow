import customtkinter as ctk
import tkinter as tk
from typing import List, Callable
import re

class EditorFrame(ctk.CTkFrame):
    def __init__(self, master, on_change: hasattr=None, get_citations_callback: Callable[[], List[str]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_change = on_change # Callback for autosave/dirty state
        self.get_citations_callback = get_citations_callback

        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) # Preview column, 0 initially
        self.grid_rowconfigure(0, weight=1)

        self.editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_frame.grid(row=0, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(0, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.editor_frame, width=400, corner_radius=10, font=("Consolas", 14), wrap="word", undo=True)
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Status Bar
        self.status_bar_frame = ctk.CTkFrame(self, height=25)
        self.status_bar_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.status_bar = ctk.CTkLabel(self.status_bar_frame, text="Parole: 0", font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10)

        self.btn_preview = ctk.CTkButton(self.status_bar_frame, text="👁 Anteprima", width=80, height=20, font=("Arial", 10), command=self.toggle_preview)
        self.btn_preview.pack(side="right", padx=10)

        self._debounce_timer = None

        # Preview Pane
        self.preview_visible = False
        self.preview_frame = ctk.CTkScrollableFrame(self, label_text="Anteprima (Lite)", width=400)
        # self.preview_frame.grid(row=0, column=1...) -> on toggle

        # Autocomplete
        self.suggestion_list = None

        # Syntax Highlighting Tags
        self.textbox._textbox.tag_config("header", foreground="#ffaa00", font=("Consolas", 14, "bold")) # Orange headers
        self.textbox._textbox.tag_config("bold", font=("Consolas", 12, "bold"))
        self.textbox._textbox.tag_config("italic", font=("Consolas", 12, "italic"))
        self.textbox._textbox.tag_config("code", foreground="#00ff00", font=("Consolas", 12)) # Green code

        self.textbox.bind("<KeyRelease>", self.on_key_release)
        self.textbox.bind("<Key>", self.on_key_press)

    def on_key_press(self, event):
        # Close suggestion list on generic keys if open, or navigate
        if self.suggestion_list and self.suggestion_list.winfo_exists():
            if event.keysym == "Escape":
                self.close_suggestions()
                return "break"
        
    def on_key_release(self, event=None):
        if event.char == "@":
            self.show_suggestions()

        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(300, self.perform_updates)
        
        if self.on_change:
            self.on_change() 
    
    def perform_updates(self):
        self.highlight_syntax()
        self.update_word_count()
        if self.preview_visible:
            self.update_preview()
        self._debounce_timer = None

    def update_word_count(self):
        text = self.textbox.get("1.0", "end-1c")
        words = len(text.split())
        self.status_bar.configure(text=f"Parole: {words}")

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

    # --- Preview Logic ---
    def toggle_preview(self):
        self.preview_visible = not self.preview_visible
        if self.preview_visible:
            self.grid_columnconfigure(1, weight=1)
            self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            self.update_preview()
        else:
            self.preview_frame.grid_forget()
            self.grid_columnconfigure(1, weight=0)

    def update_preview(self):
        # Basic Markdown Rendering to Labels
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
            
        md_text = self.get_text()
        
        # Simple parser loop
        lines = md_text.split('\n')
        for line in lines:
            if line.startswith('# '):
                ctk.CTkLabel(self.preview_frame, text=line[2:], font=("Arial", 20, "bold"), wraplength=350, anchor="w", justify="left").pack(fill="x", pady=(10,5))
            elif line.startswith('## '):
                ctk.CTkLabel(self.preview_frame, text=line[3:], font=("Arial", 16, "bold"), wraplength=350, anchor="w", justify="left").pack(fill="x", pady=(8,4))
            elif line.startswith('!['):
                ctk.CTkLabel(self.preview_frame, text="[IMMAGINE]", text_color="gray").pack(fill="x")
            elif line.strip() == "":
                ctk.CTkLabel(self.preview_frame, text="", height=5).pack()
            else:
                ctk.CTkLabel(self.preview_frame, text=line, font=("Arial", 12), wraplength=350, anchor="w", justify="left").pack(fill="x")

    # --- Autocomplete Logic ---
    def show_suggestions(self):
        if not self.get_citations_callback: return
        citations = self.get_citations_callback()
        if not citations: return
        
        # Determine position
        self.close_suggestions()
        x, y, w, h = self.textbox.bbox("insert")
        
        # Adjustment for CTkTextbox offset inside frame
        # bbox returns relative coordinates.
        # We need a popover. CTk doesn't have a Listbox, use tk.Listbox
        
        self.suggestion_list = tk.Listbox(self, font=("Consolas", 12))
        # This placement is tricky in CTk. Let's place it absolutely relative to editor frame.
        # This is a naive implementation; real one requires coordinate mapping
        self.suggestion_list.place(x=50, y=50, width=300, height=100) # Placeholder pos
        
        for cit in citations:
            self.suggestion_list.insert(tk.END, cit)
            
        self.suggestion_list.bind("<<ListboxSelect>>", self.on_suggestion_select)
        self.suggestion_list.bind("<FocusOut>", lambda e: self.close_suggestions())
        self.suggestion_list.focus_set()

    def close_suggestions(self):
        if self.suggestion_list:
            self.suggestion_list.destroy()
            self.suggestion_list = None

    def on_suggestion_select(self, event):
        if not self.suggestion_list: return
        selection = self.suggestion_list.curselection()
        if selection:
            res = self.suggestion_list.get(selection[0])
            # Insert
            # We typed '@', cursor is after it.
            # Insert the key. 
            # Note: citations usually come as "key - Title". We just want "key".
            key = res.split(' ')[0]
            self.textbox.insert("insert", key)
            self.close_suggestions()
