
import customtkinter as ctk
import tkinter.messagebox as msg
from pathlib import Path
from typing import Callable
from datetime import datetime
from src.engine.models import ProjectManifest
from src.utils.paths import get_templates_dir
from src.utils.i18n import I18N
from src.ui.theme import Theme
from src.utils.icons import IconFactory

class ProjectCard(ctk.CTkFrame):
    def __init__(self, master, project_path: Path, on_click: Callable, on_export: Callable, **kwargs):
        super().__init__(master, fg_color=Theme.COLOR_PANEL, corner_radius=10, border_width=1, border_color=Theme.COLOR_BORDER, **kwargs)
        self.project_path = project_path
        self.on_click = on_click
        
        # Hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # Grid layout inside card
        self.grid_columnconfigure(0, weight=1)
        
        # Icon
        self.icon = ctk.CTkButton(self, text="", image=IconFactory.get_icon("folder", size=(40,40)), 
                                  fg_color="transparent", hover=False, 
                                  command=lambda: on_click(project_path))
        self.icon.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text=project_path.name, font=("Segoe UI", 16, "bold"), text_color=Theme.TEXT_MAIN)
        self.lbl_title.grid(row=1, column=0, padx=10, sticky="ew")
        
        # Date
        mtime = datetime.fromtimestamp(project_path.stat().st_mtime)
        self.lbl_date = ctk.CTkLabel(self, text=mtime.strftime("%d/%m/%Y"), font=("Segoe UI", 12), text_color=Theme.TEXT_DIM)
        self.lbl_date.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Fake Progress Bar (Visual candy)
        self.progress = ctk.CTkProgressBar(self, height=4, progress_color=Theme.COLOR_ACCENT)
        self.progress.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress.set(0.3) # Dummy value, logic could be added

        # Make all children clickable
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda e: on_click(project_path))
            child.bind("<Enter>", self.on_enter)
            child.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(fg_color=Theme.COLOR_PANEL_HOVER, border_color=Theme.COLOR_ACCENT)
    
    def on_leave(self, event):
        self.configure(fg_color=Theme.COLOR_PANEL, border_color=Theme.COLOR_BORDER)

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, project_manager, on_project_selected: Callable[[Path], None], **kwargs):
        super().__init__(master, fg_color=Theme.COLOR_BG, **kwargs)
        self.pm = project_manager
        self.on_project_selected = on_project_selected

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        self.header.grid(row=0, column=0, sticky="ew", padx=40, pady=40)
        
        ctk.CTkLabel(self.header, text="Dashboard", font=("Segoe UI", 32, "bold"), text_color=Theme.TEXT_MAIN).pack(side="left")
        
        # New Project Button (Accent)
        self.btn_new = ctk.CTkButton(self.header, text="+ Nuovo Progetto", 
                                     font=("Segoe UI", 14, "bold"),
                                     fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                                     height=40,
                                     command=self.create_new_project)
        self.btn_new.pack(side="right")
        
        self.btn_import = ctk.CTkButton(self.header, text="Importa", 
                                        fg_color="transparent", border_width=1, border_color=Theme.COLOR_BORDER,
                                        width=80,
                                        command=self.import_project_dialog)
        self.btn_import.pack(side="right", padx=10)

        # --- Content Area ---
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.scrollable.grid_columnconfigure((0,1,2,3), weight=1) # 4 Columns
        
        self.refresh_list()

    def refresh_list(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        projects = self.pm.list_projects()
        projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        if not projects:
            self._show_empty_state()
            return

        # Grid Layout
        cols = 4
        for i, p_path in enumerate(projects):
            card = ProjectCard(self.scrollable, p_path, 
                               on_click=self.on_project_selected,
                               on_export=self.export_project_dialog)
            card.grid(row=i//cols, column=i%cols, padx=10, pady=10, sticky="nsew")

    def _show_empty_state(self):
        container = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        container.pack(expand=True, pady=100)
        
        # Big Icon
        ctk.CTkButton(container, text="", image=IconFactory.get_icon("project", size=(64,64)), 
                     fg_color="transparent", hover=False).pack(pady=20)
        
        ctk.CTkLabel(container, text="Nessun progetto trovato", font=("Segoe UI", 20, "bold"), text_color=Theme.TEXT_MAIN).pack()
        ctk.CTkLabel(container, text="Crea il tuo primo progetto per iniziare a scrivere.", font=("Segoe UI", 14), text_color=Theme.TEXT_DIM).pack(pady=(5, 30))
        
        ctk.CTkButton(container, text="Crea Progetto", 
                      fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                      width=200, height=50, font=("Segoe UI", 16, "bold"),
                      command=self.create_new_project).pack()

    def import_project_dialog(self):
        from customtkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Zip Files", "*.zip")])
        if path:
            try:
                new_path = self.pm.import_project(Path(path))
                self.refresh_list()
                msg.showinfo("Successo", f"Progetto importato: {new_path.name}")
            except Exception as e:
                msg.showerror("Errore Import", str(e))

    def export_project_dialog(self, project_path):
        from customtkinter import filedialog
        import datetime
        default_name = f"{project_path.name}_{datetime.datetime.now().strftime('%Y%m%d')}.zip"
        path = filedialog.asksaveasfilename(initialfile=default_name, filetypes=[("Zip Files", "*.zip")])
        if path:
            try:
                self.pm.export_project(project_path, Path(path))
                msg.showinfo("Successo", "Esportazione completata.")
            except Exception as e:
                msg.showerror("Errore Export", str(e))

    def create_new_project(self):
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                name = dialog.result["title"]
                author = dialog.result["author"]
                template_path = dialog.result.get("template_path")
                self.pm.create_project(name, author=author, template_path=template_path)
                
                if self.pm.manifest:
                    self.pm.manifest.candidate = dialog.result["candidate"]
                    self.pm.manifest.supervisor = dialog.result["supervisor"]
                    self.pm.manifest.year = dialog.result["year"]
                    self.pm._save_manifest(self.pm.current_project_path, self.pm.manifest)
                
                self.refresh_list()
                msg.showinfo("Successo", f"Progetto creato: {name}")
            except Exception as e:
                msg.showerror("Errore", str(e))

class NewProjectDialog(ctk.CTkToplevel):
    def __init__(self, master):
        self.bg_color = Theme.COLOR_PANEL
        super().__init__(master, fg_color=Theme.COLOR_PANEL)
        self.title("Nuovo Progetto")
        self.geometry("450x550")
        self.result = None
        
        # Center content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(content, text="Nuovo Progetto", font=("Segoe UI", 24, "bold"), text_color=Theme.TEXT_MAIN).pack(pady=(0, 20), anchor="w")

        self.grid_columnconfigure(1, weight=1)

        def make_entry(parent, label):
            ctk.CTkLabel(parent, text=label, text_color=Theme.TEXT_DIM).pack(anchor="w", pady=(10, 5))
            e = ctk.CTkEntry(parent, fg_color=Theme.COLOR_BG, border_color=Theme.COLOR_BORDER, text_color=Theme.TEXT_MAIN)
            e.pack(fill="x")
            return e

        self.entry_title = make_entry(content, "Nome Progetto (Cartella)")
        self.entry_candidate = make_entry(content, "Candidato")
        self.entry_supervisor = make_entry(content, "Relatore")
        self.entry_year = make_entry(content, "Anno Accademico")

        ctk.CTkLabel(content, text="Template", text_color=Theme.TEXT_DIM).pack(anchor="w", pady=(10, 5))
        self.combo_template = ctk.CTkOptionMenu(content, values=self.get_templates(), fg_color=Theme.COLOR_BG, button_color=Theme.COLOR_ACCENT)
        self.combo_template.pack(fill="x")

        self.btn_ok = ctk.CTkButton(content, text="Crea Progetto", 
                                    fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                                    height=40, font=("Segoe UI", 14, "bold"),
                                    command=self.on_ok)
        self.btn_ok.pack(pady=30, fill="x")
    
    def get_templates(self):
        t_dir = get_templates_dir()
        if not t_dir.exists(): return ["Default"]
        return [f.name for f in t_dir.glob("*.typ")]

    def on_ok(self):
        t = self.entry_title.get()
        c = self.entry_candidate.get()
        if not t: return
        
        self.result = {
            "title": t,
            "author": c,
            "candidate": c,
            "supervisor": self.entry_supervisor.get(),
            "year": self.entry_year.get()
        }
        selected_tmpl = self.combo_template.get()
        if selected_tmpl:
             self.result["template_path"] = get_templates_dir() / selected_tmpl
        self.destroy()
