

# Runtime patch for PyInstaller Tcl/Tk support
import os
import sys
from pathlib import Path

if hasattr(sys, '_MEIPASS'):
    base_path = Path(sys._MEIPASS)
    
    # Direct mapping
    os.environ['TCL_LIBRARY'] = str(base_path / "tcl")
    os.environ['TK_LIBRARY'] = str(base_path / "tk")

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ui.app import ThesisFlowApp

def main():
    app = ThesisFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()
