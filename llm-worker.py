import os
import json
import requests
from tqdm import tqdm
import time

# 配置
INPUT_DIR = 'new'        # 输入 JSON 文件所在目录
OUTPUT_DIR = 'md_new'         # 输出清洗后 Markdown 文件的目录
API_ENDPOINT = 'https://api.gonggroup.in/v1/chat/completions'  # OpenAI API 端点
API_KEY = os.getenv('OPENAI_API_KEY')  # 从环境变量中获取 API 密钥

# 速率限制配置
MAX_TOKENS_PER_MINUTE = 200000  # 每分钟最大 token 数
TOKENS_USED_IN_CURRENT_MINUTE = 0
START_TIME = time.time()

# 待处理文件列表
PENDING_FILES_PATH = 'pending_files.json'

# 检查 API_KEY 是否存在
if not API_KEY:
    raise ValueError("API_KEY 未设置。请在环境变量中设置 OPENAI_API_KEY。")

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 定义优化后的提示模板（英文版本）
COMBINED_PROMPT_TEMPLATE = """
Please review the following VASP Markdown content and clean and format it for inclusion in a large language model's training corpus. Perform the following tasks:

1. **Format Correction**: Ensure the Markdown syntax is correct and fix any formatting errors.
2. **LaTeX Equation Standardization**:
    - Use `$$` to enclose block-level equations.
    - Ensure the equation is on a single line without unnecessary line breaks or carriage returns.
    - Verify that the LaTeX syntax is correct and compatible with Typora rendering.
    - Remove any unnecessary spaces or line breaks within the equation to enhance readability.
3. **Remove Irrelevant Markers**: Eliminate all unnecessary markers, such as `\\n`.
4. **Exclude Specific Sections**: Remove sections that contain phrases like `examples that use this tag` and `reference`.

Please provide the cleaned and formatted Markdown content without any additional explanations or text.

Content:
---
{content}
---
"""

def load_pending_files():
    """
    加载待处理文件列表。如果不存在，则根据输入目录和输出目录的差异创建。
    """
    input_files = set([f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.json') or f.lower().endswith('.jsonl')])
    output_files = set([os.path.splitext(f)[0] + '.md' for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.md')])
    
    # 从输出文件中获取已经完成的 JSON 文件名（不含扩展名）
    completed = set([os.path.splitext(f)[0] for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.md')])
    
    # 计算待处理文件
    pending = list(input_files - set([f + '.json' for f in completed]))
    
    # 如果存在 pending_files.json，加载并合并
    if os.path.exists(PENDING_FILES_PATH):
        with open(PENDING_FILES_PATH, 'r', encoding='utf-8') as f:
            saved_pending = json.load(f)
        # 合并新的待处理文件和之前保存的
        pending = list(set(pending).union(set(saved_pending)))
    else:
        with open(PENDING_FILES_PATH, 'w', encoding='utf-8') as f:
            json.dump(pending, f, ensure_ascii=False, indent=2)
    
    return pending

def save_pending_files(pending):
    """
    保存当前待处理文件列表。
    """
    with open(PENDING_FILES_PATH, 'w', encoding='utf-8') as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

def get_session():
    """
    获取 requests 会话，配置重试策略。
    """
    session = requests.Session()
    retry = requests.adapters.Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def process_content(content):
    """
    调用 GPT-4o-mini 模型清洗和格式化内容。
    """
    prompt = COMBINED_PROMPT_TEMPLATE.format(content=content)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an assistant that helps clean and format technical documents for inclusion in a training corpus."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 16384,
        "temperature": 0.5
    }
    
    session = get_session()
    
    try:
        response = session.post(API_ENDPOINT, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        
        response_data = response.json()
        choices = response_data.get('choices', [])
        if choices:
            content_piece = choices[0].get('message', {}).get('content', '')
            return content_piece.strip(), 0
        else:
            print("未生成任何内容")
            return None, 0
    
    except requests.exceptions.SSLError as e:
        print(f"SSL错误: {e}")
        return None, 0
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None, 0
    except KeyError:
        print("响应格式错误:", response.text)
        return None, 0

def process_file(filename, pending):
    """
    处理单个 JSON 文件，清洗和格式化内容，保存为 .md 文件。
    """
    input_filepath = os.path.join(INPUT_DIR, filename)
    base_filename = os.path.splitext(filename)[0]
    output_filename = base_filename + '.md'
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(input_filepath, 'r', encoding='utf-8') as infile:
        try:
            data = json.load(infile)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误 in {input_filepath}: {e}")
            return 0  # 返回使用的 token 数为 0
    
    content = data.get('content', '')
    if not content:
        print(f"{input_filepath} 中未找到 content。跳过。")
        return 0  # 返回使用的 token 数为 0
    
    # 清洗和格式化内容
    cleaned_content, tokens_used = process_content(content)
    
    if cleaned_content:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_content)
    else:
        print(f"{input_filepath} 清洗失败。原内容未保存。")
        # 不保存任何内容
    
    # 从待处理列表中移除该文件
    pending.remove(filename)
    save_pending_files(pending)
    
    return tokens_used

def rate_limit(tokens):
    """
    控制 API 请求的速率，确保每分钟 token 使用量不超过限制。
    """
    global TOKENS_USED_IN_CURRENT_MINUTE, START_TIME
    current_time = time.time()
    elapsed_time = current_time - START_TIME
    if elapsed_time >= 60:
        # 已经过了一分钟，重置计数器
        TOKENS_USED_IN_CURRENT_MINUTE = 0
        START_TIME = current_time
    if TOKENS_USED_IN_CURRENT_MINUTE + tokens > MAX_TOKENS_PER_MINUTE:
        # 需要等待
        sleep_time = 60 - elapsed_time
        print(f"已达到每分钟最大 token 数等待 {sleep_time:.2f} 秒。")
        time.sleep(sleep_time)
        # 重置计数器
        TOKENS_USED_IN_CURRENT_MINUTE = 0
        START_TIME = time.time()
    TOKENS_USED_IN_CURRENT_MINUTE += tokens

def main():
    pending = load_pending_files()
    
    if not pending:
        print("没有待处理的文件。")
        return
    
    print(f"找到 {len(pending)} 个待处理的文件。开始处理...")
    
    for filename in tqdm(pending.copy(), desc="处理文件"):
        try:
            tokens_used = process_file(filename, pending)
            rate_limit(tokens_used)
        except Exception as exc:
            print(f"{filename} 生成异常: {exc}")
            # 如果出错，可以选择不移除文件，确保下次运行时继续处理
            # 这里选择不移除，以便下次运行继续处理
            pass
    
    print("所有文件处理完成。")
    # 删除 pending 文件列表
    if os.path.exists(PENDING_FILES_PATH):
        os.remove(PENDING_FILES_PATH)

if __name__ == "__main__":
    main()