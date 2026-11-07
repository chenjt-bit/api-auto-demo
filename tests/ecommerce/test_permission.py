"""
这个测试用例集是测试real_server的
用你学过的 Fixture 夹具，写出完整的业务自动化：
随机注册一个普通用户。
登录 admin，拿到 Token2。
测试越权：用 Token1 去请求 /admin/users，断言状态码为 403。
测试正常：用 Token2 去请求 /admin/users，断言状态码为 200。
"""
import allure
import pytest

from common.assertions import assert_json, assert_status

pytestmark = pytest.mark.ecommerce

#1、测试登录admin管理员
@allure.id("ecommerce_permission_001")
def test_login_admin(ecommerce_login_api):
    payload = {
        "username":"admin",
        "password":"admin123"
    }
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 200, "管理员登录")
    token = response.json()["access_token"]
    assert isinstance(token,str) and len(token) > 0

# 2、测试用 Token1 去请求 /admin/users，断言状态码为 403。
@allure.id("ecommerce_permission_002")
def test_user_token_get_users(api_client,user_headers_factory):
    response = api_client.get(f"{api_client.base_url}/admin/users",headers=user_headers_factory())
    assert_status(response, 403, "普通用户访问 /admin/users")

# 3、测试用Token2去请求/admin/users，断言状态码为200
@allure.id("ecommerce_permission_003")
def test_admin_get_users(api_client):
    login_response = api_client.post(f"{api_client.base_url}/login",json={"username":"admin","password":"admin123"})
    assert_status(login_response, 200, "管理员登录")
    token = login_response.json()["access_token"]
    admin_headers = {"Authorization":f"Bearer {token}"}
    response = api_client.get(f"{api_client.base_url}/admin/users",headers =admin_headers)
    assert_status(response, 200, "管理员访问 /admin/users")


# 4、不带 Token 访问管理接口，应返回 401
@allure.id("ecommerce_permission_004")
@allure.title("不带 Token 访问管理接口，断言 401")
def test_admin_users_without_token(api_client):
    response = api_client.get(f"{api_client.base_url}/admin/users")
    assert_status(response, 401, "无 Token 访问 /admin/users")
    assert_json(response, detail="未登录")
