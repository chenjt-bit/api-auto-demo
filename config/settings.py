# config/settings.py
# 配置一些基本信息的公共信息，类似全局变量
# BASE_URL = "https://jsonplaceholder.typicode.com"
BASE_URL = "http://127.0.0.1:8081"
db_path = "mock_server/ecommerce.db"
accounts = {
        "admin": {"username": "admin", "password": "admin123"},
        "user": {"username": "user001", "password": "123456"}
    }
CONNECT_TIMEOUT = 3  # 敲门等 3 秒
READ_TIMEOUT = 10    # 读数据等 10 秒