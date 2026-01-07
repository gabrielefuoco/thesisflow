
import customtkinter as ctk
from pathlib import Path
import threading
import tkinter.messagebox as msg

from src.ui.editor import EditorFrame
from src.ui.toolbar import ToolbarFrame
from src.ui.dashboard import DashboardFrame
from src.ui.sidebar import SidebarFrame
from src.ui.bibliography import BibliographyFrame
from src.ui.bibliography import BibliographyFrame
from src.engine.compiler import CompilerEngine, CompilationError
from src.engine.project_manager import ProjectManager
from src.utils.logger import setup_logger, get_logger
from src.utils.paths import get_pandoc_exe, get_typst_exe

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ThesisFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ThesisFlow - Write Markdown, Publish Typst")
        self.geometry("1100x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.logger = setup_logger()
        self.check_dependencies()

        self.pm = ProjectManager()
        self.current_chapter = None
        self.pm = ProjectManager()
        self.current_chapter = None
        self.view_mode = "editor" # or 'bibliography'
        self.is_dirty = False
        
        # Autosave Timer
        self.autosave_interval = 60000 # 60 seconds
        self.after(self.autosave_interval, self.autosave_loop)

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
                                    on_move_chapter=self.move_chapter,
                                    on_show_bib=self.open_bibliography,
                                    on_open_settings=self.open_settings_dialog,
                                    on_rename_chapter=self.rename_chapter_dialog,
                                    on_delete_chapter=self.delete_chapter_confirm)
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
        self.editor = EditorFrame(self.content_area, on_change=self.mark_dirty, get_citations_callback=self.get_citation_keys)
        self.editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.bib_editor = None # Lazy init
        
        # --- End Views ---
    
    def check_dependencies(self):
        missing = []
        if not get_pandoc_exe().exists(): missing.append("Pandoc")
        if not get_typst_exe().exists(): missing.append("Typst")
        
        if missing:
             self.logger.warning(f"Missing dependencies: {', '.join(missing)}")
             self.after(500, lambda: msg.showwarning("Dipendenze Mancanti", f"Attenzione, i seguenti eseguibili non sono stati trovati:\n{', '.join(missing)}\n\nLa compilazione potrebbe fallire."))

    def mark_dirty(self):
        self.is_dirty = True
    
    def autosave_loop(self):
        if self.is_dirty and self.view_mode == "editor" and self.current_chapter:
            print("Autosaving...") # Debug
            self.save_current_chapter()
        self.after(self.autosave_interval, self.autosave_loop)

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
            self.is_dirty = False

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

    def move_chapter(self, direction):
        if not self.current_chapter: return
        self.pm.move_chapter(self.current_chapter, direction)
        self.refresh_sidebar()
        # Keep selection?
        # self.sidebar.select... (logic is not implemented in sidebar fully, but UI rebuilds)
        # We should ensure the current chapter remains "active" visually. 
        # Since refresh_sidebar destroys widgets, we need to handle that, 
        # OR just refreshing is enough and user re-clicks. 
        # To be nice:
        # But for now basic functionality.
    
    def rename_chapter_dialog(self, chapter):
        dialog = ctk.CTkInputDialog(text="Nuovo Titolo:", title="Rinomina Capitolo")
        new_title = dialog.get_input()
        if new_title:
            self.pm.rename_chapter(chapter, new_title)
            self.refresh_sidebar()

    def delete_chapter_confirm(self, chapter):
        confirm = msg.askyesno("Elimina Capitolo", f"Sei sicuro di voler eliminare '{chapter.title}'?")
        if confirm:
            self.pm.delete_chapter(chapter)
            if self.current_chapter and self.current_chapter.id == chapter.id:
                self.current_chapter = None
                self.editor.set_text("")
            self.refresh_sidebar()


    def open_settings_dialog(self):
        from src.ui.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self, self.pm.manifest)
        self.wait_window(dialog)
        
        if dialog.result:
            # Update manifest
            self.pm.manifest.title = dialog.result["title"]
            self.pm.manifest.candidate = dialog.result["candidate"]
            self.pm.manifest.supervisor = dialog.result["supervisor"]
            self.pm.manifest.year = dialog.result["year"]
            self.pm.manifest.citation_style = dialog.result["citation_style"]
            
            # Save
            self.pm._save_manifest(self.pm.current_project_path, self.pm.manifest)
            
            # Refresh UI
            self.title(f"ThesisFlow - {self.pm.manifest.title}")
            msg.showinfo("Settings", "Impostazioni salvate.")

    def on_compile(self):
        # Save whichever view is active
        if self.view_mode == "editor":
            self.save_current_chapter()
        elif self.view_mode == "bibliography" and self.bib_editor:
            self.bib_editor.save()
        
        if not self.pm.current_project_path:
            return
        
        # Lock UI
        self.toolbar.btn_compile.configure(state="disabled", text="Compilazione...")

        self.logger.info(f"Compiling project: {self.pm.current_project_path}")
        
        def run_compile():
            engine = CompilerEngine(self.pm.current_project_path)
            try:
                engine.compile()
                pdf_path = engine.output_pdf
                self.after(0, lambda: self._on_compile_success(pdf_path))
            except CompilationError as e:
                self.after(0, lambda: self._on_compile_error(e))
            except Exception as e:
                self.after(0, lambda: msg.showerror("Errore Generico", str(e)))
            finally:
                 self.after(0, self._on_compile_finished)

        threading.Thread(target=run_compile, daemon=True).start()

    def _on_compile_finished(self):
        self.toolbar.btn_compile.configure(state="normal", text="COMPILA PDF") # Assuming original text

    def _on_compile_error(self, error: CompilationError):
        # Show custom dialog with details
        dialog = ctk.CTkToplevel(self)
        dialog.title("Errore di Compilazione")
        dialog.geometry("600x400")
        
        ctk.CTkLabel(dialog, text=str(error), text_color="red", font=("Arial", 14, "bold")).pack(pady=10)
        
        textbox = ctk.CTkTextbox(dialog, font=("Consolas", 12))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", error.details)

    def _on_compile_success(self, pdf_path):
        import os
        msg.showinfo("Compilazione", f"PDF generato con successo:\n{pdf_path}")
        try:
            os.startfile(pdf_path)
        except Exception:
            pass

    def get_citation_keys(self):
        if not self.pm.current_project_path: return []
        bib_path = self.pm.current_project_path / "references.bib"
        if not bib_path.exists(): return []
        
        # Simple parsing of @type{key, ...}
        import re
        content = bib_path.read_text(encoding="utf-8")
        keys = re.findall(r'@\w+\{([^,]+),', content)
        return keys

    def on_close(self):
        if self.is_dirty:
            self.save_current_chapter() # Force save
        self.destroy()
