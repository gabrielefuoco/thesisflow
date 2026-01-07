
import customtkinter as ctk
from src.engine.models import Chapter
from typing import Callable

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, on_chapter_select: Callable[[Chapter], None], on_add_chapter: Callable[[], None], on_show_bib: Callable[[], None], **kwargs):
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        self.on_chapter_select = on_chapter_select
        self.on_add_chapter = on_add_chapter
        self.on_show_bib = on_show_bib

        self.grid_rowconfigure(2, weight=1) # List expands
        self.grid_columnconfigure(0, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self, text="ThesisFlow", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Add Chapter Button
        self.btn_add = ctk.CTkButton(self, text="+ Nuovo Capitolo", command=self.on_add_chapter)
        self.btn_add.grid(row=1, column=0, padx=10, pady=10)
        
        # Chapter List Container
        self.chapter_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chapter_list.grid(row=2, column=0, sticky="nsew")

        # Bottom Actions
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.btn_bib = ctk.CTkButton(self.bottom_frame, text="Bibliografia", fg_color="gray", command=self.on_show_bib)
        self.btn_bib.pack(padx=10, pady=5)

    def update_chapters(self, chapters: list[Chapter]):
        for widget in self.chapter_list.winfo_children():
            widget.destroy()

        for i, chapter in enumerate(chapters):
            btn = ctk.CTkButton(self.chapter_list, text=chapter.title, anchor="w",
                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                command=lambda c=chapter: self.on_chapter_select(c))
            btn.pack(fill="x", pady=2)
