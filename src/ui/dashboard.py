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
    def __init__(self, master, project_path: Path, on_click: Callable, on_export: Callable, on_delete: Callable, is_compact=False, **kwargs):
        super().__init__(master, fg_color=Theme.COLOR_PANEL, corner_radius=16, border_width=1, border_color=Theme.COLOR_BORDER, **kwargs)
        self.project_path = project_path
        self.on_click = on_click
        self.on_delete = on_delete
        
        # Hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        mtime = datetime.fromtimestamp(project_path.stat().st_mtime)
        
        if is_compact:
            # Compact Row for "All Projects"
            self.grid_columnconfigure(1, weight=1)
            
            # Icon as a small badge
            self.icon_frame = ctk.CTkFrame(self, fg_color=Theme.COLOR_BG, width=40, height=40, corner_radius=10)
            self.icon_frame.grid(row=0, column=0, padx=15, pady=12)
            self.icon_frame.grid_propagate(False)
            
            self.icon_lbl = ctk.CTkLabel(self.icon_frame, text="", image=IconFactory.get_icon("folder", size=(20,20)))
            self.icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            self.lbl_title = ctk.CTkLabel(self, text=project_path.name, font=(Theme.FONT_FAMILY, 14, "bold"), text_color=Theme.TEXT_MAIN, anchor="w")
            self.lbl_title.grid(row=0, column=1, padx=(0,10), sticky="ew")
            
            self.lbl_date = ctk.CTkLabel(self, text=mtime.strftime("%d %b %Y"), font=(Theme.FONT_FAMILY, 12), text_color=Theme.TEXT_DIM)
            self.lbl_date.grid(row=0, column=2, padx=15, sticky="e")
            
            # Action buttons
            self.btn_del = ctk.CTkButton(self, text="", image=IconFactory.get_icon("trash", size=(14,14)),
                                        fg_color="transparent", hover_color="#ef4444", width=32, height=32, corner_radius=8,
                                        command=lambda: on_delete(project_path))
            self.btn_del.grid(row=0, column=3, padx=(0, 15), sticky="e")
            
        else:
            # Full Project Card for "Recent"
            self.grid_columnconfigure(0, weight=1)
            
            # Large Folder Icon Badge
            self.icon_frame = ctk.CTkFrame(self, fg_color=Theme.COLOR_BG, width=80, height=80, corner_radius=20)
            self.icon_frame.grid(row=0, column=0, pady=(30, 20))
            self.icon_frame.grid_propagate(False)
            
            self.icon_lbl = ctk.CTkLabel(self.icon_frame, text="", image=IconFactory.get_icon("folder", size=(40,40)))
            self.icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            self.lbl_title = ctk.CTkLabel(self, text=project_path.name, font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.TEXT_MAIN)
            self.lbl_title.grid(row=1, column=0, padx=20, sticky="ew")
            
            self.lbl_date = ctk.CTkLabel(self, text=f"Ultima modifica: {mtime.strftime('%d %B %Y')}", font=(Theme.FONT_FAMILY, 13), text_color=Theme.TEXT_DIM)
            self.lbl_date.grid(row=2, column=0, padx=20, pady=(8, 30), sticky="ew")
            
            # Hidden Delete (Only visible on hover would be cool, but CTK limitation on children visibility triggers)
            self.btn_del = ctk.CTkButton(self, text="", image=IconFactory.get_icon("trash", size=(16,16)),
                                        fg_color="transparent", hover_color="#ef4444", width=36, height=36, corner_radius=10,
                                        command=lambda: on_delete(project_path))
            self.btn_del.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)

        # Make card clickable (excluding specific buttons)
        self.bind("<Button-1>", lambda e: on_click(project_path))
        for child in [self.icon_frame, self.icon_lbl, self.lbl_title, self.lbl_date]:
            child.bind("<Button-1>", lambda e: on_click(project_path))
            child.bind("<Enter>", self.on_enter)
            child.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(fg_color=Theme.COLOR_PANEL_HOVER, border_color=Theme.COLOR_ACCENT)
    
    def on_leave(self, event):
        self.configure(fg_color=Theme.COLOR_PANEL, border_color=Theme.COLOR_BORDER)

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, project_controller, on_project_selected: Callable[[Path], None], **kwargs):
        super().__init__(master, fg_color=Theme.COLOR_BG, **kwargs)
        self.controller = project_controller
        self.on_project_selected = on_project_selected

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=50, pady=(60, 40))
        
        ctk.CTkLabel(self.header, text="Dashboard", font=(Theme.FONT_FAMILY, 42, "bold"), text_color=Theme.TEXT_MAIN).pack(side="left")
        
        # New Project Button (Accent)
        self.btn_new = ctk.CTkButton(self.header, text="+ Nuovo Progetto", 
                                     font=(Theme.FONT_FAMILY, 14, "bold"),
                                     fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                                     height=46, corner_radius=23,
                                     command=self.create_new_project)
        self.btn_new.pack(side="right")
        
        self.btn_import = ctk.CTkButton(self.header, text="Importa", 
                                        font=(Theme.FONT_FAMILY, 14),
                                        fg_color="transparent", border_width=1, border_color=Theme.COLOR_BORDER,
                                        text_color=Theme.TEXT_MAIN, hover_color=Theme.COLOR_PANEL_HOVER,
                                        width=110, height=46, corner_radius=23,
                                        command=self.import_project_dialog)
        self.btn_import.pack(side="right", padx=15)

        # --- Content Area ---
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.scrollable.grid_columnconfigure(0, weight=1) # 1 Column layout for sections
        
        self.refresh_list()

    def refresh_list(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        projects = self.controller.list_projects()
        projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        if not projects:
            self._show_empty_state()
            return

        # Split Recent vs All
        recent = projects[:3]
        others = projects[3:] if len(projects) > 3 else []
        
        # SECTION: Recent
        lbl_recent = ctk.CTkLabel(self.scrollable, text="Progetti Recenti", font=(Theme.FONT_FAMILY, 22, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_recent.pack(anchor="w", pady=(10, 20), padx=10)
        
        recent_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        recent_frame.pack(fill="x", pady=(0, 40))
        recent_frame.grid_columnconfigure((0,1,2), weight=1)
        
        for i, p_path in enumerate(recent):
            card = ProjectCard(recent_frame, p_path, on_click=self.on_project_selected, on_export=self.export_project_dialog, on_delete=self.delete_project_confirm, is_compact=False)
            card.grid(row=0, column=i, padx=10, sticky="ew")
 
        # SECTION: All Projects
        if others:
            lbl_all = ctk.CTkLabel(self.scrollable, text="Altri Progetti", font=(Theme.FONT_FAMILY, 22, "bold"), text_color=Theme.TEXT_MAIN)
            lbl_all.pack(anchor="w", pady=(10, 20), padx=10)
             
            all_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
            all_frame.pack(fill="x")
            all_frame.grid_columnconfigure((0,1), weight=1) # 2 columns
            
            for i, p_path in enumerate(others):
                card = ProjectCard(all_frame, p_path, on_click=self.on_project_selected, on_export=self.export_project_dialog, on_delete=self.delete_project_confirm, is_compact=True)
                card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")

    def _show_empty_state(self):
        container = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        container.pack(expand=True, pady=100)
        
        # Big Icon
        ctk.CTkButton(container, text="", image=IconFactory.get_icon("project", size=(80,80)), 
                     fg_color="transparent", hover=False).pack(pady=20)
        
        ctk.CTkLabel(container, text="Nessun progetto trovato", font=("Segoe UI", 24, "bold"), text_color=Theme.TEXT_MAIN).pack()
        ctk.CTkLabel(container, text="Crea il tuo primo progetto per iniziare a scrivere.", font=("Segoe UI", 16), text_color=Theme.TEXT_DIM).pack(pady=(10, 40))
        
        ctk.CTkButton(container, text="Crea Progetto", 
                      fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                      width=220, height=54, font=("Segoe UI", 18, "bold"),
                      corner_radius=27,
                      command=self.create_new_project).pack()

    def import_project_dialog(self):
        from customtkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Zip Files", "*.zip")])
        if path:
            try:
                new_path = self.controller.import_project(Path(path))
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
                self.controller.export_project(project_path, Path(path))
                msg.showinfo("Successo", "Esportazione completata.")
            except Exception as e:
                msg.showerror("Errore Export", str(e))

    def delete_project_confirm(self, project_path):
        if msg.askyesno("Elimina Progetto", f"Sei sicuro di voler eliminare definitivamente il progetto:\n'{project_path.name}'?\n\nQuesta azione non è reversibile."):
            try:
                self.controller.delete_project(project_path)
                self.refresh_list()
            except Exception as e:
                msg.showerror("Errore Eliminazione", str(e))

    def create_new_project(self):
        templates = self.controller.get_templates()
        dialog = NewProjectDialog(self, templates)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                name = dialog.result["title"]
                author = dialog.result["author"]
                template_path = dialog.result.get("template_path")
                
                # Combine creation and update
                self.controller.create_project(name, author=author, template_path=template_path, **dialog.result)
                
                self.refresh_list()
                msg.showinfo("Successo", f"Progetto creato: {name}")
            except Exception as e:
                msg.showerror("Errore", str(e))

class NewProjectDialog(ctk.CTkToplevel):
    def __init__(self, master, templates: list[str]):
        super().__init__(master, fg_color=Theme.COLOR_PANEL)
        self.title("Nuovo Progetto")
        self.geometry("500x600")
        self.result = None
        
        # Center content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=50, pady=50)
        
        ctk.CTkLabel(content, text="Nuovo Progetto", font=("Segoe UI", 28, "bold"), text_color=Theme.TEXT_MAIN).pack(pady=(0, 30), anchor="w")

        def make_entry(parent, label, placeholder=""):
            ctk.CTkLabel(parent, text=label, text_color=Theme.TEXT_DIM, font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 6))
            e = ctk.CTkEntry(parent, fg_color=Theme.COLOR_BG, border_color=Theme.COLOR_BORDER, text_color=Theme.TEXT_MAIN, height=38, placeholder_text=placeholder)
            e.pack(fill="x")
            return e

        self.entry_title = make_entry(content, "Nome Progetto (Cartella)", "Es. TesiMagistrale")
        self.entry_candidate = make_entry(content, "Candidato", "Es. Mario Rossi")
        self.entry_supervisor = make_entry(content, "Relatore", "Es. Prof. Verdi")
        self.entry_year = make_entry(content, "Anno Accademico", "Es. 2025/2026")

        ctk.CTkLabel(content, text="Template", text_color=Theme.TEXT_DIM, font=("Segoe UI", 12)).pack(anchor="w", pady=(15, 6))
        self.combo_template = ctk.CTkOptionMenu(content, values=templates, fg_color=Theme.COLOR_PANEL_HOVER, button_color=Theme.COLOR_ACCENT, text_color=Theme.TEXT_MAIN, height=38)
        self.combo_template.pack(fill="x")

        self.btn_ok = ctk.CTkButton(content, text="Crea Progetto", 
                                    fg_color=Theme.COLOR_ACCENT, hover_color=Theme.COLOR_ACCENT_HOVER,
                                    height=48, font=("Segoe UI", 16, "bold"),
                                    command=self.on_ok)
        self.btn_ok.pack(pady=40, fill="x")

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
