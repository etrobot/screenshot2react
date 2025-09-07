#!/usr/bin/env python3

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright
import aiohttp
import subprocess

async def take_screenshot(url, output_path):
    """Take a screenshot of the first screen of a webpage."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Set viewport to a standard size
            await page.set_viewport_size({"width": 1280, "height": 800})
            
            # Navigate to the URL
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for network idle
            try:
                await page.wait_for_load_state('networkidle', timeout=30000)
            except:
                print("Network idle timeout, continuing with execution...")
            
            # Additional wait time for any remaining async content
            await page.wait_for_timeout(2000)
            
            # Take screenshot of the first screen (viewport)
            await page.screenshot(path=output_path, full_page=False)
            print(f"Screenshot saved: {output_path}")
            
        except Exception as e:
            print(f"Error taking screenshot of {url}: {e}")
            return False
        finally:
            await browser.close()
    
    return True

async def process_with_gemini(image_path, output_path, api_key):
    """Process image with Gemini to remove text and generate studio photo."""
    try:
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare the API request
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [
                    {
                        "text": "remove all text and recreate it as a realistic high quality studio photo"
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": encoded_image
                        }
                    }
                ]
            }]
        }
        
        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract the base64 image data from the response
                    try:
                        image_data = result['candidates'][0]['content']['parts'][0]['data']
                        # Decode and save the image
                        image_bytes = base64.b64decode(image_data)
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        print(f"Gemini processed image saved: {output_path}")
                        return True
                    except (KeyError, IndexError, ValueError) as e:
                        print(f"Error extracting image data from Gemini response: {e}")
                        print(f"Response: {result}")
                        return False
                else:
                    print(f"Gemini API error: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return False
    except Exception as e:
        print(f"Error processing with Gemini: {e}")
        return False

async def process_url(url, output_dir, api_key):
    """Process a single URL: take screenshot and process with Gemini."""
    # Create a safe filename from the URL
    safe_name = "".join(c for c in url if c.isalnum() or c in ('-', '.', '_')).rstrip()
    screenshot_path = os.path.join(output_dir, f"{safe_name}_screenshot.png")
    gemini_path = os.path.join(output_dir, f"{safe_name}_gemini.png")
    
    print(f"\nProcessing {url}")
    
    # Take screenshot
    if await take_screenshot(url, screenshot_path):
        # Process with Gemini
        await process_with_gemini(screenshot_path, gemini_path, api_key)
    else:
        print(f"Failed to take screenshot of {url}")

async def main():
    # Check if API key is provided
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Create output directory
    output_dir = "processed_screenshots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Read URLs from file
    urls_file = "tests/url.txt"
    if not os.path.exists(urls_file):
        print(f"Error: {urls_file} not found")
        sys.exit(1)
    
    with open(urls_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} URLs to process")
    
    # Process each URL
    for url in urls:
        await process_url(url, output_dir, api_key)

if __name__ == "__main__":
    asyncio.run(main())