import os
import json

def md_to_jsonl(folder_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as jsonl_file:
        for filename in os.listdir(folder_path):
            if filename.endswith('.md'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as md_file:
                    content = md_file.read()
                    
                    # 创建JSON对象
                    json_obj = {
                        "file_name": filename,
                        "content": content
                    }
                    
                    # 将JSON对象写入.jsonl文件
                    jsonl_file.write(json.dumps(json_obj) + '\n')

# 使用脚本
folder_path = '/Users/mastreina/Desktop/vasp_wiki_html_240912/md_all/wiki'  # 替换为您的md文件所在的文件夹路径
output_file = 'vaspwiki_website.jsonl'  # 输出的.jsonl文件名

md_to_jsonl(folder_path, output_file)
print(f"已将所有md文件合并到 {output_file}")