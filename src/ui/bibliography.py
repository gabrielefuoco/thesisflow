
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
        pm = self.winfo_toplevel().project_controller.pm # Access PM via Controller or App
        # Or simpler if we know App structure:
        # pm = self.winfo_toplevel().pm 
        # Since App has self.pm = self.project_controller.pm, this works.
        pm = self.winfo_toplevel().pm
        target = self.project_root / "references.bib"
        if target.exists():
             content = pm.read_file_content(target)
             self.textbox.delete("1.0", "end")
             self.textbox.insert("1.0", content)
    
    def save(self):
        if not self.project_root: return
        pm = self.winfo_toplevel().pm
        text = self.textbox.get("1.0", "end-1c")
        target = self.project_root / "references.bib"
        pm.save_file_content(target, text)
        pm.bib_service.load_bibliography(target) # Reload service
        msg.showinfo("Info", "Bibliografia salvata.")

    def open_citation_dialog(self):
        CitationDialog(self, self.on_add_citation)

    def on_add_citation(self, bibtex_entry):
        self.textbox.insert(tk.END, "\n" + bibtex_entry + "\n")

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
        
        # DOI Lookup
        frame_doi = ctk.CTkFrame(self)
        frame_doi.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(frame_doi, text="Cerca DOI:").pack(side="left", padx=5)
        self.entry_doi_search = ctk.CTkEntry(frame_doi, placeholder_text="10.1038/...")
        self.entry_doi_search.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_search = ctk.CTkButton(frame_doi, text="🔍", width=40, command=self.lookup_doi)
        self.btn_search.pack(side="left", padx=5)

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
        self.on_success(entry)
        self.destroy()

    def lookup_doi(self):
        doi = self.entry_doi_search.get().strip()
        if not doi: return
        
        # UI Feedback
        self.btn_search.configure(state="disabled", text="⏳")
        self.entry_doi_search.configure(state="disabled")
        
        # Allow thread to find PM safely
        # Toplevel might be App, but accessing GUI widgets from thread is bad?
        # Accessing `pm` instance is fine if it's thread safe.
        # But `self.master.winfo_toplevel()` must be called in Main Thread.
        pm = self.master.winfo_toplevel().pm

        import threading
        def run_lookup():
            try:
                data = pm.resolve_doi(doi)
                self.after(0, lambda: self._on_lookup_success(data))
            except Exception as e:
                self.after(0, lambda e=e: self._on_lookup_error(e))
        
        threading.Thread(target=run_lookup, daemon=True).start()

    def _on_lookup_success(self, data):
        self.fill_from_data(data)
        self._reset_search_ui()

    def _on_lookup_error(self, error):
        msg.showerror("Errore DOI", str(error))
        self._reset_search_ui()

    def _reset_search_ui(self):
        self.btn_search.configure(state="normal", text="🔍")
        self.entry_doi_search.configure(state="normal")

    def fill_from_data(self, data: dict):
        # Set Type
        if data["type"] in ["article", "book", "misc"]:
             self.type_var.set(data["type"])
        else:
             self.type_var.set("misc")

        # Fill fields
        fields_data = data["fields"]
        if "title" in self.fields: self.fields["title"].delete(0, tk.END); self.fields["title"].insert(0, fields_data["title"])
        if "author" in self.fields: self.fields["author"].delete(0, tk.END); self.fields["author"].insert(0, fields_data["author"])
        if "year" in self.fields: self.fields["year"].delete(0, tk.END); self.fields["year"].insert(0, fields_data["year"])
        if "publisher" in self.fields: self.fields["publisher"].delete(0, tk.END); self.fields["publisher"].insert(0, fields_data["publisher"])
        if "doi" in self.fields: self.fields["doi"].delete(0, tk.END); self.fields["doi"].insert(0, fields_data["doi"])
        if "id" in self.fields and fields_data.get("id"):
             self.fields["id"].delete(0, tk.END); self.fields["id"].insert(0, fields_data["id"])

        msg.showinfo("Successo", "Dati importati dal DOI!")


