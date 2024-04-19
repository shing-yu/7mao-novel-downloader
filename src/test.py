import pexpect
import sys
import time

test_book_url = 'https://www.qimao.com/shuku/1815772/'

process = pexpect.spawn('python3 app.py', encoding='utf-8', timeout=10)
process.logfile = sys.stdout
process.expect('按Enter键继续...')
process.sendline('')
# mode 1 test
process.expect('请输入您的选择（1~9）:（默认“1”）')
process.sendline('1')
process.expect('请输入链接/ID，或输入s以进入搜索模式：')
process.sendline(test_book_url)
process.sendline('')
process.sendline('')
# process.expect('按Enter键退出程序（按Ctrl+C重新开始）...')
time.sleep(10)
process.sendcontrol('c')
# mode 2 test
process.expect('请输入您的选择（1~9）:（默认“1”）')
process.sendline('2')
input('urls.txt准备好后按Enter键继续测试')
process.sendline('')
process.sendline('')
process.sendline('')
# process.expect('按Enter键退出程序（按Ctrl+C重新开始）...')
time.sleep(10)
process.sendcontrol('c')
# mode 3 test
process.expect('请输入您的选择（1~9）:（默认“1”）')
process.sendline('3')
process.expect('请输入链接/ID，或输入s以进入搜索模式：')
process.sendline(test_book_url)
process.sendline('')
process.sendline('')
# process.expect('按Enter键退出程序（按Ctrl+C重新开始）...')
time.sleep(10)
process.sendcontrol('c')
# mode 4 test
process.expect('请输入您的选择（1~9）:（默认“1”）')
process.sendline('4')
process.expect('请输入链接/ID，或输入s以进入搜索模式：')
process.sendline(test_book_url)
process.sendline('')
# process.expect('按Enter键退出程序（按Ctrl+C重新开始）...')
time.sleep(10)
process.sendcontrol('c')
# mode 6 test
process.expect('请输入您的选择（1~9）:（默认“1”）')
process.sendline('6')
process.expect('请选择更新模式:1 -> 单个更新 2-> 批量更新')
process.sendline('1')
process.sendline('废土之上.txt')
process.sendline('')
# done
print('All tests passed')
