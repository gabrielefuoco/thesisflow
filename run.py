import os
import sys
from pathlib import Path
import customtkinter as ctk

# Tcl/Tk Fix for PyInstaller
# if hasattr(sys, '_MEIPASS'):
#     base_path = Path(sys._MEIPASS)
#     # Direct mapping to bundled folders
#     os.environ['TCL_LIBRARY'] = str(base_path / "tcl")
#     os.environ['TK_LIBRARY'] = str(base_path / "tk")

# Import the App
# Since this script is in the root, 'src' is a direct package.
from src.ui.app import ThesisFlowApp

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = ThesisFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()
