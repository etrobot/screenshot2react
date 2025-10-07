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


def extract_webpage_text(page):
    """
    Extract text content from webpage using the external extract_text.js file.
    
    Args:
        page: Playwright page object
        
    Returns:
        str: Extracted text content formatted for analysis
    """
    try:
        print("📊 开始提取页面文本...")
        
        # Read the external JavaScript file
        js_file_path = os.path.join(os.path.dirname(__file__), 'extract_text.js')
        
        if not os.path.exists(js_file_path):
            print(f"❌ 未找到文本提取JS文件: {js_file_path}")
            return ""
        
        with open(js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Inject the JavaScript file into the page
        page.evaluate(js_content)
        
        # Execute the text extraction function
        extracted_text = page.evaluate("""
            () => {
                if (typeof extractAndCopyText === 'function') {
                    // Use the function from extract_text.js, but return instead of copying
                    const extractor = new TextExtractor({
                        includeHidden: false,
                        minTextLength: 1,
                        maxDepth: 10
                    });
                    return extractor.extractIndentedText();
                } else {
                    return 'Text extraction function not found';
                }
            }
        """)
        
        if extracted_text and extracted_text != 'No content found' and extracted_text != 'Text extraction function not found':
            print(f"✅ 成功提取页面文本 ({len(extracted_text)} 字符)")
            return extracted_text
        else:
            print("⚠️  未能提取页面文本")
            return ""
            
    except Exception as e:
        print(f"❌ 页面文本提取失败: {str(e)}")
        return ""


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


def analyze_video_using_external_tool(video_path: str, prompt: str = None, output_dir: str = None) -> dict:
    """
    使用独立的 video_analysis.py 工具分析视频
    
    Args:
        video_path (str): 视频文件路径
        prompt (str): 分析提示词，如果为 None 使用默认值
        output_dir (str): 输出目录，如果为 None 则在视频文件同目录
    
    Returns:
        dict: 包含 'success', 'output_file', 'error' 的分析结果
    """
    try:
        # 构建命令行参数
        cmd = ['python3', 'video_analysis.py', video_path]
        
        # 添加自定义提示词（如果为 None 则让 video_analysis.py 使用默认提示词）
        if prompt is not None:
            cmd.extend(['-p', prompt])
        
        # 添加输出路径和格式
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        if output_dir:
            output_file = os.path.join(output_dir, f"{video_name}_analysis.md")
            cmd.extend(['-o', output_file])
        else:
            output_file = f"{os.path.splitext(video_path)[0]}_analysis.md"
        
        # 设置为 Markdown 格式
        cmd.extend(['--format', 'markdown'])
        
        print(f"🎬 启动视频分析: {os.path.basename(video_path)}")
        
        # 执行视频分析工具
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("✅ 视频分析完成")
            return {
                'success': True,
                'output_file': output_file,
                'error': None
            }
        else:
            error_msg = f"视频分析失败: {result.stderr or result.stdout}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'output_file': None,
                'error': error_msg
            }
            
    except subprocess.TimeoutExpired:
        error_msg = "视频分析超时 (5分钟)"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'output_file': None,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"视频分析工具调用错误: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'output_file': None,
            'error': error_msg
        }


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
    
    # Accept both URLs and file paths
    print(color_text("\n🌐 请输入要处理的内容:", Colors.CYAN))
    print(color_text("   • 单个URL (以 http:// 或 https:// 开头)", Colors.BLUE))
    print(color_text("   • 文件路径 (包含多个URL的 .txt 文件)", Colors.BLUE))
    print(color_text("   • 输入 'q' 退出程序", Colors.BLUE))
    
    while True:
        user_input = input(color_text("\n🔗 URL 或文件路径: ", Colors.BLUE)).strip()
        
        if not user_input:
            print(color_text("⚠️  请输入URL或文件路径", Colors.YELLOW))
            continue
            
        if user_input.lower() == 'q':
            print(color_text("👋 退出程序", Colors.MAGENTA))
            sys.exit(0)
        
        # Check if it's a URL
        if user_input.startswith(('http://', 'https://')):
            urls = [user_input]
            print(color_text(f"✅ 将处理单个URL: {user_input}", Colors.GREEN))
            break
        # Check if it's a file path
        elif os.path.exists(user_input):
            try:
                with open(user_input, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                # Validate that all lines are URLs
                valid_urls = []
                for url in urls:
                    if url.startswith(('http://', 'https://')):
                        valid_urls.append(url)
                    else:
                        print(color_text(f"⚠️  跳过无效URL: {url}", Colors.YELLOW))
                
                if valid_urls:
                    urls = valid_urls
                    print(color_text(f"✅ 从文件 {user_input} 读取到 {len(urls)} 个有效URL", Colors.GREEN))
                    break
                else:
                    print(color_text(f"❌ 文件 {user_input} 中没有找到有效的URL", Colors.RED))
                    continue
                    
            except Exception as e:
                print(color_text(f"❌ 无法读取文件 {user_input}: {e}", Colors.RED))
                continue
        else:
            print(color_text("❌ 请输入有效的URL（以 http:// 或 https:// 开头）或现有的文件路径", Colors.RED))
            continue
    
    # Simple defaults
    output_dir = "processed_screenshots"
    record_video = True
    
    print(color_text(f"📁 输出到: {output_dir}", Colors.GREEN))
    print(color_text(f"🎥 视频录制: {'开启' if record_video else '关闭'}", Colors.GREEN))
    
    return {
        'urls': urls,
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
    
    # Import and use the content capture functionality (no screenshots)
    from screenshot_capture import capture_website_content_no_screenshot
    
    try:
        # Capture website content with video recording and element removal options (no screenshots)
        success = capture_website_content_no_screenshot(url, screenshot_path, record_video=record_video, element_removal_options=element_removal_options)
        if success:
            print(f"✓ Successfully processed {url}")
            
            # If video recording was enabled and video analysis is requested, try to analyze the video with Gemini
            should_analyze = (record_video and 
                            element_removal_options and 
                            element_removal_options.get('analyze_video', False) and 
                            os.environ.get('GEMINI_API_KEY'))
            
            if should_analyze:
                # Look for video files in the website output directory
                video_files = []
                for ext in ['.mp4', '.webm', '.avi']:
                    video_files.extend(Path(website_output_dir).glob(f'*{ext}'))
                
                if video_files:
                    # Analyze the first video file found
                    video_file = video_files[0]
                    print(f"🎬 找到视频文件: {video_file}")
                    
                    # Check if we have extracted webpage text to include in the prompt
                    webpage_text = element_removal_options.get('extracted_text', '') if element_removal_options else ''
                    
                    if webpage_text:
                        print("📄 将网页文本内容加入视频分析提示词")
                        # Use DEFAULT_ANALYSIS_PROMPT from video_analysis.py + webpage text
                        enhanced_prompt = f"""{webpage_text}

Describe the layout and scrolling motion for frontend programming section by section, like:

1. Hero:
   - Layout:
   - Images:
   - Scrolling motion:
...
x. Footer:
   - Layout:
   - Images:
   - Scrolling motion:
   
Note: For each section, please provide specific details about the layout structure, any images or visual elements, and how the page behaves during scrolling (e.g., parallax effects, fade-ins, etc.)."""
                        video_prompt = enhanced_prompt
                    else:
                        # No webpage text, let video_analysis.py use its DEFAULT_ANALYSIS_PROMPT
                        video_prompt = None
                    
                    # Use external video analysis tool
                    analysis_result = analyze_video_using_external_tool(
                        str(video_file), 
                        prompt=video_prompt,
                        output_dir=website_output_dir
                    )
                    
                    if analysis_result['success']:
                        print(f"✅ 视频分析已保存到: {analysis_result['output_file']}")
                    else:
                        print(f"❌ 视频分析失败: {analysis_result['error']}")
                else:
                    print("⚠️  未找到视频文件，跳过视频分析")
            elif record_video and element_removal_options and element_removal_options.get('analyze_video', False) and not os.environ.get('GEMINI_API_KEY'):
                print("⚠️  GEMINI_API_KEY 未设置，跳过视频分析")
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
        description='🌐 Extract information from webpages: video recording, DOM, text, and element removal (NO SCREENSHOTS)',
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
    parser.add_argument('--analyze-video', action='store_true',
                       help='Enable video analysis with Gemini API (requires GEMINI_API_KEY)')
    parser.add_argument('--video-prompt', default="请详细分析这个网站滚动视频，包括：1) 主要内容和布局总结，2) 关键视觉元素和设计模式，3) 用户体验观察。",
                       help='视频分析的自定义提示词 (默认: 综合分析)')
    
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
            'delay': 2.0,
            'analyze_video': bool(os.environ.get('GEMINI_API_KEY')),  # Auto-enable if API key exists
            'video_prompt': "请详细分析这个网站滚动视频，包括：1) 主要内容和布局总结，2) 关键视觉元素和设计模式，3) 用户体验观察。"
        }
        
        print("✅ 使用默认元素移除设置:")
        print("   • 移除Framer元素")
        print("   • 移除常见不需要元素（广告、Cookie横幅等）")
        if os.environ.get('GEMINI_API_KEY'):
            print("   • 🎬 视频分析已启用 (Gemini API)")
        else:
            print("   • ⚠️  视频分析需要 GEMINI_API_KEY 环境变量")
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
            'delay': args.delay,
            'analyze_video': args.analyze_video or bool(os.environ.get('GEMINI_API_KEY')),  # Auto-enable if API key exists or explicitly requested
            'video_prompt': args.video_prompt
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
        
        # Display video analysis status
        print("🎬 Video analysis:")
        if element_removal_options.get('analyze_video', False):
            if os.environ.get('GEMINI_API_KEY'):
                print("  ✅ Video analysis enabled (Gemini API)")
            else:
                print("  ⚠️  Video analysis requested but GEMINI_API_KEY not set")
        else:
            print("  ❌ Video analysis disabled")
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