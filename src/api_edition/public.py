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
import hashlib
import random


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


headers_dict = {}


def get_qimao(book_id, chapter_id, sign):
    if book_id not in headers_dict:
        headers_dict[book_id] = get_headers(book_id)
    headers = headers_dict[book_id]
    response = requests.get(f"https://api-ks.wtzw.com/api/v1/chapter/content?"
                            f"id={book_id}&chapterId={chapter_id}&sign={sign}",
                            headers=headers)
    return response.json()


sign_key = 'd3dGiJc651gSQ8w1'


def asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("assets"), relative_path)
