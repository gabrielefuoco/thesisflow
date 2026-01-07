
import customtkinter as ctk
import logging
import tkinter as tk

class ConsolePanel(ctk.CTkFrame):
    def __init__(self, master, logger_name="ThesisFlow", **kwargs):
        super().__init__(master, height=150, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header Frame (Clickable)
        self.header_frame = ctk.CTkFrame(self, height=25, fg_color=("gray85", "gray25"), corner_radius=5)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        
        from src.utils.icons import IconFactory
        self.icon_toggle = ctk.CTkLabel(self.header_frame, text="", image=IconFactory.get_icon("down", size=(12,12), color="gray"))
        self.icon_toggle.pack(side="left", padx=5)
        
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="Console Output", font=("Arial", 11, "bold"))
        self.lbl_title.pack(side="left", padx=5)
        
        self.header_frame.bind("<Button-1>", self.toggle_collapse)
        self.lbl_title.bind("<Button-1>", self.toggle_collapse)
        self.icon_toggle.bind("<Button-1>", self.toggle_collapse)

        self.is_collapsed = False
        
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 10), state="disabled", fg_color=("white", "gray10"))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    def toggle_collapse(self, event=None):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.textbox.grid_forget()
            self.configure(height=30)
            self.icon_toggle.configure(image=IconFactory.get_icon("play", size=(12,12), color="gray")) # Right arrow approx
        else:
            self.textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            self.configure(height=150)
            self.icon_toggle.configure(image=IconFactory.get_icon("down", size=(12,12), color="gray"))

    def expand(self):
        if self.is_collapsed:
             self.toggle_collapse()
        
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
            
            # Auto-expand on error
            if record.levelno >= logging.ERROR:
                self.textbox.master.expand()
        
        # Ensure thread safety for Tkinter
        self.textbox.after(0, append)
