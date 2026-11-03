#编写电商项目登录模块的自动化测试脚本（测试用例）

import pytest
from config.settings import accounts

pytestmark = pytest.mark.ecommerce_login

# 测试普通用户正确账号与密码登录成功，断言状态码为200以及token
def test_user_login(api_client,dynamic_user_account):
    payload = dynamic_user_account
    response = api_client.post(f"{api_client.base_url}/login",json=payload)

    assert response.status_code == 200
    token =  response.json()["access_token"]
    # 断言token的数据类型是不是字符串并且断言token非空
    assert isinstance(token,str) and len(token)>0

# 测试普通用户密码错误
def test_user_login_with_wrong_pwd(api_client,dynamic_user_account):
    name = dynamic_user_account["username"]
    payload = {"username":name,"password":"123"}#正确密码是123456
    response = api_client.post(f"{api_client.base_url}/login",json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "账号或密码错误"

# 测试用户不存在时登录失败
def test_login_db_without_user(api_client):
    payload = {"username":"user002","password":"123456"}
    response = api_client.post(f"{api_client.base_url}/login",json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "账号或密码错误"

# 测试用户密码为空时登录失败，断言状态码为422：参数校验失败
def test_login_with_empty_payloay(api_client):
    #payloay = {"username":"","password":""}
    response = api_client.post(f"{api_client.base_url}/login")

    assert response.status_code == 422

# 测试账号前后有空格
def test_login_empty_ahead_name(api_client,dynamic_user_account):
    name = " " + dynamic_user_account["username"]
    payload = {"username":name,"password":"123456"}
    response = api_client.post(f"{api_client.base_url}/login",json=payload)

    assert response.status_code == 401