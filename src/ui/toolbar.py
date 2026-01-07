
import customtkinter as ctk

class ToolbarFrame(ctk.CTkFrame):
    def __init__(self, master, command_compile=None, **kwargs):
        super().__init__(master, height=50, **kwargs)
        
        self.command_compile = command_compile

        # Layout
        self.grid_columnconfigure(0, weight=0) # Left spacer
        # We'll just pack buttons left to right

        self.btn_bold = ctk.CTkButton(self, text="B", width=40, font=("Arial", 12, "bold"), command=lambda: self.master.master.editor.insert_at_cursor("**bold**"))
        self.btn_bold.grid(row=0, column=0, padx=5, pady=5)

        self.btn_italic = ctk.CTkButton(self, text="I", width=40, font=("Arial", 12, "italic"), command=lambda: self.master.master.editor.insert_at_cursor("_italic_"))
        self.btn_italic.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_math = ctk.CTkButton(self, text="Math", width=50, command=lambda: self.master.master.editor.insert_at_cursor("$E=mc^2$"))
        self.btn_math.grid(row=0, column=2, padx=5, pady=5)

        self.btn_img = ctk.CTkButton(self, text="Img", width=50, fg_color="gray", command=self.on_image_click)
        self.btn_img.grid(row=0, column=3, padx=5, pady=5)

        # Spacer
        self.spacer = ctk.CTkLabel(self, text="", width=20)
        self.spacer.grid(row=0, column=4)

        # Compile Button (Right aligned? Or just next)
        self.btn_compile = ctk.CTkButton(self, text="COMPILA", fg_color="green", hover_color="darkgreen", command=self.command_compile)
        self.btn_compile.grid(row=0, column=5, padx=20, pady=5)

    def on_image_click(self):
        from customtkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            # We need to call the app to handle the file copy via ProjectManager
            app = self.master.master
            # Assuming app has a method to add asset, or we access app.pm directly?
            # Better to have key methods on App.
            try:
                # Need to convert to Path
                from pathlib import Path
                p = Path(path)
                rel_path = app.pm.add_asset(p)
                app.editor.insert_image(rel_path)
            except Exception as e:
                print(f"Error adding image: {e}")
