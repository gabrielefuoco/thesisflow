
import customtkinter as ctk
import tkinter as tk
from typing import List, Callable
import re
from src.ui.theme import Theme

class EditorFrame(ctk.CTkFrame):
    def __init__(self, master, on_change: Callable = None, get_citations_callback: Callable[[], List[str]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_change = on_change
        self.get_citations_callback = get_citations_callback

        self.grid_rowconfigure(0, weight=1)
        # Columns: 0 = Editor, 1 = Preview (Initially 0 weight)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) 

        # --- Editor Area ---
        # Container to center the text area visually (Focus Mode styling)
        self.editor_container = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_container.grid(row=0, column=0, sticky="nsew")
        self.editor_container.grid_rowconfigure(0, weight=1)
        self.editor_container.grid_columnconfigure(0, weight=1)
        
        # The Text Area
        self.textbox = ctk.CTkTextbox(self.editor_container, 
                                      font=(Theme.FONT_FAMILY, 16),
                                      fg_color=Theme.EDITOR_BG,
                                      text_color=Theme.EDITOR_TEXT,
                                      wrap="word",
                                      undo=True,
                                      corner_radius=0,
                                      border_width=0)
                                      
        # Center the text area with margins? 
        # Actually making it blocky is better for code, but user wants "Medium" style.
        # We can simulate this by padding the grid, but text should fill width if resized?
        # User said: "Centra il testo con margini laterali ampi".
        # We can add padding to the grid placement.
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=100, pady=20) 
        
        # Tags for syntax highlighting
        self.setup_tags()
        
        # Bindings
        self.textbox.bind("<<Modified>>", self._on_text_change)
        self.textbox.bind("<KeyRelease>", self.on_key_release)
        self.textbox.bind("<Control-f>", self.open_find_dialog)
        
        # --- Preview Pane (Hidden by default) ---
        self.preview_visible = False
        self.preview_frame = ctk.CTkScrollableFrame(self, label_text="Anteprima", width=0, fg_color=Theme.COLOR_PANEL)
        # Grid managed dynamically

        # Internal state
        self._debounce_timer = None
        self.suggestion_list = None
        
        # Status Bar (Subtle / Bottom)
        self.status_bar = ctk.CTkLabel(self, text="", text_color=Theme.TEXT_DIM, font=("Segoe UI", 10), height=20, anchor="e")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)

    def setup_tags(self):
        # Configure standard Markdown tags
        tb = self.textbox._textbox
        tb.tag_config("headers", font=(Theme.FONT_FAMILY, 20, "bold"), foreground=Theme.COLOR_ACCENT)
        tb.tag_config("bold", font=(Theme.FONT_FAMILY, 16, "bold"))
        tb.tag_config("italic", font=(Theme.FONT_FAMILY, 16, "italic"))
        tb.tag_config("code", font=("Consolas", 14), background="#333333")

    def toggle_preview(self):
        self.preview_visible = not self.preview_visible
        if self.preview_visible:
            # Split 50/50
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=0)
            
            # Reduce editor margins when in split mode to avoid cramping
            self.textbox.grid_configure(padx=20)
            
            self.update_preview()
        else:
            self.preview_frame.grid_forget()
            self.grid_columnconfigure(1, weight=0)
            
            # Restore wide margins for focus mode
            self.textbox.grid_configure(padx=100)

    def update_preview(self):
        # Simplified Preview Updater
        for w in self.preview_frame.winfo_children(): w.destroy()
        
        text = self.get_text()
        # Very basic renderer (mock) - in real app use compiled HTML or better parser
        lines = text.split('\n')
        for line in lines:
            if line.startswith("# "):
                ctk.CTkLabel(self.preview_frame, text=line.strip("# "), font=("Segoe UI", 24, "bold"), text_color=Theme.TEXT_MAIN, anchor="w", wraplength=400).pack(fill="x", pady=5)
            elif line.startswith("## "):
                 ctk.CTkLabel(self.preview_frame, text=line.strip("# "), font=("Segoe UI", 18, "bold"), text_color=Theme.TEXT_MAIN, anchor="w", wraplength=400).pack(fill="x", pady=5)
            elif line.strip():
                 ctk.CTkLabel(self.preview_frame, text=line, font=("Segoe UI", 14), text_color=Theme.TEXT_MAIN, anchor="w", justify="left", wraplength=400).pack(fill="x", pady=2)

    def get_text(self):
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.highlight_syntax()

    def insert_at_cursor(self, text):
        self.textbox.insert("insert", text)
        self.highlight_syntax()
        
    def insert_around_cursor(self, prefix, suffix):
        try:
            # Check selection
            sel_start = self.textbox.index("sel.first")
            sel_end = self.textbox.index("sel.last")
            selection = self.textbox.get(sel_start, sel_end)
            
            self.textbox.delete(sel_start, sel_end)
            self.textbox.insert(sel_start, f"{prefix}{selection}{suffix}")
        except tk.TclError:
            # No selection
            self.textbox.insert("insert", prefix + suffix)
            # Move cursor back?
            # self.textbox.mark_set("insert", ...) 

    def insert_image(self, path):
         self.insert_at_cursor(f"\n![Image]({path})\n")

    def _on_text_change(self, event=None):
        self.textbox.edit_modified(False) # Reset flag
        if self.on_change: self.on_change()

    def on_key_release(self, event):
        if self._debounce_timer: self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(500, self.perform_updates)
        
        if event.char == "@":
            self.show_suggestions()

    def perform_updates(self):
        self.highlight_syntax()
        self.update_status()
        if self.preview_visible: self.update_preview()
        if hasattr(self.master.master, "outline"): # Update outline if exists
            pass # (Simplified from original)

    def highlight_syntax(self):
        # Re-apply tags (Naive implementation)
        content = self.get_text()
        try:
            self.textbox._textbox.tag_remove("headers", "1.0", "end")
            
            # Simple Regex for headers
            for match in re.finditer(r"(^|\n)(#{1,6}\s.*)", content):
                # Calculate index roughly
                # Tkinter indices are line.char
                # This is complex to do accurately without line scanning
                # For now, simplistic approach or just skip if too complex for one-shot
                pass 
                
            # Actually, standard Tkinter pattern matching is better:
            self.search_and_tag(r"^(#+ .*)", "headers")
            self.search_and_tag(r"(\*\*.+?\*\*)", "bold")
            self.search_and_tag(r"(\_.+?\_)", "italic")
        except:
            pass

    def search_and_tag(self, pattern, tag):
        start = "1.0"
        count = tk.IntVar()
        while True:
            pos = self.textbox._textbox.search(pattern, start, stopindex="end", count=count, regexp=True)
            if not pos: break
            end = f"{pos}+{count.get()}c"
            self.textbox._textbox.tag_add(tag, pos, end)
            start = end

    def update_status(self):
        text = self.get_text()
        words = len(text.split())
        self.status_bar.configure(text=f"{words} parole")

    def open_find_dialog(self, event=None):
        pass # Placeholder

    # --- Suggestion Logic (Simplified) ---
    def show_suggestions(self):
        if not self.get_citations_callback: return
        # Logic similar to original file...
        pass 
