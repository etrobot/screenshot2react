#!/usr/bin/env python3

"""
Screenshot capture module with video recording functionality.
Handles browser automation, scrolling, and video generation.
"""

import os
import subprocess
import time
import tempfile
import shutil
import random
from playwright.sync_api import sync_playwright


def create_video_from_frames_sync(frames_dir, output_path, frame_count):
    """Create MP4 video from PNG frames using ffmpeg (synchronous version)."""
    try:
        print(f"Creating video from {frame_count} frames...")
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: ffmpeg not found. Please install ffmpeg to create videos.")
            print("Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)")
            return False
        
        # Create video using ffmpeg
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-framerate', '12',  # 12 fps for 3x faster viewing (1/3 duration)
            '-i', os.path.join(frames_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',  # Good quality
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Video successfully created: {output_path}")
            return True
        else:
            print(f"Error creating video: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error in create_video_from_frames_sync: {e}")
        return False


def remove_unwanted_elements(page, options=None):
    """Remove unwanted elements from the page based on options."""
    try:
        selectors_to_remove = []
        
        # Always remove scripts and noscripts for cleaner capture
        selectors_to_remove.extend(['script', 'noscript'])
        
        if options:
            # Add Framer-specific elements if requested
            if options.get('remove_framer', False):
                framer_selectors = [
                    'div.ssr-variant',
                    'div#__framer-badge-container'
                ]
                selectors_to_remove.extend(framer_selectors)
                print("  → Removing Framer elements (ssr-variant, __framer-badge-container)")
            
            # Add common unwanted elements if requested
            if options.get('remove_common_unwanted', False):
                common_unwanted = [
                    '.advertisement',
                    '.ads',
                    '.cookie-banner',
                    '.gdpr-banner',
                    '#cookie-notice',
                    '.popup-overlay',
                    '.modal-overlay',
                    '[id*="cookie"]',
                    '[class*="cookie"]',
                    '[id*="gdpr"]',
                    '[class*="gdpr"]',
                    '.tracking-consent'
                ]
                selectors_to_remove.extend(common_unwanted)
                print("  → Removing common unwanted elements (ads, cookies, popups)")
            
            # Add custom selectors if provided
            if options.get('custom_selectors'):
                selectors_to_remove.extend(options['custom_selectors'])
                print(f"  → Removing custom elements: {', '.join(options['custom_selectors'])}")
        
        # Remove elements
        removed_count = 0
        for selector in selectors_to_remove:
            try:
                result = page.evaluate(f'''() => {{
                    const elements = document.querySelectorAll("{selector}");
                    elements.forEach(el => el.remove());
                    return elements.length;
                }}''')
                removed_count += result
            except Exception as e:
                pass  # Ignore errors for individual selectors
        
        if removed_count > 0:
            print(f"  → Removed {removed_count} unwanted elements")
        else:
            print("  → No unwanted elements found to remove")
                
    except Exception as e:
        print(f"Error removing unwanted elements: {e}")


def record_scrolling_video_sync(page, video_output_path):
    """Record a video of the scrolling process with natural human-like scrolling rhythm."""
    try:
        print("🎥 开始录制自然滚动视频...")
        
        # Get viewport dimensions
        viewport = page.viewport_size
        viewport_height = viewport["height"]
        
        # Get total page height
        total_height = page.evaluate('() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight)')
        print(f"Total page height: {total_height}px, Viewport height: {viewport_height}px")
        
        # Show progress for long pages
        if total_height > viewport_height * 3:
            print("📏 页面较长，开始录制滚动视频...")
        
        # Disable smooth scrolling and scroll-snap to prevent micro jitter during capture
        try:
            page.add_style_tag(content='html, body { scroll-behavior: auto !important; overscroll-behavior: none !important; } * { scroll-snap-type: none !important; }')
        except Exception:
            pass
        
        # Skip video recording if page is too short
        if total_height <= viewport_height * 1.5:
            print("Page is too short for meaningful video recording, skipping...")
            return True
        
        # Create temporary directory for video frames
        temp_dir = tempfile.mkdtemp()
        print(f"Created temp directory: {temp_dir}")
        
        try:
            frames = []
            current_scroll = 0
            frame_count = 0

            
            # Wait 3 seconds before starting to allow websites to fully load
            print("⏳ 等待网站加载完成 (3秒)...")
            time.sleep(3)
            
            # Take multiple frames at the beginning (staying still)
            for i in range(12):  # ~1s at 12fps
                frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
                page.screenshot(path=frame_path)
                frames.append(frame_path)
                frame_count += 1
            
            # Calculate scroll step - one viewport height for natural scrolling
            scroll_step = viewport_height - 100  # Slight overlap
            
            # Compute maximum scroll top to avoid bouncing at the bottom
            max_scroll_top = max(0, int(total_height) - int(viewport_height))

            # One-time quick wheel tick to trigger wheel-dependent rendering
            try:
                page.mouse.wheel(0, 60)
                time.sleep(0.005)  # 5ms as requested
            except Exception:
                pass

            while current_scroll < max_scroll_top - 2:

                # Compute segment target using viewport step with overlap
                target_scroll = min(current_scroll + scroll_step, max_scroll_top)

                # Per-frame eased programmatic progression (record during motion)
                seg_duration_ms = random.randint(800, 1100)  # ~0.8s-1.1s per segment
                frame_interval_s = random.uniform(0.07, 0.09)  # 70–90ms between frames
                frames_in_segment = max(8, int(seg_duration_ms / int(frame_interval_s * 1000)))

                start_y = current_scroll
                distance = max(0, target_scroll - start_y)
                if distance <= 0:
                    break

                for i in range(1, frames_in_segment + 1):
                    t = i / frames_in_segment
                    # easeOutCubic
                    eased = 1 - pow(1 - t, 3)
                    y = int(round(start_y + distance * eased))
                    page.evaluate(f'() => window.scrollTo(0, {y})')
                    # Capture each eased step to include smooth motion in the video
                    frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
                    page.screenshot(path=frame_path)
                    frames.append(frame_path)
                    frame_count += 1
                    time.sleep(frame_interval_s)

                    # Early stop if we already reached or very close to target
                    if y >= target_scroll - 1:
                        break

                # Update current scroll position (rounded to integer px)
                actual_scroll = int(page.evaluate('() => Math.round(window.pageYOffset)'))
                
                # Break if we can't scroll further
                if actual_scroll == current_scroll:
                    print("Cannot scroll further, ending video recording")
                    break
                
                current_scroll = actual_scroll
                
                # Stay still for ~1 second（段落阅读停顿）
                pause_frames = 12  # 12 frames ≈ 1 second at 12fps
                for i in range(pause_frames):
                    frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
                    page.screenshot(path=frame_path)
                    frames.append(frame_path)
                    frame_count += 1
                
                # Safety limit (allow longer capture at 12fps)
                if frame_count > 360:
                    print("⚠️  达到最大帧数限制 (360)")
                    break
                
                # Show progress for long scrolling
                if total_height > viewport_height * 3 and frame_count % 30 == 0:
                    progress = min(100, int((current_scroll / total_height) * 100))
                    # Use color-coded progress based on percentage
                    if progress < 30:
                        color_code = "\033[93m"  # Yellow
                    elif progress < 70:
                        color_code = "\033[96m"  # Cyan
                    else:
                        color_code = "\033[92m"  # Green
                    
                    progress_bar = "[" + "=" * (progress // 5) + " " * (20 - progress // 5) + "]"
                    print(f"📊 滚动进度: {color_code}{progress_bar} {progress}%\033[0m ({current_scroll}/{total_height}px)")
                
                # Show first scroll notification
                if current_scroll > 0 and not hasattr(record_scrolling_video_sync, '_first_scroll_shown'):
                    print("🔄 开始第一次滚动...")
                    record_scrolling_video_sync._first_scroll_shown = True
            
            # Take final frames at the bottom
            for i in range(12):  # ~1s at bottom for 12fps
                frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
                page.screenshot(path=frame_path)
                frames.append(frame_path)
                frame_count += 1
            
            # Removed debug output for cleaner interface
            
            # Create video from frames using ffmpeg
            if frames and len(frames) > 1:
                return create_video_from_frames_sync(temp_dir, video_output_path, frame_count)
            else:
                print("Not enough frames to create video")
                return True
                
        finally:
            # Clean up temporary directory
            print(f"Cleaning up temp directory: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)
                
    except Exception as e:
        print(f"Error recording scrolling video: {e}")
        import traceback
        traceback.print_exc()
        return False


def take_full_page_screenshot_sync(page, output_path, record_video=True):
    """Take a full page screenshot with scrolling and optional video recording (synchronous version)."""
    try:
        # Get the total height of the page
        total_height = page.evaluate("() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
        viewport_height = page.evaluate("() => window.innerHeight")
        
        print(f"Page total height: {total_height}px, viewport height: {viewport_height}px")
        
        # Record video first if requested
        video_success = True
        if record_video:
            video_output_path = output_path.replace('.png', '_scroll_video.mp4')
            print("Recording scrolling video...")
            video_success = record_scrolling_video_sync(page, video_output_path)
            if video_success:
                print(f"Scrolling video saved: {video_output_path}")
            else:
                print("Video recording failed, but continuing with screenshot")
        
        # Scroll down the page in steps to trigger lazy loading using mouse wheel
        current_position = 0
        scroll_step = viewport_height // 2  # Scroll half viewport at a time
        
        while current_position < total_height:
            # Use mouse wheel for more realistic scrolling that triggers wheel events
            target_position = min(current_position + scroll_step, total_height)
            wheel_distance = target_position - current_position
            
            # Perform wheel scrolling in smaller, smoother increments
            wheel_increments = max(1, int(wheel_distance / 50))  # Scroll in ~50px increments for smoother motion
            increment_size = wheel_distance / wheel_increments
            
            for i in range(wheel_increments):
                page.mouse.wheel(0, increment_size)
                time.sleep(0.05)  # Faster, smoother wheel events
            
            time.sleep(2)  # Wait for content to load after scrolling
            current_position = target_position
            
            # Update total height in case new content was loaded
            new_total_height = page.evaluate("() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            if new_total_height > total_height:
                total_height = new_total_height
                print(f"Page height increased to: {total_height}px")
        
        # Scroll back to top using mouse wheel
        current_scroll = page.evaluate("() => window.pageYOffset")
        if current_scroll > 0:
            # Scroll back to top with smooth wheel events
            wheel_increments = max(1, int(current_scroll / 80))  # Scroll up in ~80px increments for smoother motion
            increment_size = current_scroll / wheel_increments
            
            for i in range(wheel_increments):
                page.mouse.wheel(0, -increment_size)  # Negative for scrolling up
                time.sleep(0.03)  # Even faster for scrolling back up
        
        time.sleep(1)
        
        # Take the full page screenshot
        page.screenshot(path=output_path, full_page=True)
        print(f"Screenshot saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False


def get_main_content_dom(page):
    """Extract the main content DOM from the page."""
    try:
        # Try common main content selectors
        main_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '#main-content',
            '.content',
            '#content',
            'body > div:first-child',  # Often the main container
            'body'  # Fallback to body
        ]
        
        main_content = None
        selector_used = None
        
        for selector in main_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                main_content = elements[0].inner_html()
                selector_used = selector
                print(f"Found main content using selector: {selector}")
                break
        
        if not main_content:
            # Fallback to body content
            main_content = page.evaluate('() => document.body.innerHTML')
            selector_used = 'body'
            print("Using body content as fallback")
        
        return main_content, selector_used
        
    except Exception as e:
        print(f"Error extracting main content DOM: {e}")
        return None, None


def capture_website_content_no_screenshot(url, output_path, record_video=True, element_removal_options=None):
    """
    Main function to capture website content including DOM, text, and optional video (NO SCREENSHOTS).
    
    Args:
        url (str): The URL to capture
        output_path (str): Base path for output files (used to generate video and DOM file names)
        record_video (bool): Whether to record scrolling video
        element_removal_options (dict): Options for element removal with timeout and delay
        
    Returns:
        bool: True if successful, False otherwise
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--proxy-server=http://127.0.0.1:7890',  # Use proxy for network access
                '--disable-web-security',  # Better compatibility
                '--window-size=1280,960',  # Set consistent window size
                '--force-device-scale-factor=1'  # Set zoom level to 100%
            ]
        )
        page = browser.new_page()
        
        try:
            # Set page timeout from options or default to 30 seconds
            timeout_ms = (element_removal_options.get('timeout', 30) * 1000) if element_removal_options else 30000
            page.set_default_timeout(timeout_ms)
            
            # Set viewport to 1280x960 (4:3 aspect ratio, consistent with window size)
            page.set_viewport_size({"width": 1280, "height": 960})
            
            # Navigate to the URL with configurable timeout
            goto_timeout = (element_removal_options.get('timeout', 60) * 1000) if element_removal_options else 60000
            page.goto(url, wait_until='domcontentloaded', timeout=goto_timeout)
            
            # Start video recording immediately after page loads
            video_success = True
            if record_video:
                video_output_path = output_path.replace('.png', '_scroll_video.mp4')
                print("Starting immediate video recording after page load...")
                video_success = record_scrolling_video_sync(page, video_output_path)
                if video_success:
                    print(f"Scrolling video saved: {video_output_path}")
                else:
                    print("Video recording failed, but continuing with screenshot")
            
            # Wait for network idle after video recording
            try:
                page.wait_for_load_state('networkidle', timeout=60000)
            except:
                print("Network idle timeout, continuing with execution...")
            
            # Wait extra time for complex JavaScript rendering and animations
            delay_seconds = element_removal_options.get('delay', 2.0) if element_removal_options else 5.0
            print(f"Waiting {delay_seconds:.1f}s for page to fully render...")
            time.sleep(delay_seconds)  # Configurable delay for rendering
            
            # Remove unwanted DOM elements before processing
            print("Removing unwanted DOM elements...")
            remove_unwanted_elements(page, element_removal_options)
            
            # Extract webpage text content for video analysis
            try:
                from extract_info_from_webpage import extract_webpage_text
                extracted_text = extract_webpage_text(page)
                if extracted_text and element_removal_options is not None:
                    element_removal_options['extracted_text'] = extracted_text
                    print("✅ 页面文本已提取并准备用于视频分析")
            except Exception as e:
                print(f"⚠️  文本提取过程中出现错误: {e}")
            
            # Process content without taking screenshots
            print("Processing content without screenshots...")
            content_success = True
            
            if content_success:
                # Get main content DOM
                main_content, selector_used = get_main_content_dom(page)
                
                if main_content:
                    # Import here to avoid circular imports
                    from extract_info_from_webpage import convert_css_to_tailwind
                    from bs4 import BeautifulSoup
                    
                    # Save DOM content with inline CSS converted to Tailwind
                    dom_output_path = output_path.replace('.png', '_dom.html')
                    soup = BeautifulSoup(main_content, 'html.parser')
                    
                    # Convert inline styles to Tailwind classes
                    for tag in soup.find_all(style=True):
                        style = tag.get('style', '')
                        if style:
                            tailwind_classes = convert_css_to_tailwind(style)
                            if tailwind_classes:
                                tag['class'] = tag.get('class', []) + tailwind_classes.split()
                        if 'style' in tag.attrs:
                            del tag['style']
                    
                    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Extracted Main Content</title>
    <meta name="selector-used" content="{selector_used}">
</head>
<body>
{soup.prettify()}
</body>
</html>"""
                    with open(dom_output_path, 'w', encoding='utf-8') as f:
                        f.write(html_doc)
                    
                    print(f"DOM content saved: {dom_output_path}")
                    print(f"Content extracted using selector: {selector_used}")
            
            return content_success
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return False
        finally:
            browser.close()