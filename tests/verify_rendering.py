from src.utils.html_renderer import HTMLRenderer
from src.ui.theme import Theme
from pathlib import Path
import os

def test_html_rendering():
    # Mock project path
    project_path = Path("C:/Users/gabri/APP/Studio/Thesisflow/test_project")
    
    md_test = """
# Test Header
This is a **bold** and *italic* text.

| Column 1 | Column 2 |
| -------- | -------- |
| Value 1  | Value 2  |

- Item 1
    - Subitem 1.1
- Item 2

![Local Image](assets/image.png)
    """
    
    # Test Dark Mode
    Theme.set_mode(Theme.MODE_DARK)
    html_dark = HTMLRenderer.render(md_test, project_path)
    
    # Check for CSS colors (Slate 950 equivalent for Dark BG)
    assert "#0b1016" in html_dark or "background-color" in html_dark
    assert "file:///C:/Users/gabri/APP/Studio/Thesisflow/test_project/assets/image.png" in html_dark
    assert "<table>" in html_dark
    assert "<ul>" in html_dark
    
    # Test Light Mode
    Theme.set_mode(Theme.MODE_LIGHT)
    html_light = HTMLRenderer.render(md_test, project_path)
    
    # Check for CSS colors (White/Slate 50 for Light BG)
    assert "#f8fafc" in html_light or "#ffffff" in html_light
    
    print("HTMLRenderer verification passed!")

if __name__ == "__main__":
    try:
        test_html_rendering()
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
