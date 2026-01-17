
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
from src.ui.router import ViewRouter
from src.ui.components.breadcrumb import Breadcrumb

from src.engine.compiler import CompilationError
from src.controllers.project_controller import ProjectController
from src.controllers.session_manager import SessionManager
from src.utils.logger import setup_logger
from src.utils.icons import IconFactory

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

from src.engine.autosave import AutoSaveService

class ThesisFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ThesisFlow - Write Markdown, Publish Typst")
        self.geometry("1400x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.logger = setup_logger()
        
        # Initialize Controllers
        self.session = SessionManager()
        self.project_controller = ProjectController()
        
        # Keep pm for legacy/direct access if needed for now
        self.pm = self.project_controller.pm
        
        self.current_chapter = None
        self.current_file_path = None
        self.view_mode = "editor"
        self.is_dirty = False
        
        # State to restore after reload
        self._saved_project_path = None
        self._saved_chapter_id = None
        
        # Autosave Service
        self.autosave_service = AutoSaveService(self.autosave_callback, interval_seconds=60)
        self.autosave_service.start()

        self.check_dependencies()
        self.setup_ui()
        self.setup_router()

    def setup_router(self):
        self.router = ViewRouter(self)
        
        # Dashboard View
        self.router.register_view("dashboard", self.dashboard, 
                                  on_enter=lambda: self.dashboard.refresh_list())
        
        # Main Interface (Editor)
        self.router.register_view("editor", self.main_interface,
                                  on_exit=self._on_exit_editor)
                                  
        # Initial View
        self.router.navigate("dashboard")

    def _on_exit_editor(self):
        if self.is_dirty:
            self.save_current_file()
        self.current_chapter = None
        self.current_file_path = None

    def setup_ui(self):
        # Apply Theme BG
        self.configure(fg_color=Theme.COLOR_BG)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Views ---
        # 1. Dashboard
        self.dashboard = DashboardFrame(self, self.project_controller, on_project_selected=self.open_project)
        # Grid management moved to router

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
                                    on_back=lambda: self.router.navigate("dashboard")) # Using router
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content Area
        self.content_area = ctk.CTkFrame(self.main_interface, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(2, weight=1) # Editor expands
        self.content_area.grid_columnconfigure(0, weight=1) # Editor column
        self.content_area.grid_columnconfigure(1, weight=0) # Outline column

        self.header_frame = ctk.CTkFrame(self.content_area, height=60, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 0))
        
        self.breadcrumb = Breadcrumb(self.header_frame)
        self.breadcrumb.pack(side="left", pady=10)
        
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
        # Stop existing autosave before destroy
        if hasattr(self, 'autosave_service'):
            self.autosave_service.stop()

        # Destroy all children
        for widget in self.winfo_children():
            widget.destroy()
        
        # Re-build
        self.setup_ui()
        # Restart autosave
        self.autosave_service.start()

    def check_dependencies(self):
        missing = self.pm.check_system_health()
        
        if missing:
             self.logger.warning(f"Missing dependencies: {', '.join(missing)}")
             self.after(500, lambda: msg.showwarning("Dipendenze Mancanti", f"Attenzione, i seguenti eseguibili non sono stati trovati:\n{', '.join(missing)}\n\nLa compilazione potrebbe fallire."))

    def open_project(self, path: Path):
        try:
            self.project_controller.load_project(path)
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
        self.router.navigate("editor")
        self.title(f"ThesisFlow - {self.pm.manifest.title}")

    def show_dashboard(self):
        self.router.navigate("dashboard")
        self.title("ThesisFlow - Write Markdown, Publish Typst")

    def refresh_sidebar(self):
        if self.pm.manifest:
            self.sidebar.update_chapters(self.pm.manifest.chapters)
            self.sidebar.refresh_assets()

    def _ensure_editor_mode(self):
        """Helper to switch from bibliography back to editor mode."""
        if self.view_mode == "bibliography":
            if self.bib_editor:
                self.bib_editor.save()
                self.bib_editor.grid_forget()
            self.view_mode = "editor"
            self.editor.grid(row=2, column=0, sticky="nsew", padx=0, pady=10)

    def load_chapter(self, chapter):
        self._ensure_editor_mode()
        
        # Update Breadcrumb
        title = self.pm.manifest.title if self.pm.manifest else "Progetto"
        try:
            idx = self.pm.manifest.chapters.index(chapter) + 1
            display_title = f"{idx}. {chapter.title}"
        except (ValueError, AttributeError):
            display_title = chapter.title
            
        self.breadcrumb.update_path([title, display_title])
        
        if self.current_file_path:
             self.save_current_file()

        self.current_chapter = chapter
        if self.pm.current_project_path:
             self.current_file_path = self.pm.current_project_path / "chapters" / chapter.filename
             content = self.pm.read_file_content(self.current_file_path)
             self.editor.set_text(content)

    def load_paragraph(self, paragraph, parent_chapter):
        self._ensure_editor_mode()
        
        # Update Breadcrumb
        title = self.pm.manifest.title if self.pm.manifest else "Progetto"
        try:
            c_idx = self.pm.manifest.chapters.index(parent_chapter) + 1
            p_idx = parent_chapter.paragraphs.index(paragraph) + 1
            c_title = f"{c_idx}. {parent_chapter.title}"
            p_title = f"{c_idx}.{p_idx} {paragraph.title}"
            self.breadcrumb.update_path([title, c_title, p_title])
        except (ValueError, AttributeError):
            self.breadcrumb.update_path([title, parent_chapter.title, paragraph.title])
        
        if self.current_file_path:
             self.save_current_file()
             
        self.current_chapter = parent_chapter
        self.current_file_path = self.pm.current_project_path / "chapters" / parent_chapter.id / paragraph.filename
        
        if self.current_file_path.exists(): 
             content = self.pm.read_file_content(self.current_file_path)
             self.editor.set_text(content)
    
    def load_file(self, path: Path, parent_chapter):
        self._ensure_editor_mode()
        # Update Breadcrumb
        title = self.pm.manifest.title if self.pm.manifest else "Progetto"
        file_display = path.stem.replace('_', ' ')
        self.breadcrumb.update_path([title, parent_chapter.title, file_display])
        self.current_chapter = parent_chapter # Keep parent context
        self.current_file_path = path
        
        if path.exists(): 
             content = self.pm.read_file_content(path)
             self.editor.set_text(content)

    def open_bibliography(self):
        # Toggle back to editor if already in bibliography
        if self.view_mode == "bibliography":
            if self.current_chapter:
                self.load_chapter(self.current_chapter)
            return

        if self.view_mode == "editor" and self.current_chapter:
            self.save_current_chapter()
        
        self.view_mode = "bibliography"
        # We don't clear current_chapter anymore to allow toggling back
        self.editor.grid_forget()
        
        if not self.bib_editor:
            self.bib_editor = BibliographyFrame(self.content_area, project_root=self.pm.current_project_path)
        else:
            self.bib_editor.project_root = self.pm.current_project_path
            self.bib_editor.load()
        
        # Bibliography is currently a "sub-view" inside content_area
        # We might want to make it a primary view in the future, 
        # but for now we'll keep the current grid management for bibliography
        # since it's nested inside the main interface.
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
        
        if self.console_panel.is_collapsed:
            self.console_panel.toggle_collapse()
            
        def on_success(pdf_path):
            self.after(0, lambda: self._on_compile_success(pdf_path))
            self.after(0, lambda: self._on_compile_finished())

        def on_error(error):
            self.after(0, lambda: self._on_compile_error(error))
            self.after(0, lambda: self._on_compile_finished())
            
        def on_progress(status, fraction):
            # Update UI with progress? For now just log or toast updates
            # self.after(0, lambda: self.show_toast(status, 1000))
            pass

        self.pm.compile_project_async(on_success, on_error, on_progress)


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
        toast = ctk.CTkFrame(self, fg_color=Theme.COLOR_PANEL, border_width=1, border_color=Theme.COLOR_ACCENT, corner_radius=25)
        toast.place(relx=0.98, rely=0.95, anchor="se", x=-20, y=-20)
        ctk.CTkLabel(toast, text=message, font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(padx=25, pady=12)
        self.after(duration, toast.destroy)

    def mark_dirty(self):
        self.is_dirty = True
    
    def autosave_callback(self):
        # Safe to access UI variables? 
        # AutosaveService runs on thread, so NO!
        # We need to schedule this on main thread
        self.after(0, self._autosave_logic)
        
    def _autosave_logic(self):
        if self.is_dirty and self.view_mode == "editor" and self.current_file_path:
            self.save_current_file()

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
        if hasattr(self, 'autosave_service'):
            self.autosave_service.stop()
        if self.is_dirty: self.save_current_file()
        self.destroy()
