
import sys
import os
from pathlib import Path

# Add src to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from src.engine.compiler import CompilerEngine

def create_sample_project(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    (path / "chapters").mkdir(exist_ok=True)
    (path / "assets").mkdir(exist_ok=True)
    (path / ".thesis_data").mkdir(exist_ok=True)
    
    # Create dummy chapter
    (path / "chapters" / "01_intro.md").write_text("# Introduzione\n\nQuesta è una tesi di prova generata da **ThesisFlow**.\n\nEcco una formula: $E=mc^2$.", encoding="utf-8")
    
    print(f"Sample project created at {path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_cli.py [init|build] <project_path>")
        return

    command = sys.argv[1]
    project_path = Path(sys.argv[2]).resolve()

    if command == "init":
        create_sample_project(project_path)
    elif command == "build":
        engine = CompilerEngine(project_path)
        try:
            engine.compile()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
