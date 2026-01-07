
import customtkinter as ctk
import tkinter.messagebox as msg
from pathlib import Path
from typing import Callable
from src.engine.models import ProjectManifest
from src.utils.paths import get_templates_dir
from src.utils.i18n import I18N

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, project_manager, on_project_selected: Callable[[Path], None], **kwargs):
        super().__init__(master, **kwargs)
        self.pm = project_manager
        self.on_project_selected = on_project_selected

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # List area

        # Header
        self.lbl_title = ctk.CTkLabel(self, text="ThesisFlow Dashboard", font=("Arial", 24, "bold"))
        self.lbl_title.grid(row=0, column=0, pady=(40, 20))

        # Actions
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=1, column=0, pady=10)
        
        self.btn_new = ctk.CTkButton(self.actions_frame, text="Nuovo Progetto", command=self.create_new_project)
        self.btn_new.pack(side="left", padx=10)
        
        self.btn_import = ctk.CTkButton(self.actions_frame, text="Importa ZIP", command=self.import_project_dialog)
        self.btn_import.pack(side="left", padx=10)
        
        self.btn_refresh = ctk.CTkButton(self.actions_frame, text="Aggiorna Lista", command=self.refresh_list)
        self.btn_refresh.pack(side="left", padx=10)

        # Project List
        self.scrollable = ctk.CTkScrollableFrame(self, label_text="I tuoi Progetti")
        self.scrollable.grid(row=2, column=0, sticky="nsew", padx=50, pady=20)
        
        self.refresh_list()

    def refresh_list(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        projects = self.pm.list_projects()
        
        # Sort by modification time (newest first)
        projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        if not projects:
            ctk.CTkLabel(self.scrollable, text="Nessun progetto trovato.").pack(pady=20)
            return

        for p_path in projects:
            name = p_path.name
            # Row container
            row = ctk.CTkFrame(self.scrollable, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=5)
            
            # Open Button (Main)
            btn = ctk.CTkButton(row, text=name, 
                                command=lambda path=p_path: self.on_project_selected(path),
                                fg_color="transparent", border_width=1, border_color="gray", text_color=("black", "white"), anchor="w")
            btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            # Export Button (Small)
            btn_export = ctk.CTkButton(row, text="Export", width=60, fg_color="gray", 
                                       command=lambda path=p_path: self.export_project_dialog(path))
            btn_export.pack(side="right")

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
        # Improved Dialog with metadata
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                name = dialog.result["title"]
                author = dialog.result["author"]
                template_path = dialog.result.get("template_path")
                # Create project
                self.pm.create_project(name, author=author, template_path=template_path)
                
                # Update manifest with extra fields
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
        super().__init__(master)
        self.title("Nuovo Progetto")
        self.geometry("400x450")
        self.result = None

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Nome Progetto (Cartella)").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_title = ctk.CTkEntry(self)
        self.entry_title.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Candidato").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_candidate = ctk.CTkEntry(self)
        self.entry_candidate.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Relatore").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_supervisor = ctk.CTkEntry(self)
        self.entry_supervisor.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="Anno Accademico").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_year = ctk.CTkEntry(self)
        self.entry_year.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Template").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.combo_template = ctk.CTkOptionMenu(self, values=self.get_templates())
        self.combo_template.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        self.btn_ok = ctk.CTkButton(self, text="Crea", command=self.on_ok)
        self.btn_ok.grid(row=5, column=0, columnspan=2, pady=20)
    
    def get_templates(self):
        t_dir = get_templates_dir()
        if not t_dir.exists(): return ["Default"]
        return [f.name for f in t_dir.glob("*.typ")]

    def on_ok(self):
        t = self.entry_title.get()
        c = self.entry_candidate.get()
        if not t:
            return
        
        self.result = {
            "title": t,
            "author": c, # Author maps to candidate usually
            "candidate": c,
            "supervisor": self.entry_supervisor.get(),
            "year": self.entry_year.get()
        }
        
        # Resolve template path
        selected_tmpl = self.combo_template.get()
        if selected_tmpl:
             self.result["template_path"] = get_templates_dir() / selected_tmpl
             
        self.destroy()
