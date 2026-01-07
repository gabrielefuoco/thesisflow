
import customtkinter as ctk

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, current_manifest):
        super().__init__(master)
        self.title("Impostazioni Progetto")
        self.geometry("400x450")
        self.result = None
        self.manifest = current_manifest

        self.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self, text="Titolo Tesi").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_title = ctk.CTkEntry(self)
        self.entry_title.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entry_title.insert(0, self.manifest.title)

        # Candidate
        ctk.CTkLabel(self, text="Candidato").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_candidate = ctk.CTkEntry(self)
        self.entry_candidate.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.entry_candidate.insert(0, self.manifest.candidate or "")

        # Supervisor
        ctk.CTkLabel(self, text="Relatore").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_supervisor = ctk.CTkEntry(self)
        self.entry_supervisor.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.entry_supervisor.insert(0, self.manifest.supervisor or "")
        
        # Year
        ctk.CTkLabel(self, text="Anno Accademico").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_year = ctk.CTkEntry(self)
        self.entry_year.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        self.entry_year.insert(0, self.manifest.year or "")

        # Citation Style
        ctk.CTkLabel(self, text="Stile Citazione").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        
        # Scan for styles
        from src.utils.paths import get_resource_path
        from pathlib import Path
        styles_dir = get_resource_path("templates/styles")
        csl_files = ["Default"]
        if styles_dir.exists():
            csl_files.extend([f.name for f in styles_dir.glob("*.csl")])

        self.csl_var = ctk.StringVar(value=self.manifest.citation_style if self.manifest.citation_style else "Default")
        self.combo_csl = ctk.CTkComboBox(self, values=csl_files, variable=self.csl_var)
        self.combo_csl.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        # Save Button
        self.btn_save = ctk.CTkButton(self, text="Salva", command=self.on_save)
        self.btn_save.grid(row=5, column=0, columnspan=2, pady=20)

    def on_save(self):
        self.result = {
            "title": self.entry_title.get(),
            "candidate": self.entry_candidate.get(),
            "supervisor": self.entry_supervisor.get(),
            "year": self.entry_year.get(),
            "citation_style": self.csl_var.get()
        }
        self.destroy()
