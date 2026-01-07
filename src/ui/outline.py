import customtkinter as ctk

class OutlinePanel(ctk.CTkScrollableFrame):
    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(master, label_text="Outline", width=150, **kwargs)
        self.on_navigate = on_navigate

    def update_outline(self, headings: list):
        for widget in self.winfo_children():
            widget.destroy()

        if not headings:
            ctk.CTkLabel(self, text="No Headings", text_color="gray").pack(pady=10)
            return

        for level, text, index in headings:
            # Indent based on level (1, 2, 3...)
            display_text = text[:20] + "..." if len(text) > 20 else text
            
            # Visual hierarchy
            font = ("Arial", 12, "bold") if level == 1 else ("Arial", 11)
            padx = (level-1) * 10
            
            btn = ctk.CTkButton(self, text=display_text, 
                                anchor="w", 
                                font=font,
                                fg_color="transparent", 
                                text_color=("black", "white"),
                                height=20,
                                hover_color=("gray80", "gray30"),
                                command=lambda idx=index: self.on_navigate(idx))
            btn.pack(fill="x", pady=1, padx=(padx, 0))
