import subprocess
import threading
import re
from pathlib import Path
from typing import Callable, Optional
from src.utils.paths import get_typst_exe

class CompilationError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class AsyncCompiler:
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def compile(self, project_path: Path, on_success: Callable[[Path], None], on_error: Callable[[Exception], None]):
        """
        Starts compilation in a separate thread.
        """
        def _run():
            try:
                pdf_path = self._compile_sync(project_path)
                on_success(pdf_path)
            except Exception as e:
                on_error(e)

        threading.Thread(target=_run, daemon=True).start()

    def _compile_sync(self, project_path: Path) -> Path:
        """
        Blocking compilation logic.
        """
        typst_exe = get_typst_exe()
        if not typst_exe.exists():
            raise CompilationError("Typst executable not found.")

        input_file = project_path / "master.typ"
        output_file = project_path / f"{project_path.name}.pdf"
        
        # Ensure input exists
        if not input_file.exists():
             # Try to generate it if logic allows, or error
             # For now, error
             raise CompilationError("master.typ not found in project.")

        cmd = [str(typst_exe), "compile", str(input_file), str(output_file), "--root", str(project_path)]
        
        # Capture output for error parsing
        try:
            with self._lock:
                self._process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_path
                )
            
            stdout, stderr = self._process.communicate()
            
            if self._process.returncode != 0:
                friendly_error = self._parse_error(stderr)
                raise CompilationError("Errore durante la compilazione", details=friendly_error)
            
            return output_file
            
        except OSError as e:
             raise CompilationError(f"OS Error: {e}")
        finally:
             with self._lock:
                 self._process = None

    def _parse_error(self, stderr: str) -> str:
        """
        Parses Typst stderr to extract meaningful error messages.
        """
        lines = stderr.split('\n')
        parsed = []
        for line in lines:
            if "error:" in line:
                # Extract file and line info if possible
                # Format: error: <msg> at <file>:<line>:<col>
                parsed.append(f"❌ {line.strip()}")
            elif "warning:" in line:
                 parsed.append(f"⚠️ {line.strip()}")
            elif line.strip():
                 parsed.append(line.strip())
        
        if not parsed:
            return stderr # Return raw if no pattern matched
            
        return "\n".join(parsed)

    def cancel(self):
        with self._lock:
            if self._process:
                self._process.terminate()
