# config/settings.py
# 配置一些基本信息的公共信息，类似全局变量

import os
from dotenv import load_dotenv

# 1. 先读取当前要切到哪个环境（默认是 dev）
load_dotenv(".env")
current_env = os.getenv("ENV", "dev")

# 2. 根据当前环境，加载对应的配置文件
# 比如 current_env 是 "dev"，这里就会去加载 ".env.dev"
load_dotenv(f".env.{current_env}", override=True)

# 3. 把配置读取到系统变量里
BASE_URL = os.getenv("BASE_URL")
#DB_PATH = os.getenv("DB_PATH")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CONNECT_TIMEOUT = 3
READ_TIMEOUT = 10

accounts = {
        "admin": {"username": "admin", "password": "admin123"}
    }