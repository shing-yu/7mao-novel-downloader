import function as f
from sys import exit

version = "v3.0.0-alpha"

# 检查另一个实例是否正在运行
f.check_instance()

# 检查EULA
f.check_eula()
f.clear_screen()

# 检查更新
f.check_update(version)
f.clear_screen()

f.clear_old()

while True:
    # 程序开始
    f.start()

    if f.return_info is None:
        # 清除输入缓存
        f.clear_stdin()
        try:
            input("按Enter键退出（按Ctrl+C重新开始）...")
        except KeyboardInterrupt:
            f.clear_screen()
            continue
        exit(0)
    else:
        f.get_parameter(retry=True)
