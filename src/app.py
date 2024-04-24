"""
SL-Novel-Downloader(Qimao Edition), A downloader for www.qimao.com and com.kmxs.reader app novels.
Copyright (C) 2024  shing-yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import os
import time
from sys import exit
import platform
from SLQimao import book
from SLQimao import clear_screen, red, yellow, green, nullproxies
import SLQimao
import requests
from packaging import version
import re
import json
import hashlib
from ebooklib import epub
import sys
import atexit
import shutil


class MainProgram:
    def __init__(self):
        self.__version__: str = "v4.0.0"                     # 主程序版本
        self.mode: str = ""                                     # 模式
        self.book_id: str = "None"                              # 书籍ID（单本）
        self.books: list = []                                   # 书籍ID（批量）
        self.encoding: str = "utf-8"                            # 编码
        self.path: str = ""                                     # 保存路径
        self.user_folder: str = os.path.expanduser("~")         # 用户文件夹
        self.data_folder: str = os.path.join(self.user_folder, "SLQimao")       # 数据文件夹
        # 创建数据文件夹
        os.makedirs(self.data_folder, exist_ok=True)
        self.__rename_old_folder()                              # 重命名旧数据文件夹
        self.eula_path: str = os.path.join(self.data_folder, "eulan.txt")       # EULA文件路径
        self.config_path: str = os.path.join(self.data_folder, "config.json")   # 配置文件路径
        self.eula_url: str = "https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/EULA.md"
        # EULA地址
        self.license_url: str = "https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/LICENSE.md"
        # 开源许可证地址
        self.license_url_zh: str = "https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/LICENSE-ZH.md"
        # 开源许可证中文地址
        self.start_id: str = "None"                             # 起始章节ID
        self.sock = None                                        # 占位端口
        self.update = False                                     # 更新模式标志
        # EPUB资源文件地址
        self.font_file = self.__asset_path("HarmonyOS_Sans_SC_Regular.ttf")
        self.css1_file = self.__asset_path("page_styles.css")
        self.css2_file = self.__asset_path("stylesheet.css")

    @staticmethod
    def __asset_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            # noinspection PyProtectedMember
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("assets"), relative_path)

    def __rename_old_folder(self):
        old_data_folder = os.path.join(self.user_folder, "qimao_data")
        # 移动旧数据文件夹
        if os.path.exists(old_data_folder):
            # os.rename(old_data_folder, os.path.join(self.user_folder, "SLQimao"))
            for file in os.listdir(old_data_folder):
                shutil.move(os.path.join(old_data_folder, file), os.path.join(self.data_folder, file))
            shutil.rmtree(old_data_folder)
            # 使用移动而不是重命名，防止同时存在两个文件夹

    def __check_instance(self):
        # 通过端口检查是否有其他实例正在运行
        import socket

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(('localhost', 52511))
        except socket.error:
            print("另一个程序进程已经在运行中，请勿重复运行")
            print("将在5秒后退出程序")
            for i in range(5, 0, -1):
                print(f"{i}")
                time.sleep(1)
            exit(1)

    def __clear_old(self):
        # 清除旧版本pyppeteer残留
        if platform.system() == "Windows":
            if os.path.exists(os.path.join(self.user_folder, "AppData", "Local", "pyppeteer")):
                import shutil
                shutil.rmtree(os.path.join(self.user_folder, "AppData", "Local", "pyppeteer"))
                print("已自动为您清除旧版本pyppeteer残留")
                input("按Enter键继续...")
        else:
            if os.path.exists(os.path.join(self.user_folder, ".pyppeteer")):
                import shutil
                shutil.rmtree(os.path.join(self.user_folder, ".pyppeteer"))
                print("已自动为您清除旧版本pyppeteer残留")
                input("按Enter键继续...")

    def __check_eula(self):
        def agree_eula():
            # noinspection PyBroadException
            try:
                eula_text_ = requests.get(self.eula_url, timeout=10, proxies=nullproxies).text
                license_text = requests.get(self.license_url, timeout=10, proxies=nullproxies).text
                license_text_zh = requests.get(self.license_url_zh, timeout=10, proxies=nullproxies).text
            except Exception:
                print("获取最终用户许可协议失败，请检查网络连接")
                input("按Enter键继续...\n")
                exit(0)
            eula_date = eula_text_.splitlines()[3]
            while True:
                print(yellow + "在继续使用之前，请阅读并同意以下协议：")
                print("1. 最终用户许可协议（EULA）")
                print("2. AGPL-3.0开源许可证 (3. 中文译本（无法律效力）)")
                print("输入序号以查看对应协议，输入yes表示同意，输入no以退出程序。")
                print("您可以随时在程序内撤回同意")
                input_num_ = input("请输入：")
                if input_num_ == "1":
                    clear_screen()
                    print(eula_text_)
                    input("按Enter键继续...")
                    clear_screen()
                elif input_num_ == "2":
                    clear_screen()
                    print(license_text)
                    input("按Enter键继续...")
                    clear_screen()
                elif input_num_ == "3":
                    clear_screen()
                    print(license_text_zh)
                    input("按Enter键继续...")
                    clear_screen()
                elif input_num_ == "yes":
                    with open(self.eula_path, "w", encoding="utf-8") as f_:
                        eula_txt_ = f"""eula_url: {self.eula_url}
license_url: {self.license_url}
agreed: 
yes
eula_date: 
{eula_date}

"""
                        f_.write(eula_txt_)
                    break
                elif input_num_ == "no":
                    print("感谢您的使用！")
                    exit(0)
                else:
                    clear_screen()
                    print("输入无效，请重新输入。")
        if os.path.exists(self.eula_path):
            with open(self.eula_path, "r", encoding="utf-8") as f:
                eula_txt = f.read()
            agreed = eula_txt.splitlines()[3]
            if agreed != "yes":
                agree_eula()
                return True
            eula_date_old = eula_txt.splitlines()[5]
            # noinspection PyBroadException
            try:
                eula_text = requests.get(self.eula_url, timeout=10, proxies=nullproxies).text
            except Exception:
                print("获取最终用户许可协议失败，请检查网络连接")
                input("按Enter键继续...\n")
                exit(0)
            eula_date_new = eula_text.splitlines()[3]
            if eula_date_old != eula_date_new:
                while True:
                    print(yellow + "最终用户许可协议（EULA）已更新")
                    print(yellow + "在继续使用之前，请阅读并同意以下协议：")
                    print("1. 最终用户许可协议（EULA）")
                    print("输入序号以查看对应协议，输入yes表示同意，输入no以退出程序。")
                    print("您可以随时在程序内撤回同意")
                    input_num = input("请输入：")
                    if input_num == "1":
                        clear_screen()
                        print(eula_text)
                        input("按Enter键继续...")
                        clear_screen()
                    elif input_num == "yes":
                        with open(self.eula_path, "w", encoding="utf-8") as f:
                            eula_txt = f"""eula_url: {self.eula_url}
license_url: {self.license_url}
agreed: 
yes
eula_date: 
{eula_date_new}

"""
                            f.write(eula_txt)
                        break
                    elif input_num == "no":
                        print("感谢您的使用！")
                        exit(0)
                    else:
                        clear_screen()
                        print("输入无效，请重新输入。")
        else:
            agree_eula()
            return True
        return True

    @staticmethod
    def clear_stdin():
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            import sys
            import termios
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)

    def __check_update(self):
        def compare_versions(version1: str, version2: str) -> int:
            # 使用packaging模块进行版本比较
            v1 = version.parse(version1)
            v2 = version.parse(version2)

            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        owner = "xingyv1024"
        repo = "7mao-novel-downloader"
        api_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/latest"

        print("正在检查更新...")
        print(f"当前版本: {self.__version__}")

        if 'dev' in self.__version__ or 'alpha' in self.__version__ or 'beta' in self.__version__:
            print(yellow + '测试版本，检查更新已关闭！')
            print(yellow + '注意！您正在使用测试/预览版本！\n该版本可能极不稳定，不建议在生产环境中使用！')
            input('按Enter键继续...')
            return

        # noinspection PyBroadException
        try:
            # 发送GET请求以获取最新的发行版信息
            response = requests.get(api_url, timeout=5, proxies=nullproxies)

            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                input("按Enter键继续...\n")
                return 0
            release_info = response.json()
            if "tag_name" in release_info:
                latest_version = release_info["tag_name"]
                release_describe = release_info["body"]
                print(f"最新的发行版是：{latest_version}")
                result = compare_versions(self.__version__, latest_version)
                if result == -1:
                    # 检测是否是重要更新
                    if "!important!" in release_describe:
                        # 如果是，则弹窗提示
                        import tkinter as tk
                        from tkinter import messagebox
                        root = tk.Tk()

                        # 点击确认跳转到下载页面
                        def open_url():
                            import webbrowser
                            webbrowser.open("https://gitee.com/xingyv1024/7mao-novel-downloader/releases/latest")
                            exit(0)

                        root.withdraw()
                        result = messagebox.askokcancel("重要更新",
                                                        f"检测到重要更新！\n更新内容:\n{release_describe}\n点击确定前往下载",
                                                        icon="warning")
                        if result:
                            open_url()
                        root.destroy()
                        return
                    elif "!very important!" in release_describe:
                        # 如果是，则弹窗提示
                        import tkinter as tk
                        from tkinter import messagebox
                        root = tk.Tk()

                        # 点击确认跳转到下载页面
                        def open_url():
                            import webbrowser
                            webbrowser.open("https://gitee.com/xingyv1024/7mao-novel-downloader/releases/latest")
                            exit(0)

                        root.withdraw()
                        # 此更新不可取消
                        messagebox.showinfo("非常重要更新",
                                            f"检测到非常重要更新！\n更新内容:\n{release_describe}\n点击确定前往下载")
                        open_url()
                        root.destroy()
                        exit(0)
                    elif "|notification|" in release_describe:
                        print(f"检测到通知：\n{release_describe}")
                        input("按Enter键继续...\n")
                        return
                    print(
                        "检测到新版本\n更新可用！请到 https://gitee.com/xingyv1024/7mao-novel-downloader/releases/latest 下载最新版")
                    print(f"更新内容:\n{release_describe}")
                    input("按Enter键继续...\n")
                else:
                    print("您正在使用最新版")

            else:
                print("未获取到发行版信息。")
                input("按Enter键继续...\n")

        except BaseException:
            print(":(  检查更新失败...")
            input("按Enter键继续...\n")

    @staticmethod
    def _print_usage():
        print("欢迎使用", end=" ")
        print(yellow + "星弦小说下载器七猫版")
        print("""用户须知：
此程序开源免费，如果您付费获取，请您立即举报商家。
此程序开源部分使用AGPL-3.0许可证，详情到更多中查看。

使用本程序代表您已阅读并同意本程序最终用户许可协议(EULA)（初次启动时已展示，可在更多中再次阅读）。
（包括不得销售此程序副本，提供代下载服务需明确告知用户开源地址等）

QQ： 外1群：149050832  外2群：667146297
如果想要指定开始下载的章节，请在输入目录页链接时按Ctrl+C。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。
使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目协作者、贡献者无关。
作者不对因使用该程序而导致的任何损失或损害承担任何责任。
""")

    def __give_menu(self):
        while True:
            clear_screen()
            flag2 = True
            self._print_usage()
            print("请选择以下操作：")
            print("1. 进入正常模式")
            print("2. 进入自动批量模式")
            print("3. 进入分章保存模式")
            print("4. 进入Epub电子书模式")
            print("5. 查看更多")
            print("6. 更新已下载的小说")
            print("7. 查看贡献（赞助）者名单")
            print("8. 撤回同意/重置默认路径")
            print("9. 查看详细版本信息")
            choice = input("请输入您的选择（1~9）:（默认“1”）\n")

            # 通过用户选择，决定模式，给mode赋值
            if not choice:
                choice = '1'

            if choice == '1':
                self.mode = "normal"
                clear_screen()
                print("您已进入正常下载模式：")
                break
            elif choice == '2':
                self.mode = "batch"
                clear_screen()
                print("您已进入自动批量下载模式:")
                break
            elif choice == '3':
                self.mode = "chapter"
                clear_screen()
                print("您已进入分章保存模式:")
                break
            elif choice == '4':
                self.mode = "epub"
                clear_screen()
                print("您已进入EPUB模式，将输出epub电子书文件。\n")
                # print("EPUB模式正在开发中，敬请期待\n")
                break
            elif choice == '5':
                clear_screen()
                print("""作者：星隅（shing-yu）
    
本软件开源部分使用GNU Affero通用公共许可证v3.0（AGPL-3.0）发布；
你可以在以下位置找到该许可证的副本：
https://www.gnu.org/licenses/agpl-3.0.html

根据AGPLv3的规定，您有权在遵循许可证的前提下自由使用、修改和分发本软件。
请注意，根据许可证的要求，任何对本软件的修改和分发都必须包括原始的版权声明和AGPLv3的完整文本，且必须提供源代码。

本软件提供的是按"原样"提供的，没有任何明示或暗示的保证，包括但不限于适销性和特定用途的适用性。作者不对任何直接或间接损害或其他责任承担任何责任。在适用法律允许的最大范围内，作者明确放弃了所有明示或暗示的担保和条件。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目贡献者无关。作者不对因使用该程序而导致的任何损失或损害承担任何责任。

请在使用本程序之前确保遵守相关法律法规和网站的使用政策，如有疑问，请咨询法律顾问。

ibxff所作用户脚本:https://greasyfork.org/zh-CN/scripts/479460
（对于4.0版本及后续版本，已不再使用以上脚本中的方式，但仍感谢ibxff的代码对本项目的启发）
开源仓库地址:https://github.com/xing-yv/7mao-novel-downloader
gitee地址:https://gitee.com/xingyv1024/7mao-novel-downloader
作者B站主页:https://space.bilibili.com/1920711824
提出反馈:https://github.com/shing-yu/7mao-novel-downloader/issues/new
(请在右侧Label处选择issue类型以得到更快回复)

最终用户许可协议(EULA)：https://gitee.com/xingyv1024/fanqie-novel-download/blob/main/EULA.md
""")
                input("按Enter键返回...")
                clear_screen()
            elif choice == '6':
                self.update = True
                self.__update()
                break
            elif choice == '7':
                clear_screen()
                contributors_url = 'https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/CONTRIBUTORS.md'
                try:
                    contributors = requests.get(contributors_url, timeout=5, proxies=nullproxies)

                    # 检查响应状态码
                    if contributors.status_code == 200:
                        contributor_md_content = contributors.text
                        print(contributor_md_content)
                    else:
                        print(f"获取贡献名单失败，HTTP响应代码: {contributors.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"发生错误: {e}")
                input("按Enter键返回...")
                clear_screen()
            elif choice == '8':
                clear_screen()
                cho = input("1-> 撤回同意  2-> 重置默认路径\n")
                if cho == '1':
                    while True:
                        sure = input("您确定要撤回同意吗(yes/no)(默认:no): ")
                        if not sure:
                            sure = "no"
                        if sure.lower() == "yes":
                            break
                        elif sure.lower() == "no":
                            flag2 = False
                            break
                        else:
                            print("输入无效，请重新输入。")
                    if flag2 is False:
                        clear_screen()
                        continue
                    else:
                        with open(self.eula_path, "w", encoding="utf-8") as f:
                            eula_txt = f"""eula_url: {self.eula_url}
license_url: {self.license_url}
agreed: 
no
eula_date: 
None

"""
                            f.write(eula_txt)
                        print("您已撤回同意")
                        input("按Enter键退出程序...")
                        exit(0)
                elif cho == '2':
                    os.remove(self.config_path)
                    print("已重置默认路径")
                    input("按Enter键退出程序...")
                    exit(0)
                else:
                    print("输入无效")
                    input("按Enter键退出程序...")
                    exit(0)
            elif choice == '9':
                clear_screen()
                print(f"系统版本: {platform.platform()}")
                print(f"当前用户名: {os.getlogin()}")
                print(f"主程序框架版本: {self.__version__}")
                print(f"SLQimao内核版本: {SLQimao.__version__}")
                print(f"程序文件路径: {os.path.abspath(__file__)}")
                print(f"数据文件夹路径: {self.data_folder}")
                input("按Enter键返回...")
            else:
                print("无效的选择，请重新输入。")

    @staticmethod
    def __deal_url(url):
        try:
            if url.isdigit():
                return url
            elif "www.qimao.com/shuku/" in url:
                return re.search(r"www.qimao.com/shuku/(\d+)", url).group(1)
            elif "app-share.wtzw.com" in url:
                return re.search(r"article-detail/(\d+)", url).group(1)
            else:
                return None
        except AttributeError:
            return None

    def __get_param(self):
        # 判断是否批量模式
        if self.mode == "batch":
            while True:
                if not os.path.exists('urls.txt'):
                    with open('urls.txt', 'x', encoding='utf-8'):
                        pass
                print("请在程序同文件夹(或执行目录)下的urls.txt中，以每行一个的形式写入链接/ID")
                try:
                    os.startfile('urls.txt')
                    print("您正在使用Windows，文件应该已自动弹出窗口")
                except AttributeError:
                    print("您正在使用非Windows系统，请手动打开文件")
                input("完成后请按Enter键继续:")
                status = self.__batch_ready()
                if not status:
                    print("请重新在urls.txt中写入链接/ID")
                    continue
                break
        else:
            # 输入链接/ID
            while True:
                try:
                    url = input("请输入链接/ID，或输入s以进入搜索模式：\n")
                    if url.lower() == 's':
                        print("正在进入搜索模式...")
                        self.book_id = book.search()
                        if not self.book_id:
                            print(yellow + "\n您取消了搜索，请重新输入。")
                            continue
                        break
                    else:
                        self.book_id = self.__deal_url(url)
                        if not self.book_id:
                            print(yellow + "无法识别的内容，请重新输入。")
                            continue
                        break
                except KeyboardInterrupt:
                    print(yellow + "由于4.0版本底层变更，指定起始章节不再能加速下载，程序仍会下载全部章节，只在合并时跳过不需要的章节。")
                    if self.mode == "epub":
                        print(yellow + "EPUB模式不支持指定起始章节")
                        input("按Enter键继续...")
                    elif self.mode == "chapter":
                        print(yellow + "分章模式不支持指定起始章节ID，请手动删除不需要的章节文件")
                        input("按Enter键继续...")
                    else:
                        while True:
                            start_chapter_id = input("您已按下Ctrl+C，请输入起始章节的id(输入help以查看帮助):\n")
                            if start_chapter_id == 'help':
                                print("\n打开小说章节阅读界面，上方链接中第二串的数字即为章节id\n请输入您想要开始下载的章节的id\n")
                                continue
                            elif start_chapter_id.isdigit():
                                self.start_id = start_chapter_id
                                break
                            else:
                                print("无效的输入，请重新输入")

        # 选择编码
        while True:
            if self.mode == "epub":
                break
            txt_encoding_num = input("请输入保存文件所使用的编码(默认:1)：1 -> utf-8 | 2 -> gb2312 | 3-> 输入编码\n")

            if not txt_encoding_num:
                txt_encoding_num = '1'

            # 检查用户选择文件编码是否正确
            if txt_encoding_num == '1':
                self.encoding = 'utf-8'
                break
            elif txt_encoding_num == '2':
                self.encoding = 'gb2312'
                break
            elif txt_encoding_num == '3':
                print("手动输入编码")
                while True:
                    print("支持的编码：https://docs.python.org/3/library/codecs.html#standard-encodings")
                    self.encoding = input("请输入编码：")
                    # 验证编码是否有效
                    try:
                        "测试".encode(self.encoding)
                    except LookupError:
                        print("无效的编码，请重新输入")
                        continue
                    break
                break
            else:
                print("输入无效，请重新输入。")
        if self.mode != "epub":
            print(f"您选择的编码是：{self.encoding}")

        # 询问保存路径
        while True:

            type_path = input("是否自行选择保存路径(yes/no)(默认:no):")

            if not type_path:
                type_path = "no"

            if type_path.lower() == "yes":
                print("您选择了自定义保存路径，请在弹出窗口中选择保存路径。")
                self.path = self.__get_path(custom=True)
                break

            elif type_path.lower() == "no":
                if self.mode == "batch" or self.mode == "chapter":
                    print("您未选择自定义保存路径，请在获取完成后到默认路径下output文件夹寻找文件。")
                    print("(初始默认路径为程序所在文件夹，命令行为执行目录)")
                    self.path = self.__get_path(custom=False)
                else:
                    print("您未选择自定义保存路径，请在获取完成后到默认路径下寻找文件。")
                    print("(初始默认路径为程序所在文件夹，命令行为执行目录)")
                    self.path = self.__get_path(custom=False)
                break

            else:
                print("输入无效，请重新输入。")
                continue

    def __get_path(self, custom):
        if custom:
            import tkinter as tk
            from tkinter import filedialog
            # 创建一个Tkinter窗口，但不显示它
            root = tk.Tk()
            root.withdraw()
            while True:
                # 弹出选择窗口
                path = filedialog.askdirectory()
                # 检查用户是否取消了对话框
                if not path:
                    print("您没有选择保存路径，请重新选择！")
                    continue
                else:
                    print("已选择保存路径")
                    break
            cho = input("是否使用此路径覆盖此模式默认保存路径（y/n(d)）？")
            if not cho or cho == "n":
                pass
            else:
                # 如果配置文件不存在，则创建
                if not os.path.exists(self.config_path):
                    with open(self.config_path, "w") as c:
                        json.dump({"path": {f"{self.mode}": path}}, c)
                else:
                    with open(self.config_path, "r") as c:
                        config = json.load(c)
                    config["path"][f"{self.mode}"] = path
                    with open(self.config_path, "w") as c:
                        json.dump(config, c)
            root.destroy()
            return path
        else:
            # 检测是否有默认路径
            if not os.path.exists(self.config_path):
                if self.mode == "batch" or self.mode == "chapter":
                    return "output"
                else:
                    return "."  # 默认路径为程序所在文件夹
            else:
                with open(self.config_path, "r") as c:
                    config = json.load(c)
                if f"{self.mode}" in config["path"]:
                    return config["path"][f"{self.mode}"]
                else:
                    if self.mode == "batch" or self.mode == "chapter":
                        return "output"
                    else:
                        return "."  # 默认路径为程序所在文件夹

    def __batch_ready(self):
        with open('urls.txt', 'r', encoding='utf-8') as f:
            urls = f.readlines()
        for i, url in enumerate(urls):
            if not url:
                # 跳过空行
                continue
            book_id = self.__deal_url(url)
            if not book_id:
                print(red + f"无法识别的内容：第{i + 1}行，{url}")
                return False
            self.books.append(book_id)
        if not self.books:
            print(red + "urls.txt内容为空，请检查")
            return False
        return True

    def __update(self):
        print(yellow + "由于4.0版本底层变更，更新功能不再可用，程序实质上进行的是重新下载并覆盖")

        def onefile():
            txt_file_path = None
            while True:
                m_epub = False
                # 提示用户输入路径
                user_path = input("请将要更新的小说拖动到窗口中，然后按 Enter 键:（支持4.0新版本下载的epub）\n")

                if ".txt" in user_path:
                    pass
                elif ".epub" in user_path:
                    m_epub = True
                    print(yellow + "EPUB更新模式处于测试阶段，如发现问题请及时反馈。")
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
            update(txt_file_path, m_epub)

        def batch():
            # 指定小说文件夹
            novel_folder = "更新"
            os.makedirs(novel_folder, exist_ok=True)
            input("请在程序目录下”更新“文件夹内放入需更新的文件（支持4.0新版本下载的epub）\n按Enter键继续...")
            novel_files = [file for file in os.listdir(novel_folder) if file.endswith(".txt") or file.endswith(".epub")]
            if not novel_files:
                print("没有可更新的文件")
                return
            for novel_file in novel_files:
                update(os.path.join(novel_folder, novel_file), novel_file.endswith(".epub"))

        def update(file_path: str, m_epub):
            novel_name = None
            try:
                if m_epub is True:
                    # 根据元信息获取小说id
                    epubo = epub.read_epub(file_path, options={"ignore_ncx": True})
                    novel_name = epubo.title
                    book_id = epubo.get_metadata("DC", "bookid")[0][0]
                    novel = book.Book(book_id)
                    novel.ready()
                    novel.toepub(os.path.dirname(file_path), font=self.font_file,
                                 css1=self.css1_file, css2=self.css2_file)
                    return

                txt_file = os.path.basename(file_path)

                upd_file_path = os.path.join(self.data_folder, txt_file.replace(".txt", ".upd"))
                novel_name = txt_file.replace(".txt", "")

                if os.path.exists(upd_file_path):

                    print(f"正在尝试更新: {novel_name}")
                    # 读取用于更新的文件元数据
                    with open(upd_file_path, 'r') as file:
                        lines = file.readlines()

                    # 保存上次更新时间和上次章节id到变量
                    last_update_time = lines[0].strip()
                    self.book_id = self.__deal_url(lines[1].strip())
                    last_chapter_id = lines[2].strip()
                    encoding = lines[3].strip()
                    if len(lines) >= 5:
                        save_sha256 = lines[4].strip()
                        skip_hash = 0
                    else:
                        print(yellow + "此小说可能由老版本下载，跳过hash校验")
                        save_sha256 = None
                        skip_hash = 1
                    hash_sha256 = hashlib.sha256()
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_sha256.update(chunk)
                    fact_sha256 = hash_sha256.hexdigest()
                    if skip_hash == 0:
                        if fact_sha256 != save_sha256:
                            print(red + "hash校验未通过！")
                            while True:
                                upd_choice = input(f"这往往意味着文件已被修改，是否继续更新？(yes/no):")
                                if upd_choice == "yes":
                                    break
                                elif upd_choice == "no":
                                    print(red + "更新已取消")
                                    return
                                else:
                                    print("输入错误，请重新输入")
                        else:
                            print(green + "hash校验通过！")
                    print(f"上次更新时间{last_update_time}")
                    novel = book.Book(self.book_id)
                    novel.ready()
                    if novel.catalog[-1]["id"] == last_chapter_id:
                        print(f"{novel_name} 已是最新，不需要更新。\n")
                        return
                    novel.totxt(os.path.dirname(file_path), encoding)
                    print(f"{novel_name} 已更新完成。\n")
                    novel.write_update(self.data_folder)
                else:
                    print(f"{txt_file} 不是通过此工具下载，无法更新")
            except Exception as e:
                print(red + f"小说{novel_name}更新失败！Error: {e}")
                return

        # 请用户选择更新模式
        while True:
            update_mode = input("请选择更新模式:1 -> 单个更新 2-> 批量更新\n")
            if not update_mode:
                update_mode = '1'
            if update_mode == '1':
                onefile()
                return
            elif update_mode == '2':
                batch()
                return
            else:
                print("无效的选择，请重新输入。")

    def __download(self):
        os.makedirs(self.path, exist_ok=True)

        def normal():
            try:
                novel = book.Book(self.book_id)
                novel.ready()
                novel.totxt(self.path, self.encoding, self.start_id)
                novel.write_update(self.data_folder)
            except Exception as e:
                print(red + f"下载失败！Error: {e}")

        def batch():
            for book_id in self.books:
                try:
                    novel = book.Book(book_id)
                    novel.ready()
                    novel.totxt(self.path, self.encoding)
                    novel.write_update(self.data_folder)
                except Exception as e:
                    print(red + f"下载失败！跳过此小说！Error: {e}")
                    continue

        def chapter():
            try:
                novel = book.Book(self.book_id)
                novel.ready()
                novel.totxt_ecs(self.path, self.encoding)
            except Exception as e:
                print(red + f"下载失败！Error: {e}")

        def epub_():
            try:
                novel = book.Book(self.book_id)
                novel.ready()
                novel.toepub(self.path, font=self.font_file, css1=self.css1_file, css2=self.css2_file)
            except Exception as e:
                print(red + f"下载失败！Error: {e}")

        # match self.mode:
        #     case "normal":
        #         normal()
        #     case "batch":
        #         batch()
        #     case "chapter":
        #         chapter()
        #     case "epub":
        #         epub_()
        if self.mode == "normal":
            normal()
        elif self.mode == "batch":
            batch()
        elif self.mode == "chapter":
            chapter()
        elif self.mode == "epub":
            epub_()

    def run(self):
        self.__check_instance()
        self.__check_eula()
        self.__check_update()
        self.__clear_old()
        while True:
            self.__give_menu()
            try:
                if self.update:
                    self.clear_stdin()
                    input("按Enter键退出程序（按Ctrl+C重新开始）...")
                    break
                self.__get_param()
                self.__download()
                self.clear_stdin()
                print("下载任务结束")
                input("按Enter键退出程序（按Ctrl+C重新开始）...")
                break
            except KeyboardInterrupt:
                clear_screen()
                continue
        exit(0)


if __name__ == "__main__":
    def free_port():
        # 退出时释放端口
        if main.sock:
            main.sock.close()
    atexit.register(free_port)
    main = MainProgram()
    main.run()
