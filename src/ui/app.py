
import customtkinter as ctk
import threading
import tkinter.messagebox as msg
from pathlib import Path

from src.ui.editor import EditorFrame
from src.ui.toolbar import ToolbarFrame
from src.ui.dashboard import DashboardFrame
from src.ui.sidebar import SidebarFrame
from src.ui.bibliography import BibliographyFrame
from src.ui.console import ConsolePanel
from src.ui.theme import Theme

from src.engine.compiler import CompilerEngine, CompilationError
from src.engine.project_manager import ProjectManager
from src.utils.logger import setup_logger
from src.utils.paths import get_pandoc_exe, get_typst_exe
from src.utils.icons import IconFactory

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ThesisFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Apply Theme BG
        self.configure(fg_color=Theme.COLOR_BG)

        self.title("ThesisFlow - Write Markdown, Publish Typst")
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.logger = setup_logger()
        self.check_dependencies()

        self.pm = ProjectManager()
        self.current_chapter = None
        self.current_file_path = None
        self.view_mode = "editor"
        self.is_dirty = False
        
        # Autosave Timer
        self.autosave_interval = 60000 
        self.after(self.autosave_interval, self.autosave_loop)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Views ---
        # 1. Dashboard
        self.dashboard = DashboardFrame(self, self.pm, on_project_selected=self.open_project)
        self.dashboard.grid(row=0, column=0, sticky="nsew")

        # 2. Main Interface
        self.main_interface = ctk.CTkFrame(self, fg_color="transparent")
        self.main_interface.grid_columnconfigure(1, weight=1)
        self.main_interface.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = SidebarFrame(self.main_interface, 
                                    on_chapter_select=self.load_chapter,
                                    on_add_chapter=self.add_chapter_dialog,
                                    on_move_chapter=self.move_chapter,
                                    on_show_bib=self.open_bibliography,
                                    on_open_settings=self.open_settings_dialog,
                                    on_rename_chapter=self.rename_chapter_dialog,
                                    on_delete_chapter=self.delete_chapter_confirm)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content Area
        self.content_area = ctk.CTkFrame(self.main_interface, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(2, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.content_area, height=60, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 0))
        
        self.lbl_chapter_title = ctk.CTkLabel(self.header_frame, text="", font=("Segoe UI", 24, "bold"), text_color=Theme.TEXT_MAIN)
        self.lbl_chapter_title.pack(side="left")
        
        self.btn_compile = ctk.CTkButton(self.header_frame, text="PUBBLICA PDF", 
                                         font=("Segoe UI", 12, "bold"),
                                         fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                                         image=IconFactory.get_icon("play", size=(16,16)),
                                         compound="right",
                                         command=self.on_compile)
        self.btn_compile.pack(side="right")
        
        self.btn_preview_toggle = ctk.CTkButton(self.header_frame, text="Anteprima", width=80, 
                                                fg_color="transparent", border_width=1, border_color=Theme.COLOR_BORDER,
                                                command=lambda: self.editor.toggle_preview())
        self.btn_preview_toggle.pack(side="right", padx=10)

        # Toolbar
        self.toolbar = ToolbarFrame(self.content_area, command_compile=self.on_compile)
        self.toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 0))

        # Editor
        self.editor = EditorFrame(self.content_area, on_change=self.mark_dirty, get_citations_callback=self.get_citation_keys)
        self.editor.grid(row=2, column=0, sticky="nsew", padx=0, pady=10)

        self.bib_editor = None
        
        # Console (Hidden)
        self.console_panel = ConsolePanel(self.content_area)

    def check_dependencies(self):
        missing = []
        if not get_pandoc_exe().exists(): missing.append("Pandoc")
        if not get_typst_exe().exists(): missing.append("Typst")
        
        if missing:
             self.logger.warning(f"Missing dependencies: {', '.join(missing)}")
             self.after(500, lambda: msg.showwarning("Dipendenze Mancanti", f"Attenzione, i seguenti eseguibili non sono stati trovati:\n{', '.join(missing)}\n\nLa compilazione potrebbe fallire."))

    def open_project(self, path: Path):
        try:
            self.pm.load_project(path)
            self.show_editor_interface()
            self.refresh_sidebar()
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
        self.lbl_chapter_title.configure(text=chapter.title)
        
        if self.view_mode == "editor" and self.current_chapter:
             self.save_current_chapter()
        elif self.view_mode == "bibliography" and self.bib_editor:
             self.bib_editor.save()

        self.view_mode = "editor"
        if self.bib_editor: self.bib_editor.grid_forget()
        self.editor.grid(row=2, column=0, sticky="nsew", padx=0, pady=10)

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
        self.bib_editor.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def on_compile(self, fmt="pdf"):
        if self.view_mode == "editor":
            self.save_current_chapter()
        elif self.view_mode == "bibliography" and self.bib_editor:
            self.bib_editor.save()
        
        if not self.pm.current_project_path: return
        
        self.btn_compile.configure(state="disabled", text="Compilazione...")
        self.show_toast("Compilazione avviata...")
        self.logger.info(f"Compiling project: {self.pm.current_project_path}")
        
        def run_compile():
            engine = CompilerEngine(self.pm.current_project_path, self.pm.manifest)
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

    def _on_compile_success(self, pdf_path):
        import os
        msg.showinfo("Compilazione", f"PDF generato con successo:\n{pdf_path}")
        try:
            os.startfile(pdf_path)
        except Exception:
            pass

    def _on_compile_error(self, error):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Errore di Compilazione")
        dialog.geometry("600x400")
        ctk.CTkLabel(dialog, text=str(error), text_color="red").pack(pady=10)
        textbox = ctk.CTkTextbox(dialog)
        textbox.pack(fill="both", expand=True)
        textbox.insert("1.0", error.details)

    def _on_compile_finished(self):
        self.btn_compile.configure(state="normal", text="PUBBLICA PDF")

    def show_toast(self, message, duration=3000):
        toast = ctk.CTkFrame(self, fg_color=Theme.COLOR_PANEL, border_width=1, border_color=Theme.COLOR_ACCENT, corner_radius=20)
        toast.place(relx=0.98, rely=0.95, anchor="se")
        ctk.CTkLabel(toast, text=message, font=("Segoe UI", 12), text_color=Theme.TEXT_MAIN).pack(padx=20, pady=10)
        self.after(duration, toast.destroy)

    def mark_dirty(self):
        self.is_dirty = True
    
    def autosave_loop(self):
        if self.is_dirty and self.view_mode == "editor" and self.current_file_path:
            self.save_current_file()
        self.after(self.autosave_interval, self.autosave_loop)

    def save_current_file(self):
        if self.current_file_path:
            text = self.editor.get_text()
            self.current_file_path.write_text(text, encoding="utf-8")
            self.is_dirty = False
    
    def save_current_chapter(self):
        self.save_current_file()

    def add_chapter_dialog(self):
        dialog = ctk.CTkInputDialog(text="Titolo del Capitolo:", title="Nuovo Capitolo")
        title = dialog.get_input()
        if title:
            if self.view_mode == "editor": self.save_current_chapter()
            self.pm.create_chapter(title)
            self.refresh_sidebar()
            self.load_chapter(self.pm.manifest.chapters[-1])

    def move_chapter(self, direction):
        if not self.current_chapter: return
        self.pm.move_chapter(self.current_chapter, direction)
        self.refresh_sidebar()
    
    def rename_chapter_dialog(self, chapter):
        dialog = ctk.CTkInputDialog(text="Nuovo Titolo:", title="Rinomina Capitolo")
        new_title = dialog.get_input()
        if new_title:
            self.pm.rename_chapter(chapter, new_title)
            self.refresh_sidebar()

    def delete_chapter_confirm(self, chapter):
        if msg.askyesno("Elimina", f"Eliminare '{chapter.title}'?"):
            self.pm.delete_chapter(chapter)
            if self.current_chapter == chapter:
                self.current_chapter = None
                self.editor.set_text("")
            self.refresh_sidebar()

    def open_settings_dialog(self):
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self, self.pm.manifest)
        self.wait_window(dialog)
        if dialog.result:
            self.pm.manifest.title = dialog.result["title"]
            self.pm.manifest.candidate = dialog.result["candidate"]
            self.pm.manifest.supervisor = dialog.result["supervisor"]
            self.pm.manifest.year = dialog.result["year"]
            self.pm.manifest.citation_style = dialog.result["citation_style"]
            self.pm._save_manifest(self.pm.current_project_path, self.pm.manifest)
            self.title(f"ThesisFlow - {self.pm.manifest.title}")
            msg.showinfo("Settings", "Impostazioni salvate.")

    def get_citation_keys(self):
        if not self.pm.current_project_path: return []
        bib_path = self.pm.current_project_path / "references.bib"
        if not bib_path.exists(): return []
        import re
        content = bib_path.read_text(encoding="utf-8")
        return re.findall(r'@\w+\{([^,]+),', content)

    def on_close(self):
        if self.is_dirty: self.save_current_file()
        self.destroy()
