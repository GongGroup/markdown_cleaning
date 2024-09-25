import os
import json
from bs4 import BeautifulSoup
import html2text

def extract_main_content(html_content):
    """
    提取 HTML 中的主要内容。
    """
    soup = BeautifulSoup(html_content, 'lxml')

    # 提取<title>
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else 'No Title'

    # 提取<h1>标题
    h1_tag = soup.find('h1', id='firstHeading')
    h1 = h1_tag.get_text(strip=True) if h1_tag else 'No Heading'

    # 提取主要内容区域
    content_div = soup.find('div', id='mw-content-text')
    if not content_div:
        return title, h1, 'No Content Found'

    # 如果页面是重定向，提取重定向目标
    redirect_div = content_div.find('div', class_='redirectMsg')
    if redirect_div:
        redirect_text = redirect_div.get_text(separator='\n', strip=True)
        return title, h1, redirect_text

    # 提取所有可见的内容
    # 可以根据需要进一步筛选或处理特定的子元素
    main_content = content_div.get_text(separator='\n', strip=True)

    return title, h1, main_content

def convert_html_to_markdown(html_content):
    """
    将 HTML 内容转换为 Markdown 格式。
    """
    h = html2text.HTML2Text()
    h.ignore_links = False  # 保留链接
    h.ignore_images = False  # 保留图片
    h.ignore_emphasis = False  # 保留强调
    markdown = h.handle(html_content)
    return markdown

def process_html_file(input_path, output_path, convert_to_md=False):
    """
    处理单个 HTML 文件，提取主要内容并保存。
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        html_content = infile.read()

    title, h1, main_content = extract_main_content(html_content)

    # 组织为 JSON 结构
    record = {
        "title": title,
        "heading": h1,
        "content": main_content
    }

    # 转换为 Markdown（可选）
    if convert_to_md:
        markdown_content = convert_html_to_markdown(main_content)
        record["content_markdown"] = markdown_content

    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(record, outfile, ensure_ascii=False, indent=2)

    print(f"Processed {input_path} -> {output_path}")

def batch_process_html(input_dir, output_dir, convert_to_md=False):
    """
    批量处理指定目录中的所有 HTML 文件。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.html') or filename.lower().endswith('.htm'):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.json'
            output_path = os.path.join(output_dir, output_filename)
            process_html_file(input_path, output_path, convert_to_md)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="提取 HTML 中的主要内容并转换为 JSON 或 Markdown。")
    parser.add_argument('--input_dir', type=str, required=True, help="输入 HTML 文件所在目录。")
    parser.add_argument('--output_dir', type=str, required=True, help="输出 JSON 文件保存目录。")
    parser.add_argument('--convert_to_md', action='store_true', help="是否将内容转换为 Markdown。")
    args = parser.parse_args()

    batch_process_html(args.input_dir, args.output_dir, args.convert_to_md)