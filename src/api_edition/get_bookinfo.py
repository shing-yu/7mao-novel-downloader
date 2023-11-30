
# 开发者注意:
# 七猫网页在点击类名为：tab-inner 的”作品目录“按钮后
# 才会显示目录内容

import asyncio
import os
import public as p
from bs4 import BeautifulSoup
import re

# 设置镜像下载地址
os.environ["PYPPETEER_DOWNLOAD_HOST"] = "https://mirrors.huaweicloud.com"
from pyppeteer import launch  # noqa: E402


async def get_book_info(url):
    # 创建一个Pyppeteer的Browser实例
    browser = await launch()

    # 创建一个新的页面
    page = await browser.newPage()

    # 访问网页
    await page.goto(url)

    # 等待加载完成
    await page.waitForSelector('.tab-inner')

# ==================== 获取简介 ====================

    # 在获取目录前，先获取小说简介
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    intro = soup.find('p', class_='intro').get_text().replace(' ', '\n')

# ==================== 获取简介结束 ====================

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
    html = await page.content()

    # 解析网页源码
    soup = BeautifulSoup(html, "html.parser")

# ==================== 获取标题 ====================

    # 获取小说标题
    title = soup.find('div', {'class': 'title clearfix'}).find('span', {'class': 'txt'}).text
    # , class_ = "info-name"
    # 替换非法字符
    title = p.rename(title)

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

# ==================== 获取信息结束 ====================

    # 匹配类名，找出目录标签，获取目录列表
    chapters = soup.select('li[class^="clearfix ref-catalog-li-"]')

    # 关闭Browser实例
    await browser.close()

    return {'intro': intro, 'title': title, 'info': info, 'chapters': chapters}
