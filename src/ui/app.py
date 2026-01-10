
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
from src.ui.outline import OutlinePanel
from src.ui.theme import Theme

from src.engine.compiler import CompilationError
from src.engine.project_manager import ProjectManager
from src.utils.logger import setup_logger
from src.utils.icons import IconFactory

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ThesisFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ThesisFlow - Write Markdown, Publish Typst")
        self.geometry("1400x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.logger = setup_logger()
        
        self.pm = ProjectManager()
        self.current_chapter = None
        self.current_file_path = None
        self.view_mode = "editor"
        self.is_dirty = False
        
        # State to restore after reload
        self._saved_project_path = None
        self._saved_chapter_id = None
        
        # Autosave Timer
        self.autosave_interval = 60000 
        self.after(self.autosave_interval, self.autosave_loop)

        self.check_dependencies()
        self.setup_ui()

    def setup_ui(self):
        # Apply Theme BG
        self.configure(fg_color=Theme.COLOR_BG)
        
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
                                    on_delete_chapter=self.delete_chapter_confirm,
                                    on_theme_toggle=self.toggle_theme,
                                    on_back=self.show_dashboard) # Passed callback
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content Area
        self.content_area = ctk.CTkFrame(self.main_interface, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(2, weight=1) # Editor expands
        self.content_area.grid_columnconfigure(0, weight=1) # Editor column
        self.content_area.grid_columnconfigure(1, weight=0) # Outline column

        # Header
        self.header_frame = ctk.CTkFrame(self.content_area, height=60, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 0))
        
        self.lbl_chapter_title = ctk.CTkLabel(self.header_frame, text="", font=("Segoe UI", 24, "bold"), text_color=Theme.TEXT_MAIN)
        self.lbl_chapter_title.pack(side="left")
        
        self.btn_compile = ctk.CTkButton(self.header_frame, text="PUBBLICA PDF", 
                                         font=("Segoe UI", 12, "bold"),
                                         fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                                         image=IconFactory.get_icon("play", size=(16,16)),
                                         compound="right",
                                         command=self.on_compile)
        self.btn_compile.pack(side="right")

        # Toolbar
        self.toolbar = ToolbarFrame(self.content_area, command_compile=self.on_compile, command_focus=self.toggle_focus_mode)
        self.toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 0))

        # Editor
        self.editor = EditorFrame(self.content_area, on_change=self.mark_dirty, get_citations_callback=self.get_citation_keys)
        self.editor.grid(row=2, column=0, sticky="nsew", padx=0, pady=10)
        
        # Link Editor to Toolbar
        self.toolbar.editor = self.editor

        # Outline (Right)
        self.outline = OutlinePanel(self.content_area, on_navigate=self.editor.scroll_to, height=500)
        self.outline.grid(row=2, column=1, sticky="nsew", padx=(0, 10), pady=10)

        self.bib_editor = None
        
        # Console (Bottom)
        self.console_panel = ConsolePanel(self.content_area)
        self.console_panel.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.console_panel.expand() 
        self.console_panel.toggle_collapse()
        
        self.focus_mode = False

        # Restore state if needed
        if self._saved_project_path:
             self.open_project(self._saved_project_path)


    def toggle_focus_mode(self):
        self.focus_mode = not self.focus_mode
        
        if self.focus_mode:
            self.sidebar.grid_remove() # Hide Sidebar
            self.header_frame.grid_remove() # Hide Header
            self.console_panel.grid_remove() # Hide Console
            self.outline.grid_remove() # Hide Outline
            
            # Maximize content area
            self.content_area.grid_configure(padx=0, pady=0)
            
            # Editor expands
            self.editor.grid_configure(padx=40) # More centering
        else:
            self.sidebar.grid()
            self.header_frame.grid()
            self.console_panel.grid()
            self.outline.grid()
            
            # Restore margins
            self.content_area.grid_configure(padx=0)
            self.editor.grid_configure(padx=0)

    def toggle_theme(self):
        new_mode = Theme.toggle_mode()
        self.logger.info(f"Switched theme to {new_mode}")
        
        # Save state
        if self.pm.current_project_path:
            self._saved_project_path = self.pm.current_project_path
            # Could save scroll position, current chapter etc.
            if self.current_chapter:
                self._saved_chapter_id = self.current_chapter.id
        
        self.reload_ui()

    def reload_ui(self):
        # Destroy all children
        for widget in self.winfo_children():
            widget.destroy()
        
        # Re-build
        self.setup_ui()

    def check_dependencies(self):
        missing = self.pm.check_system_health()
        
        if missing:
             self.logger.warning(f"Missing dependencies: {', '.join(missing)}")
             self.after(500, lambda: msg.showwarning("Dipendenze Mancanti", f"Attenzione, i seguenti eseguibili non sono stati trovati:\n{', '.join(missing)}\n\nLa compilazione potrebbe fallire."))

    def open_project(self, path: Path):
        try:
            self.pm.load_project(path)
            self.show_editor_interface()
            self.refresh_sidebar()
            if self.pm.manifest.chapters:
                # If we have a saved chapter to restore
                target_chapter = self.pm.manifest.chapters[0]
                if self._saved_chapter_id:
                     found = next((c for c in self.pm.manifest.chapters if c.id == self._saved_chapter_id), None)
                     if found: target_chapter = found
                     self._saved_chapter_id = None
                
                self.load_chapter(target_chapter)
            else:
                self.editor.set_text("")
                self.current_chapter = None
        except Exception as e:
            msg.showerror("Errore Caricamento", str(e))

    def show_editor_interface(self):
        self.dashboard.grid_forget()
        self.main_interface.grid(row=0, column=0, sticky="nsew")
        self.title(f"ThesisFlow - {self.pm.manifest.title}")

    def show_dashboard(self):
        if self.is_dirty: self.save_current_file()
        
        self.current_chapter = None
        self.current_file_path = None
        self.pm.current_project_path = None
        self.pm.manifest = None
        self._saved_project_path = None # Clear "last open" state
        
        self.title("ThesisFlow - Write Markdown, Publish Typst")
        self.main_interface.grid_forget()
        self.dashboard.refresh_list()
        self.dashboard.grid(row=0, column=0, sticky="nsew")

    def refresh_sidebar(self):
        if self.pm.manifest:
            self.sidebar.update_chapters(self.pm.manifest.chapters)
            self.sidebar.refresh_assets()

    def load_chapter(self, chapter):
        self.lbl_chapter_title.configure(text=chapter.title)
        
        if self.view_mode == "editor" and self.current_file_path:
             self.save_current_file()
        elif self.view_mode == "bibliography" and self.bib_editor:
             self.bib_editor.save()
             self.bib_editor.grid_forget()

        self.view_mode = "editor"
        if self.bib_editor: self.bib_editor.grid_forget() # Ensure hidden
        self.editor.grid(row=2, column=0, sticky="nsew", padx=0, pady=10)

        self.current_chapter = chapter
        if self.pm.current_project_path:
             self.current_file_path = self.pm.current_project_path / "chapters" / chapter.filename
             content = self.pm.read_file_content(self.current_file_path)
             self.editor.set_text(content)
    
    def load_file(self, path: Path, parent_chapter):
        if self.view_mode == "editor" and self.current_file_path:
             self.save_current_file()
             
        self.lbl_chapter_title.configure(text=f"{parent_chapter.title} > {path.stem.replace('_', ' ')}")
        self.current_chapter = parent_chapter # Keep parent context
        self.current_file_path = path
        
        if path.exists(): 
             content = self.pm.read_file_content(path)
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
        
        # Auto-expand console
        if self.console_panel.is_collapsed:
            self.console_panel.toggle_collapse()
        
        def run_compile():
            try:
                pdf_path = self.pm.compile_project()
                self.after(0, lambda p=pdf_path: self._on_compile_success(p))
            except CompilationError as e:
                err_copy = e 
                self.after(0, lambda err=err_copy: self._on_compile_error(err))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda m=err_msg: msg.showerror("Errore Generico", m))
            finally:
                 self.after(0, self._on_compile_finished)

        threading.Thread(target=run_compile, daemon=True).start()

    def _on_compile_success(self, pdf_path):
        msg.showinfo("Compilazione", f"PDF generato con successo:\n{pdf_path}")
        try:
            self.pm.open_generated_pdf(pdf_path)
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
            self.pm.save_file_content(self.current_file_path, text)
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
        styles = self.pm.list_citation_styles()
        dialog = SettingsDialog(self, self.pm.manifest, styles)
        self.wait_window(dialog)
        if dialog.result:
            self.pm.update_settings(dialog.result)
            self.title(f"ThesisFlow - {self.pm.manifest.title}")
            msg.showinfo("Settings", "Impostazioni salvate.")

    def get_citation_keys(self):
        return self.pm.get_citation_keys()

    def on_close(self):
        if self.is_dirty: self.save_current_file()
        self.destroy()
