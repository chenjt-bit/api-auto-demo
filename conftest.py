# 在这个文件中创建pytest的钩子函数
# 实现在命令行切换pytest时的环境
import pytest
import os

# 钩子函数是固定命名：pytest_addoption
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "test", "prod"],  # ← 新增这行
        help="指定测试环境：dev,test,prod"
    )

# 🌟 新增这个钩子：在框架初始化时，把参数写进环境变量
def pytest_configure(config):
    # 获取命令行传入的 --env 参数
    env = config.getoption("--env")
    # 将其写入系统环境变量
    os.environ["ENV"] = env
    print(f"\n 正在启动测试，当前环境切换为: {env}")