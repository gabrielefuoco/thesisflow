import customtkinter as ctk
import tkinter as tk
from typing import List, Callable
import re
from src.ui.theme import Theme
from src.ui.components.line_numbers import LineNumbers
from src.ui.components.find_replace import FindReplaceDialog
from src.ui.components.citation_popup import CitationPopup
from src.utils.html_renderer import HTMLRenderer
from tkhtmlview import HTMLLabel

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
        self.textbox.bind("<ButtonRelease-1>", self.on_click)
        self.textbox.bind("<Control-f>", self.open_find_dialog)
        
        self.preview_visible = False
        self.preview_container = ctk.CTkFrame(self, width=0, fg_color=Theme.COLOR_PANEL)
        self.html_label = HTMLLabel(self.preview_container, html="<h1>Anteprima</h1>", background=Theme.COLOR_BG)
        self.html_label.pack(fill="both", expand=True, padx=10, pady=10)

        self._debounce_timer = None
        self.suggestion_popup = None
        
        self.status_bar = ctk.CTkLabel(self, text="", text_color=Theme.TEXT_DIM, font=("Segoe UI", 10), height=20, anchor="e")
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10)

    def _on_scroll(self, *args):
        self.line_numbers.redraw()

    def setup_tags(self):
        tb = self.textbox._textbox
        # Header tags
        tb.tag_config("h1", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), foreground=Theme.COLOR_ACCENT)
        tb.tag_config("h2", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), foreground=Theme.COLOR_ACCENT)
        tb.tag_config("h3", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H3, "bold"), foreground=Theme.COLOR_ACCENT)
        
        # Markdown marker tags (hidden by default)
        tb.tag_config("md_marker", elide=True, foreground=Theme.TEXT_DIM)
        
        # Styling tags
        tb.tag_config("bold", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MAIN, "bold"))
        tb.tag_config("italic", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MAIN, "italic"))
        tb.tag_config("code", font=("Consolas", 14), background="#333333")
        tb.tag_config("link", foreground=Theme.COLOR_ACCENT, underline=True)

    def toggle_preview(self):
        self.preview_visible = not self.preview_visible
        if self.preview_visible:
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=1)
            self.preview_container.grid(row=0, column=2, sticky="nsew", padx=(5,0), pady=0)
            self.textbox.grid_configure(padx=(10, 20))
            self.update_preview()
        else:
            self.preview_container.grid_forget()
            self.grid_columnconfigure(2, weight=0)
            self.textbox.grid_configure(padx=(10, 100))

    def update_preview(self):
        text = self.get_text()
        pm = getattr(self.master.master, 'pm', None)
        project_path = pm.current_project_path if pm else None
        
        html = HTMLRenderer.render(text, project_path)
        self.html_label.set_html(html)

    def render_markdown(self, text, parent):
        """Deprecated: using HTMLRenderer instead."""
        pass

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
        self._debounce_timer = self.after(100, self.perform_updates)
        
        if event.char == "@":
            self.show_suggestions()

    def on_click(self, event):
        # When clicking, we might change lines, so we need to update elision
        self.highlight_syntax()

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
        tb = self.textbox._textbox
        # Clear all markdown tags
        for tag in ["h1", "h2", "h3", "md_marker", "bold", "italic", "link"]:
            tb.tag_remove(tag, "1.0", "end")
            
        text = self.get_text()
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_idx = i + 1
            
            # 1. Headers
            h_match = re.match(r"^(#{1,3})\s+(.*)", line)
            if h_match:
                level = len(h_match.group(1))
                tag = f"h{level}"
                tb.tag_add(tag, f"{line_idx}.0", f"{line_idx}.end")
                # Mark only the '#' and the space after it for elision
                tb.tag_add("md_marker", f"{line_idx}.0", f"{line_idx}.{level + 1}")
                
            # 2. Bold / Italic
            def tag_markers(pattern, styling_tag, group_num=2):
                for m in re.finditer(pattern, line):
                    # Whole match
                    start_char = m.start()
                    end_char = m.end()
                    
                    # Style the content
                    tb.tag_add(styling_tag, f"{line_idx}.{m.start(group_num)}", f"{line_idx}.{m.end(group_num)}")
                    
                    # Elide the markers
                    # Pattern must have 3 groups: [prefix, content, suffix]
                    tb.tag_add("md_marker", f"{line_idx}.{m.start(1)}", f"{line_idx}.{m.end(1)}")
                    tb.tag_add("md_marker", f"{line_idx}.{m.start(3)}", f"{line_idx}.{m.end(3)}")

            tag_markers(r"(\*\*)(.+?)(\*\*)", "bold")
            tag_markers(r"(\_)(.+?)(\_)", "italic")
            
            # 3. Links [text](url)
            for m in re.finditer(r"(\[)(.+?)(\]\(.+?\))", line):
                 tb.tag_add("link", f"{line_idx}.{m.start(2)}", f"{line_idx}.{m.end(2)}")
                 tb.tag_add("md_marker", f"{line_idx}.{m.start(1)}", f"{line_idx}.{m.end(1)}")
                 tb.tag_add("md_marker", f"{line_idx}.{m.start(3)}", f"{line_idx}.{m.end(3)}")

        self.reveal_syntax()

    def reveal_syntax(self):
        """Removes the md_marker tag from the current line so the user can edit markdown."""
        tb = self.textbox._textbox
        try:
            cursor_pos = tb.index("insert")
            line_num = cursor_pos.split('.')[0]
            tb.tag_remove("md_marker", f"{line_num}.0", f"{line_num}.end")
        except:
            pass

    def search_and_tag(self, pattern, tag):
        # Deprecated by new highlight_syntax logic but kept for safety if used elsewhere
        pass

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
