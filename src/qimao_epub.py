import os
import yaml
import json

# 导入必要的模块
import requests
from requests.exceptions import Timeout
from ebooklib import epub
import re
import time
from tqdm import tqdm
import public as p
from colorama import Fore, Style, init

init(autoreset=True)


# 定义正常模式用来下载7猫小说的函数
def qimao_epub(url, path_choice, config_path):
    book_id = re.search(r"/(\d+)/", url).group(1)

    try:
        title, intro, author, img_url, chapters = p.get_book_info(url, mode='epub')
        # 下载封面
        response = requests.get(img_url, timeout=10, proxies=p.proxies)
    except Timeout:
        print(Fore.RED + Style.BRIGHT + "连接超时，请检查网络连接是否正常。")
        return
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    # 创建epub电子书
    book = epub.EpubBook()

    # 获取图像的内容
    img_data = response.content

    # 保存图像到本地文件
    with open("cover.jpg", "wb") as f:
        f.write(img_data)

    # 创建一个封面图片
    book.set_cover("image.jpg", open('cover.jpg', 'rb').read())

    # 删除封面
    os.remove('cover.jpg')

    # 设置书的元数据
    book.set_title(title)
    book.set_language('zh-CN')
    book.add_author(author)
    book.add_metadata('DC', 'description', intro)

    yaml_data = {
        'qmid': book_id
    }
    yaml_content = yaml.dump(yaml_data)

    # 设置 qmid 元数据
    yaml_item = epub.EpubItem(uid='yaml', file_name='metadata.yaml', media_type='application/octet-stream',
                              content=yaml_content)
    book.add_item(yaml_item)

    # intro chapter
    intro_e = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='hr')
    intro_e.content = (f'<img src="image.jpg" alt="Cover Image"/>'
                       f'<h1>{title}</h1>'
                       f'<p>{intro}</p>')
    book.add_item(intro_e)

    font_file = p.asset_path("HarmonyOS_Sans_SC_Regular.ttf")
    css1_file = p.asset_path("page_styles.css")
    css2_file = p.asset_path("stylesheet.css")
    # 打开资源文件
    with open(font_file, 'rb') as f:
        font_content = f.read()
    with open(css1_file, 'r', encoding='utf-8') as f:
        css1_content = f.read()
    with open(css2_file, 'r', encoding='utf-8') as f:
        css2_content = f.read()

    # 创建一个EpubItem实例来存储你的字体文件
    font = epub.EpubItem(
        uid="font",
        file_name="fonts/HarmonyOS_Sans_SC_Regular.ttf",  # 这将是字体文件在epub书籍中的路径和文件名
        media_type="application/vnd.ms-opentype",
        content=font_content,
    )
    # 创建一个EpubItem实例来存储你的CSS样式
    nav_css1 = epub.EpubItem(
        uid="style_nav1",
        file_name="style/page_styles.css",  # 这将是CSS文件在epub书籍中的路径和文件名
        media_type="text/css",
        content=css1_content,
    )
    nav_css2 = epub.EpubItem(
        uid="style_nav2",
        file_name="style/stylesheet.css",  # 这将是CSS文件在epub书籍中的路径和文件名
        media_type="text/css",
        content=css2_content,
    )

    # 将资源文件添加到书籍中
    book.add_item(font)
    book.add_item(nav_css1)
    book.add_item(nav_css2)

    # 创建索引
    book.toc = (epub.Link('intro.xhtml', '简介', 'intro'),)
    book.spine = ['nav', intro_e]

    try:

        # 定义目录索引
        toc_index = ()

        chapter_id_name = 0
        # 遍历每个章节链接
        for chapter in tqdm(chapters):
            chapter_id_name += 1
            time.sleep(0.25)

            result = p.get_api(book_id, chapter)

            if result == "skip":
                continue
            elif result == "terminate":
                break
            else:
                chapter_title, chapter_content, chapter_id = result

            # # 提取文章标签中的文本
            # chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)
            chapter_text = re.sub(r'\n', '</p><p>', chapter_content)

            # 在小说内容字符串中添加章节标题和内容
            # 在小说内容字符串中添加章节标题和内容
            text = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{chapter_id_name}.xhtml')
            text.add_item(nav_css1)
            text.add_item(nav_css2)
            text.content = (f'<h2 class="titlecss">{chapter_title}</h2>'
                            f'<p>{chapter_text}</p>')

            toc_index = toc_index + (text,)
            book.spine.append(text)

            # 加入epub
            book.add_item(text)

            # 打印进度信息
            tqdm.write(f"已获取 {chapter_title}")

        # 加入书籍索引
        book.toc = toc_index
    except BaseException as e:
        # 捕获所有异常
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    # 添加 navigation 文件
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

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
        default_extension = ".epub"
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
                    json.dump({"path": {"epub": folder_path}}, c)
            else:
                with open(config_path, "r") as c:
                    config = json.load(c)
                config["path"]["epub"] = folder_path
                with open(config_path, "w") as c:
                    json.dump(config, c)

    elif path_choice == 0:
        # 定义文件名，检测是否有默认路径
        if not os.path.exists(config_path):
            file_path = title + ".epub"
        else:
            with open(config_path, "r") as c:
                config = json.load(c)
            if "epub" in config["path"]:
                file_path = os.path.join(config["path"]["epub"], f"{title}.epub")
            else:
                file_path = title + ".epub"

    epub.write_epub(file_path, book, {})

    print("文件已保存！")
    return
