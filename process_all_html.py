import os
from extract_md import extract_main_content

def process_all_html_files(input_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录中的所有文件
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.html'):
                # 构建输入文件的完整路径
                input_path = os.path.join(root, file)
                
                # 构建输出文件的路径,将.html替换为.md
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path[:-5] + '.md')
                
                # 确保输出文件的目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 调用extract_main_content函数处理文件
                try:
                    extract_main_content(input_path, output_path)
                    print(f"已处理: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"处理 {input_path} 时出错: {str(e)}")

if __name__ == '__main__':
    input_directory = '/Users/mastreina/Desktop/vasp_wiki_html_240912/www.vasp.at'  # 请替换为实际的输入目录路径
    output_directory = '/Users/mastreina/Desktop/vasp_wiki_html_240912/md_all'  # 请替换为实际的输出目录路径
    process_all_html_files(input_directory, output_directory)