import sys
from pathlib import Path

# Add the current directory to the path so we can import section_screenshots
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import os

# Import the functions we want to test
from section_screenshots import screenshot_sections

async def test_lyniq_website():
    """Test the screenshot_sections function with the Lyniq website."""
    
    # Create a permanent directory for output
    perm_dir = "lyniq_output"
    os.makedirs(perm_dir, exist_ok=True)
    
    # URL of the Lyniq website
    url = "https://lyniq.framer.website"
    
    print(f"Testing screenshot_sections with {url}")
    print(f"Output will be saved to {perm_dir}")
    
    try:
        # Run the screenshot function
        await screenshot_sections(url, perm_dir)
        
        # Check what files were created
        output_files = list(Path(perm_dir).glob('*'))
        html_files = list(Path(perm_dir).glob('*.html'))
        
        print(f"\nTest completed! Files saved in {perm_dir}")
        print(f"Total files: {len(output_files)}")
        print(f"HTML files: {len(html_files)}")
        
        # List the generated files
        print("\nGenerated files:")
        for file in output_files:
            print(f"  - {file.name}")
            
        # Show content of one HTML file as example
        if html_files:
            print(f"\nExample content from {html_files[0].name}:")
            with open(html_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
                # Show first 500 characters
                print(content[:500] + "..." if len(content) > 500 else content)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_lyniq_website())