import datetime
import hashlib
import os
import re
import time
import json
import base64
# 导入必要的模块
from colorama import Fore, Style, init
from tqdm import tqdm

import public as p

init(autoreset=True)


# 定义正常模式用来下载7猫小说的函数
def qimao_n(url, encoding, path_choice, data_folder, start_chapter_id,
            config_path):

    book_id = re.search(r"/(\d+)/", url).group(1)

    # 调用异步函数获取7猫信息（模拟浏览器）
    try:
        title, content, chapters = p.get_book_info(url)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    # 检查用户是否指定起始章节
    start_index = 0
    if start_chapter_id == '0':
        pass
    else:
        # 找到起始章节的索引
        for i, chapter in enumerate(chapters):
            chapter_id_tmp = chapter["id"]
            if chapter_id_tmp == start_chapter_id:  # 将 开始索引设置为用户的值
                start_index = i
    file_path = None
    # 根据main.py中用户选择的路径方式，选择自定义路径或者默认
    if path_choice == 1:
        import tkinter as tk
        from tkinter import filedialog
        # 创建一个Tkinter窗口，但不显示它
        root = tk.Tk()
        root.withdraw()

        print("您选择了自定义保存路径，请您在弹出窗口中选择路径。")

        # 设置默认文件名和扩展名
        default_extension = ".txt"
        default_filename = f"{title}"

        while True:

            # 弹出文件对话框以选择保存位置和文件名
            file_path = filedialog.asksaveasfilename(
                defaultextension=default_extension,
                filetypes=[("Text Files", "*" + default_extension)],
                initialfile=default_filename
            )

            # 检查用户是否取消了对话框
            if not file_path:
                # 用户取消了对话框，提示重新选择
                print("您没有选择路径，请重新选择！")
                continue
            break
        # 询问用户是否保存此路径
        cho = input("是否使用此路径覆盖此模式默认保存路径（y/n(d)）？")
        if not cho or cho == "n":
            pass
        else:
            # 提取文件夹路径
            folder_path = os.path.dirname(file_path)
            # 如果配置文件不存在，则创建
            if not os.path.exists(config_path):
                with open(config_path, "w") as c:
                    json.dump({"path": {"normal": folder_path}}, c)
            else:
                with open(config_path, "r") as c:
                    config = json.load(c)
                config["path"]["normal"] = folder_path
                with open(config_path, "w") as c:
                    json.dump(config, c)

    elif path_choice == 0:
        # 定义文件名，检测是否有默认路径
        if not os.path.exists(config_path):
            file_path = title + ".txt"
        else:
            with open(config_path, "r") as c:
                config = json.load(c)
            if "normal" in config["path"]:
                file_path = os.path.join(config["path"]["normal"], f"{title}.txt")
            else:
                file_path = title + ".txt"

    chapter_id = None

    length = len(chapters)
    encryption_index = length // 2

    try:
        # 遍历每个章节链接
        for i, chapter in enumerate(tqdm(chapters[start_index:], desc="下载进度")):
            time.sleep(0.25)

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

    except BaseException as e:

        # 捕获所有异常，及时保存文件
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        print("正在尝试保存文件...")
        # 根据编码转换小说内容字符串为二进制数据
        data = content.encode(encoding, errors='ignore')

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(data)

        print("文件已保存！")
        return
