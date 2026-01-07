
import customtkinter as ctk
from src.engine.models import Chapter
from typing import Callable
from src.utils.i18n import I18N

import tkinter as tk # For Menu

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, on_chapter_select: Callable[[Chapter], None], on_add_chapter: Callable[[], None], on_move_chapter: Callable[[str], None], on_show_bib: Callable[[], None], on_open_settings: Callable[[], None], on_rename_chapter: Callable[[Chapter], None] = None, on_delete_chapter: Callable[[Chapter], None] = None, **kwargs):
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        self.on_chapter_select = on_chapter_select
        self.on_add_chapter = on_add_chapter
        self.on_move_chapter = on_move_chapter # 'up' or 'down'
        self.on_show_bib = on_show_bib
        self.on_show_bib = on_show_bib
        self.on_open_settings = on_open_settings
        self.on_rename_chapter = on_rename_chapter
        self.on_delete_chapter = on_delete_chapter
        self.on_export_as = kwargs.get("on_export_as") # New callback
        
        self.project_root = None # Needs to be set!
        
        self.selected_chapter_id = None

        self.grid_rowconfigure(2, weight=1) # List expands
        self.grid_columnconfigure(0, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self, text="ThesisFlow", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Add Chapter Button
        self.btn_add = ctk.CTkButton(self, text="+ Nuovo Capitolo", command=self.on_add_chapter)
        self.btn_add.grid(row=1, column=0, padx=10, pady=10)
        
        from src.utils.icons import IconFactory
        from src.ui.tooltip import ToolTip
        
        # Actions Row
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_add = ctk.CTkButton(self.actions_frame, text="", image=IconFactory.get_icon("plus"), width=30, command=self.on_add_chapter)
        self.btn_add.pack(side="left", padx=2)
        ToolTip(self.btn_add, I18N.t("btn_new_chapter"))
        
        self.btn_up = ctk.CTkButton(self.actions_frame, text="", image=IconFactory.get_icon("up"), width=30, command=lambda: self.on_move_chapter("up"))
        self.btn_up.pack(side="left", padx=2)
        ToolTip(self.btn_up, I18N.t("ctx_up", "Su")) # Missing key, define later or use default
        
        self.btn_down = ctk.CTkButton(self.actions_frame, text="", image=IconFactory.get_icon("down"), width=30, command=lambda: self.on_move_chapter("down"))
        self.btn_down.pack(side="left", padx=2)
        ToolTip(self.btn_down, I18N.t("ctx_down", "Giù"))
        
        # Tabview for Content
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=5)
        self.tabview.add(I18N.t("sidebar_title"))
        self.tabview.add(I18N.t("sidebar_assets"))
        
        # --- TAB: Structure ---
        self.tab_struct = self.tabview.tab(I18N.t("sidebar_title"))
        self.tab_struct.grid_columnconfigure(0, weight=1)
        self.tab_struct.grid_rowconfigure(0, weight=1) # List expands

        self.chapter_list = ctk.CTkScrollableFrame(self.tab_struct, fg_color="transparent")
        self.chapter_list.pack(fill="both", expand=True)

        # --- TAB: Assets ---
        self.tab_assets = self.tabview.tab(I18N.t("sidebar_assets"))
        self.tab_assets.grid_columnconfigure(0, weight=1)
        self.tab_assets.grid_rowconfigure(0, weight=1)
        
        self.asset_list = ctk.CTkScrollableFrame(self.tab_assets, fg_color="transparent")
        self.asset_list.pack(fill="both", expand=True)
        ctk.CTkButton(self.tab_assets, text="🔄 Aggiorna", command=self.refresh_assets, height=20).pack(pady=5)
        
        # Bottom Actions
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.btn_bib = ctk.CTkButton(self.bottom_frame, text=I18N.t("btn_bib"), fg_color="gray", command=self.on_show_bib)
        self.btn_bib.pack(padx=10, pady=5)

        self.btn_settings = ctk.CTkButton(self.bottom_frame, text=I18N.t("btn_settings"), fg_color="gray", command=self.on_settings)
        self.btn_settings.pack(padx=10, pady=5)
        
        self.btn_close = ctk.CTkButton(self.bottom_frame, text=I18N.t("btn_close_project"), fg_color="darkred", hover_color="red", command=self.on_close_project)
        self.btn_close.pack(padx=10, pady=(5, 10))
        
        # New Export Menu
        self.btn_export_menu = ctk.CTkOptionMenu(self.bottom_frame, values=["Export PDF", "Export DOCX", "Export LaTeX"], command=self.handle_export_menu)
        self.btn_export_menu.set("Export As...")
        self.btn_export_menu.pack(padx=10, pady=5)
        
    def handle_export_menu(self, choice):
        fmt = "pdf"
        if "DOCX" in choice: fmt = "docx"
        if "LaTeX" in choice: fmt = "tex"
        
        # Trigger export in App
        # Need to signal app. Hack access master.master
        if hasattr(self.master.master, "on_compile"):
            # We need to pass format. Existing on_compile takes no args? 
            # We should probably modify App.on_compile to take format.
             self.master.master.on_compile(fmt)
             
        self.btn_export_menu.set("Export As...")

        # Appearance Mode
        self.lbl_mode = ctk.CTkLabel(self.bottom_frame, text="Tema:", font=("Arial", 10))
        self.lbl_mode.pack(pady=(5,0))
        self.option_mode = ctk.CTkOptionMenu(self.bottom_frame, values=["System", "Dark", "Light"], 
                                             command=self.change_appearance_mode, width=100)
        self.option_mode.pack(padx=10, pady=5)

    def on_close_project(self):
         # Need access to App.close_project
         if hasattr(self.master.master, "close_project"):
             self.master.master.close_project()

    def refresh_assets(self):
        # Clear
        for widget in self.asset_list.winfo_children():
            widget.destroy()
            
        # Get Assets from Project Manager (via App)
        # Ideally Sidebar should receive PM or path, or call callback.
        # Hack: access master.master.pm
        try:
            pm = self.master.master.pm
            if not pm.current_project_path: return
            
            assets_dir = pm.current_project_path / "assets"
            if not assets_dir.exists(): return
            
            for f in assets_dir.iterdir():
                if f.is_file():
                    btn = ctk.CTkButton(self.asset_list, text=f.name, anchor="w", fg_color="transparent", border_width=1,
                                        command=lambda n=f.name: self.insert_asset(n))
                    btn.pack(fill="x", pady=2)
        except Exception as e:
            print(f"Error loading assets: {e}")

    def insert_asset(self, filename):
        # Insert markdown to clipboard or editor
        md = f"![Desc](assets/{filename})"
        # Insert to editor
        # Hacky access to app
        try:
             self.master.master.editor.insert_at_cursor(md)
        except:
             pass

    def change_appearance_mode(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)

    def on_settings(self):
        # We need to access the app or project manager. 
        # The Sidebar doesn't hold reference to PM directly, but it can call a callback or access master.
        # Let's add a callback for settings.
        if hasattr(self, 'on_open_settings'):
            self.on_open_settings()


    def update_chapters(self, chapters: list[Chapter]):
        for widget in self.chapter_list.winfo_children():
            widget.destroy()

        # We need project root to scan folders. Hack: access master.master.pm
        pm = self.master.master.pm
        if pm.current_project_path:
             self.project_root = pm.current_project_path

        for i, chapter in enumerate(chapters):
            # Chapter Container
            chap_frame = ctk.CTkFrame(self.chapter_list, fg_color="transparent")
            chap_frame.pack(fill="x", pady=2)

            # Main Chapter Button
            btn = ctk.CTkButton(chap_frame, text=chapter.title, anchor="w",
                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                command=lambda c=chapter: self.on_chapter_select(c))
            btn.pack(fill="x")
            
            # Context Menu Binding
            btn.bind("<Button-3>", lambda event, c=chapter: self.show_context_menu(event, c))
            
            # Sub-files (if folder)
            if self.project_root:
                chap_path = self.project_root / "chapters" / chapter.filename
                if chap_path.is_dir():
                    # Scan for .md files
                    from pathlib import Path
                    # List master.md first? No, master opens with main button. List others.
                    for f in sorted(chap_path.glob("*.md")):
                        if f.name == "master.md": continue
                        
                        sub_btn = ctk.CTkButton(chap_frame, text=f"  ↳ {f.stem.replace('_', ' ')}", 
                                              fg_color="transparent", 
                                              text_color="gray",
                                              anchor="w",
                                              height=20,
                                              font=("Arial", 11),
                                              command=lambda p=f, c=chapter: self.load_file_trigger(p, c))
                        sub_btn.pack(fill="x")

    def load_file_trigger(self, path, chapter):
        # Call app.load_file
        self.master.master.load_file(path, chapter)

    def show_context_menu(self, event, chapter):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Aggiungi Sezione", command=lambda: self.add_subsection_dialog(chapter))
        menu.add_command(label="Rinomina Capitolo", command=lambda: self.on_rename_chapter(chapter) if self.on_rename_chapter else None)
        menu.add_command(label="Elimina Capitolo", command=lambda: self.on_delete_chapter(chapter) if self.on_delete_chapter else None)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def add_subsection_dialog(self, chapter):
        dialog = ctk.CTkInputDialog(text="Nome Sezione:", title="Nuova Sezione")
        name = dialog.get_input()
        if name:
             self.master.master.pm.create_subsection(chapter, name)
             # Refresh
             self.master.master.refresh_sidebar()
