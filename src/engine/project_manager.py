
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Callable
from src.engine.models import ProjectManifest, Chapter, Paragraph
from src.utils.paths import get_templates_dir

from src.engine.citation_service import BibliographyService

class ProjectManager:
    def __init__(self, projects_root: Path = None):
        if projects_root:
            self.projects_root = projects_root
        else:
             # Default to user documents
            self.projects_root = Path.home() / "Documents" / "ThesisFlow_Projects"
        
        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.current_project_path: Optional[Path] = None
        self.manifest: Optional[ProjectManifest] = None
        self.bib_service = BibliographyService()

    def list_projects(self) -> List[Path]:
        """Returns a list of valid project directories."""
        projects = []
        if not self.projects_root.exists():
            return []
            
        for d in self.projects_root.iterdir():
            if d.is_dir() and (d / ".thesis_data" / "manifest.json").exists():
                projects.append(d)
        return projects

    def check_system_health(self) -> List[str]:
        """Checks for required external tools."""
        from src.utils.paths import get_pandoc_exe, get_typst_exe
        missing = []
        if not get_pandoc_exe().exists(): missing.append("Pandoc")
        if not get_typst_exe().exists(): missing.append("Typst")
        return missing

    def get_citation_keys(self) -> List[str]:
        """Extracts citation keys from the project's bibliography."""
        return self.bib_service.get_citation_keys()

    def list_assets(self) -> List[Path]:
        """Returns list of asset files in the project."""
        if not self.current_project_path: return []
        assets_dir = self.current_project_path / "assets"
        if not assets_dir.exists(): return []
        return list(assets_dir.glob("*"))

    def list_subsections(self, chapter: Chapter) -> List[Path]:
        """Returns list of subsection files for a chapter."""
        if not self.current_project_path: return []
        # Convention: chapters/<id>/<files>
        chap_dir = self.current_project_path / "chapters" / chapter.id
        if not chap_dir.is_dir(): return []
        
        files = []
        for f in sorted(chap_dir.glob("*.md")):
            if f.name == "master.md": continue
            files.append(f)
        return files

    def read_file_content(self, path: Path) -> str:
        """Reads text content from a path."""
        # Security check? ensure path is within project
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def save_file_content(self, path: Path, content: str):
        """Saves text content to a path."""
        # Ensure parent exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def create_project(self, name: str, author: str, template_path: Path = None) -> Path:
        """Creates a new project structure."""
        safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip()
        project_dir = self.projects_root / safe_name
        
        if project_dir.exists():
            raise FileExistsError(f"Project '{safe_name}' already exists.")

        # Scaffolding
        (project_dir / ".thesis_data").mkdir(parents=True)
        (project_dir / "assets").mkdir()
        (project_dir / "chapters").mkdir()
        
        # Manifest
        manifest = ProjectManifest(title=name, author=author)
        self._save_manifest_internal(project_dir, manifest)
        
        # Template Handling
        target_master = project_dir / "master.typ"
        if template_path and template_path.exists():
            shutil.copy(template_path, target_master)
        else:
             # Default Master Template
            default_master = get_templates_dir() / "master_default.typ"
            if default_master.exists():
                shutil.copy(default_master, target_master)
            else:
                # Fallback
                target_master.write_text('#include ".thesis_data/temp/compiled_body.typ"', encoding="utf-8")
            
        self.current_project_path = project_dir
        self.manifest = manifest
        # Create first chapter default
        self.create_chapter("Capitolo 1: Introduzione")
        
        # Init Bib
        (project_dir / "references.bib").touch()
        self.bib_service.load_bibliography(project_dir / "references.bib")
        
        return project_dir

    def list_templates(self) -> List[str]:
        """Lists available project templates."""
        t_dir = get_templates_dir()
        if not t_dir.exists(): return ["Default"]
        return [f.name for f in t_dir.glob("*.typ")]

    def list_citation_styles(self) -> List[str]:
        """Lists available CSL citation styles."""
        from src.utils.paths import get_resource_path
        styles_dir = get_resource_path("templates/styles")
        csl_files = ["Default"]
        if styles_dir.exists():
            csl_files.extend([f.name for f in styles_dir.glob("*.csl")])
        return csl_files

    def load_project(self, project_dir: Path):
        manifest_path = project_dir / ".thesis_data" / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError("Invalid project: manifest.json missing.")
        
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.manifest = ProjectManifest.from_dict(data)
        self.current_project_path = project_dir
        self.bib_service.load_bibliography(project_dir / "references.bib")
        
        # Soft migration: check for paragraphs in chapter subdirectories
        self._migrate_paragraphs_if_needed()

    def _migrate_paragraphs_if_needed(self):
        """Discovers existing sub-sections and adds them to manifest if missing."""
        if not self.manifest or not self.current_project_path: return
        
        migrated = False
        for chapter in self.manifest.chapters:
            chap_dir = self.current_project_path / "chapters" / chapter.id
            if chap_dir.is_dir():
                # Scan for .md files that aren't master.md and not in manifest
                existing_filenames = {p.filename for p in chapter.paragraphs}
                for f in sorted(chap_dir.glob("*.md")):
                    if f.name == "master.md": continue
                    if f.name not in existing_filenames:
                        # Found a loose file, add to manifest
                        p_id = f.stem.split('_')[-1] if '_' in f.stem else uuid.uuid4().hex[:8]
                        new_p = Paragraph(id=p_id, title=f.stem.replace('_', ' '), filename=f.name)
                        chapter.paragraphs.append(new_p)
                        migrated = True
        
        if migrated:
            self.save_settings()

    def create_chapter(self, title: str) -> Chapter:
        if not self.manifest or not self.current_project_path:
            raise RuntimeError("No project loaded.")

        cid = str(uuid.uuid4())[:8]
        filename = f"chap_{cid}.md"
        chapter = Chapter(id=cid, title=title, filename=filename)
        
        # Write file
        file_path = self.current_project_path / "chapters" / filename
        file_path.write_text(f"# {title}\n\nScrivi qui il tuo contenuto...", encoding="utf-8")
        
        self.manifest.chapters.append(chapter)
        self._save_manifest_internal(self.current_project_path, self.manifest)
        return chapter

    def create_paragraph(self, chapter: Chapter, title: str) -> Paragraph:
        """Creates a paragraph file in the chapter's directory and updates manifest."""
        if not self.current_project_path:
             raise RuntimeError("No project loaded")
        
        cid = chapter.id
        base_dir = self.current_project_path / "chapters" / cid
        base_dir.mkdir(exist_ok=True, parents=True)
        
        pid = uuid.uuid4().hex[:8]
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
        filename = f"{safe_title}_{pid}.md"
        
        file_path = base_dir / filename
        file_path.write_text(f"## {title}\n\n", encoding="utf-8")

        new_paragraph = Paragraph(id=pid, title=title, filename=filename)
        chapter.paragraphs.append(new_paragraph)
        self.save_settings()
        return new_paragraph

    def create_subsection(self, chapter: Chapter, title: str):
        """Deprecated: Use create_paragraph instead."""
        self.create_paragraph(chapter, title)

    def delete_paragraph(self, chapter: Chapter, paragraph: Paragraph):
        """Deletes a paragraph file and removes from manifest."""
        if not self.current_project_path: return
        
        chapter.paragraphs = [p for p in chapter.paragraphs if p.id != paragraph.id]
        self.save_settings()
        
        file_path = self.current_project_path / "chapters" / chapter.id / paragraph.filename
        if file_path.exists():
            file_path.unlink()

    def move_paragraph(self, chapter: Chapter, paragraph: Paragraph, direction: str):
        """Moves a paragraph 'up' or 'down' in the chapter list."""
        idx = -1
        for i, p in enumerate(chapter.paragraphs):
            if p.id == paragraph.id:
                idx = i
                break
        
        if idx == -1: return

        new_idx = idx
        if direction == "up" and idx > 0:
            new_idx = idx - 1
        elif direction == "down" and idx < len(chapter.paragraphs) - 1:
            new_idx = idx + 1
        
        if new_idx != idx:
            chapter.paragraphs[idx], chapter.paragraphs[new_idx] = chapter.paragraphs[new_idx], chapter.paragraphs[idx]
            self.save_settings()

    def export_project(self, project_path: Path, export_path: Path):
        """Exports the project as a ZIP archive."""
        import shutil
        if not project_path.exists():
            raise FileNotFoundError("Project path not found")
        
        # Create zip
        base_name = str(export_path).replace(".zip", "")
        shutil.make_archive(base_name, 'zip', project_path)

    def import_project(self, zip_path: Path) -> Path:
        """Imports a project from a ZIP archive."""
        import shutil
        if not zip_path.exists():
            raise FileNotFoundError("Zip file not found")
            
        # Extract to temp first to read manifest?
        # Or just extract to projects root with unique name
        # Assumption: Zip contains project folder or contents?
        # Let's extract to a temp folder to check name
        temp_dir = self.projects_root / ".temp_import"
        if temp_dir.exists(): shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        shutil.unpack_archive(zip_path, temp_dir)
        
        # Check structure
        # If single folder inside, move it. If loose files, move temp_dir as project.
        items = list(temp_dir.iterdir())
        if len(items) == 1 and items[0].is_dir():
             candidate = items[0]
        else:
             candidate = temp_dir
             
        manifest_file = candidate / ".thesis_data" / "manifest.json"
        
        if not manifest_file.exists():
             shutil.rmtree(temp_dir)
             raise ValueError("Il file ZIP non contiene un progetto ThesisFlow valido (manifest.json mancante).")
             
        # Read Manifest for name
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        title = data.get("title", "Imported Project")
        
        # Determine unique destination
        safe_name = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
        dest_path = self.projects_root / safe_name
        counter = 1
        while dest_path.exists():
             dest_path = self.projects_root / f"{safe_name}_{counter}"
             counter += 1
             
        shutil.move(candidate, dest_path)
        if temp_dir.exists(): shutil.rmtree(temp_dir) # Cleanup if we didn't move it directly
        
        return dest_path

    def delete_project(self, project_path: Path):
        """Deletes a project directory."""
        import shutil
        if project_path.exists():
            shutil.rmtree(project_path)

    def resolve_doi(self, doi: str) -> dict:
        """Resolves a DOI to BibTeX fields using crossref.org."""
        import urllib.request
        import json
        
        # Clean DOI
        doi = doi.replace("http://doi.org/", "").replace("https://doi.org/", "")
        
        url = f"https://api.crossref.org/works/{doi}"
        try:
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                data = json.loads(response.read().decode())
                item = data.get("message", {})
                
                # Map to fields
                fields = {
                    "id": item.get("DOI", "").split("/")[-1], # Simple ID gen
                    "title": item.get("title", [""])[0],
                    "author": " and ".join([f"{a.get('family', '')}, {a.get('given', '')}" for a in item.get("author", [])]),
                    "year": str(item.get("issued", {}).get("date-parts", [[0]])[0][0]),
                    "publisher": item.get("publisher", ""),
                    "doi": item.get("DOI", "")
                }
                
                return {"type": item.get("type", "misc"), "fields": fields}
        except Exception as e:
            raise Exception(f"Errore nel recupero DOI: {e}")

    def update_settings(self, settings: dict):
        if not self.manifest: return
        self.manifest.bib_style = settings.get("citation_style", self.manifest.bib_style)
        self.manifest.template = settings.get("template", self.manifest.template)
        # Save
        self._save_manifest_internal(self.current_project_path, self.manifest)

    def _save_manifest_internal(self, path: Path, manifest: ProjectManifest):
        # ... logic to save manifest ...
        mp = path / ".thesis_data" / "manifest.json"
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        file_path.write_text(content, encoding="utf-8")

    def rename_chapter(self, chapter: Chapter, new_title: str):
        if not self.manifest: return
        # Update model
        chapter.title = new_title
        # Save manifest
        self._save_manifest_internal(self.current_project_path, self.manifest)
        
        # Optionally update content header if it exists?
        # Let's keep it simple: just metadata rename.
        
    def delete_chapter(self, chapter: Chapter):
        if not self.manifest: return
        
        # Remove from list
        self.manifest.chapters = [c for c in self.manifest.chapters if c.id != chapter.id]
        self._save_manifest_internal(self.current_project_path, self.manifest)
        
        # Remove file
        file_path = self.current_project_path / "chapters" / chapter.filename
        if file_path.exists():
            file_path.unlink()

    def move_chapter(self, chapter: Chapter, direction: str):
        """Moves a chapter 'up' or 'down' in the list."""
        if not self.manifest: return
        
        idx = -1
        for i, c in enumerate(self.manifest.chapters):
            if c.id == chapter.id:
                idx = i
                break
        
        if idx == -1: return

        new_idx = idx
        if direction == "up" and idx > 0:
            new_idx = idx - 1
        elif direction == "down" and idx < len(self.manifest.chapters) - 1:
            new_idx = idx + 1
        
        if new_idx != idx:
            # Swap
            self.manifest.chapters[idx], self.manifest.chapters[new_idx] = self.manifest.chapters[new_idx], self.manifest.chapters[idx]
            self._save_manifest_internal(self.current_project_path, self.manifest)

    def get_chapter_content(self, chapter: Chapter) -> str:
        if not self.current_project_path:
             return ""
        path = self.current_project_path / "chapters" / chapter.filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def save_settings(self):
        """Saves the current manifest (settings) to disk."""
        if not self.current_project_path or not self.manifest:
            raise RuntimeError("No project to save.")
        self._save_manifest_internal(self.current_project_path, self.manifest)

    def _save_manifest_internal(self, project_dir: Path, manifest: ProjectManifest):
        path = project_dir / ".thesis_data" / "manifest.json"
        
        # Atomic Write
        temp_path = path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
            if path.exists():
                path.unlink() # Windows replace requires target check sometimes, shutil.move is safer or just rename
            temp_path.rename(path)
        except Exception as e:
            print(f"Error saving manifest: {e}")
            if temp_path.exists(): temp_path.unlink()
            raise e

    def add_asset(self, source_path: Path) -> str:
        """Copies an asset file to the project assets directory and returns relative path."""
        if not self.current_project_path:
            raise ValueError("No project loaded")
        
        assets_dir = self.current_project_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        dest_path = assets_dir / source_path.name
        
        # Collision handling: rename if exists
        if dest_path.exists():
            base = dest_path.stem
            ext = dest_path.suffix
            counter = 1
            while dest_path.exists():
                dest_path = assets_dir / f"{base}_{counter}{ext}"
                counter += 1
        
        # Simple copy
        import shutil
        shutil.copy2(source_path, dest_path)
        
        # Return path relative to project root (standard markdown format)
        return f"assets/{dest_path.name}"

    def export_project(self, project_path: Path, dest_zip: Path):
        """Archives the project folder to a zip file."""
        import shutil
        # make_archive works on the root_dir. 
        # project_path is c:/.../MyProject
        # we want zip to contain MyProject/... or just contents? 
        # Usually import expects a folder. Let's zip the content to keep it simple, 
        # or zip the folder itself. 
        # Best practice: zip the folder so extracting gives you the folder.
        
        base_name = str(dest_zip).replace(".zip", "")
        shutil.make_archive(base_name, 'zip', root_dir=project_path.parent, base_dir=project_path.name)

    def import_project(self, zip_path: Path) -> Path:
        """Extracts a zip project to the projects directory. Returns path to extracted project."""
        import shutil
        import zipfile
        
        # Check if valid zip
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Not a valid zip file")

        # Basic Structure Validation
        has_manifest = False
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                if "manifest.json" in name:
                    has_manifest = True
                    break
        
        if not has_manifest:
             raise ValueError("Invalid Project: manifest.json not found in archive.")

        # Destination
        dest_dir = self.projects_root
        
        # We need to handle potential naming conflicts or weird zip structures.
        # Assuming the zip contains a single root folder "MyProject/"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Inspection could be complex. Let's just extract.
            # If the user zipped the *contents* (manifest.json at root of zip), we need a folder.
            # If user zipped the *folder*, we get MyProject/manifest.json.
            
            # Heuristic: Check first file
            first = zf.infolist()[0].filename
            is_folder_packed = '/' in first and not first.startswith('__MACOSX')
            
            if is_folder_packed:
                # Extract as is
                zf.extractall(dest_dir)
                # Find what we extracted? 
                extracted_name = first.split('/')[0]
                return dest_dir / extracted_name
            else:
                # Contents packed. Create a folder based on zip name
                name = zip_path.stem
                new_project_path = dest_dir / name
                new_project_path.mkdir(exist_ok=True)
                zf.extractall(new_project_path)
                return new_project_path

    def compile_project_async(self, on_success: Callable[[Path], None], on_error: Callable[[Exception], None], on_progress: Callable[[str], None] = None):
        """Compiles the project asynchronously, including MD->Typst conversion."""
        if not self.current_project_path or not self.manifest:
             on_error(RuntimeError("No project loaded."))
             return

        from src.engine.compiler import AsyncCompiler, CompilationError
        from src.engine.pandoc_wrapper import PandocWrapper
        
        # We need to run the whole pipeline in a thread, 
        # because conversion is also blocking/slow.
        import threading
        
        def _pipeline():
            try:
                if on_progress: on_progress("Preparazione...", 0.1)
                
                # 1. Conversion Phase
                pandoc = PandocWrapper()
                temp_dir = self.current_project_path / ".thesis_data" / "temp"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                compiled_body_path = temp_dir / "compiled_body.typ"
                
                # Logic to convert chapters
                # We build a single body file or multiple files?
                # Let's build individual typst files and include them.
                
                includes = []
                
                total_chapters = len(self.manifest.chapters)
                
                for i, chapter in enumerate(self.manifest.chapters):
                    if on_progress: on_progress(f"Conversione {chapter.title}...", 0.1 + (0.5 * (i / total_chapters)))
                    
                    # 1.1 Read and Resolve Chapter Content
                    full_md = self._resolve_chapter_markdown(chapter)
                    
                    # 1.2 Convert to Typst
                    typ_filename = f"{chapter.id}.typ"
                    typ_path = temp_dir / typ_filename
                    pandoc.convert_markdown_to_typst(full_md, typ_path)
                    
                    # 1.3 Add to master body
                    includes.append(f'#include "{typ_filename}"')
                
                # Write compiled_body.typ
                compiled_body_path.write_text("\n\n".join(includes), encoding="utf-8")
                
                if on_progress: on_progress("Compilazione PDF...", 0.7)
                
                # 2. Compilation Phase
                # Use AsyncCompiler synchronously inside this thread?
                # AsyncCompiler.compile is async. 
                # We can use _compile_sync if we had access, or just use subprocess directly here since we are ALREADY in a thread.
                # Reuse AsyncCompiler logic? 
                # Let's instantiate it and call its internal sync method if possible or just replicate.
                # Better: AsyncCompiler is designed to be called from UI. 
                # ProjectManager._pipeline IS the async worker here.
                # So let's re-implement the call or make AsyncCompiler have a sync method.
                
                compiler = AsyncCompiler()
                # We can't call compile() because it spawns ANOTHER thread and returns.
                # We want to wait.
                # Let's use compiler._compile_sync (it's protected but we are internal friend-ish).
                # Or make it public.
                # Let's assume we can call _compile_sync.
                
                pdf_path = compiler._compile_sync(self.current_project_path)
                
                if on_progress: on_progress("Completato!", 1.0)
                on_success(pdf_path)
                
            except Exception as e:
                on_error(e)

        threading.Thread(target=_pipeline, daemon=True).start()

    def _resolve_chapter_markdown(self, chapter: Chapter) -> str:
        """Concatenates chapter content with its structured paragraphs."""
        if not self.current_project_path: return ""
        
        # 1. Read Master Chapter file
        md_path = self.current_project_path / "chapters" / chapter.filename
        content = md_path.read_text(encoding="utf-8") if md_path.exists() else f"# {chapter.title}\n"
        
        # 2. Append Paragraphs
        paragraph_contents = []
        for p in chapter.paragraphs:
            p_path = self.current_project_path / "chapters" / chapter.id / p.filename
            if p_path.exists():
                p_text = p_path.read_text(encoding="utf-8")
                # Ensure it starts with a proper heading if it doesn't already?
                # Actually create_paragraph adds it.
                paragraph_contents.append(p_text)
        
        if paragraph_contents:
            content += "\n\n" + "\n\n".join(paragraph_contents)
            
        return content

    def _resolve_includes(self, file_path: Path, depth=0) -> str:
        """Legacy helper for manual {{ include }} directives."""
        if depth > 5: return "" 
        if not file_path.exists(): return ""
        
        content = file_path.read_text(encoding="utf-8")
        import re
        
        def repl(match):
            inc_path_str = match.group(1)
            candidate = self.current_project_path / "chapters" / inc_path_str
            if not candidate.exists():
                return f"**Error: Check include path {inc_path_str}**"
            
            return self._resolve_includes(candidate, depth+1)
            
        return re.sub(r'\{\{\s*include:\s*(.+?)\s*\}\}', repl, content)

    # Deprecated synchronous compile
    def compile_project(self) -> Path:
        raise NotImplementedError("Use compile_project_async")

    def open_generated_pdf(self, pdf_path: Path):
        """Opens the generated PDF file with the default system viewer."""
        import os
        import platform
        import subprocess

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            if platform.system() == "Windows":
                os.startfile(pdf_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(pdf_path)], check=True)
            else:
                subprocess.run(["xdg-open", str(pdf_path)], check=True)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            # We don't raise here strictly, or we could. 
            # The UI might want to know, so let's re-raise or handle gracefully.
            raise e

    def update_settings(self, settings: dict):
        """Updates project settings and saves the manifest."""
        if not self.manifest:
            raise RuntimeError("No project loaded")
        
        # Update fields if present
        if "title" in settings: self.manifest.title = settings["title"]
        if "author" in settings: self.manifest.author = settings["author"]
        if "candidate" in settings: self.manifest.candidate = settings["candidate"]
        if "supervisor" in settings: self.manifest.supervisor = settings["supervisor"]
        if "year" in settings: self.manifest.year = settings["year"]
        if "citation_style" in settings: self.manifest.citation_style = settings["citation_style"]
        
        self.save_settings()

    def get_bibliography_content(self) -> str:
        """Reads the bibliography file content."""
        if not self.current_project_path: return ""
        bib_path = self.current_project_path / "references.bib"
        if bib_path.exists():
            return bib_path.read_text(encoding="utf-8")
        return ""

    def save_bibliography_content(self, content: str):
        """Saves content to the bibliography file."""
        if not self.current_project_path:
             raise RuntimeError("No project loaded.")
        bib_path = self.current_project_path / "references.bib"
        bib_path.write_text(content, encoding="utf-8")

    def resolve_doi(self, doi: str) -> dict:
        """Resolves a DOI to BibTeX data using Crossref."""
        import urllib.request
        import urllib.error
        import re

        url = f"https://doi.org/{doi}"
        req = urllib.request.Request(url, headers={"Accept": "application/x-bibtex"})
        
        try:
            with urllib.request.urlopen(req) as response:
                bibtex = response.read().decode("utf-8")
                return self._parse_bibtex_internal(bibtex)
        except Exception as e:
            raise RuntimeError(f"DOI Resolution failed: {e}")

    def _parse_bibtex_internal(self, bibtex: str) -> dict:
        """Parses a BibTeX string and returns a dictionary of fields."""
        import re
        data = {"type": "misc", "fields": {}}
        
        # Detect type
        m_type = re.search(r'@(\w+)\{', bibtex)
        if m_type:
            data["type"] = m_type.group(1).lower()
        
        # Helper to extract field
        def get_field(name):
            pat = rf"{name}\s*=\s*[\"{{]?(.*?)[\"}}],?\s*(?:\n|$)"
            m = re.search(pat, bibtex, re.IGNORECASE)
            return m.group(1) if m else ""
            
        data["fields"]["title"] = get_field("title")
        data["fields"]["author"] = get_field("author")
        data["fields"]["year"] = get_field("year")
        data["fields"]["publisher"] = get_field("publisher") or get_field("journal")
        data["fields"]["doi"] = get_field("doi") or get_field("url")
        data["fields"]["id"] = ""
        
        # Key
        m_key = re.search(r'@\w+\{([^,]+),', bibtex)
        if m_key:
            data["fields"]["id"] = m_key.group(1)
            
        return data

    def get_asset_markdown(self, filename: str) -> str:
        """Returns the markdown string for embedding an asset."""
        # Centralizes asset path logic
        return f"![{filename}](assets/{filename})"

    def delete_project(self, project_path: Path):
        """Deletes a project directory."""
        if not project_path.exists():
            return
            
        # Security check: must be inside projects_root
        try:
             # resolve() handles symlinks and '..'
            resolved_path = project_path.resolve()
            resolved_root = self.projects_root.resolve()
            
            if not str(resolved_path).startswith(str(resolved_root)):
                 raise PermissionError("Cannot delete projects outside the projects directory.")
                 
            if resolved_path == resolved_root:
                 raise PermissionError("Cannot delete the root projects directory.")
                 
            import shutil
            shutil.rmtree(resolved_path)
            
            if self.current_project_path == project_path:
                self.current_project_path = None
                self.manifest = None
                
        except Exception as e:
            raise RuntimeError(f"Failed to delete project: {e}")

