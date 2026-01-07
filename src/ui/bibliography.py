
import customtkinter as ctk
from pathlib import Path
import tkinter.messagebox as msg

class BibliographyFrame(ctk.CTkFrame):
    def __init__(self, master, project_root: Path = None, **kwargs):
        super().__init__(master, **kwargs)
        self.project_root = project_root
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.lbl = ctk.CTkLabel(self, text="Bibliografia (BibTeX)", font=("Arial", 16, "bold"))
        self.lbl.grid(row=0, column=0, pady=10)

        self.textbox = ctk.CTkTextbox(self, width=400, corner_radius=10, font=("Consolas", 12))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.btn_save = ctk.CTkButton(self, text="Salva Bibliografia", command=self.save)
        self.btn_save.grid(row=2, column=0, pady=10)

        self.load()

    def load(self):
        if not self.project_root: return
        bib_path = self.project_root / "references.bib"
        if bib_path.exists():
            self.textbox.insert("1.0", bib_path.read_text(encoding="utf-8"))
    
    def save(self):
        if not self.project_root: return
        text = self.textbox.get("1.0", "end-1c")
        bib_path = self.project_root / "references.bib"
        bib_path.write_text(text, encoding="utf-8")
        msg.showinfo("Info", "Bibliografia salvata.")
