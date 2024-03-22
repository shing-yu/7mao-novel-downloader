# 导入必要的模块

import re
import os
import json
import time
import base64
import datetime
from tqdm import tqdm
import hashlib
import public as p
from colorama import Fore, Style, init

init(autoreset=True)


def qimao_b(encoding, path_choice, data_folder,
            config_path):

    if not os.path.exists("urls.txt"):
        print("url.txt文件不存在")
        return "file does not exist"

    try:
        # 打开url.txt文件
        with open("urls.txt", "r") as file:
            lines = file.readlines()

        # 检查文件是否为空
        if not lines or all(not line.strip() for line in lines):
            print("urls.txt文件为空")
            return
        else:
            # 检查每行格式，并且不是空行
            urls = []
            for i, line in enumerate(lines, start=1):
                line = line.strip()
                try:
                    if line is False:
                        continue
                        # 如果是空行，则跳过
                    elif line.isdigit():
                        book_id = line
                        urls.append("https://www.qimao.com/shuku/" + book_id + "/")
                    elif "www.qimao.com/shuku/" in line:
                        book_id = re.search(r"www.qimao.com/shuku/(\d+)", line).group(1)
                        urls.append("https://www.qimao.com/shuku/" + book_id + "/")
                    elif "app-share.wtzw.com" in line:
                        book_id = re.search(r"article-detail/(\d+)", line).group(1)
                        urls.append("https://www.qimao.com/shuku/" + book_id + "/")
                    else:
                        print(Fore.YELLOW + Style.BRIGHT + f"无法识别的内容：第{i}行\n内容：{line}")
                        return "file syntax is incorrect"
                except AttributeError:
                    print(Fore.YELLOW + Style.BRIGHT + f"链接无法识别：第{i}行\n内容：{line}")
                    return "file syntax is incorrect"

        print("urls.txt文件内容符合要求")

        # 定义文件夹路径
        folder_path = None
        # 如果用户选择自定义路径
        if path_choice == 1:
            import tkinter as tk
            from tkinter import filedialog
            # 创建一个Tkinter窗口，但不显示它
            root = tk.Tk()
            root.withdraw()

            print("您选择了自定义保存路径，请您在弹出窗口中选择保存文件夹。")

            while True:

                # 弹出文件对话框以选择保存位置和文件名
                folder_path = filedialog.askdirectory()

                # 检查用户是否取消了对话框
                if not folder_path:
                    # 用户取消了对话框，提示重新选择
                    print("您没有选择保存文件夹，请重新选择！")
                    continue
                else:
                    print("已选择保存文件夹")
                    break
            # 询问用户是否保存此路径
            cho = input("是否使用此路径覆盖此模式默认保存路径（y/n(d)）？")
            if not cho or cho == "n":
                pass
            else:
                # 如果配置文件不存在，则创建
                if not os.path.exists(config_path):
                    with open(config_path, "w") as c:
                        json.dump({"path": {"batch": folder_path}}, c)
                else:
                    with open(config_path, "r") as c:
                        config = json.load(c)
                    config["path"]["batch"] = folder_path
                    with open(config_path, "w") as c:
                        json.dump(config, c)

        elif path_choice == 0:

            # 定义文件名，检测是否有默认路径
            if not os.path.exists(config_path):
                folder_path = "output"
            else:
                with open(config_path, "r") as c:
                    config = json.load(c)
                if "batch" in config["path"]:
                    folder_path = config["path"]["batch"]
                else:
                    folder_path = "output"
            os.makedirs(folder_path, exist_ok=True)

        # 对于文件中的每个url，执行函数
        for url in urls:
            url = url.strip()  # 移除行尾的换行符
            if url:  # 如果url不为空（即，跳过空行）
                download_novels(url, encoding, folder_path, data_folder)
                time.sleep(1)

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生错误：{str(e)}")
        return f"发生错误：{str(e)}"


# 定义批量模式用来下载番茄小说的函数
def download_novels(url, encoding, folder_path, data_folder):

    book_id = re.search(r"/(\d+)/", url).group(1)

    # 调用异步函数获取7猫信息（模拟浏览器）
    try:
        title, content, chapters = p.get_book_info(url)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    print(f"\n开始 《{title}》 的下载")

    chapter_id = None

    length = len(chapters)
    encryption_index = length // 2

    # 遍历每个章节链接
    for i, chapter in enumerate(tqdm(chapters, desc="下载进度")):

        time.sleep(1)
        result = p.get_api(book_id, chapter)

        if result == "skip":
            continue
        elif result == "terminate":
            break
        else:
            chapter_title, chapter_text, chapter_id = result

        # 在小说内容字符串中添加章节标题和内容
        content += f"\n\n\n{chapter_title}\n\n{chapter_text}"

        if i == encryption_index:
            content += base64.b64decode("CgoK5pys5bCP6K+06YCa6L+H5YWN6LS55byA5rqQ"
                                        "5LiL6L295bel5YW3IGh0dHBzOi8vc291cmwuY24vZHZGS0VSIOS4i+i9veOAguWmguaenOaCqO"
                                        "mBh+WIsOaUtui0ue+8jOivt+S4vuaKpeW5tuiBlOezu+S9nOiAhQoK").decode()

        # 打印进度信息
        tqdm.write(f"已获取 {chapter_title}")

    # 根据main.py中用户选择的路径方式，选择自定义路径或者默认

    file_path = os.path.join(folder_path, f"{title}.txt")

    # 根据编码转换小说内容字符串为二进制数据
    data = content.encode(encoding, errors='ignore')

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(data)

    # 打印完成信息
    print(f"已保存{title}.txt")

    # 计算文件 sha256 值
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    sha256_hash = hash_sha256.hexdigest()

    # 保存小说更新源文件
    upd_file_path = os.path.join(data_folder, f"{title}.upd")
    # 获取当前系统时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 创建要写入元信息文件的内容
    meta_content = f"{current_time}\n{url}\n{chapter_id}\n{encoding}\n{sha256_hash}"
    # 打开文件并完全覆盖内容
    with open(upd_file_path, "w") as file:
        file.write(meta_content)

    print("已完成")
