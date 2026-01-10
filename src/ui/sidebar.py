import customtkinter as ctk
import tkinter as tk
from typing import Callable
from pathlib import Path
from src.engine.models import Chapter
from src.utils.i18n import I18N
from src.ui.theme import Theme
from src.utils.icons import IconFactory
from src.ui.tooltip import ToolTip

class AccordionSection(ctk.CTkFrame):
    def __init__(self, master, title, icon_name="folder", is_open=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.is_open = is_open
        self.title = title
        
        # Header (Clickable)
        self.header = ctk.CTkButton(self, text=title, anchor="w", 
                                    fg_color="transparent", hover_color=Theme.COLOR_PANEL_HOVER,
                                    text_color=Theme.TEXT_DIM, font=("Segoe UI", 12, "bold"),
                                    command=self.toggle)
        self.header.pack(fill="x")
        
        # Content Container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        if is_open:
            self.content.pack(fill="both", expand=True)
            
        self.update_icon()
        
    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.content.pack(fill="both", expand=True)
        else:
            self.content.pack_forget()
        self.update_icon()

    def update_icon(self):
        icon = "chevron_down" if self.is_open else "chevron_right"
        self.header.configure(image=IconFactory.get_icon(icon, size=(12,12)))

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, on_chapter_select: Callable[[Chapter], None], on_add_chapter, on_move_chapter, on_show_bib, on_open_settings, on_rename_chapter=None, on_delete_chapter=None, on_theme_toggle=None, on_back=None, **kwargs):
        super().__init__(master, width=250, corner_radius=0, fg_color=Theme.COLOR_PANEL, **kwargs)
        
        self.on_chapter_select = on_chapter_select
        self.on_add_chapter = on_add_chapter
        self.on_move_chapter = on_move_chapter
        self.on_show_bib = on_show_bib
        self.on_open_settings = on_open_settings
        self.on_rename_chapter = on_rename_chapter
        self.on_delete_chapter = on_delete_chapter
        self.on_theme_toggle = on_theme_toggle
        self.on_back = on_back
        
        self.selected_chapter_id = None
        self.project_root = None # Set later via refresh

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Header ---
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.logo_frame.grid(row=0, column=0, sticky="ew")
        
        # Back Button
        if self.on_back:
            self.btn_back = ctk.CTkButton(self.logo_frame, text="", image=IconFactory.get_icon("chevron_left", size=(20,20)),
                                          width=40, height=40, fg_color="transparent", hover_color=Theme.COLOR_PANEL_HOVER,
                                          command=self.on_back)
            self.btn_back.pack(side="left", padx=(10, 0), pady=10)
            ToolTip(self.btn_back, "Torna alla Dashboard")

        ctk.CTkLabel(self.logo_frame, text="ThesisFlow", font=("Segoe UI", 18, "bold"), text_color=Theme.TEXT_MAIN).pack(side="left", padx=10, pady=20)

        # --- Content (Scrollable) ---
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=1, column=0, sticky="nsew")
        
        # Section: Chapters
        self.sec_chapters = AccordionSection(self.scroll_container, "CAPITOLI", is_open=True)
        self.sec_chapters.pack(fill="x", pady=5)
        
        # Section: Assets
        self.sec_assets = AccordionSection(self.scroll_container, "ASSETS", is_open=False)
        self.sec_assets.pack(fill="x", pady=5)
        
        # --- Footer ---
        self.footer = ctk.CTkFrame(self, fg_color=Theme.COLOR_BG, height=50, corner_radius=0)
        self.footer.grid(row=2, column=0, sticky="ew")
        
        # Settings & Bib & Actions
        self.create_footer_button("settings", self.on_open_settings, "Impostazioni")
        self.create_footer_button("file", self.on_show_bib, "Bibliografia")
        self.create_footer_button("plus", self.on_add_chapter, "Nuovo Capitolo")
        
        # Theme Toggle
        if self.on_theme_toggle:
            self.create_footer_button("sun", self.on_theme_toggle, "Cambia Tema") 
            
        self.create_footer_button("play", self.handle_compile_shortcut, "Compila PDF")

    def handle_compile_shortcut(self):
        if hasattr(self.master.master, "on_compile"):
            self.master.master.on_compile()

    def create_footer_button(self, icon, command, tooltip):
        btn = ctk.CTkButton(self.footer, text="", image=IconFactory.get_icon(icon, size=(16,16)), 
                            width=40, height=40, fg_color="transparent", hover_color=Theme.COLOR_PANEL_HOVER,
                            command=command)
        btn.pack(side="left", padx=2, expand=True)
        ToolTip(btn, tooltip)
        
    def update_chapters(self, chapters: list[Chapter]):
        # Clear content
        for widget in self.sec_chapters.content.winfo_children():
            widget.destroy()
            
        # Get PM reference
        pm = self.master.master.pm
        self.project_root = pm.current_project_path

        for chapter in chapters:
            self.render_chapter_item(chapter)

    def render_chapter_item(self, chapter: Chapter):
        # Item Container
        frame = ctk.CTkFrame(self.sec_chapters.content, fg_color="transparent")
        frame.pack(fill="x")
        
        # Selection Indicator (Left Border simulated)
        is_selected = self.selected_chapter_id == chapter.id
        bg_color = Theme.COLOR_PANEL_HOVER if is_selected else "transparent"
        text_color = Theme.COLOR_ACCENT if is_selected else Theme.TEXT_MAIN
        
        btn = ctk.CTkButton(frame, text=chapter.title, anchor="w",
                            fg_color=bg_color, hover_color=Theme.COLOR_PANEL_HOVER,
                            text_color=text_color,
                            font=("Segoe UI", 13),
                            command=lambda c=chapter: self.on_chapter_click(c))
        btn.pack(fill="x", padx=0)
        
        # Context Menu
        btn.bind("<Button-3>", lambda event, c=chapter: self.show_context_menu(event, c))
        
        # Sub-files scan
        if self.project_root:
            subsections = self.master.master.pm.list_subsections(chapter)
            for f in subsections:
                # Sub-item
                sub_btn = ctk.CTkButton(frame, text=f"  {f.stem.replace('_', ' ')}", 
                                      fg_color="transparent", hover_color=Theme.COLOR_PANEL_HOVER,
                                      text_color=Theme.TEXT_DIM,
                                      anchor="w", height=24, font=("Segoe UI", 12),
                                      command=lambda p=f, c=chapter: self.master.master.load_file(p, c))
                sub_btn.pack(fill="x")

    def on_chapter_click(self, chapter):
        self.selected_chapter_id = chapter.id
        self.on_chapter_select(chapter)
        self.update_chapters(self.master.master.pm.manifest.chapters)

    def show_context_menu(self, event, chapter):
        menu = tk.Menu(self, tearoff=0, bg=Theme.COLOR_PANEL, fg="white") 
        menu.add_command(label="Aggiungi Sezione", command=lambda: self.add_subsection_dialog(chapter))
        menu.add_command(label="Rinomina", command=lambda: self.on_rename_chapter(chapter) if self.on_rename_chapter else None)
        menu.add_command(label="Sposta Su", command=lambda: self.on_move_chapter("up"))
        menu.add_command(label="Sposta Giù", command=lambda: self.on_move_chapter("down"))
        menu.add_separator()
        menu.add_command(label="Elimina", command=lambda: self.on_delete_chapter(chapter) if self.on_delete_chapter else None)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def add_subsection_dialog(self, chapter):
        dialog = ctk.CTkInputDialog(text="Nome Sezione:", title="Nuova Sezione")
        name = dialog.get_input()
        if name:
             self.master.master.pm.create_subsection(chapter, name)
             self.update_chapters(self.master.master.pm.manifest.chapters)

    def refresh_assets(self):
        # Clear existing
        for widget in self.sec_assets.content.winfo_children():
            widget.destroy()

        # Use PM
        assets = self.master.master.pm.list_assets()
        
        if not assets:
            ctk.CTkLabel(self.sec_assets.content, text="No assets found", text_color="gray").pack()
            return
            
        for asset in assets:
            self.render_asset_item(asset)

    def render_asset_item(self, asset_path: Path):
        # Frame for hover effect
        frame = ctk.CTkFrame(self.sec_assets.content, fg_color="transparent")
        frame.pack(fill="x", pady=1)
        
        # Determine icon based on suffix
        icon = "image" if asset_path.suffix.lower() in ['.png', '.jpg', '.jpeg'] else "file"
        
        btn = ctk.CTkButton(frame, text=asset_path.name, 
                            image=IconFactory.get_icon(icon, size=(12,12)),
                            anchor="w", fg_color="transparent", 
                            text_color=Theme.TEXT_MAIN, hover_color=Theme.COLOR_PANEL_HOVER,
                            height=24,
                            command=lambda: self.insert_asset(asset_path.name))
        btn.pack(fill="x", padx=10)
        ToolTip(btn, "Clicca per inserire nell'editor")

    def insert_asset(self, filename):
        # Insert markdown image syntax via PM
        pm = self.master.master.pm
        markup = pm.get_asset_markdown(filename)
        self.master.master.editor.insert_at_cursor(markup)
