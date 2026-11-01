import pytest
import requests
from config.settings import BASE_URL,CONNECT_TIMEOUT,READ_TIMEOUT

@pytest.fixture(scope="session")# 装饰器
def api_client():
    # 1. 准备阶段：创建一个 Session 对象
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    
    session.base_url = BASE_URL
    
    # 💡 核心技巧：给 session 统一配置超时
    # 这是一个元组 (连接超时时间, 读取超时时间)
    session.timeout = (CONNECT_TIMEOUT,READ_TIMEOUT)

    # 2. 把准备好的东西交出去
    yield session

    # 3. 清理阶段：测试跑完后，关掉连接
    session.close()

# 创建token的夹具形象
@pytest.fixture(scope="session")
def auth_token(api_client):
    #获取token的方式：给登录接口发送登录请求，对响应结果进行筛选
    # 1. 登录
    payload = {"username": "ceshi001", "password": "123456"}
    # 注意：为了防止没注册就登录，这里可能要先调注册接口(真实业务里注册通常不会在每次跑测试都调，这里为了方便直接用固定账号)
    # ... 假设已经注册成功 ...
    response = api_client.post(f"{api_client.base_url}/login", json=payload)

    # 2. 防御性断言：如果连登录都失败，后面的测试不用跑了，直接报错
    assert response.status_code == 200, "前置登录失败，拿不到Token！"
    
    # 3. 提取 token
    token = response.json()["access_token"]
    return token