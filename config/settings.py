# config/settings.py
# 配置一些基本信息的公共信息，类似全局变量

import os
from dotenv import load_dotenv

# 1. 封装成函数，每次调用时才去读取环境变量和文件
def get_base_url():
    current_env = os.getenv("ENV", "dev")
    load_dotenv(f".env.{current_env}", override=True)
    return os.getenv("BASE_URL", "http://127.0.0.1:8081")

def get_db_password():
    current_env = os.getenv("ENV", "dev")
    load_dotenv(f".env.{current_env}", override=True)
    return os.getenv("DB_PASSWORD", "123456")

CONNECT_TIMEOUT = 3
READ_TIMEOUT = 10

accounts = {
        "admin": {"username": "admin", "password": "admin123"}
    }