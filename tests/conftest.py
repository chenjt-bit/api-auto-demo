import pytest
import requests
import pymysql
from pymysql.cursors import DictCursor
from config.settings import get_base_url,CONNECT_TIMEOUT,READ_TIMEOUT

#api_client:api（接口）client（用户端）：这个夹具负责所有接口请求的发送
@pytest.fixture(scope="session")
def api_client():
    # 1. 准备阶段：创建一个 Session 对象
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    
    session.base_url = get_base_url()
    # 💡 核心技巧：给 session 统一配置超时
    # 这是一个元组 (连接超时时间, 读取超时时间)
    session.timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)

    # 2. 把准备好的东西交出去
    yield session

    # 3. 清理阶段：测试跑完后，关掉连接
    session.close()
    
# 创建一个调用数据库的夹具，返回想查的数据库数据
@pytest.fixture
def db_message():
    # 连接真实的 MySQL
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="123456",
        database="ecommerce",  # 这里我们需要在 MySQL 里建个库
        cursorclass=DictCursor  # 返回字典格式
    )
    
    cursor = conn.cursor()
    yield cursor
    cursor.close()
    conn.close()