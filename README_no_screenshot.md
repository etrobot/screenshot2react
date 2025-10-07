# 网页内容提取工具 (无截图版本)

这是原始截图工具的简化版本，**移除了所有截图和视频录制功能**，专注于网页内容的提取和处理。

## 🚀 主要功能

✅ **保留的功能：**
- 📄 提取网页DOM结构并保存为HTML文件
- 📝 提取网页文本内容并保存为TXT文件
- 🎨 将内联CSS样式转换为Tailwind CSS类
- 🗑️ 移除不需要的元素（广告、Cookie横幅、Framer元素等）
- 📁 为每个网站创建单独的文件夹组织输出

❌ **移除的功能：**
- 📸 网页截图
- 🎥 滚动视频录制
- 🎬 视频分析 (Gemini API)

## 📦 安装依赖

```bash
# 安装Python依赖
pip install playwright beautifulsoup4

# 安装Playwright浏览器
playwright install chromium

# 确保有Node.js环境 (用于CSS转换)
node --version
```

## 🛠️ 使用方法

### 基本用法

```bash
# 处理单个URL
python process_content.py https://example.com

# 处理多个URL (从文件读取)
python process_content.py urls.txt

# 指定输出目录
python process_content.py https://example.com -o my_content
```

### 元素移除选项

```bash
# 移除Framer特定元素
python process_content.py https://framer.site --remove-framer

# 移除所有常见不需要元素
python process_content.py https://example.com --remove-all-unwanted

# 使用自定义CSS选择器移除元素
python process_content.py https://example.com --custom-selectors ".ad-banner" "#popup"
```

### 高级选项

```bash
# 设置页面加载超时和等待时间
python process_content.py https://example.com --timeout 60 --delay 5.0
```

## 📂 输出结构

工具会为每个网站创建一个单独的文件夹：

```
extracted_content/
├── example_com/
│   ├── example_com_content_dom.html    # DOM结构 (带Tailwind类)
│   └── example_com_content_text.txt    # 提取的文本内容
├── github_com_user_repo/
│   ├── github_com_user_repo_content_dom.html
│   └── github_com_user_repo_content_text.txt
└── ...
```

## 🔧 与原版本的对比

| 功能 | 原版本 (extract_info_from_webpage.py) | 新版本 (process_content.py) |
|------|--------------------------------|----------------------------|
| 网页截图 | ✅ | ❌ 已移除 |
| 视频录制 | ✅ | ❌ 已移除 |
| 视频分析 | ✅ (需要API) | ❌ 已移除 |
| DOM提取 | ✅ | ✅ |
| 文本提取 | ✅ | ✅ |
| CSS转换 | ✅ | ✅ |
| 元素移除 | ✅ | ✅ |
| 处理速度 | 较慢 (截图+视频) | 更快 (仅内容) |
| 存储空间 | 大 (图片+视频) | 小 (仅文本) |

## 💡 使用场景

这个无截图版本适合以下场景：

- 🕷️ **网页内容爬取**: 只需要获取网页的文本和DOM结构
- 🔍 **SEO分析**: 分析网页的文本内容和结构
- 📊 **内容审计**: 批量检查多个网页的内容
- 🎨 **样式提取**: 获取网页的CSS样式并转换为Tailwind
- ⚡ **快速处理**: 需要快速处理大量网页而不需要视觉效果

## 🚫 何时不适用

如果您需要以下功能，请使用原版本：

- 📸 保存网页的视觉截图
- 🎥 录制页面滚动效果
- 🎬 AI分析视频内容
- 🖼️ 视觉设计参考

## 📝 示例输出

### DOM文件 (example_com_content_dom.html)
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Extracted Content from https://example.com</title>
    <meta name="source-url" content="https://example.com">
    <meta name="selector-used" content="main">
    <meta name="extraction-time" content="2024-01-15 10:30:45">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <!-- 提取的DOM内容，内联样式已转换为Tailwind类 -->
</body>
</html>
```

### 文本文件 (example_com_content_text.txt)
```
网页标题
  导航菜单项1
  导航菜单项2
主要内容区域
  段落1内容...
  段落2内容...
页脚信息
```

这样您就可以专注于内容提取，而不需要处理截图文件的存储和管理！