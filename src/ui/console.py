
import customtkinter as ctk
import logging
import tkinter as tk

class ConsolePanel(ctk.CTkFrame):
    def __init__(self, master, logger_name="ThesisFlow", **kwargs):
        super().__init__(master, height=150, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title bar logic for collapsing could go here, but keep simple for now
        self.lbl_title = ctk.CTkLabel(self, text="Console Output", font=("Arial", 12, "bold"))
        self.lbl_title.grid(row=0, column=0, sticky="w", padx=5)
        
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 10), state="disabled", fg_color=("white", "gray10"))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Setup logging handler
        self.logger = logging.getLogger(logger_name)
        self.handler = ConsoleUiHandler(self.textbox)
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

class ConsoleUiHandler(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
    
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.textbox.configure(state="normal")
            self.textbox.insert("end", msg + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")
        
        # Ensure thread safety for Tkinter
        self.textbox.after(0, append)
