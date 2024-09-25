from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re

def custom_md(html):
    # 自定义转换函数
    markdown = md(html)
    
    # 删除所有数学公式，包括 {\\displaystyle ...} 和单独的字母公式
    markdown = re.sub(r'\{\\displaystyle.*?\}', '', markdown, flags=re.DOTALL)
    markdown = re.sub(r'E\s*d\s*i\s*s\s*p', '', markdown, flags=re.DOTALL)
    
    # 删除图片链接
    markdown = re.sub(r'!\[.*?\]\(.*?\)', '', markdown, flags=re.DOTALL)
    
    # 删除超链接，只保留链接文本
    markdown = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown)
    
    # 删除"Retrieved from"行及其后的URL
    markdown = re.sub(r'\nRetrieved from.*', '', markdown, flags=re.DOTALL)
    
    # 删除多余的空行
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    # 合并只有不超过三个字母和其他有效字符的行，同时删除被合并行中的所有空格
    lines = markdown.split('\n')
    merged_lines = []
    for line in lines:
        if len(line.strip()) <= 3 and merged_lines:
            merged_lines[-1] += ' ' + line.strip()
        else:
            merged_lines.append(line)
    markdown = '\n'.join(merged_lines)
    
    # 再次删除可能残留的单个字母行
    markdown = re.sub(r'\n[A-Za-z]\n', '\n', markdown)
    
    # 优化公式中的空格，使其成为正确的 LaTeX 公式
    def fix_latex_spaces(match):
        formula = match.group(1)
        fixed_formula = re.sub(r'\s+', '', formula)
        return '{\\displaystyle ' + fixed_formula + '}'
    
    markdown = re.sub(r'\{\\displaystyle\s*(.*?)\}', fix_latex_spaces, markdown, flags=re.DOTALL)
    
    # 删除从 "References" 或 "Related tags and articles" 开始到文档末尾的所有内容
    markdown = re.sub(r'(References|Related tags and articles).*$', '', markdown, flags=re.DOTALL | re.IGNORECASE)
    
    return markdown.strip()  # 使用strip()去除首尾的空白字符

def extract_main_content(html_path, markdown_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    content = soup.find('div', id='mw-content-text')
    markdown = custom_md(str(content))
    with open(markdown_path, 'w', encoding='utf-8') as file:
        file.write(markdown)

if __name__ == '__main__':
    extract_main_content('www.vasp.at/wiki/index.php/IVDW.html', 'IVDW.md')