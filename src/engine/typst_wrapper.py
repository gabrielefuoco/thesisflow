
import subprocess
import shutil
from pathlib import Path
from src.utils.paths import get_typst_exe

class TypstWrapper:
    def __init__(self):
        self.exe = get_typst_exe()
        if not self.exe.exists():
             if shutil.which("typst"):
               self.exe = Path(shutil.which("typst"))
             else:
               raise FileNotFoundError(f"Typst executable not found at {self.exe}")

    def compile(self, input_path: Path, output_path: Path = None):
        """
        Compiles a Typst file to PDF.
        """
        cmd = [str(self.exe), "compile", str(input_path)]
        
        if output_path:
            cmd.append(str(output_path))

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if process.returncode != 0:
            raise RuntimeError(f"Typst failed: {process.stderr}")
