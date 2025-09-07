#!/usr/bin/env python3

import asyncio
import os
import sys
from playwright.async_api import async_playwright
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes


def convert_css_to_tailwind(css):
    """
    Convert CSS styles to Tailwind CSS classes using the convert_css.js script.
    
    Args:
        css (str): CSS style string to convert
        
    Returns:
        str: Space-separated Tailwind CSS classes, or empty string if conversion fails
    """
    process = subprocess.Popen(
        ['node', 'convert_css.js'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(css)
    if process.returncode != 0:
        print(f"Error converting CSS: {stderr}")
        return ""
    
    # Strip whitespace and return the converted classes
    return stdout.strip()


async def screenshot_sections(url, output_dir, selector='section'):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Navigate to the URL with a longer timeout
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Wait for network idle with a longer timeout
        try:
            await page.wait_for_load_state('networkidle', timeout=60000)
        except:
            print("Network idle timeout, continuing with execution...")
        
        # Improved scrolling to load all dynamic content
        print("Scrolling to load dynamic content...")
        previous_height = -1
        stable_count = 0
        while stable_count < 3:  # Wait for height to be stable for 3 checks
            # Scroll to bottom
            await page.evaluate('() => window.scrollTo(0, document.body.scrollHeight)')

            # Wait for a bit to let content load
            await page.wait_for_timeout(2000)

            # Get current page height
            current_height = await page.evaluate('() => document.body.scrollHeight')

            if current_height == previous_height:
                stable_count += 1
                print(f"Page height stable at {current_height}px ({stable_count}/3)")
            else:
                stable_count = 0
                print(f"Page height changed to {current_height}px")

            previous_height = current_height

            # Also break if we've scrolled a lot (safety measure)
            if previous_height > 100000:  # 100k pixels
                print("Reached max scroll height limit.")
                break
        print("Finished scrolling.")
        
        # Additional wait time for any remaining async content
        await page.wait_for_timeout(3000)
        
        # Debug: Print available elements
        element_count = await page.evaluate(f'() => document.querySelectorAll("{selector}").length')
        print(f"Found {element_count} elements matching selector '{selector}'")
        
        # Find all matching elements
        elements = await page.query_selector_all(selector)
        
        # If no elements found, try common container selectors
        if len(elements) == 0:
            common_selectors = ['div', '.container', '.content', '.card', '.panel', 'article']
            for common_selector in common_selectors:
                elements = await page.query_selector_all(common_selector)
                if len(elements) > 0:
                    print(f"Found {len(elements)} elements using alternative selector '{common_selector}'")
                    selector = common_selector
                    break
        
        print(f"Found {len(elements)} elements")
        
        # Screenshot each element and save its HTML content
        for i, element in enumerate(elements):
            try:
                # Check if element is still attached to the DOM
                is_attached = await element.is_visible()
                if not is_attached:
                    print(f'Skipped detached element {i+1}')
                    continue
                    
                # Get the HTML content of the element
                html_content = await element.inner_html()
                
                # Check if element has content before screenshotting
                has_content = len(html_content.strip()) > 0
                if has_content:
                    # Scroll element into view
                    await element.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)  # Wait for scroll animation

                    # Save screenshot of the viewport
                    # screenshot_filename = os.path.join(output_dir, f'element_{i+1}.png')
                    # await page.screenshot(path=screenshot_filename)
                    # print(f'Saved screenshot: {screenshot_filename}')
                    
                    soup = BeautifulSoup(html_content, 'lxml')

                    # Download images and update src attributes
                    img_tags = soup.find_all('img')
                    for j, img_tag in enumerate(img_tags):
                        if 'src' in img_tag.attrs:
                            img_url = img_tag['src']
                            if not img_url or img_url.startswith('data:'):
                                continue

                            absolute_img_url = urljoin(page.url, img_url)

                            try:
                                response = await page.request.get(absolute_img_url)
                                if response.ok:
                                    image_data = await response.body()
                                    
                                    content_type = response.headers.get('content-type')
                                    ext = mimetypes.guess_extension(content_type) if content_type else ''
                                    
                                    if not ext:
                                        parsed_url = urlparse(absolute_img_url)
                                        path_parts = os.path.splitext(parsed_url.path)
                                        ext = path_parts[1] if len(path_parts) > 1 else ''

                                    image_filename = f'element_{i+1}_img_{j+1}{ext or ".jpg"}'
                                    image_path = os.path.join(output_dir, image_filename)
                                    
                                    with open(image_path, 'wb') as f:
                                        f.write(image_data)
                                    
                                    print(f'Saved image: {image_path}')
                                    
                                    img_tag['src'] = image_filename
                                else:
                                    print(f"Failed to download image: {absolute_img_url} (status: {response.status})")

                            except Exception as e:
                                print(f"Error downloading image {absolute_img_url}: {e}")
                    
                    # Convert inline styles to Tailwind CSS
                    for tag in soup.find_all(style=True):
                        style = tag['style']
                        tailwind_classes = convert_css_to_tailwind(style)
                        if tailwind_classes:
                            tag['class'] = tag.get('class', []) + tailwind_classes.split()
                        del tag['style']

                    # Remove all <path> elements
                    for path_tag in soup.find_all('path'):
                        path_tag.decompose()
                    
                    modified_html = soup.prettify()

                    # Save HTML content
                    html_filename = os.path.join(output_dir, f'element_{i+1}.html')
                    with open(html_filename, 'w', encoding='utf-8') as f:
                        f.write(modified_html)
                    print(f'Saved HTML: {html_filename}')
                else:
                    print(f'Skipped empty element {i+1}')
            except Exception as e:
                print(f'Error processing element {i+1}: {e}')
                continue
        
        await browser.close()


def main():
    if len(sys.argv) != 3:
        print('Usage: python section_screenshots.py <URL> <output_directory>')
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2]
    
    asyncio.run(screenshot_sections(url, output_dir))


if __name__ == '__main__':
    main()