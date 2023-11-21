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


import os

# 导入必要的模块
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import re
import time
from tqdm import tqdm
import public as p
from colorama import Fore, Style, init
import asyncio
import hashlib

# 设置镜像下载地址
os.environ["PYPPETEER_DOWNLOAD_HOST"] = "https://mirrors.huaweicloud.com"
from pyppeteer import launch  # noqa: E402

init(autoreset=True)


# 定义正常模式用来下载7猫小说的函数
def qimao_epub(url, path_choice):
    book_id = re.search(r"/(\d+)/", url).group(1)

    html1, html2 = asyncio.run(get_html(url))

    # 创建epub电子书
    book = epub.EpubBook()

    # 解析网页源码
    soup1 = BeautifulSoup(html1, "html.parser")
    soup2 = BeautifulSoup(html2, "html.parser")

    # 获取小说标题
    title = soup1.find('div', {'class': 'title clearfix'}).find('span', {'class': 'txt'}).text
    # , class_ = "info-name"
    # 替换非法字符
    title = p.rename(title)

    # 获取小说信息
    # info = soup.find("div", class_="page-header-info").get_text()

    # 获取小说简介
    intro = soup1.find('p', class_='intro').get_text().replace(' ', '\n')

    # 获取小说作者
    author_name = soup1.find('div', {'class': 'sub-title'}).find('a').text.strip()

    # 获取封面链接
    img_div = soup1.find('div', {'class': 'wrap-pic'})
    img = img_div.find('img')
    img_url = img['src']

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
    book.add_author(author_name)
    book.add_metadata('DC', 'description', intro)

    # intro chapter
    intro_e = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='hr')
    intro_e.content = (f'<html><head></head><body>'
                       f'<img src="image.jpg" alt="Cover Image"/>'
                       f'<h1>{title}</h1>'
                       f'<p>{intro}</p>'
                       f'</body></html>')
    book.add_item(intro_e)

    # 创建索引
    book.toc = (epub.Link('intro.xhtml', '简介', 'intro'),)
    book.spine = ['nav', intro_e]

    try:
        chapters = soup2.select('li[class^="clearfix ref-catalog-li-"]')

        # 定义目录索引
        toc_index = ()

        chapter_id_name = 0
        # 遍历每个章节链接
        for chapter in tqdm(chapters):
            chapter_id_name += 1
            time.sleep(0.25)
            # 获取章节标题
            chapter_title = chapter.find("span", {"class": "txt"}).get_text().strip()

            # 获取章节网址
            chapter_url = chapter.find("a")["href"]

            # 获取章节 id
            chapter_id = re.search(r"/(\d+)-(\d+)/", chapter_url).group(2)

            # 尝试获取章节内容
            chapter_content = None
            retry_count = 1
            while retry_count < 4:  # 设置最大重试次数
                try:
                    param_string = f"chapterId={chapter_id}id={book_id}{p.sign_key}"
                    sign = hashlib.md5(param_string.encode()).hexdigest()
                    encrypted_content = p.get_qimao(book_id, chapter_id, sign)
                except Exception as e:

                    tqdm.write(Fore.RED + Style.BRIGHT + f"发生异常: {e}")
                    if retry_count == 1:
                        tqdm.write(f"{chapter_title} 获取失败，正在尝试重试...")
                    tqdm.write(f"第 ({retry_count}/3) 次重试获取章节内容")
                    retry_count += 1  # 否则重试
                    continue

                if "data" in encrypted_content and "content" in encrypted_content["data"]:
                    encrypted_content = encrypted_content['data']['content']
                    chapter_content = p.decrypt_qimao(encrypted_content)
                    chapter_content = re.sub('<br>', '\n', chapter_content)
                    break  # 如果成功获取章节内容，跳出重试循环
                else:
                    if retry_count == 1:
                        tqdm.write(f"{chapter_title} 获取失败，正在尝试重试...")
                    tqdm.write(f"第 ({retry_count}/3) 次重试获取章节内容")
                    retry_count += 1  # 否则重试

            if retry_count == 4:
                tqdm.write(f"无法获取章节内容: {chapter_title}，跳过。")
                continue  # 重试次数过多后，跳过当前章节

            # # 提取文章标签中的文本
            # chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)
            chapter_text = f'{chapter_title}\n' + chapter_content
            chapter_text = re.sub(r'\n', '</p><p>', chapter_text)

            # 在小说内容字符串中添加章节标题和内容
            text = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{chapter_id_name}.xhtml')
            text.content = chapter_text

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

    elif path_choice == 0:
        # 定义文件名
        file_path = title + ".epub"

    epub.write_epub(file_path, book, {})

    print("文件已保存！")
    return


async def get_html(url):

    # 创建一个Pyppeteer的Browser实例
    browser = await launch()

    # 创建一个新的页面
    page = await browser.newPage()

    # 访问网页
    await page.goto(url)

    # 等待加载完成
    await page.waitForSelector('.tab-inner')

    # 获取切换前小说信息
    html1 = await page.content()

    # 模拟点击目录按钮，切换网页内容
    # 在页面上执行JavaScript代码，模拟点击目录
    await page.evaluate('''() => {
            var elements = document.getElementsByClassName('tab-inner');
            for(var i=0; i<elements.length; i++){
                elements[i].click();
            }
        }''')

    # 等待页面加载
    await asyncio.sleep(1)

    # 获取网页源代码
    html2 = await page.content()

    await browser.close()

    return html1, html2
