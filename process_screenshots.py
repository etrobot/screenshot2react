#!/usr/bin/env python3

import os
import sys
import subprocess
import time
from pathlib import Path

# ANSI color codes for colored output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def color_text(text, color_code):
    return f"{color_code}{text}{Colors.END}"


def convert_css_to_tailwind(css: str) -> str:
    """
    Convert CSS styles to Tailwind CSS classes using the convert_css.js script.
    Returns a space-separated string of Tailwind classes, or empty string on failure.
    """
    try:
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
        return (stdout or "").strip()
    except Exception as e:
        print(f"convert_css_to_tailwind error: {e}")
        return ""


def get_user_preferences():
    """Get user preferences for element removal through interactive prompts."""
    print("\n" + "="*60)
    print("🎯 ELEMENT REMOVAL OPTIONS")
    print("="*60)
    
    preferences = {
        'remove_framer': False,
        'remove_common_unwanted': False,
        'remove_custom': False,
        'custom_selectors': []
    }
    
    # Ask about Framer elements
    print("\n📋 1. Framer-specific elements:")
    print("   • div.ssr-variant (SSR variant overlays)")
    print("   • div#__framer-badge-container (Framer badges)")
    
    while True:
        choice = input("   ❓ Remove Framer elements? (y/N): ").lower().strip()
        if choice in ['y', 'yes', '']:
            preferences['remove_framer'] = True
            print("   ✅ Framer elements will be removed")
            break
        elif choice in ['n', 'no']:
            print("   ❌ Framer elements will be kept")
            break
        else:
            print("   ⚠️  Please enter 'y' or 'n'")
    
    # Ask about common unwanted elements
    print("\n📋 2. Common unwanted elements:")
    print("   • Advertisements (.ads, .advertisement)")
    print("   • Cookie banners (.cookie-banner, #cookie-notice)")
    print("   • GDPR notices (.gdpr-banner)")
    print("   • Popup overlays (.popup-overlay, .modal-overlay)")
    print("   • Tracking consent (.tracking-consent)")
    
    while True:
        choice = input("   ❓ Remove common unwanted elements? (y/N): ").lower().strip()
        if choice in ['y', 'yes', '']:
            preferences['remove_common_unwanted'] = True
            print("   ✅ Common unwanted elements will be removed")
            break
        elif choice in ['n', 'no']:
            print("   ❌ Common unwanted elements will be kept")
            break
        else:
            print("   ⚠️  Please enter 'y' or 'n'")
    
    # Ask about custom selectors
    print("\n📋 3. Custom CSS selectors:")
    while True:
        choice = input("   ❓ Add custom CSS selectors to remove? (y/N): ").lower().strip()
        if choice in ['y', 'yes']:
            preferences['remove_custom'] = True
            print("   💡 Enter CSS selectors one by one (press Enter with empty line to finish):")
            while True:
                selector = input("   🎯 Selector: ").strip()
                if not selector:
                    if preferences['custom_selectors']:
                        print("   ✅ Finished adding custom selectors")
                    else:
                        print("   ❌ No custom selectors added")
                    break
                preferences['custom_selectors'].append(selector)
                print(f"   ➕ Added: {selector}")
            break
        elif choice in ['n', 'no', '']:
            print("   ❌ Custom selectors disabled")
            break
        else:
            print("   ⚠️  Please enter 'y' or 'n'")
    
    return preferences


def get_interactive_input():
    """Get user input interactively without command line arguments."""
    print("\n" + "="*60)
    print(color_text("🎮 完全交互模式", Colors.MAGENTA + Colors.BOLD))
    print("="*60)
    
    # Simple single URL input for now
    print(color_text("\n🌐 请输入要处理的网站URL:", Colors.CYAN))
    
    while True:
        url = input(color_text("🔗 URL: ", Colors.BLUE)).strip()
        
        if not url:
            print(color_text("⚠️  请输入URL", Colors.YELLOW))
            continue
            
        if url.lower() == 'q':
            print(color_text("👋 退出程序", Colors.MAGENTA))
            sys.exit(0)
            
        if url.startswith(('http://', 'https://')):
            break
        else:
            print(color_text("❌ 请输入有效的URL（以 http:// 或 https:// 开头）", Colors.RED))
    
    # Simple defaults
    output_dir = "processed_screenshots"
    record_video = True
    
    print(color_text(f"✅ 将处理: {url}", Colors.GREEN))
    print(color_text(f"📁 输出到: {output_dir}", Colors.GREEN))
    print(color_text(f"🎥 视频录制: {'开启' if record_video else '关闭'}", Colors.GREEN))
    
    return {
        'urls': [url],
        'output_dir': output_dir,
        'record_video': record_video
    }


def process_url(url, base_output_dir, record_video=True, element_removal_options=None):
    """
    Process a single URL by creating a dedicated folder and taking screenshots.
    Each website gets its own organized folder instead of dumping everything in root directory.
    
    Args:
        url (str): The URL to process
        base_output_dir (str): Base output directory
        record_video (bool): Whether to record scrolling video
        element_removal_options (dict): Options for element removal
    """
    # Create a safe filename from the URL by extracting domain and path
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    
    # Extract domain without protocol
    domain = parsed_url.netloc.replace('www.', '')
    
    # Extract path and clean it
    path = parsed_url.path.strip('/').replace('/', '_')
    
    # Combine domain and path, then clean for filesystem
    if path:
        folder_name = f"{domain}_{path}"
    else:
        folder_name = domain
    
    # Remove or replace invalid filename characters
    safe_folder_name = "".join(c if c.isalnum() or c in ('-', '.', '_') else '_' for c in folder_name)
    safe_folder_name = safe_folder_name.strip('_').replace('__', '_')  # Clean up multiple underscores
    
    # Create individual folder for this website to keep things organized
    website_output_dir = os.path.join(base_output_dir, safe_folder_name)
    os.makedirs(website_output_dir, exist_ok=True)
    
    screenshot_path = os.path.join(website_output_dir, f"{safe_folder_name}_full_page.png")
    
    print(f"\n🌐 正在处理: {url}")
    print(f"📁 输出文件夹: {website_output_dir}")
    
    # Show processing steps
    if record_video:
        print("🎥 将录制滚动视频")
    if element_removal_options and (element_removal_options.get('remove_framer') or element_removal_options.get('remove_common_unwanted')):
        print("🗑️  将移除不需要的元素")
    
    # Import and use the screenshot capture functionality
    from screenshot_capture import capture_website_content
    
    try:
        # Capture website content with optional video recording and element removal options
        success = capture_website_content(url, screenshot_path, record_video=record_video, element_removal_options=element_removal_options)
        if success:
            print(f"✓ Successfully processed {url}")
        else:
            print(f"✗ Failed to process {url}")
        return success
    except Exception as e:
        print(f"✗ Error processing {url}: {e}")
        return False
    

def main():    
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='🌐 Process websites with screenshots, video recording, and element removal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s urls.txt -o my_screenshots
  %(prog)s https://framer.site --remove-framer --no-video
  %(prog)s websites.txt -i
  %(prog)s (直接回车进入完全交互模式)

Interactive mode (-i) allows you to choose which elements to remove during processing.
"""
    )
    parser.add_argument('input', nargs='?', help='URL to process or path to .txt file containing URLs (one per line)')
    parser.add_argument('-o', '--output', default='processed_screenshots', 
                       help='Output directory (default: %(default)s)')
    parser.add_argument('--no-video', action='store_true', 
                       help='Disable video recording (faster processing)')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Enable interactive mode for element removal options')
    parser.add_argument('--remove-framer', action='store_true', 
                       help='Remove Framer-specific elements (ssr-variant, __framer-badge-container)')
    parser.add_argument('--remove-all-unwanted', action='store_true', 
                       help='Remove all common unwanted elements (ads, cookies, GDPR banners, etc.)')
    parser.add_argument('--custom-selectors', nargs='+', metavar='SELECTOR',
                       help='Custom CSS selectors to remove (space-separated)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Page load timeout in seconds (default: %(default)s)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay after page load before screenshot (default: %(default)s)')
    
    # Check if no arguments provided - enter full interactive mode
    if len(sys.argv) == 1:
        print("🎮 进入完全交互模式...")
        interactive_config = get_interactive_input()
        urls = interactive_config['urls']
        output_dir = interactive_config['output_dir']
        record_video = interactive_config['record_video']
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # In full interactive mode, skip detailed element removal options
        # and use simple defaults
        element_removal_options = {
            'remove_framer': True,  # Default to removing Framer elements
            'remove_common_unwanted': True,  # Default to removing common unwanted
            'remove_custom': False,
            'custom_selectors': [],
            'timeout': 30,
            'delay': 2.0
        }
        
        print("✅ 使用默认元素移除设置:")
        print("   • 移除Framer元素")
        print("   • 移除常见不需要元素（广告、Cookie横幅等）")
        print()
        
    else:
        # Parse command line arguments
        args = parser.parse_args()
        
        if not args.input:
            print("❌ 错误: 需要提供URL或文件路径")
            print("   使用 --help 查看使用方法")
            sys.exit(1)
        
        # Create output directory
        output_dir = args.output
        os.makedirs(output_dir, exist_ok=True)
        
        record_video = not args.no_video
        
        # Determine element removal options
        element_removal_options = {
            'remove_framer': False,
            'remove_common_unwanted': False,
            'remove_custom': False,
            'custom_selectors': [],
            'timeout': args.timeout,
            'delay': args.delay
        }
        
        # Handle element removal options
        if args.interactive:
            print("🎮 Starting interactive mode...")
            element_removal_options = get_user_preferences()
        else:
            # Use command line flags
            element_removal_options['remove_framer'] = args.remove_framer
            element_removal_options['remove_common_unwanted'] = args.remove_all_unwanted
            
            # Handle custom selectors from command line
            if args.custom_selectors:
                element_removal_options['remove_custom'] = True
                element_removal_options['custom_selectors'] = args.custom_selectors
                print(f"🔧 Custom selectors from CLI: {', '.join(args.custom_selectors)}")
        
        # Determine if input is URL or file
        urls = []
        if args.input.startswith(('http://', 'https://')):
            # Single URL
            urls = [args.input]
            print(f"🔗 Processing single URL: {args.input}")
        else:
            # File path
            urls_file = args.input
            if not os.path.exists(urls_file):
                print(f"❌ Error: {urls_file} not found")
                sys.exit(1)
            
            with open(urls_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(f"📄 Found {len(urls)} URLs to process from {urls_file}")
    
    if not urls:
        print("❌ No URLs to process")
        sys.exit(1)
    
    # Display features enabled (only in command line mode)
    if len(sys.argv) > 1:
        print(f"📁 Output directory: {output_dir}")
        print("🚀 Features enabled:")
        print("  ✅ 1920x1080 resolution")
        print("  ✅ Headless mode for better performance") 
        print("  ✅ Organized folder structure per website")
        print("  ✅ DOM extraction with CSS-to-Tailwind conversion")
        
        # Use record_video instead of args.no_video
        if not record_video:
            print("  ❌ Video recording disabled")
        else:
            print("  ✅ Video recording enabled (requires ffmpeg)")
        
        # Display element removal status
        print("🗑️  Element removal options:")
        if element_removal_options['remove_framer']:
            print("  ✅ Framer elements (ssr-variant, __framer-badge-container)")
        else:
            print("  ❌ Framer elements")
        
        if element_removal_options['remove_common_unwanted']:
            print("  ✅ Common unwanted elements (ads, cookies, popups)")
        else:
            print("  ❌ Common unwanted elements")
        
        if element_removal_options['custom_selectors']:
            print(f"  ✅ Custom selectors: {', '.join(element_removal_options['custom_selectors'])}")
        else:
            print("  ❌ Custom selectors")
        print()
    else:
        # Simplified display for full interactive mode
        print(f"\n📊 配置汇总:")
        print(f"   📁 输出目录: {output_dir}")
        print(f"   🎥 视频录制: {'✅ 开启' if record_video else '❌ 关闭'}")
        print(f"   🌐 处理URL数量: {len(urls)}")
        print()
    
    # Process each URL with enhanced progress display
    success_count = 0
    start_time = time.time()
    
    print("🚦 Starting processing...")
    print("-" * 60)
    
    for i, url in enumerate(urls, 1):
        url_start = time.time()
        print(f"\n📦 [{i}/{len(urls)}] Processing: {url}")
        
        success = process_url(url, output_dir, record_video=record_video, element_removal_options=element_removal_options)
        
        url_duration = time.time() - url_start
        if success:
            success_count += 1
            print(f"✅ Completed in {url_duration:.1f}s - {success_count}/{i} successful")
        else:
            print(f"❌ Failed in {url_duration:.1f}s - {success_count}/{i} successful")
    
    total_duration = time.time() - start_time
    print("-" * 60)
    print(f"\n🎉 Processing complete!") 
    print(f"   Total time: {total_duration:.1f}s")
    print(f"   Success rate: {success_count}/{len(urls)} URLs")
    
    if success_count == len(urls):
        print(f"✅ All {success_count} URLs processed successfully!")
    elif success_count > 0:
        print(f"⚠️  Partial success: {success_count} succeeded, {len(urls) - success_count} failed")
        print(f"   Failed URLs: {len(urls) - success_count}")
        sys.exit(1)
    else:
        print(f"❌ All {len(urls)} URLs failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()