import customtkinter as ctk
import tkinter as tk

class FindReplaceDialog(ctk.CTkToplevel):
    def __init__(self, master, text_widget):
        super().__init__(master)
        self.text_widget = text_widget
        self.title("Trova e Sostituisci")
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(master)
        
        ctk.CTkLabel(self, text="Trova:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_find = ctk.CTkEntry(self)
        self.entry_find.grid(row=0, column=1, padx=10, pady=10)
        self.entry_find.focus_set()
        
        ctk.CTkButton(self, text="Trova Tutto", command=self.find_next).grid(row=2, column=0, columnspan=2, pady=10)

    def find_next(self):
        target = self.entry_find.get()
        if not target: return
        
        self.text_widget.tag_remove("found", "1.0", "end")
        self.text_widget.tag_config("found", background="yellow", foreground="black")
        
        count = tk.IntVar()
        start = "1.0"
        first_pos = None
        
        while True:
            pos = self.text_widget.search(target, start, stopindex="end", count=count, nocase=True)
            if not pos: break
            
            end = f"{pos}+{count.get()}c"
            self.text_widget.tag_add("found", pos, end)
            
            if not first_pos: first_pos = pos
            start = end
        
        if first_pos:
            self.text_widget.see(first_pos)
