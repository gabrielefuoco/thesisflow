

import PyInstaller.__main__
import customtkinter
import os
import sys
import tkinter
from pathlib import Path

def build():
    # Get CustomTkinter path for data inclusion
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Define project root
    project_root = Path(__file__).parent
    
    # Binaries and Templates
    bin_path = project_root / "bin"
    templates_path = project_root / "templates"
    
    if not bin_path.exists():
        print(f"Error: {bin_path} does not exist. Please create it and add pandoc.exe/typst.exe.")
        return

    # Locate Tcl/Tk support files
    tcl_root = tkinter.Tcl().eval('info library')
    parent_dir = os.path.dirname(tcl_root)
    tk_root = None
    for item in os.listdir(parent_dir):
        if item.startswith('tk') and os.path.isdir(os.path.join(parent_dir, item)):
            tk_root = os.path.join(parent_dir, item)
            break
            
    if not tk_root:
        tk_root = tcl_root.replace("tcl", "tk")

    # Verify init.tcl
    if not (Path(tcl_root) / "init.tcl").exists():
        print(f"WARNING: init.tcl not found in {tcl_root}!")
    
    # Bundle straightforwardly to 'tcl' and 'tk' to match the fixed paths in main_gui.py
    print(f"Bundling Tcl from: {tcl_root} -> tcl")
    print(f"Bundling Tk from:  {tk_root} -> tk")

    assets_path = project_root / "assets"
    
    # PyInstaller arguments
    args = [
        str(project_root / "run.py"), # CHANGED: Use root run.py
        '--name=ThesisFlow',
        '--noconsole',
        '--onedir', 
        '--clean',
        f'--add-data={ctk_path};customtkinter/',
        f'--add-data={bin_path};bin/',
        f'--add-data={templates_path};templates/',
        f'--add-data={assets_path};assets/',
        
        # Simplified mapping
        f'--add-data={tcl_root};tcl/',
        f'--add-data={tk_root};tk/',
        
        # Ensure project root is in path so 'src.engine' imports resolve
        f'--paths={project_root}',
        
        # NUCLEAR OPTION: Collect EVERYTHING from src
        '--collect-all=src',
    ]


    print("Running PyInstaller with args:")
    for a in args:
        print(a)

    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()

