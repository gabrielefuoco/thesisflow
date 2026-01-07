
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

        # Add Citation Button
        self.btn_add = ctk.CTkButton(self, text="+ Aggiungi Citazione", fg_color="green", command=self.open_citation_dialog)
        self.btn_add.grid(row=3, column=0, pady=(0, 10))

        self.load()

    def load(self):
        if not self.project_root: return
        bib_path = self.project_root / "references.bib"
        if bib_path.exists():
            self.textbox.insert("1.0", bib_path.read_text(encoding="utf-8"))
    
    def save(self):
        if not self.project_root: return
        text = self.textbox.get("1.0", "end-1c")
        bib_path.write_text(text, encoding="utf-8")
        msg.showinfo("Info", "Bibliografia salvata.")

    def open_citation_dialog(self):
        CitationDialog(self, self.on_add_citation)

    def on_add_citation(self, bibtex_entry):
        self.textbox.insert(tk.END, "\n" + bibtex_entry + "\n")
        # Auto save? Let's just update text for now.

import tkinter as tk

class CitationDialog(ctk.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Aggiungi Citazione")
        self.geometry("400x500")
        self.on_success = on_success
        
        self.type_var = ctk.StringVar(value="article")
        
        ctk.CTkLabel(self, text="Tipo").pack(pady=5)
        ctk.CTkOptionMenu(self, variable=self.type_var, values=["article", "book", "website", "misc"]).pack(pady=5)
        
        self.fields = {}
        # Common fields
        for field in ["Key (es. smith2020)", "Title", "Author", "Year", "Publisher/Journal", "URL/DOI"]:
            ctk.CTkLabel(self, text=field).pack(pady=2)
            entry = ctk.CTkEntry(self)
            entry.pack(fill="x", padx=20)
            # Map label to specific key for bibtex
            key_map = {
                "Key (es. smith2020)": "id",
                "Title": "title",
                "Author": "author",
                "Year": "year",
                "Publisher/Journal": "publisher", # logic to split later
                "URL/DOI": "doi" 
            }
            self.fields[key_map[field]] = entry

        ctk.CTkButton(self, text="Genera & Aggiungi", command=self.generate).pack(pady=20)

    def generate(self):
        ctype = self.type_var.get()
        vals = {k: v.get().strip() for k, v in self.fields.items()}
        
        if not vals["id"]:
            msg.showerror("Errore", "La Key è obbligatoria.")
            return

        # Basic BibTeX construction
        entry = f"@{ctype}{{{vals['id']},\n"
        if vals["title"]: entry += f"  title = {{{vals['title']}}},\n"
        if vals["author"]: entry += f"  author = {{{vals['author']}}},\n"
        if vals["year"]: entry += f"  year = {{{vals['year']}}},\n"
        
        # Publisher/Journal ambiguity
        if vals["publisher"]:
            if ctype == "article":
                entry += f"  journal = {{{vals['publisher']}}},\n"
            else:
                entry += f"  publisher = {{{vals['publisher']}}},\n"
        
        if vals["doi"]:
             if "http" in vals["doi"]:
                 entry += f"  url = {{{vals['doi']}}},\n"
             else:
                 entry += f"  doi = {{{vals['doi']}}},\n"
        
        entry += "}"
        
        self.on_success(entry)
        self.destroy()
