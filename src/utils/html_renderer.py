import markdown2
from src.ui.theme import Theme
from pathlib import Path

class HTMLRenderer:
    @staticmethod
    def get_styles() -> str:
        """Generates a CSS <style> block based on the current Theme."""
        bg = Theme.COLOR_BG
        text = Theme.TEXT_MAIN
        text_dim = Theme.TEXT_DIM
        accent = Theme.COLOR_ACCENT
        font = Theme.FONT_FAMILY
        
        return f"""
        <style>
            body {{
                background-color: {bg};
                color: {text};
                font-family: {font}, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                margin: 20px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {accent};
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            h1 {{ font-size: 1.8em; border-bottom: 1px solid {Theme.COLOR_BORDER}; padding-bottom: 0.3em; }}
            h2 {{ font-size: 1.5em; }}
            h3 {{ font-size: 1.2em; }}
            
            code {{
                background-color: {Theme.COLOR_PANEL};
                padding: 2px 4px;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            pre {{
                background-color: {Theme.COLOR_PANEL};
                padding: 10px;
                border-radius: 6px;
                overflow-x: auto;
                border: 1px solid {Theme.COLOR_BORDER};
            }}
            blockquote {{
                border-left: 4px solid {accent};
                margin: 0;
                padding-left: 15px;
                color: {text_dim};
                font-style: italic;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid {Theme.COLOR_BORDER};
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: {Theme.COLOR_PANEL_HOVER};
            }}
            img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                margin: 10px 0;
            }}
            a {{
                color: {accent};
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            hr {{
                border: 0;
                border-top: 1px solid {Theme.COLOR_BORDER};
                margin: 20px 0;
            }}
            ul, ol {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 0.5em;
            }}
        </style>
        """

    @classmethod
    def render(cls, md_text: str, project_path: Path = None) -> str:
        """Converts markdown to full HTML string with styles."""
        import re
        
        # Pre-process image paths: ![alt](relative/path) -> ![alt](file:///absolute/path)
        processed_md = md_text
        if project_path:
            def replace_path(match):
                alt = match.group(1)
                rel_path = match.group(2)
                # Skip if already absolute or URL
                if rel_path.startswith(("http://", "https://", "file://", "/")):
                    return match.group(0)
                
                abs_path = (project_path / rel_path).resolve().as_posix()
                return f'![{alt}](file:///{abs_path})'
            
            processed_md = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_path, md_text)

        # Enable GFM extras
        extras = ["tables", "fenced-code-blocks", "task_list", "header-ids", "metadata"]
        
        html_content = markdown2.markdown(processed_md, extras=extras)
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            {cls.get_styles()}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        return full_html
