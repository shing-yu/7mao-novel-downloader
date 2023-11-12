import public as p
import requests
from bs4 import BeautifulSoup
import re

# 初始化“ua”
ua = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0.0.0 "
    "Safari/537.36"
)

headers = {
    "User-Agent": ua
}

# 获取网页源码
response = requests.get('https://www.qimao.com/shuku/222767/', headers=headers)
html = response.text
print(html)

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

intro = soup.find('p', class_='intro').get_text().replace(' ', '\n')
# print(intro)

# 使用正则表达式匹配类名
# pattern = re.compile('clearfix ref-catalog-li.*')
# clearfix ref-catalog-li-16480917400001
li_tags = soup.find_all('li', {'class': 'clearfix ref-catalog-li-16480917400001'})

# 打印匹配到的li标签
for li in li_tags:
    print(str(li))
