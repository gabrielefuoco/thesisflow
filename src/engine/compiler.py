
from pathlib import Path
import shutil
from .pandoc_wrapper import PandocWrapper
from .typst_wrapper import TypstWrapper
from src.utils.paths import get_templates_dir

class CompilerEngine:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        # Implicit structure based on SDD
        self.temp_dir = self.project_root / ".thesis_data" / "temp"
        self.chapters_dir = self.project_root / "chapters"
        self.assets_dir = self.project_root / "assets"
        self.master_file = self.project_root / "master.typ"
        self.output_pdf = self.project_root / "Tesi_Finale.pdf"
        
        self.pandoc = PandocWrapper()
        self.typst = TypstWrapper()

    def _prepare_temp(self):
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _concatenate_chapters(self) -> str:
        manifest_path = self.project_root / ".thesis_data" / "manifest.json"
        
        if manifest_path.exists():
            # Use manifest order
            import json
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                chapters = data.get("chapters", [])
                full_text = ""
                for chap in chapters:
                    filename = chap.get("filename")
                    path = self.chapters_dir / filename
                    if path.exists():
                        full_text += path.read_text(encoding="utf-8") + "\n\n"
                return full_text
            except Exception as e:
                print(f"Error reading manifest: {e}. Falling back to alphabetical.")

        # Fallback: alphabetical
        md_files = sorted(self.chapters_dir.glob("*.md"))
        full_text = ""
        for md in md_files:
            full_text += md.read_text(encoding="utf-8") + "\n\n"
        return full_text

    def compile(self):
        print("Step 1: Preparing build environment...")
        self._prepare_temp()

        # Generate metadata.typ for Front Matter
        self._generate_typst_metadata()

        print("Step 2: Aggregating content...")
        full_markdown = self._concatenate_chapters()
        
        # Inject Bibliography Metadata if references.bib exists
        bib_path = self.project_root / "references.bib"
        if bib_path.exists():
            print("Bibliography found, injecting metadata...")
            # Prepend YAML metadata for Pandoc
            yaml_block = "---\nbibliography: references.bib\n---\n\n"
            full_markdown = yaml_block + full_markdown

        if not full_markdown:
            print("Warning: No markdown content found.")
            full_markdown = "*Nessun contenuto.*"

        print("Step 3: Converting Markdown -> Typst (Pandoc)...")
        compiled_body_path = self.temp_dir / "compiled_body.typ"

        # Determine CSL path from manifest
        manifest_path = self.project_root / ".thesis_data" / "manifest.json"
        csl_path: Optional[Path] = None
        if manifest_path.exists():
            import json
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                citation_style = data.get("citation_style")
                if citation_style and citation_style != "Default":
                    from src.utils.paths import get_resource_path
                    potential_csl_path = get_resource_path(f"templates/styles/{citation_style}.csl")
                    if potential_csl_path.exists():
                        print(f"Using CSL: {potential_csl_path}")
                        csl_path = potential_csl_path
                    else:
                        print(f"CSL not found: {potential_csl_path}. Falling back to default.")
            except Exception as e:
                print(f"Error reading manifest for CSL: {e}. Falling back to default.")

        try:
             self.typst.compile(self.master_file, self.output_pdf)
        except RuntimeError as e:
             # Extract stderr from message "Typst failed: <stderr>"
             msg = str(e)
             if "Typst failed:" in msg:
                 stderr = msg.split("Typst failed:", 1)[1].strip()
                 raise CompilationError("Errore durante la compilazione Typst", details=stderr)
             raise e
             
        print(f"Done! Output at: {self.output_pdf}")
        
        print(f"Done! Output at: {self.output_pdf}")

class CompilationError(Exception):
    def __init__(self, message, details=""):
        super().__init__(message)
        self.details = details

    def _generate_typst_metadata(self):
        # Reads manifest and writes .thesis_data/temp/metadata.typ
        manifest_path = self.project_root / ".thesis_data" / "manifest.json"
        metadata_content = ""
        
        if manifest_path.exists():
            import json
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                title = data.get("title", "Titolo")
                author = data.get("author", "Autore")
                candidate = data.get("candidate", author)
                supervisor = data.get("supervisor", "Relatore")
                year = data.get("year", "2024")
                
                metadata_content = f'''
#let title = "{title}"
#let candidate = "{candidate}"
#let supervisor = "{supervisor}"
#let year = "{year}"
'''
            except Exception as e:
                print(f"Error reading manifest for metadata: {e}")
        
        (self.temp_dir / "metadata.typ").write_text(metadata_content, encoding="utf-8")

    def _create_default_master(self):
        print("Master file not found, creating default...")
        default_master = get_templates_dir() / "master_default.typ"
        if default_master.exists():
            shutil.copy(default_master, self.master_file)
        else:
             # Fallback
            self.master_file.write_text('#include ".thesis_data/temp/compiled_body.typ"', encoding="utf-8")
