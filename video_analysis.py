#!/usr/bin/env python3
"""
独立的视频分析工具 - 使用 Gemini API 分析视频内容
支持通过代理访问 API，专门用于分析网站录制的视频
"""

import os
import sys
import argparse
import base64
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional

# ANSI 颜色代码
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

def color_text(text: str, color_code: str) -> str:
    """给文本添加颜色"""
    return f"{color_code}{text}{Colors.END}"


def analyze_video_with_gemini(
    video_path: str, 
    prompt: str = "请分析这个视频并提供详细描述。", 
    api_key: Optional[str] = None,
    proxy_url: str = "http://127.0.0.1:7890",
    model: str = "gemini-2.0-flash-exp"
) -> Dict:
    """
    使用 Google Gemini API 分析视频文件
    
    Args:
        video_path (str): 视频文件路径
        prompt (str): 分析提示词
        api_key (str, optional): Gemini API 密钥，如果为 None 则从环境变量获取
        proxy_url (str): 代理服务器地址
        model (str): 使用的 Gemini 模型
    
    Returns:
        Dict: 包含 'success', 'content', 'error', 'metadata' 的分析结果
    """
    if api_key is None:
        api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        return {
            'success': False,
            'content': '',
            'error': 'GEMINI_API_KEY 环境变量未设置',
            'metadata': {}
        }
    
    if not os.path.exists(video_path):
        return {
            'success': False,
            'content': '',
            'error': f'视频文件不存在: {video_path}',
            'metadata': {}
        }
    
    try:
        print(f"🎬 {color_text('开始分析视频', Colors.CYAN)}: {video_path}")
        
        # 获取文件信息
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size_mb > 20:  # Gemini API 限制
            return {
                'success': False,
                'content': '',
                'error': f'视频文件过大: {file_size_mb:.1f}MB (限制: 20MB)',
                'metadata': {'file_size_mb': file_size_mb}
            }
        
        print(f"📊 文件大小: {file_size_mb:.1f}MB")
        
        # 编码视频为 base64
        print("🔄 编码视频文件...")
        with open(video_path, 'rb') as video_file:
            video_data = base64.b64encode(video_file.read()).decode('utf-8')
        
        # 准备 API 请求
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "video/mp4",
                            "data": video_data
                        }
                    },
                    {"text": prompt}
                ]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 8192,
            }
        }
        
        # 配置代理
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        } if proxy_url else None
        
        print(f"🌐 {color_text('发送请求到 Gemini API', Colors.BLUE)} (通过代理: {proxy_url})")
        print(f"🤖 使用模型: {model}")
        
        # 发送 API 请求
        start_time = time.time()
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            proxies=proxies,
            timeout=120  # 增加超时时间
        )
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # 提取分析内容
            if 'candidates' in result and result['candidates']:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    content = candidate['content']['parts'][0].get('text', '')
                    
                    metadata = {
                        'file_size_mb': file_size_mb,
                        'request_time_seconds': round(request_time, 2),
                        'model': model,
                        'prompt_length': len(prompt),
                        'response_length': len(content)
                    }
                    
                    print(f"✅ {color_text('视频分析完成', Colors.GREEN)} ({request_time:.1f}s)")
                    return {
                        'success': True,
                        'content': content,
                        'error': None,
                        'metadata': metadata
                    }
            
            return {
                'success': False,
                'content': '',
                'error': f'API 响应格式异常: {result}',
                'metadata': {'response': result}
            }
        else:
            error_msg = f"API 请求失败 (状态码 {response.status_code}): {response.text}"
            print(f"❌ {color_text(error_msg, Colors.RED)}")
            return {
                'success': False,
                'content': '',
                'error': error_msg,
                'metadata': {'status_code': response.status_code}
            }
            
    except requests.exceptions.ProxyError as e:
        error_msg = f"代理连接失败: {str(e)}"
        print(f"❌ {color_text(error_msg, Colors.RED)}")
        return {
            'success': False,
            'content': '',
            'error': error_msg,
            'metadata': {}
        }
    except requests.exceptions.Timeout as e:
        error_msg = f"请求超时: {str(e)}"
        print(f"❌ {color_text(error_msg, Colors.RED)}")
        return {
            'success': False,
            'content': '',
            'error': error_msg,
            'metadata': {}
        }
    except Exception as e:
        error_msg = f"视频分析错误: {str(e)}"
        print(f"❌ {color_text(error_msg, Colors.RED)}")
        return {
            'success': False,
            'content': '',
            'error': error_msg,
            'metadata': {}
        }


def save_analysis_result(analysis_result: Dict, video_path: str, output_file: Optional[str] = None, format_type: str = "markdown") -> str:
    """
    保存分析结果到文件
    
    Args:
        analysis_result (Dict): 分析结果
        video_path (str): 原始视频文件路径
        output_file (str, optional): 输出文件路径，如果为 None 则自动生成
        format_type (str): 输出格式 ("markdown" 或 "txt")
    
    Returns:
        str: 输出文件路径
    """
    # 确保输出文件在与视频相同的目录
    video_dir = os.path.dirname(os.path.abspath(video_path))
    video_name = Path(video_path).stem
    
    if output_file is None:
        if format_type == "markdown":
            output_file = os.path.join(video_dir, f"{video_name}_analysis.md")
        else:
            output_file = os.path.join(video_dir, f"{video_name}_analysis.txt")
    else:
        # 如果指定了输出文件但没有目录，放在视频目录
        if not os.path.dirname(output_file):
            output_file = os.path.join(video_dir, output_file)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if format_type == "markdown":
                # Markdown 格式
                f.write("# 🎬 视频分析报告\n\n")
                
                # 基本信息
                f.write("## 📋 基本信息\n\n")
                f.write(f"- **📁 视频文件**: `{os.path.basename(video_path)}`\n")
                f.write(f"- **📅 分析时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **🎯 分析状态**: {'✅ 成功' if analysis_result['success'] else '❌ 失败'}\n\n")
                
                # 元数据
                if 'metadata' in analysis_result and analysis_result['metadata']:
                    f.write("## 📊 分析元数据\n\n")
                    f.write("| 项目 | 值 |\n")
                    f.write("|------|----|\n")
                    for key, value in analysis_result['metadata'].items():
                        f.write(f"| {key} | {value} |\n")
                    f.write("\n")
                
                # 分析结果或错误信息
                if analysis_result['success']:
                    f.write("## 📝 分析结果\n\n")
                    f.write(analysis_result['content'])
                    f.write("\n\n")
                else:
                    f.write("## ❌ 错误信息\n\n")
                    f.write("```\n")
                    f.write(analysis_result['error'])
                    f.write("\n```\n\n")
                
                # 工具信息
                f.write("---\n\n")
                f.write("*🔗 生成工具: video_analysis.py*\n")
                
            else:
                # 纯文本格式（原有格式）
                f.write("🎬 视频分析报告\n")
                f.write("=" * 60 + "\n\n")
                
                # 基本信息
                f.write(f"📁 视频文件: {os.path.basename(video_path)}\n")
                f.write(f"📅 分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"🎯 分析状态: {'✅ 成功' if analysis_result['success'] else '❌ 失败'}\n\n")
                
                # 元数据
                if 'metadata' in analysis_result and analysis_result['metadata']:
                    f.write("📊 分析元数据:\n")
                    f.write("-" * 30 + "\n")
                    for key, value in analysis_result['metadata'].items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                # 分析结果或错误信息
                if analysis_result['success']:
                    f.write("📝 分析结果:\n")
                    f.write("-" * 30 + "\n")
                    f.write(analysis_result['content'])
                    f.write("\n\n")
                else:
                    f.write("❌ 错误信息:\n")
                    f.write("-" * 30 + "\n")
                    f.write(analysis_result['error'])
                    f.write("\n\n")
                
                f.write("🔗 生成工具: video_analysis.py\n")
        
        print(f"💾 {color_text('分析结果已保存', Colors.GREEN)}: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ {color_text(f'保存文件失败: {str(e)}', Colors.RED)}")
        return ""


def find_video_files(directory: str) -> List[str]:
    """
    在指定目录中查找视频文件
    
    Args:
        directory (str): 目录路径
    
    Returns:
        List[str]: 视频文件路径列表
    """
    video_extensions = ['.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv']
    video_files = []
    
    path = Path(directory)
    if path.is_file():
        if path.suffix.lower() in video_extensions:
            return [str(path)]
        else:
            return []
    
    for ext in video_extensions:
        video_files.extend(path.glob(f'*{ext}'))
        video_files.extend(path.glob(f'**/*{ext}'))  # 递归搜索
    
    return [str(f) for f in video_files]


def main():
    parser = argparse.ArgumentParser(
        description='🎬 独立视频分析工具 - 使用 Gemini API 分析视频内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s video.mp4
  %(prog)s video.mp4 -p "分析网站的用户界面设计"
  %(prog)s video_folder/ --batch
  %(prog)s video.mp4 --model gemini-2.0-flash-exp
  %(prog)s video.mp4 --proxy http://127.0.0.1:7890

环境变量:
  GEMINI_API_KEY    Gemini API 密钥 (必需)

支持的视频格式: .mp4, .webm, .avi, .mov, .mkv, .flv
"""
    )
    
    parser.add_argument('input', help='视频文件路径或包含视频文件的目录')
    parser.add_argument('-p', '--prompt', 
                       default="请详细分析这个视频，包括：1) 主要内容和布局总结，2) 关键视觉元素和设计模式，3) 用户体验观察。",
                       help='分析提示词 (默认: 综合分析)')
    parser.add_argument('-o', '--output', help='输出文件路径 (可选，默认自动生成)')
    parser.add_argument('--model', default='gemini-2.0-flash-exp',
                       help='Gemini 模型 (默认: %(default)s)')
    parser.add_argument('--proxy', default='http://127.0.0.1:7890',
                       help='代理服务器地址 (默认: %(default)s)')
    parser.add_argument('--no-proxy', action='store_true',
                       help='禁用代理')
    parser.add_argument('--batch', action='store_true',
                       help='批量处理目录中的所有视频文件')
    parser.add_argument('--api-key', help='Gemini API 密钥 (也可通过环境变量 GEMINI_API_KEY 设置)')
    parser.add_argument('--format', choices=['markdown', 'txt'], default='markdown',
                       help='输出文件格式 (默认: %(default)s)')
    
    args = parser.parse_args()
    
    # 显示工具信息
    print(f"\n🎬 {color_text('独立视频分析工具', Colors.MAGENTA + Colors.BOLD)}")
    print("=" * 60)
    
    # 检查 API 密钥
    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print(f"❌ {color_text('错误: 未设置 GEMINI_API_KEY', Colors.RED)}")
        print("   设置方法: export GEMINI_API_KEY=your_api_key")
        print("   或使用: --api-key your_api_key")
        sys.exit(1)
    
    # 配置代理
    proxy_url = None if args.no_proxy else args.proxy
    
    # 查找视频文件
    if os.path.isfile(args.input):
        video_files = [args.input]
        print(f"📁 处理单个文件: {args.input}")
    elif os.path.isdir(args.input):
        if not args.batch:
            print(f"❌ {color_text('输入是目录，请使用 --batch 进行批量处理', Colors.RED)}")
            sys.exit(1)
        video_files = find_video_files(args.input)
        print(f"📁 在目录中找到 {len(video_files)} 个视频文件")
    else:
        print(f"❌ {color_text(f'文件或目录不存在: {args.input}', Colors.RED)}")
        sys.exit(1)
    
    if not video_files:
        print(f"❌ {color_text('未找到视频文件', Colors.RED)}")
        sys.exit(1)
    
    # 显示配置
    print(f"\n⚙️  配置信息:")
    print(f"   🤖 模型: {args.model}")
    print(f"   🌐 代理: {proxy_url or '禁用'}")
    print(f"   📝 提示词长度: {len(args.prompt)} 字符")
    print(f"   📊 文件数量: {len(video_files)}")
    print()
    
    # 处理视频文件
    success_count = 0
    start_time = time.time()
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n📦 [{i}/{len(video_files)}] 处理: {color_text(os.path.basename(video_file), Colors.CYAN)}")
        print("-" * 50)
        
        # 分析视频
        result = analyze_video_with_gemini(
            video_file, 
            prompt=args.prompt,
            api_key=api_key,
            proxy_url=proxy_url,
            model=args.model
        )
        
        # 保存结果
        if result['success']:
            output_file = args.output if len(video_files) == 1 else None
            save_analysis_result(result, video_file, output_file, format_type=args.format)
            success_count += 1
            print(f"✅ {color_text('处理完成', Colors.GREEN)}")
        else:
            print(f"❌ {color_text('处理失败', Colors.RED)}: {result['error']}")
    
    # 显示总结
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"🎉 {color_text('批量处理完成', Colors.MAGENTA + Colors.BOLD)}")
    print(f"   ⏱️  总耗时: {total_time:.1f}s")
    print(f"   📊 成功率: {success_count}/{len(video_files)} ({success_count/len(video_files)*100:.1f}%)")
    
    if success_count == len(video_files):
        print(f"✅ {color_text('全部处理成功！', Colors.GREEN)}")
        sys.exit(0)
    elif success_count > 0:
        print(f"⚠️  {color_text('部分成功', Colors.YELLOW)}: {len(video_files) - success_count} 个文件失败")
        sys.exit(1)
    else:
        print(f"❌ {color_text('全部失败！', Colors.RED)}")
        sys.exit(1)


if __name__ == "__main__":
    main()