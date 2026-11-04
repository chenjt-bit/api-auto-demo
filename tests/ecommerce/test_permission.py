"""
这个测试用例集是测试real_server的
用你学过的 Fixture 夹具，写出完整的业务自动化：
随机注册一个普通用户。
登录 admin，拿到 Token2。
测试越权：用 Token1 去请求 /admin/users，断言状态码为 403。
测试正常：用 Token2 去请求 /admin/users，断言状态码为 200。
"""
import pytest
from config.settings import accounts

pytestmark = pytest.mark.ecommerce

#1、测试登录admin管理员
def test_login_admin(api_client):
    payload = accounts["admin"]
    response = api_client.post(f"{api_client.base_url}/login",json=payload)

    assert response.status_code == 200

# 2、测试用 Token1 去请求 /admin/users，断言状态码为 403。
def test_user_token_get_users(api_client,user_headers):
    response = api_client.get(f"{api_client.base_url}/admin/users",headers=user_headers)
    assert  response.status_code == 403

# 3、测试用Token2去请求/admin/users，断言状态码为200
def test_admin_get_users(api_client,admin_headers):
    response = api_client.get(f"{api_client.base_url}/admin/users",headers =admin_headers)
    assert response.status_code == 200

