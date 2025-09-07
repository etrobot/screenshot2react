# Screenshot to React Converter

This tool converts screenshots of web pages into React components by:
1. Taking screenshots of sections in a web page
2. Converting CSS styles to Tailwind CSS classes
3. Generating clean HTML files that can be used in React projects

## Features

- Takes screenshots of web page sections using Playwright
- Converts CSS styles to Tailwind CSS classes
- Downloads images and updates image references
- Generates clean HTML output

## Installation

1. Install Python dependencies:
   ```
   pip install -e .
   ```

2. Install Node.js dependencies for CSS conversion:
   ```
   npm install
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

## Usage

1. Run the screenshot tool:
   ```
   python section_screenshots.py <URL> <output_directory>
   ```

2. View the generated HTML files in the frontend:
   ```
   cd frontend
   npm run dev
   ```

## Testing

Run tests with:
```
python -m pytest tests/
```