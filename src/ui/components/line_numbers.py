import tkinter as tk
from src.ui.theme import Theme

class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self.redraw, add='+')
        self.text_widget.bind('<Configure>', self.redraw, add='+')
        self.text_widget.bind("<<Modified>>", self.redraw, add='+')
        self.text_widget.bind('<MouseWheel>', self.redraw, add='+')
        self.text_widget.bind('<Button-1>', self.redraw, add='+')
        self.text_widget.bind('<Return>', self.redraw, add='+')
        
    def redraw(self, *args):
        self.delete("all")
        
        i = self.text_widget.index("@0,0")
        while True:
            dline= self.text_widget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(40, y, anchor="ne", text=linenum, fill=Theme.TEXT_DIM, font=("Consolas", 10))
            i = self.text_widget.index(f"{i}+1line")
