import customtkinter as ctk
from src.ui.theme import Theme
from src.utils.icons import IconFactory

class Breadcrumb(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.parts = []
        self.labels = []
        self.separators = []

    def update_path(self, path_parts: list):
        """
        Updates the breadcrumb with a list of strings representing the hierarchy.
        Example: ["My Thesis", "Chapter 1", "Paragraph 1.1"]
        """
        # Clear existing
        for label in self.labels:
            label.destroy()
        for sep in self.separators:
            sep.destroy()
        
        self.labels = []
        self.separators = []
        self.parts = path_parts

        for i, part in enumerate(self.parts):
            # Add separator if not first
            if i > 0:
                sep = ctk.CTkLabel(self, text=">", font=(Theme.FONT_FAMILY, 14), text_color=Theme.TEXT_DIM)
                sep.pack(side="left", padx=10)
                self.separators.append(sep)
            
            # Add label
            is_last = (i == len(self.parts) - 1)
            font_weight = "bold" if is_last else "normal"
            text_color = Theme.TEXT_MAIN if is_last else Theme.TEXT_DIM
            
            label = ctk.CTkLabel(self, text=part, font=(Theme.FONT_FAMILY, 14, font_weight), text_color=text_color)
            label.pack(side="left")
            self.labels.append(label)
