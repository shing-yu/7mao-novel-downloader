# 导入必要的模块
import re
import os
import time
import json
from tqdm import tqdm
import public as p
from colorama import Fore, Style, init

init(autoreset=True)


# 定义分章节保存模式用来下载7猫小说的函数
def qimao_c(url, encoding, path_choice, start_chapter_id,
            config_path):
    book_id = re.search(r"/(\d+)/", url).group(1)

    # 调用异步函数获取7猫信息（模拟浏览器）
    try:
        title, introduction, chapters = p.get_book_info(url)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    # 获取保存路径
    book_folder = get_folder_path(path_choice, title, config_path)
    # 创建保存文件夹
    os.makedirs(book_folder, exist_ok=True)

    # 转换简介内容格式
    introduction_data = introduction.encode(encoding, errors='ignore')

    # 定义简介路径
    introduction_use = False
    introduction_path = None

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

    # 遍历每个章节链接
    for chapter in tqdm(chapters[start_index:], desc="下载进度"):

        time.sleep(0.25)
        result = p.get_api(book_id, chapter)

        if result == "skip":
            continue
        elif result == "terminate":
            break
        else:
            chapter_title, chapter_text, _ = result

        # 在章节内容字符串中添加章节标题和内容
        content_all = f"{chapter_title}\n{chapter_text}"

        # 转换章节内容格式
        data = content_all.encode(encoding, errors='ignore')

        # 重置file_path
        # noinspection PyUnusedLocal
        file_path = None

        # 生成最终文件路径

        # 使用用户选择的文件夹路径和默认文件名来生成完整的文件路径

        file_path = os.path.join(book_folder, f"{chapter_title}.txt")
        if introduction_use is False:
            introduction_path = os.path.join(book_folder, "简介.txt")

        if introduction_use is False:
            with open(introduction_path, "wb") as f:
                f.write(introduction_data)
            tqdm.write("简介已保存")
            # 将简介保存标记为已完成
            introduction_use = True

        with open(file_path, "wb") as f:
            f.write(data)

        # 打印进度信息
        tqdm.write(f"已获取: {chapter_title}")


def get_folder_path(path_choice, title, config_path):
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

            # 弹出文件对话框以选择保存位置
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
                    json.dump({"path": {"chapter": folder_path}}, c)
            else:
                with open(config_path, "r") as c:
                    config = json.load(c)
                config["path"]["chapter"] = folder_path
                with open(config_path, "w") as c:
                    json.dump(config, c)
    elif path_choice == 0:

        # 定义文件名，检测是否有默认路径
        if not os.path.exists(config_path):
            folder_path = "output"
        else:
            with open(config_path, "r") as c:
                config = json.load(c)
            if "chapter" in config["path"]:
                folder_path = config["path"]["chapter"]
            else:
                folder_path = "output"
        os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{title}")
