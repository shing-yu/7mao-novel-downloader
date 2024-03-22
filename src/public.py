"""
作者：星隅（xing-yv）

版权所有（C）2023 星隅（xing-yv）

本软件根据GNU通用公共许可证第三版（GPLv3）发布；
你可以在以下位置找到该许可证的副本：
https://www.gnu.org/licenses/gpl-3.0.html

根据GPLv3的规定，您有权在遵循许可证的前提下自由使用、修改和分发本软件。
请注意，根据许可证的要求，任何对本软件的修改和分发都必须包括原始的版权声明和GPLv3的完整文本。

本软件提供的是按"原样"提供的，没有任何明示或暗示的保证，包括但不限于适销性和特定用途的适用性。作者不对任何直接或间接损害或其他责任承担任何责任。在适用法律允许的最大范围内，作者明确放弃了所有明示或暗示的担保和条件。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目协作者、贡献者无关。作者不对因使用该程序而导致的任何损失或损害承担任何责任。

请在使用本程序之前确保遵守相关法律法规和网站的使用政策，如有疑问，请咨询法律顾问。

无论您对程序进行了任何操作，请始终保留此信息。
"""

import re
import os
import sys
# pycrypto模块已不再使用，使用pycryptodome模块
# noinspection PyPackageRequirements
from Crypto.Cipher import AES
# noinspection PyPackageRequirements
from Crypto.Util.Padding import unpad
from base64 import b64decode
import requests
from tqdm import tqdm
import hashlib
import random
from colorama import Fore, Style, init

init(autoreset=True)


proxies = {
    "http": None,
    "https": None
}


def get_headers(book_id):

    version_list = [
        '73720', '73700',
        '73620', '73600',
        '73500',
        '73420', '73400',
        '73328', '73325', '73320', '73300',
        '73220', '73200',
        '73100', '73000', '72900',
        '72820', '72800',
        '70720', '62010', '62112',
    ]

    random.seed(book_id)

    version = random.choice(version_list)

    headers = {
        "AUTHORIZATION": "",
        "app-version": f"{version}",
        "application-id": "com.****.reader",
        "channel": "unknown",
        "net-env": "1",
        "platform": "android",
        "qm-params": "",
        "reg": "0",
    }

    # 获取 headers 的所有键并排序
    keys = sorted(headers.keys())

    # 生成待签名的字符串
    sign_str = ''.join([k + '=' + str(headers[k]) for k in keys]) + sign_key

    # 生成签名
    headers['sign'] = hashlib.md5(sign_str.encode()).hexdigest()

    return headers


def sign_url_params(params):

    keys = sorted(params.keys())

    # 生成待签名的字符串
    sign_str = ''.join([k + '=' + str(params[k]) for k in keys]) + sign_key

    # 使用MD5哈希生成签名
    signature = hashlib.md5(sign_str.encode()).hexdigest()

    # 将签名添加到参数字典中
    params['sign'] = signature

    return params


# 替换非法字符
def rename(name):
    # 定义非法字符的正则表达式模式
    illegal_characters_pattern = r'[\/:*?"<>|]'

    # 定义替换的中文符号
    replacement_dict = {
        '/': '／',
        ':': '：',
        '*': '＊',
        '?': '？',
        '"': '“',
        '<': '＜',
        '>': '＞',
        '|': '｜'
    }

    # 使用正则表达式替换非法字符
    sanitized_path = re.sub(illegal_characters_pattern, lambda x: replacement_dict[x.group(0)], name)

    return sanitized_path


# 定义解密函数
def decrypt(data, iv):
    # print(f"Decrypting data: {data}")
    # print(f"Using iv: {iv}")
    key = bytes.fromhex('32343263636238323330643730396531')
    iv = bytes.fromhex(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted = unpad(cipher.decrypt(bytes.fromhex(data)), AES.block_size)
    return decrypted.decode('utf-8')


# 定义qimao函数
def decrypt_qimao(content):
    # print(f"Decrypting content: {content}")
    txt = b64decode(content)
    iv = txt[:16].hex()
    # print(f"IV: {iv}")
    fntxt = decrypt(txt[16:].hex(), iv).strip().replace('\n', '<br>')
    return fntxt


def get_api(book_id, chapter):
    # 获取章节标题
    chapter_title = chapter["title"]
    chapter_title = rename(chapter_title)

    # 获取章节 id
    chapter_id = chapter["id"]

    # 尝试获取章节内容
    chapter_content = None
    while True:
        retry_count = 1
        while retry_count < 4:  # 设置最大重试次数
            try:
                encrypted_content = send_request(book_id, chapter_id)
            except Exception as e:

                tqdm.write(Fore.RED + Style.BRIGHT + f"发生异常: {e}")
                if retry_count == 1:
                    tqdm.write(f"{chapter_title} 获取失败，正在尝试重试...")
                tqdm.write(f"第 ({retry_count}/3) 次重试获取章节内容")
                retry_count += 1  # 否则重试
                continue

            if "data" in encrypted_content and "content" in encrypted_content["data"]:
                encrypted_content = encrypted_content['data']['content']
                chapter_content = decrypt_qimao(encrypted_content)
                chapter_content = re.sub('<br>', '\n', chapter_content)
                break  # 如果成功获取章节内容，跳出重试循环
            else:
                if retry_count == 1:
                    tqdm.write(f"{chapter_title} 获取失败，正在尝试重试...")
                tqdm.write(f"第 ({retry_count}/3) 次重试获取章节内容")
                retry_count += 1  # 否则重试

        if retry_count == 4:
            import tkinter as tk
            from tkinter import font, messagebox
            tqdm.write(Fore.RED + Style.BRIGHT + f"无法获取章节内容: {chapter_title}")
            tqdm.write(Fore.YELLOW + Style.BRIGHT + "请在弹出窗口中选择处理方式")
            choice = None

            def on_button_click(value):
                nonlocal choice
                choice = value
                window.destroy()

            # 弹窗请用户选择处理方式
            window = tk.Tk()
            window.title("番茄下载器 - 选择处理方式")
            # 获取屏幕宽度和高度
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            # 计算窗口宽和高
            x = (screen_width - 400) / 2
            y = (screen_height - 260) / 2
            window.geometry(f"400x260+{int(x)}+{int(y)}")

            # 不允许调整大小
            window.resizable(False, False)

            # 获取默认字体并设置字体大小
            default_font_family = font.nametofont("TkDefaultFont").actual()["family"]
            font1 = font.Font(family=default_font_family, size=12)
            font2 = font.Font(family=default_font_family, size=8)

            label = tk.Label(window, text=f"无法获取章节内容: \n{chapter_title}", pady=10, font=font1)
            label.pack()

            label2 = tk.Label(window, text="已达最大重试次数\n您希望程序如何处理此问题：", font=font2)
            label2.pack()

            button1_frame = tk.Frame(window)
            button1_frame.pack()
            button1 = tk.Button(button1_frame, text="跳过此章节 (1)", command=lambda: on_button_click("1"), font=font1)
            button1.pack(pady=5)

            button2_frame = tk.Frame(window)
            button2_frame.pack()
            button2 = tk.Button(button2_frame, text="再次重试 (2)", command=lambda: on_button_click("2"), font=font1)
            button2.pack(pady=5)

            button3_frame = tk.Frame(window)
            button3_frame.pack()
            button3 = tk.Button(button3_frame, text="终止下载并保存 (3)", command=lambda: on_button_click("3"),
                                font=font1)
            button3.pack(pady=5)

            def on_closing():
                messagebox.showwarning("警告", "您必须选择处理方式，程序才能继续运行")

            window.protocol("WM_DELETE_WINDOW", on_closing)

            window.mainloop()
            if choice == "1":
                return "skip"
            elif choice == "2":
                continue
            elif choice == "3":
                return "terminate"
        else:
            break

    return chapter_title, chapter_content, chapter_id


def send_request(book_id, chapter_id):

    headers = get_headers(book_id)

    params = {
        "id": book_id,
        "chapterId": chapter_id,
    }

    params = sign_url_params(params)

    response = requests.get(f"https://api-ks.wtzw.com/api/v1/chapter/content", headers=headers, params=params,
                            proxies=proxies, timeout=10)
    return response.json()


sign_key = 'd3dGiJc651gSQ8w1'


def asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("assets"), relative_path)


def get_book_info(url, mode="normal"):
    # 提取ID
    book_id = re.search(r"/(\d+)/", url).group(1)
    # 请求API
    info = requests.get(f"https://api-bc.wtzw.com/api/v1/reader/detail?id={book_id}", proxies=proxies,
                        timeout=12).json()

    # 提取信息
    title = info["data"]["title"]
    author = info["data"]["author"]
    intro = info["data"]["intro"]
    words_num = info["data"]["words_num"]
    tags = [tag["title"] for tag in info["data"]["book_tag_list"]]
    tags = str(tags).replace("'", "").replace("[", "").replace("]", "")

    content = f"""如果需要小说更新，请勿修改文件名
使用 @星隅(xing-yv) 所作开源工具下载
开源仓库地址:https://github.com/xing-yv/7mao-novel-downloader
Gitee:https://gitee.com/xingyv1024/7mao-novel-downloader/
任何人无权限制您访问本工具，如果有向您提供代下载服务者未事先告知您工具的获取方式，请向作者举报:xing_yv@outlook.com

名称：{title}
作者：{author}
标签：{tags}
简介：{intro}
字数：{words_num}
"""

    # 请求章节列表
    params = {
        'chapter_ver': '0',
        'id': book_id,
    }
    response = requests.get("https://api-ks.wtzw.com/api/v1/chapter/chapter-list",
                            params=sign_url_params(params),
                            headers=get_headers(book_id),
                            proxies=proxies,
                            timeout=12).json()

    # {
    #     "data": {
    #         "id": "1784910",
    #         "type": "chapter_lists",
    #         "chapter_lists": [
    #             {
    #                 "id": "17059219910001",
    #                 "content_md5": "bac8397a6dc95bbfdacbde5b60f9e345",
    #                 "index": "1",
    #                 "title": "第一章 离乡",
    #                 "words": "5968",
    #                 "chapter_sort": 1
    #             },

    chapters = response["data"]["chapter_lists"]
    # 使用chapter_sort排序
    chapters.sort(key=lambda x: x["chapter_sort"])

    if mode == "epub":
        img_url = info["data"]["image_link"]
        return title, intro, author, img_url, chapters

    return title, content, chapters
