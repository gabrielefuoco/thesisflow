import customtkinter as ctk
import tkinter as tk
from typing import List, Callable
import re
from src.ui.theme import Theme
from src.ui.components.line_numbers import LineNumbers
from src.ui.components.find_replace import FindReplaceDialog
from src.ui.components.citation_popup import CitationPopup

class EditorFrame(ctk.CTkFrame):
    def __init__(self, master, on_change: Callable = None, get_citations_callback: Callable[[], List[str]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_change = on_change
        self.get_citations_callback = get_citations_callback

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Line Nums
        self.grid_columnconfigure(1, weight=1) # Editor
        self.grid_columnconfigure(2, weight=0) # Preview

        # --- Editor Container ---
        self.editor_container = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_container.grid(row=0, column=1, sticky="nsew")
        self.editor_container.grid_rowconfigure(0, weight=1)
        self.editor_container.grid_columnconfigure(1, weight=1) 
        self.editor_container.grid_columnconfigure(0, weight=0)
        
        # The Text Area
        self.textbox = ctk.CTkTextbox(self.editor_container, 
                                      font=(Theme.FONT_FAMILY, 16),
                                      fg_color=Theme.EDITOR_BG,
                                      text_color=Theme.EDITOR_TEXT,
                                      wrap="word",
                                      undo=True,
                                      corner_radius=0,
                                      border_width=0)
        self.textbox.grid(row=0, column=1, sticky="nsew", padx=(10, 100), pady=20) 
        
        # Line Numbers
        self.line_numbers = LineNumbers(self.editor_container, self.textbox, width=50, bg=Theme.COLOR_BG, highlightthickness=0)
        self.line_numbers.grid(row=0, column=0, sticky="ns", pady=20)
        
        self.textbox._textbox.configure(yscrollcommand=self._on_scroll)
        
        self.setup_tags()
        
        self.textbox.bind("<<Modified>>", self._on_text_change)
        self.textbox.bind("<KeyRelease>", self.on_key_release)
        self.textbox.bind("<Control-f>", self.open_find_dialog)
        
        self.preview_visible = False
        self.preview_frame = ctk.CTkScrollableFrame(self, label_text="Anteprima", width=0, fg_color=Theme.COLOR_PANEL)

        self._debounce_timer = None
        self.suggestion_popup = None
        
        self.status_bar = ctk.CTkLabel(self, text="", text_color=Theme.TEXT_DIM, font=("Segoe UI", 10), height=20, anchor="e")
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10)

    def _on_scroll(self, *args):
        self.line_numbers.redraw()

    def setup_tags(self):
        tb = self.textbox._textbox
        tb.tag_config("headers", font=(Theme.FONT_FAMILY, 20, "bold"), foreground=Theme.COLOR_ACCENT)
        tb.tag_config("bold", font=(Theme.FONT_FAMILY, 16, "bold"))
        tb.tag_config("italic", font=(Theme.FONT_FAMILY, 16, "italic"))
        tb.tag_config("code", font=("Consolas", 14), background="#333333")

    def toggle_preview(self):
        self.preview_visible = not self.preview_visible
        if self.preview_visible:
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=1)
            self.preview_frame.grid(row=0, column=2, sticky="nsew", padx=(5,0), pady=0)
            self.textbox.grid_configure(padx=(10, 20))
            self.update_preview()
        else:
            self.preview_frame.grid_forget()
            self.grid_columnconfigure(2, weight=0)
            self.textbox.grid_configure(padx=(10, 100))

    def update_preview(self):
        for w in self.preview_frame.winfo_children(): w.destroy()
        text = self.get_text()
        self.render_markdown(text, self.preview_frame)

    def render_markdown(self, text, parent):
        pm = self.master.master.pm
        lines = text.split('\n')
        current_block = []
        
        def flush_block():
            if current_block:
                content = "\n".join(current_block)
                if not content.strip(): return
                lbl = ctk.CTkLabel(parent, text=content, font=("Segoe UI", 14), text_color=Theme.TEXT_MAIN, anchor="w", justify="left", wraplength=400)
                lbl.pack(fill="x", pady=2, padx=5)
                current_block.clear()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                flush_block()
                continue
            
            if stripped.startswith("# "):
                flush_block()
                ctk.CTkLabel(parent, text=stripped[2:], font=("Segoe UI", 24, "bold"), text_color=Theme.TEXT_MAIN, anchor="w", wraplength=400).pack(fill="x", pady=(10, 5), padx=5)
            elif stripped.startswith("## "):
                flush_block()
                ctk.CTkLabel(parent, text=stripped[3:], font=("Segoe UI", 20, "bold"), text_color=Theme.TEXT_MAIN, anchor="w", wraplength=400).pack(fill="x", pady=(8, 4), padx=5)
            elif stripped.startswith("### "):
                flush_block()
                ctk.CTkLabel(parent, text=stripped[4:], font=("Segoe UI", 16, "bold"), text_color=Theme.TEXT_MAIN, anchor="w", wraplength=400).pack(fill="x", pady=(5, 2), padx=5)
            elif stripped.startswith("![") and "](" in stripped and stripped.endswith(")"):
                flush_block()
                try:
                    start = stripped.index("](") + 2
                    end = stripped.rindex(")")
                    img_path_str = stripped[start:end]
                    if pm and pm.current_project_path:
                        full_path = pm.current_project_path / img_path_str
                        if full_path.exists():
                             from PIL import Image
                             try:
                                 pil_img = Image.open(full_path)
                                 w, h = pil_img.size
                                 max_w = 380
                                 if w > max_w:
                                     ratio = max_w / w
                                     new_h = int(h * ratio)
                                     ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(max_w, new_h))
                                 else:
                                     ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w, h))
                                 ctk.CTkLabel(parent, text="", image=ctk_img).pack(pady=10)
                             except Exception:
                                 ctk.CTkLabel(parent, text=f"[Invalid Image: {img_path_str}]", text_color="red").pack(pady=5)
                        else:
                             ctk.CTkLabel(parent, text=f"[Image Not Found: {img_path_str}]", text_color="red").pack(pady=5)
                except Exception:
                     ctk.CTkLabel(parent, text=f"[Image syntax error]", text_color="red").pack(pady=5)
            elif stripped.startswith("> "):
                flush_block()
                q_frame = ctk.CTkFrame(parent, fg_color=Theme.COLOR_PANEL_HOVER, border_width=0) 
                q_frame.pack(fill="x", padx=(10, 5), pady=2)
                border = ctk.CTkFrame(q_frame, width=4, fg_color=Theme.COLOR_ACCENT)
                border.pack(side="left", fill="y")
                ctk.CTkLabel(q_frame, text=stripped[2:], font=("Segoe UI", 14, "italic"), text_color=Theme.TEXT_DIM, anchor="w", wraplength=380).pack(side="left", fill="x", padx=5, pady=5)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                flush_block()
                l_frame = ctk.CTkFrame(parent, fg_color="transparent")
                l_frame.pack(fill="x", padx=5, pady=0)
                ctk.CTkLabel(l_frame, text="•", font=("Segoe UI", 14, "bold"), text_color=Theme.COLOR_ACCENT).pack(side="left", anchor="n")
                ctk.CTkLabel(l_frame, text=stripped[2:], font=("Segoe UI", 14), text_color=Theme.TEXT_MAIN, anchor="w", wraplength=370).pack(side="left", fill="x")
            elif stripped == "---":
                flush_block()
                ctk.CTkFrame(parent, height=2, fg_color=Theme.COLOR_BORDER).pack(fill="x", pady=10, padx=20)
            else:
                current_block.append(line)
        flush_block()

    def get_text(self):
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.highlight_syntax()
        self.line_numbers.redraw()

    def insert_at_cursor(self, text):
        self.textbox.insert("insert", text)
        self.highlight_syntax()
        self.line_numbers.redraw()
        
    def insert_around_cursor(self, prefix, suffix):
        try:
            sel_start = self.textbox.index("sel.first")
            sel_end = self.textbox.index("sel.last")
            selection = self.textbox.get(sel_start, sel_end)
            self.textbox.delete(sel_start, sel_end)
            self.textbox.insert(sel_start, f"{prefix}{selection}{suffix}")
        except tk.TclError:
            self.textbox.insert("insert", prefix + suffix)
        self.line_numbers.redraw()

    def insert_image(self, path):
         self.insert_at_cursor(f"\\n![Image]({path})\\n")

    def _on_text_change(self, event=None):
        self.textbox.edit_modified(False)
        if self.on_change: self.on_change()
        self.line_numbers.redraw()

    def on_key_release(self, event):
        if self._debounce_timer: self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(500, self.perform_updates)
        
        if event.char == "@":
            self.show_suggestions()

    def perform_updates(self):
        self.highlight_syntax()
        self.update_status()
        if self.preview_visible: self.update_preview()
        self.line_numbers.redraw()
        
        outline_panel = None
        for child in self.master.winfo_children():
            from src.ui.outline import OutlinePanel
            if isinstance(child, OutlinePanel):
                outline_panel = child
                break
        if outline_panel:
            headings = self.extract_headings()
            outline_panel.update_outline(headings)

    def extract_headings(self):
        headings = []
        text = self.get_text()
        for idx, line in enumerate(text.split('\\n')):
            match = re.match(r"^(#{1,3})\s+(.*)", line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                index = f"{idx + 1}.0"
                headings.append((level, title, index))
        return headings

    def scroll_to(self, index):
        self.textbox.see(index)
        self.line_numbers.redraw()

    def highlight_syntax(self):
        try:
            self.textbox._textbox.tag_remove("headers", "1.0", "end")
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
        FindReplaceDialog(self, self.textbox)

    def show_suggestions(self):
        if not self.get_citations_callback: return
        keys = self.get_citations_callback()
        if not keys: return
        
        if self.suggestion_popup: return 
        
        try:
             bbox = self.textbox.bbox("insert") 
             if not bbox: return 
        except: return

        self.suggestion_popup = CitationPopup(self.textbox, keys, self.insert_citation, bbox)
        # Bind popup close? CitationPopup handles FocusOut.
        # But we need to cleanup self.suggestion_popup when it destroys itself.
        # Ideally CitationPopup calls back when destroyed or we inspect logic.
        # For simple usage, we can check `if self.suggestion_popup and self.suggestion_popup.winfo_exists()`
        # But `CitationPopup` is Toplevel.
        
    def insert_citation(self, key):
        self.insert_at_cursor(f"{key}")
        self.suggestion_popup = None
