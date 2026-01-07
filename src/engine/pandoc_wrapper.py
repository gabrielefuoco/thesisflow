
import subprocess
import shutil
from pathlib import Path
from src.utils.paths import get_pandoc_exe

class PandocWrapper:
    def __init__(self):
        self.exe = get_pandoc_exe()
        if not self.exe.exists():
            # Fallback for dev if not in bin/ but in PATH (optional)
            if shutil.which("pandoc"):
               self.exe = Path(shutil.which("pandoc"))
            else:
               raise FileNotFoundError(f"Pandoc executable not found at {self.exe}")

    def convert_markdown_to_typst(self, input_text: str, output_path: Path):
        """
        Converts Markdown string to a Typst file using Pandoc.
        Enabled extensions: +tex_math_dollars (for $...$ math)
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.exe),
            "--from", "markdown+tex_math_dollars",
            "--to", "typst",
            "--citeproc", # Basic citation processing if needed here, usually handled by typst hayagura but pandoc can do it too.
                          # Wait, SDD says "Pandoc transforms this...". 
                          # Actually for Typst ecosystem, standard BibTeX is often handled by Typst packages (hayagura).
                          # But let's stick to the prompt's implication: Pandoc generates Typst code.
            "--output", str(output_path)
        ]

        # In a real app we might want to feed input via stdin to avoid temp files for input,
        # but here we pass input_text via communicate.
        
        process = subprocess.run(
            cmd,
            input=input_text,
            text=True,
            capture_output=True,
            encoding='utf-8'
        )

        if process.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {process.stderr}")
