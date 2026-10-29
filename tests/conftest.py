import pytest
import requests
from config.settings import BASE_URL,TIME_OUT

@pytest.fixture# 装饰器
def api_client():
    # 1. 准备阶段：创建一个 Session 对象
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    
    session.base_url = BASE_URL
    session.time_out = TIME_OUT
    # 2. 把准备好的东西交出去
    yield session

    # 3. 清理阶段：测试跑完后，关掉连接
    session.close()
