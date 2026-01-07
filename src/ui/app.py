
import customtkinter as ctk
from pathlib import Path
import threading
import tkinter.messagebox as msg

from src.ui.editor import EditorFrame
from src.ui.toolbar import ToolbarFrame
from src.ui.dashboard import DashboardFrame
from src.ui.sidebar import SidebarFrame
from src.ui.bibliography import BibliographyFrame
from src.engine.compiler import CompilerEngine
from src.engine.project_manager import ProjectManager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ThesisFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ThesisFlow - Write Markdown, Publish Typst")
        self.geometry("1100x700")

        self.pm = ProjectManager()
        self.current_chapter = None
        self.view_mode = "editor" # or 'bibliography'

        # Container config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Views ---
        # 1. Dashboard
        self.dashboard = DashboardFrame(self, self.pm, on_project_selected=self.open_project)
        self.dashboard.grid(row=0, column=0, sticky="nsew")

        # 2. Main Editor Interface (Initially hidden)
        self.main_interface = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_interface.grid_columnconfigure(1, weight=1) # Editor area
        self.main_interface.grid_rowconfigure(0, weight=1)

        # Sidebar (Left)
        self.sidebar = SidebarFrame(self.main_interface, 
                                    on_chapter_select=self.load_chapter,
                                    on_add_chapter=self.add_chapter_dialog,
                                    on_show_bib=self.open_bibliography)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content Area (Right)
        self.content_area = ctk.CTkFrame(self.main_interface, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(1, weight=1) # Editor/Bib row
        self.content_area.grid_columnconfigure(0, weight=1)

        # Top Bar
        self.toolbar = ToolbarFrame(self.content_area, command_compile=self.on_compile)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Editors Stack
        self.editor = EditorFrame(self.content_area)
        self.editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.bib_editor = None # Lazy init
        
        # --- End Views ---

    def open_project(self, path: Path):
        try:
            self.pm.load_project(path)
            self.show_editor_interface()
            self.refresh_sidebar()
            
            # Load first chapter if exists
            if self.pm.manifest.chapters:
                self.load_chapter(self.pm.manifest.chapters[0])
            else:
                self.editor.set_text("")
                self.current_chapter = None
                
        except Exception as e:
            msg.showerror("Errore Caricamento", str(e))

    def show_editor_interface(self):
        self.dashboard.grid_forget()
        self.main_interface.grid(row=0, column=0, sticky="nsew")
        self.title(f"ThesisFlow - {self.pm.manifest.title}")

    def refresh_sidebar(self):
        if self.pm.manifest:
            self.sidebar.update_chapters(self.pm.manifest.chapters)

    def load_chapter(self, chapter):
        # Save previous if needed
        if self.view_mode == "editor" and self.current_chapter:
            self.save_current_chapter()
        elif self.view_mode == "bibliography" and self.bib_editor:
             self.bib_editor.save()

        # Switch view
        self.view_mode = "editor"
        if self.bib_editor: self.bib_editor.grid_forget()
        self.editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.current_chapter = chapter
        content = self.pm.get_chapter_content(chapter)
        self.editor.set_text(content)

    def open_bibliography(self):
        if self.view_mode == "editor" and self.current_chapter:
            self.save_current_chapter()
        
        self.view_mode = "bibliography"
        self.current_chapter = None
        
        self.editor.grid_forget()
        
        if not self.bib_editor:
            self.bib_editor = BibliographyFrame(self.content_area, project_root=self.pm.current_project_path)
        else:
            self.bib_editor.project_root = self.pm.current_project_path
            self.bib_editor.load()
            
        self.bib_editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))


    def save_current_chapter(self):
        if self.current_chapter:
            text = self.editor.get_text()
            self.pm.update_chapter_content(self.current_chapter, text)

    def add_chapter_dialog(self):
        dialog = ctk.CTkInputDialog(text="Titolo del Capitolo:", title="Nuovo Capitolo")
        title = dialog.get_input()
        if title:
            # Save current first
            if self.view_mode == "editor": self.save_current_chapter()

            self.pm.create_chapter(title)
            self.refresh_sidebar()
            # Select new chapter
            self.load_chapter(self.pm.manifest.chapters[-1])

    def on_compile(self):
        # Save whichever view is active
        if self.view_mode == "editor":
            self.save_current_chapter()
        elif self.view_mode == "bibliography" and self.bib_editor:
            self.bib_editor.save()
        
        if not self.pm.current_project_path:
            return

        print(f"Compiling project: {self.pm.current_project_path}")
        
        def run_compile():
            engine = CompilerEngine(self.pm.current_project_path)
            try:
                engine.compile()
                pdf_path = engine.output_pdf
                self.after(0, lambda: self._on_compile_success(pdf_path))
            except Exception as e:
                self.after(0, lambda: msg.showerror("Errore Compilazione", str(e)))

        threading.Thread(target=run_compile, daemon=True).start()

    def _on_compile_success(self, pdf_path):
        import os
        msg.showinfo("Compilazione", f"PDF generato con successo:\n{pdf_path}")
        try:
            os.startfile(pdf_path)
        except Exception:
            pass
