# SL-Novel-Downloader(Qimao Edition)
**星弦小说下载器（七猫版）**
支持下载几乎所有七猫免费小说app/网站的小说，支持txt与epub格式，拥有极快的下载速度。
QQ： 外1群：149050832  外2群：667146297  TG: https://t.me/FQTool
感谢贡献（赞助）者们对本项目的支持，你可以在[此处](https://github.com/shing-yu/7mao-novel-downloader/blob/main/CONTRIBUTORS.md)获取贡献和赞助者名单。

使用方法：[点击查看详细教程](https://www.yuque.com/xinv/main/fv1r551p2qcfapuh)

## 许可证

**注意：本项目在v4.0.0版本更新之后，开源部分已经更改为GNU Affero通用公共许可证v3.0（AGPL-3.0）许可证。**  
如果您不想使用新版本的许可证，您可以在[v3.0.0分支（只读）](https://github.com/shing-yu/7mao-novel-downloader/tree/v3.0.0)继续获取旧版本的代码，并遵守GPL-3.0许可证。

本项目开源部分基于AGPL-3.0开源，您可以在[此处](https://www.gnu.org/licenses/agpl-3.0.html)获取该许可证的副本。

出于保护因素，项目内核模块的核心部分代码经社区讨论，决定暂时保持私有状态。（不包括非核心部分代码）  
如果您想要参与内核核心模块的开发，或获取内核核心模块的源代码，请向任一社区成员提交申请。

对于不遵守许可证的行为，我们将列入[项目耻辱柱](https://github.com/shing-yu/7mao-novel-downloader/blob/main/HallOfShame.md)。

## 关于4.0+版本对Windows7操作系统的支持

本项目在4.0.0版本，虽然仍会以非CI构建方式提供适用于Windows7的二进制文件，但不再提供对Windows7的支持（包括但不限于单独BUG修复、功能更新等）。  
4.0.0之后的版本中，如无全平台严重bug，将不再提供适用于Windows7的二进制文件。
建议您尽快升级到Windows10或更高版本，以获得更好的体验。

## 贡献

我们非常欢迎并感谢所有的贡献者。如果你对这个项目有兴趣并希望做出贡献，以下是一些你可以参与的方式：

### 报告问题

如果你在使用过程中发现了问题，或者有任何改进的建议，欢迎通过 [Issues](https://github.com/shing-yu/7mao-novel-downloader/issues) 页面提交问题或建议。

### 提交代码

如果你想直接改进代码，可以 [Fork 本项目](https://github.com/shing-yu/7mao-novel-downloader/fork)，然后提交 Pull Request。

在提交 Pull Request 之前：

- 确保代码可以通过test.py中的所有测试。
- 请确保您的代码符合Python的[PEP8](https://www.python.org/dev/peps/pep-0008/)规范。
- 请确保您的代码在所有操作系统上都能正常运行。
- 如果您想在本项目中添加新功能，请先创建一个issue，并在issue中详细描述您的想法。
- 建议：在您的代码中添加明确注释，以帮助其他人理解。
- 可选：在您的commit信息中使用[约定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)规范。
- 可选：使用 GPG 密钥签名您的提交。  

(使用可选项可以帮助我们快速审查您的Pull Request。)

我们会将您的贡献计入贡献者名单。您可以在[此处](https://github.com/shing-yu/7mao-novel-downloader/blob/main/CONTRIBUTORS.md)获取贡献和赞助者名单。
感谢您的贡献！

## 自行封装&修改

在封装&修改此脚本之前，请确保已安装以下内容：

- Python 3.x（3.0-） 
- OR
- Python 3.10+（4.0+）
- 所需的Python库：requests、beautifulsoup4、packaging、ebooklib

您可以从从src目录获取程序源代码

您可以使用pip安装所需的库：

```shell
pip install -r requirements.txt
```

## 免责声明

此程序旨在用于与Python网络爬虫和网页处理技术相关的教育和研究目的。不应将其用于任何非法活动或侵犯他人权利的行为。用户对使用此程序引发的任何法律责任和风险负有责任，作者和项目贡献者不对因使用程序而导致的任何损失或损害承担责任。

在使用此程序之前，请确保遵守相关法律法规以及网站的使用政策，并在有任何疑问或担忧时咨询法律顾问。

## 鸣谢

感谢[byddgithubzh](https://github.com/byddgithubzh)为4.0+版本提供了全新的API接口。  
感谢[ibxff](https://github.com/ibxff)([GreasyFork](https://greasyfork.org/zh-CN/users/995944-ibxff))所作[脚本](https://greasyfork.org/zh-CN/scripts/479460)为本项目提供了最初的启发。  
最后，感谢全球所有参与开源项目的贡献者，你们为开源社区的繁荣和发展做出了巨大的贡献。

## Star趋势

![Stars](https://api.star-history.com/svg?repos=shing-yu/7mao-novel-downloader&type=Date)

## 赞助

如果您想要支持我的开发，欢迎赞助，感谢您的支持！

[爱发电](https://afdian.net/a/shingyu)

或者使用微信扫描下方二维码赞助：

<img src="https://pic2.ziyuan.wang/user/guest/2024/04/202310091746639_4d914a1707164.png" style="zoom:30%;"  alt=""/>
