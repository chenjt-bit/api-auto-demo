import pytest
import requests
import time
from config.settings import BASE_URL,CONNECT_TIMEOUT,READ_TIMEOUT,accounts

#api_client:api（接口）client（用户端）：这个夹具负责所有接口请求的发送
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
def auth_token(api_client,setup_test_user):
    #获取token的方式：给登录接口发送登录请求，对响应结果进行筛选
    # 1. 登录
    payload = setup_test_user
    # 注意：为了防止没注册就登录，这里可能要先调注册接口(真实业务里注册通常不会在每次跑测试都调，这里为了方便直接用固定账号)
    # ... 假设已经注册成功 ...
    response = api_client.post(f"{api_client.base_url}/login", json=payload)

    # 2. 防御性断言：如果连登录都失败，后面的测试不用跑了，直接报错
    assert response.status_code == 200, "前置登录失败，拿不到Token！"
    
    # 3. 提取 token
    token = response.json()["access_token"]
    return token

#创建一个注册的夹具，将注册时用到的数据信息发送出去
@pytest.fixture(scope="session")
def setup_test_user(api_client):
    """
    自动前置准备：在测试开始前，确保数据库有这个账号
    """
    payload = {"username":"ceshi001","password":"123456"}
    response = api_client.post(f"{api_client.base_url}/register",json=payload)

    # 企业级断言：要么注册成功(200)，要么报“用户名已存在”(400)
    # 只要是这两个结果，都说明环境是正常的，前置准备算成功
    if response.status_code == 200:
        print("\n✅ 测试前置：新用户注册成功")
    elif response.status_code == 400 and "已存在" in response.text:
        print("\nℹ️ 测试前置：用户已存在，直接复用")
    else:
        # 如果是别的报错（比如 500 服务器崩了），必须让测试直接 ERROR！
        pytest.fail(f"❌ 测试前置失败！注册接口异常，状态码: {response.status_code}")

    return payload

#将获取token的操作打包成一个函数（通过角色获取）
def get_token_by_role(api_client,role):
    #accounts是一个字典数据，里面有俩个字典数据一个是admin，一个是普通用户
    payload = accounts[role]
    response = api_client.post(f"{api_client.base_url}/login",json=payload)
    assert response.status_code == 200
    body = response.json()
    return body["access_token"]

@pytest.fixture(scope="module") # 建议用 module 而不是 session，防止过期
def admin_headers(api_client):
    token = get_token_by_role(api_client, "admin")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def user_headers(api_client):
    token = get_token_by_role(api_client, "user")
    return {"Authorization": f"Bearer {token}"}

#1.
#先写一个专门生成动态账号的夹具
@pytest.fixture(scope="module")
def dynamic_user_account(api_client):
    """动态注册一个全新的普通用户，保证每次测试环境干净"""
    unique_name = f"user_{int(time.time())}"
    payload = {"username": unique_name, "password": "123456"}

    # 注册
    res = api_client.post(f"{api_client.base_url}/register", json=payload)
    # 允许 200 (成功) 或者 400 (虽然时间戳大概率不重复，但加上更稳健)
    assert res.status_code in [200, 400]

    return payload  # 返回 {"username": "user_xxx", "password": "123456"}


# 2. 改造你的 user_headers 夹具，让它依赖刚才生成的账号
@pytest.fixture(scope="module")
def user_headers_new(api_client, dynamic_user_account):
    """用刚才动态注册的账号去登录，获取 Token"""
    res = api_client.post(f"{api_client.base_url}/login", json=dynamic_user_account)
    assert res.status_code == 200, "前置登录失败，拿不到Token"

    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}