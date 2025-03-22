import re
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time  # 新增时间模块导入


def parse_curl_command(curl_command):
    # 预处理输入：移除换行符和多余空格
    curl_command = re.sub(r'\\\n\s*', ' ', curl_command)  # 处理换行符
    curl_command = re.sub(r'\s+', ' ', curl_command).strip()
    
    url_pattern = r"curl\s*['\"]([^'\"]+)['\"]"
    header_pattern = r"-H\s*['\"]([^:]+?)\s*:\s*(.*?)\s*['\"]"

    url_match = re.search(url_pattern, curl_command)
    if not url_match:
        raise ValueError("未从 curl 命令中找到有效的 URL。")
    url = url_match.group(1)

    headers = {}
    for header_match in re.finditer(header_pattern, curl_command):
        key = header_match.group(1).strip()
        value = header_match.group(2).strip()
        print(f'解析到header: {key}={value}')
        headers[key] = value

    return url, headers


def download_video(url, headers, save_path, progress_callback=None):
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        block_size = 8192  # 使用更大的块大小，提高下载效率
        downloaded_size = 0
        start_time = time.time()
        
        with open(save_path, 'wb') as file:
            for data in response.iter_content(block_size):
                if data:
                    file.write(data)
                    downloaded_size += len(data)
                    if progress_callback:
                        progress_callback(len(data), downloaded_size, total_size, start_time)
        print(f"下载完成，保存路径：{save_path}")

    except requests.exceptions.RequestException as e:
        print(f"下载过程中出现请求错误：{e}")
        raise e
    except Exception as e:
        print(f"发生意外错误：{e}")
        raise e


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title("视频下载工具")
        
        self.curl_command = tk.StringVar()
        self.save_path = tk.StringVar(value='./downloaded_video.mp4')
        self.progress = 0
        self.accumulated = 0  # 累积计数器
        self.last_update = 0  # 时间戳记录
        self.total_size = 0   # 文件总大小
        self.download_speed = 0  # 下载速度
        self.progress_text = tk.StringVar(value="准备下载...")
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0)
        
        ttk.Label(main_frame, text="CURL命令:").grid(row=0, column=0, sticky=tk.W)
        self.curl_entry = tk.Text(main_frame, width=60, height=4)
        self.curl_entry.grid(row=1, column=0, columnspan=2, pady=5)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.curl_entry.yview)
        scrollbar.grid(row=1, column=2, sticky='ns')
        self.curl_entry['yscrollcommand'] = scrollbar.set
        
        ttk.Label(main_frame, text="保存路径:").grid(row=2, column=0, sticky=tk.W)
        self.path_entry = ttk.Entry(main_frame, width=50, textvariable=self.save_path)
        self.path_entry.grid(row=3, column=0, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.choose_save_path).grid(row=3, column=1, padx=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # 添加进度显示标签
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_text)
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        self.download_btn = ttk.Button(main_frame, text="开始下载", command=self.start_download)
        self.download_btn.grid(row=6, column=0, columnspan=2, pady=10)
    
    def choose_save_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4文件", "*.mp4")])
        if path:
            self.save_path.set(path)
    
    def start_download(self):
        curl_command = self.curl_entry.get("1.0", tk.END).strip()
        if not curl_command:
            messagebox.showerror("错误", "请输入有效的CURL命令")
            return
        
        try:
            url, headers = parse_curl_command(curl_command)
        except Exception as e:
            messagebox.showerror("解析错误", str(e))
            return
        
        self.download_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        
        download_thread = threading.Thread(
            target=self.run_download,
            args=(url, headers, self.save_path.get())
        )
        download_thread.start()
    
    def run_download(self, url, headers, save_path):
        try:
            # 重置进度显示
            self.progress_text.set("准备下载...")
            self.progress = 0
            self.accumulated = 0
            self.total_size = 0
            self.download_speed = 0
            
            download_video(
                url,
                headers,
                save_path,
                progress_callback=lambda size, downloaded, total, start_time: 
                    self.root.after(10, self.update_progress, size, downloaded, total, start_time)
            )
            self.root.after(10, self.on_download_success)
        except Exception as e:
            self.root.after(10, self.on_download_error, str(e))
    
    def update_progress(self, chunk_size, downloaded_size, total_size, start_time):
        self.accumulated += chunk_size
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # 更新总大小信息
        if self.total_size != total_size:
            self.total_size = total_size
            self.progress_bar['maximum'] = total_size
        
        # 计算下载速度 (bytes/second)
        if elapsed_time > 0:
            self.download_speed = downloaded_size / elapsed_time
        
        # 更新进度条和进度文本
        current_time_ms = current_time * 1000
        if self.accumulated >= 1024*1024 or (current_time_ms - self.last_update) > 100:
            # 更新进度条
            self.progress_bar['value'] = downloaded_size
            
            # 格式化显示信息
            if total_size > 0:
                percent = (downloaded_size / total_size) * 100
            else:
                percent = 0
                
            # 格式化大小显示
            def format_size(size):
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0 or unit == 'GB':
                        break
                    size /= 1024.0
                return f"{size:.2f} {unit}"
            
            # 格式化速度显示
            speed_text = format_size(self.download_speed) + "/s"
            
            # 更新进度文本
            self.progress_text.set(
                f"下载进度: {percent:.1f}% ({format_size(downloaded_size)}/{format_size(total_size)}) 速度: {speed_text}"
            )
            
            # 重置累积计数器和时间戳
            self.accumulated = 0
            self.last_update = current_time_ms
    
    def on_download_success(self):
        self.download_btn.config(state=tk.NORMAL)
        messagebox.showinfo("完成", "视频下载完成！")
    
    def on_download_error(self, error_msg):
        self.download_btn.config(state=tk.NORMAL)
        messagebox.showerror("下载错误", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
    