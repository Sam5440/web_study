import os
from bs4 import BeautifulSoup

def get_html_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.text
            return os.path.basename(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return os.path.basename(file_path)

def generate_index_html():
    # 基础HTML模板
    html_template = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Study 导航页</title>
    <style>
        body {
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .header-container {
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            margin-bottom: 20px;
        }
        .layout-toggle {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .layout-toggle:hover {
            background: #2980b9;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
            max-width: 1200px;
            margin: 0 auto;
            transition: all 0.3s ease;
        }
        .single-column .card {
            width: 800px;
        }
        .card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            width: 400px;
            transition: transform 0.3s ease, box-shadow 0.3s ease, width 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .card-title {
            background: #3498db;
            color: white;
            padding: 15px;
            margin: 0;
            font-size: 1.2em;
        }
        .card-content {
            padding: 15px;
        }
        .preview-frame {
            width: 100%;
            height: 300px;
            border: none;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .card-link {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }
        .card-link:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="header-container">
        <h1>Web Study 导航页</h1>
        <button class="layout-toggle" id="layoutToggle">切换为单列布局</button>
    </div>
    <div class="container" id="container">
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.getElementById('container');
            const layoutToggle = document.getElementById('layoutToggle');
            
            layoutToggle.addEventListener('click', function() {
                container.classList.toggle('single-column');
                if (container.classList.contains('single-column')) {
                    layoutToggle.textContent = '切换为双列布局';
                } else {
                    layoutToggle.textContent = '切换为单列布局';
                }
            });
        });
    </script>
'''

    # 遍历目录获取HTML文件
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
    # sort逆序
    # html_files.sort()
    html_files.sort(reverse=True)
    print(html_files)

    # 生成卡片内容
    cards = []
    for html_file in html_files:
        title = get_html_title(html_file)
        card = f'''
        <div class="card">
            <h2 class="card-title">{title} ({html_file})</h2>
            <div class="card-content">
                <iframe src="{html_file}" class="preview-frame"></iframe>
                <a href="{html_file}" class="card-link" target="_blank">在新窗口打开</a>
            </div>
        </div>'''
        cards.append(card)

    # 组合完整的HTML
    full_html = html_template + '\n'.join(cards) + '''
    </div>
</body>
</html>'''

    # 写入index.html文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

if __name__ == '__main__':
    generate_index_html()