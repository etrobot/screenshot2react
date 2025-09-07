import sys
from pathlib import Path

# Add the current directory to the path so we can import section_screenshots
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import os
import tempfile
from playwright.async_api import async_playwright

# Import the functions we want to test
from section_screenshots import screenshot_sections

def test_screenshot_sections():
    """Test the screenshot_sections function with a simple HTML page."""
    
    # Create a permanent directory for output screenshots
    perm_dir = "test_screenshots_output"
    os.makedirs(perm_dir, exist_ok=True)
    
    # Test HTML content with multiple sections
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <section>
            <h1>Section 1</h1>
            <p>This is the first section</p>
        </section>
        <section>
            <h1>Section 2</h1>
            <p>This is the second section</p>
        </section>
        <section>
            <h1>Section 3</h1>
            <p>This is the third section</p>
        </section>
    </body>
    </html>
    """
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_html_file = f.name
    
    try:
        # Run the screenshot function
        asyncio.run(screenshot_sections(f'file://{temp_html_file}', perm_dir))
        
        # Check that screenshots were created
        screenshot_files = list(Path(perm_dir).glob('section_*.png'))
        assert len(screenshot_files) == 3, f"Expected 3 screenshots, got {len(screenshot_files)}"
        
        # Check that each screenshot file exists
        for i in range(1, 4):
            screenshot_path = Path(perm_dir) / f'section_{i}.png'
            assert screenshot_path.exists(), f"Screenshot {screenshot_path} does not exist"
        
        print(f"All tests passed! Screenshots saved in {perm_dir}")
        
    finally:
        # Clean up the temporary HTML file
        os.unlink(temp_html_file)

if __name__ == '__main__':
    test_screenshot_sections()