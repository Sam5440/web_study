import os
import re

def remove_html_comments(file_path):
    """从指定的 HTML 文件中移除注释"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用正则表达式移除 HTML 注释 (<!-- ... -->)
        # re.DOTALL 使 '.' 匹配包括换行符在内的所有字符
        cleaned_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

        # 如果内容有变化，则写回文件
        if cleaned_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"已移除文件 '{file_path}' 中的注释。")
        else:
            print(f"文件 '{file_path}' 中未找到注释或无需修改。")

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。")
    except Exception as e:
        print(f"处理文件 '{file_path}' 时发生错误：{e}")

def process_directory(directory='.'):
    """处理指定目录下的所有 HTML 文件"""
    print(f"开始处理目录 '{directory}' 中的 HTML 文件...")
    for filename in os.listdir(directory):
        if filename.lower().endswith('.html'):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path): # 确保是文件而不是目录
                remove_html_comments(file_path)
    print("处理完成。")

if __name__ == "__main__":
    # 获取当前脚本所在的目录，或直接使用当前工作目录 '.'
    # current_directory = os.path.dirname(os.path.abspath(__file__))
    current_directory = '.'
    process_directory(current_directory)