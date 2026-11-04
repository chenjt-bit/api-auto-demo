#编写电商项目登录模块的自动化测试脚本（测试用例）

import pytest
from config.settings import accounts
from api.ecommerce_login_api import eCommerceLoginApi

pytestmark = pytest.mark.ecommerce_login

@pytest.fixture
def ecommerce_login_api(api_client):
    return eCommerceLoginApi(api_client)

# 测试普通用户正确账号与密码登录成功，断言状态码为200以及token
def test_user_login(dynamic_user_account,ecommerce_login_api):
    payload = dynamic_user_account
    response = ecommerce_login_api.get_login(payload)

    assert response.status_code == 200
    token =  response.json()["access_token"]
    # 断言token的数据类型是不是字符串并且断言token非空
    assert isinstance(token,str) and len(token)>0

# 测试普通用户密码错误
def test_user_login_with_wrong_pwd(dynamic_user_account,ecommerce_login_api):
    name = dynamic_user_account["username"]
    payload = {"username":name,"password":"123"}#正确密码是123456
    response = ecommerce_login_api.get_login(payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "账号或密码错误"

# 测试用户不存在时登录失败
def test_login_db_without_user(ecommerce_login_api):
    payload = {"username":"user002","password":"123456"}
    response = ecommerce_login_api.get_login(payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "账号或密码错误"

# 测试用户密码为空时登录失败，断言状态码为422：参数校验失败
def test_login_with_empty_payloay(ecommerce_login_api):
    #payloay = {"username":"","password":""}
    response = ecommerce_login_api.get_login()

    assert response.status_code == 422

# 测试账号前后有空格
def test_login_empty_ahead_name(dynamic_user_account,ecommerce_login_api):
    name = " " + dynamic_user_account["username"]
    payload = {"username":name,"password":"123456"}
    response = ecommerce_login_api.get_login(payload)

    assert response.status_code == 401