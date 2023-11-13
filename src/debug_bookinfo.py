
# 开发者注意:
# 七猫网页在点击类名为：tab-inner 的”作品目录“按钮后
# 才会显示目录内容

import asyncio
import os
import public as p
from bs4 import BeautifulSoup
import re
from colorama import Fore, Style, init
init(autoreset=True)

# 设置镜像下载地址
os.environ["PYPPETEER_DOWNLOAD_HOST"] = "https://mirrors.huaweicloud.com"
from pyppeteer import launch  # noqa: E402


async def get_book_info(url):
    # 创建一个Pyppeteer的Browser实例
    browser = await launch()

    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已创建浏览器实例")

    # 创建一个新的页面
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})  # 设置窗口大小
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]窗口大小1920x1080")

    # 访问网页
    response = await page.goto(url)
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]HTTP状态码: {response.status}")

    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]正在访问网页")

    # 等待加载完成
    await page.waitForSelector('.tab-inner')

    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]网页已加载完成")
    await page.screenshot({'path': '111.png'})  # 截屏并保存
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]截图已保存至111.png")

# ==================== 获取简介 ====================

    # 在获取目录前，先获取小说简介
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    intro = soup.find('p', class_='intro').get_text().replace(' ', '\n')

    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已获取小说简介")

# ==================== 获取简介结束 ====================

    # 模拟点击目录按钮，切换网页内容
    # 在页面上执行JavaScript代码，模拟点击目录

    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]运行JavaScript代码模拟点击")

    await page.evaluate('''() => {
        var elements = document.getElementsByClassName('tab-inner');
        for(var i=0; i<elements.length; i++){
            elements[i].click();
        }
    }''')

    # 等待页面加载
    await asyncio.sleep(1)

    await page.screenshot({'path': '222.png'})  # 截屏并保存
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]截图已保存至222.png")

    # 获取网页源代码
    html = await page.content()

    # 解析网页源码
    soup = BeautifulSoup(html, "html.parser")

# ==================== 获取标题 ====================

    # 获取小说标题
    title = soup.find('div', {'class': 'title clearfix'}).find('span', {'class': 'txt'}).text
    # , class_ = "info-name"
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已获取小说标题")
    # 替换非法字符
    title = p.rename(title)
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已尝试替换非法字符")

# ==================== 获取标题结束 ====================

# ==================== 获取信息 ====================

    info_div = soup.find('div', class_='wrap-txt')

    # 在每个div标签中，找到类为'btns-wrap clearfix'的div标签
    btn = info_div.find('div', class_='btns-wrap clearfix')

    # 如果找到了btn标签，就从原div标签中移除它
    if btn is not None:
        btn.extract()

    # 获取剩余的文本
    info_text = info_div.get_text()

    # 使用re模块的sub函数，将text中的多个连续的空格替换为一个空格
    info_text = re.sub(r'\s+', ' ', info_text)

    info = info_text + '\n'
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已获取小说信息")

# ==================== 获取信息结束 ====================

    # 匹配类名，找出目录标签，获取目录列表
    chapters = soup.select('li[class^="clearfix ref-catalog-li-"]')
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已获取目录列表")

    # 关闭Browser实例
    await browser.close()
    print(Fore.YELLOW + Style.BRIGHT + f"[DEBUG]已关闭浏览器实例")

    return {'intro': intro, 'title': title, 'info': info, 'chapters': chapters}

# 运行异步任务
# asyncio.run(main())
