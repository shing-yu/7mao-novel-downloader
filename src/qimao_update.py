# 导入必要的模块
import re
import os
import time
import datetime
from tqdm import tqdm
import hashlib
import public as p
from colorama import Fore, Style, init

import requests
from requests.exceptions import Timeout
import yaml
from ebooklib import epub

init(autoreset=True)


# 定义7猫更新函数
def qimao_update(data_folder):

    # 请用户选择更新模式
    while True:
        update_mode = input("请选择更新模式:1 -> 单个更新 2-> 批量更新 3-> epub批量\n")
        if not update_mode:
            update_mode = '1'
        if update_mode == '1':
            onefile(data_folder)
            return
        elif update_mode == '2':
            break
        elif update_mode == '3':
            epub_batch_update()
            return
        else:
            print("无效的选择，请重新输入。")

    # 指定小说文件夹
    novel_folder = "更新"

    os.makedirs(novel_folder, exist_ok=True)

    input("请在程序目录下”更新“文件夹内放入需更新的文件\n按 Enter 键继续...")

    novel_files = [file for file in os.listdir(novel_folder) if file.endswith(".txt")]

    if not novel_files:
        print("没有可更新的文件")
        return

    no_corresponding_files = True  # 用于标记是否存在对应的txt和upd文件

    for txt_file in novel_files:
        txt_file_path = os.path.join(novel_folder, txt_file)
        # 寻找book_id
        # with open(txt_file_path, "r") as tmp:
        #     # 读取第一行
        #     first_line = tmp.readline().strip()  # 读取并去除前后空白字符
        #
        #     # 检测是否全部是数字
        #     if first_line.isdigit():
        #         book_id = first_line
        #     else:
        #         print(f"{txt_file} 不是通过此工具下载，无法更新")

        upd_file_path = os.path.join(data_folder, txt_file.replace(".txt", ".upd"))
        novel_name = txt_file.replace(".txt", "")

        if os.path.exists(upd_file_path):

            print(f"正在尝试更新: {novel_name}")
            # 读取用于更新的文件元数据
            with open(upd_file_path, 'r') as file:
                lines = file.readlines()

            # 保存上次更新时间和上次章节id到变量
            last_update_time = lines[0].strip()
            url = lines[1].strip()
            last_chapter_id = lines[2].strip()
            encoding = lines[3].strip()
            if len(lines) >= 5:
                save_sha256 = lines[4].strip()
                skip_hash = 0
            else:
                print(Fore.YELLOW + Style.BRIGHT + "此小说可能由老版本下载，跳过hash校验")
                save_sha256 = None
                skip_hash = 1
            hash_sha256 = hashlib.sha256()
            with open(txt_file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            fact_sha256 = hash_sha256.hexdigest()
            if skip_hash == 0:
                if fact_sha256 != save_sha256:
                    print(Fore.RED + Style.BRIGHT + "hash校验未通过！")
                    while True:
                        upd_choice = input(f"这往往意味着文件已被修改，是否继续更新？(yes/no):")
                        if upd_choice == "yes":
                            skip_this = 0
                            break
                        elif upd_choice == "no":
                            skip_this = 1
                            break
                        else:
                            print("输入错误，请重新输入")
                    if skip_this == 1:
                        print(Fore.RED + Style.BRIGHT + f"《{novel_name}》的更新已取消")
                        continue
                else:
                    print(Fore.GREEN + Style.BRIGHT + "hash校验通过！")
            print(f"上次更新时间{last_update_time}")
            result = download_novel(url, encoding, last_chapter_id, txt_file_path)
            if result == "DN":
                print(f"{novel_name} 已是最新，不需要更新。\n")
            elif result == "Timeout":
                print(Fore.RED + Style.BRIGHT + "更新失败")
            elif result == "Not Found":
                print(Fore.RED + Style.BRIGHT + "更新失败")
            else:
                print(f"{novel_name} 已更新完成。\n")
                # 计算文件 sha256 值
                hash_sha256 = hashlib.sha256()
                with open(txt_file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)
                sha256_hash = hash_sha256.hexdigest()
                # 获取当前系统时间
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 创建要写入元信息文件的内容
                new_content = f"{current_time}\n{url}\n{result}\n{encoding}\n{sha256_hash}"
                # 打开文件并完全覆盖内容
                with open(upd_file_path, "w") as file:
                    file.write(new_content)

            no_corresponding_files = False
        else:
            print(f"{novel_name} 不是通过此工具下载，无法更新")

    if no_corresponding_files:
        print("没有可更新的文件")


# 定义更新7猫小说的函数
def download_novel(url, encoding, start_chapter_id, txt_file_path):

    book_id = re.search(r"/(\d+)/", url).group(1)

    # 调用异步函数获取7猫信息（模拟浏览器）
    try:
        _, _, chapters = p.get_book_info(url)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    last_chapter_id = None
    # 找到起始章节的索引
    start_index = 0
    for i, chapter in enumerate(chapters):
        chapter_id_tmp = chapter["id"]
        if chapter_id_tmp == start_chapter_id:  # 更新函数，所以前进一个章节
            start_index = i + 1
        last_chapter_id = chapter_id_tmp

    # 判断是否已经最新
    if start_index >= len(chapters):
        return "DN"  # 返回Don't Need.

    # 打开文件
    with open(txt_file_path, 'ab') as f:
        chapter_id_now = start_chapter_id
        try:
            # 从起始章节开始遍历每个章节链接
            for chapter in tqdm(chapters[start_index:], desc="更新进度"):
                result = p.get_api(book_id, chapter)

                if result == "skip":
                    continue
                elif result == "terminate":
                    break
                else:
                    chapter_title, chapter_text, chapter_id_now = result

                # 在小说内容字符串中添加章节标题和内容
                content = f"\n\n\n{chapter_title}\n\n{chapter_text}"

                # 根据编码转换小说内容字符串为二进制数据
                data = content.encode(encoding, errors='ignore')

                # 将数据追加到文件中
                f.write(data)

                # 打印进度信息
                tqdm.write(f"已增加: {chapter_title}")

        except BaseException as e:

            # 捕获所有异常，及时保存文件
            print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
            print(Fore.RED + Style.BRIGHT + f"更新已被中断")

            return chapter_id_now

    # 返回更新完成
    return last_chapter_id


def onefile(data_folder):
    txt_file_path = None
    while True:
        m_epub = False
        # 提示用户输入路径
        user_path = input("请将要更新的小说拖动到窗口中，然后按 Enter 键:（支持新版本下载的epub）\n")
        if ".txt" in user_path:
            pass
        elif ".epub" in user_path:
            m_epub = True
            print(Fore.YELLOW + Style.BRIGHT + "EPUB更新模式处于测试阶段，如发现问题请及时反馈。")
        else:
            print("路径不正确，请重新输入")
            continue

        # 使用os.path.normpath()来规范化路径
        txt_file_path = os.path.normpath(user_path)
        # 检测文件是否存在
        if os.path.exists(txt_file_path):
            break
        else:
            print("文件不存在，请重新输入")
            continue

    if m_epub is True:
        qimao_epub_update(user_path)
        return

    txt_file = os.path.basename(txt_file_path)
    # # 寻找book_id
    # with open(txt_file_path, "r") as tmp:
    #     # 读取第一行
    #     first_line = tmp.readline().strip()  # 读取并去除前后空白字符
    #
    #     # 检测是否全部是数字
    #     if first_line.isdigit():
    #         book_id = first_line
    #     else:
    #         print(f"{txt_file} 不是通过此工具下载，无法更新")

    upd_file_path = os.path.join(data_folder, txt_file.replace(".txt", ".upd"))
    novel_name = txt_file.replace(".txt", "")

    if os.path.exists(upd_file_path):

        print(f"正在尝试更新: {novel_name}")
        # 读取用于更新的文件元数据
        with open(upd_file_path, 'r') as file:
            lines = file.readlines()

        # 保存上次更新时间和上次章节id到变量
        last_update_time = lines[0].strip()
        url = lines[1].strip()
        last_chapter_id = lines[2].strip()
        encoding = lines[3].strip()
        if len(lines) >= 5:
            save_sha256 = lines[4].strip()
            skip_hash = 0
        else:
            print(Fore.YELLOW + Style.BRIGHT + "此小说可能由老版本下载，跳过hash校验")
            save_sha256 = None
            skip_hash = 1
        hash_sha256 = hashlib.sha256()
        with open(txt_file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        fact_sha256 = hash_sha256.hexdigest()
        if skip_hash == 0:
            if fact_sha256 != save_sha256:
                print(Fore.RED + Style.BRIGHT + "hash校验未通过！")
                while True:
                    upd_choice = input(f"这往往意味着文件已被修改，是否继续更新？(yes/no):")
                    if upd_choice == "yes":
                        break
                    elif upd_choice == "no":
                        print(Fore.RED + Style.BRIGHT + "更新已取消")
                        return
                    else:
                        print("输入错误，请重新输入")
            else:
                print(Fore.GREEN + Style.BRIGHT + "hash校验通过！")
        print(f"上次更新时间{last_update_time}")
        result = download_novel(url, encoding, last_chapter_id, txt_file_path)
        if result == "DN":
            print(f"{novel_name} 已是最新，不需要更新。\n")
        elif result == "Timeout":
            print(Fore.RED + Style.BRIGHT + "更新失败")
        elif result == "Not Found":
            print(Fore.RED + Style.BRIGHT + "更新失败")
        else:
            print(f"{novel_name} 已更新完成。\n")
            # 计算文件 sha256 值
            hash_sha256 = hashlib.sha256()
            with open(txt_file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            sha256_hash = hash_sha256.hexdigest()
            # 获取当前系统时间
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 创建要写入元信息文件的内容
            new_content = f"{current_time}\n{url}\n{result}\n{encoding}\n{sha256_hash}"
            # 打开文件并完全覆盖内容
            with open(upd_file_path, "w") as file:
                file.write(new_content)
    else:
        print(f"{txt_file} 不是通过此工具下载，无法更新")


def epub_batch_update():
    print(Fore.YELLOW + Style.BRIGHT + "EPUB更新模式处于测试阶段，如发现问题请及时反馈。")
    # 指定小说文件夹
    novel_folder = "epub更新"

    os.makedirs(novel_folder, exist_ok=True)

    input("请在程序目录下”epub更新“文件夹内放入需更新的epub文件\n按 Enter 键继续...")

    novel_files = [file for file in os.listdir(novel_folder) if file.endswith(".epub")]

    if not novel_files:
        print("没有可更新的文件")
        return

    for epub_file in novel_files:
        print(f"正在更新: {epub_file}")
        epub_file_path = os.path.join(novel_folder, epub_file)
        # noinspection PyBroadException
        try:
            qimao_epub_update(epub_file_path)
        except Exception:
            # 导入打印异常信息的模块
            import traceback
            # 打印异常信息
            print(Fore.RED + Style.BRIGHT + "发生错误，请保存以下信息并联系开发者：")
            traceback.print_exc()


def qimao_epub_update(book_path):

    # 读取需要更新的epub文件
    book_o = epub.read_epub(book_path, {'ignore_ncx': True})

    # 创建epub电子书
    book = epub.EpubBook()

    # 获取book_id
    try:
        yaml_item = book_o.get_item_with_id('yaml')
        yaml_content = yaml_item.get_content().decode('utf-8')
        book_id = yaml.safe_load(yaml_content)['qmid']
    except AttributeError:
        print('当前仅支持更新2.10版本及以上下载的epub小说')
        return

    url = f"https://www.qimao.com/shuku/{book_id}/"

    try:
        title, intro, author, img_url, chapters = p.get_book_info(url, mode='epub')
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"发生异常: \n{e}")
        return

    # 下载封面
    response = requests.get(img_url)
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
            context = book_o.get_item_with_href(f'chapter_{chapter_id_name}.xhtml')
            if context is not None:
                chapter_title = chapter['title']
                # 提取文章标签中的文本
                chapter_text = re.search(r"<body>([\s\S]*?)</body>", context.get_content().decode()).group(1)
                chapter_text = re.sub(r'<h2.*?>.*?</h2>', '', chapter_text)
            else:
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
                chapter_text = "<p>" + chapter_text + "</p>"

            # 在小说内容字符串中添加章节标题和内容
            # 在小说内容字符串中添加章节标题和内容
            text = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{chapter_id_name}.xhtml')
            text.add_item(nav_css1)
            text.add_item(nav_css2)
            text.content = (f'<h2 class="titlecss">{chapter_title}</h2>'
                            f'{chapter_text}')

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

    yaml_data = {
        'qmid': book_id
    }
    yaml_content = yaml.dump(yaml_data)

    # 设置 fqid 元数据
    yaml_item = epub.EpubItem(uid='yaml', file_name='metadata.yaml', media_type='application/octet-stream',
                              content=yaml_content)
    book.add_item(yaml_item)

    epub.write_epub(book_path, book, {})

    print("文件已保存！更新结束！")
    return
