#!/usr/bin/env python3
"""
将 Markdown 文件转换为 PDF
使用 markdown + weasyprint
"""

import markdown
from weasyprint import HTML, CSS
import sys
from pathlib import Path


def md_to_pdf(md_file, pdf_file=None):
    """将 Markdown 文件转换为 PDF"""

    md_path = Path(md_file)
    if not md_path.exists():
        print(f"错误: 文件不存在 {md_file}")
        return False

    # 如果未指定 PDF 文件名，使用同名
    if pdf_file is None:
        pdf_file = md_path.with_suffix(".pdf")

    print(f"正在转换: {md_path.name}")
    print(f"输出到: {pdf_file}")

    # 读取 Markdown 内容
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 转换为 HTML
    html_content = markdown.markdown(
        md_content, extensions=["tables", "fenced_code", "toc", "nl2br"]
    )

    # 添加 CSS 样式
    css_style = """
    @page {
        size: A4;
        margin: 2.5cm;
        @bottom-center {
            content: counter(page);
            font-size: 10pt;
        }
    }
    
    body {
        font-family: "Noto Sans CJK SC", "WenQuanYi Micro Hei", "Microsoft YaHei", sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }
    
    h1 {
        color: #2c3e50;
        font-size: 24pt;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 0;
    }
    
    h2 {
        color: #34495e;
        font-size: 18pt;
        border-bottom: 2px solid #bdc3c7;
        padding-bottom: 8px;
        margin-top: 25px;
    }
    
    h3 {
        color: #7f8c8d;
        font-size: 14pt;
        margin-top: 20px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10pt;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }
    
    th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        font-size: 10pt;
    }
    
    pre {
        background-color: #f4f4f4;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        border-left: 4px solid #3498db;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 15px 0;
        padding: 10px 20px;
        background-color: #ecf0f1;
        font-style: italic;
    }
    
    hr {
        border: none;
        border-top: 2px solid #ecf0f1;
        margin: 25px 0;
    }
    
    strong {
        color: #2c3e50;
    }
    
    em {
        color: #7f8c8d;
    }
    """

    # 包装 HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{md_path.stem}</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # 转换为 PDF
    try:
        HTML(string=full_html).write_pdf(pdf_file, stylesheets=[CSS(string=css_style)])
        print(f"✓ 转换成功: {pdf_file}")
        return True
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 md_to_pdf.py <markdown文件> [pdf文件]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = md_to_pdf(md_file, pdf_file)
    sys.exit(0 if success else 1)
