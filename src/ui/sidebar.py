
import customtkinter as ctk
from src.engine.models import Chapter
from typing import Callable

import tkinter as tk # For Menu

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, on_chapter_select: Callable[[Chapter], None], on_add_chapter: Callable[[], None], on_move_chapter: Callable[[str], None], on_show_bib: Callable[[], None], on_open_settings: Callable[[], None], on_rename_chapter: Callable[[Chapter], None] = None, on_delete_chapter: Callable[[Chapter], None] = None, **kwargs):
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        self.on_chapter_select = on_chapter_select
        self.on_add_chapter = on_add_chapter
        self.on_move_chapter = on_move_chapter # 'up' or 'down'
        self.on_show_bib = on_show_bib
        self.on_open_settings = on_open_settings
        self.on_rename_chapter = on_rename_chapter
        self.on_delete_chapter = on_delete_chapter
        
        self.selected_chapter_id = None

        self.grid_rowconfigure(2, weight=1) # List expands
        self.grid_columnconfigure(0, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self, text="ThesisFlow", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Add Chapter Button
        self.btn_add = ctk.CTkButton(self, text="+ Nuovo Capitolo", command=self.on_add_chapter)
        self.btn_add.grid(row=1, column=0, padx=10, pady=10)
        
        # Actions Row
        # Let's redesign row 1
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_add = ctk.CTkButton(self.actions_frame, text="+", width=30, command=self.on_add_chapter)
        self.btn_add.pack(side="left", padx=2)
        
        self.btn_up = ctk.CTkButton(self.actions_frame, text="▲", width=30, command=lambda: self.on_move_chapter("up"))
        self.btn_up.pack(side="left", padx=2)
        
        self.btn_down = ctk.CTkButton(self.actions_frame, text="▼", width=30, command=lambda: self.on_move_chapter("down"))
        self.btn_down.pack(side="left", padx=2)
        
        # Chapter List Container
        self.chapter_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chapter_list.grid(row=2, column=0, sticky="nsew")

        # Bottom Actions
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.btn_bib = ctk.CTkButton(self.bottom_frame, text="Bibliografia", fg_color="gray", command=self.on_show_bib)
        self.btn_bib.pack(padx=10, pady=5)

        self.btn_settings = ctk.CTkButton(self.bottom_frame, text="Impostazioni", fg_color="gray", command=self.on_settings)
        self.btn_settings.pack(padx=10, pady=5)

        # Appearance Mode
        self.lbl_mode = ctk.CTkLabel(self.bottom_frame, text="Tema:", font=("Arial", 10))
        self.lbl_mode.pack(pady=(10,0))
        self.option_mode = ctk.CTkOptionMenu(self.bottom_frame, values=["System", "Dark", "Light"], 
                                             command=self.change_appearance_mode, width=100)
        self.option_mode.pack(padx=10, pady=5)

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

        for i, chapter in enumerate(chapters):
            btn = ctk.CTkButton(self.chapter_list, text=chapter.title, anchor="w",
                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                command=lambda c=chapter: self.on_chapter_select(c))
            btn.pack(fill="x", pady=2)
            
            # Context Menu Binding
            btn.bind("<Button-3>", lambda event, c=chapter: self.show_context_menu(event, c))
            
    def show_context_menu(self, event, chapter):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Rinomina", command=lambda: self.on_rename_chapter(chapter) if self.on_rename_chapter else None)
        menu.add_command(label="Elimina", command=lambda: self.on_delete_chapter(chapter) if self.on_delete_chapter else None)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
