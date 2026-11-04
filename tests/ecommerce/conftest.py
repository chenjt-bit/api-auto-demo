import pytest
# import requests
import time
from config.settings import accounts

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
def user_headers(api_client, dynamic_user_account):
    """用刚才动态注册的账号去登录，获取 Token"""
    res = api_client.post(f"{api_client.base_url}/login", json=dynamic_user_account)
    assert res.status_code == 200, "前置登录失败，拿不到Token"

    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}