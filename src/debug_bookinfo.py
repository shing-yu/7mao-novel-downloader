import asyncio
from pyppeteer import launch
# from pyppeteer import chromium_downloader
import public as p
# import requests
from bs4 import BeautifulSoup
import re
# 更换阿里源下载chromium
# chromium_downloader.BASE_URL = 'http://mirrors.huaweicloud.com/chromium-browser-snapshots/'
# TODO: 实现DEBUG模式的书籍信息获取代码

async def main():
    # 创建一个Pyppeteer的Browser实例
    browser = await launch()

    # 创建一个新的页面
    page = await browser.newPage()

    # 访问网页
    url = 'https://www.qimao.com/shuku/222767/'  # 请替换为你需要爬取的网页URL
    await page.goto(url)
    await asyncio.sleep(5)

    await page.waitForSelector('.tab-inner')

    # 获取页面截图
    screenshot2 = await page.screenshot()

    # 将截图数据写入到文件中
    with open('screenshot2.png', 'wb') as f:
        f.write(screenshot2)

    # # 在这里添加你的点击操作
    # await page.click('.tab-inner')
    # 在页面上执行JavaScript代码
    await page.evaluate('''() => {
        var elements = document.getElementsByClassName('tab-inner');
        for(var i=0; i<elements.length; i++){
            elements[i].click();
        }
    }''')

    # 等待页面加载
    # await page.waitForTimeout(5000)
    await asyncio.sleep(5)

    # 获取页面截图
    screenshot = await page.screenshot()

    # 将截图数据写入到文件中
    with open('screenshot.png', 'wb') as f:
        f.write(screenshot)

    # 获取网页源代码
    html = await page.content()

    print(str(html))

    # 你可以在这里使用BeautifulSoup解析html，获取你需要的数据
    # 解析网页源码
    soup = BeautifulSoup(html, "html.parser")

    # 获取小说标题
    title = soup.find('div', {'class': 'title clearfix'}).find('span', {'class': 'txt'}).text
    # , class_ = "info-name"
    # 替换非法字符
    title = p.rename(title)

    # print(title)
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

    # print(info)

    # intro = soup.find('p', class_='intro').get_text().replace(' ', '\n')
    # print(intro)

    # 使用正则表达式匹配类名
    # pattern = re.compile('clearfix ref-catalog-li.*')
    # clearfix ref-catalog-li-16480917400001
    # li_tags = soup.find_all('li', {'class': pattern})
    li_tags = soup.select('li[class^="clearfix ref-catalog-li-"]')
    print("目录标签数" + str(len(li_tags)))

    # 打印匹配到的li标签
    # for li in li_tags:
    #     print(str(li))

    # 关闭Browser实例
    await browser.close()

# 运行异步任务
asyncio.run(main())
