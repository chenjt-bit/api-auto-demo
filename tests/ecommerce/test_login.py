#编写电商项目登录模块的自动化测试脚本（测试用例）

import allure
import pytest

from common.assertions import assert_json, assert_status

pytestmark = pytest.mark.ecommerce_login

@allure.id("ecommerce_login_user_001")
@allure.title("普通用户正确账号密码登录成功")
def test_user_login(user_factory,ecommerce_login_api):
    user = user_factory()
    payload = {
        "username":user["username"],
        "password":user["password"]
    }
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 200, "正确账号密码登录")
    token = response.json()["access_token"]
    # 断言token的数据类型是不是字符串并且断言token非空
    assert isinstance(token,str) and len(token)>0

@allure.id("ecommerce_login_user_002")
@allure.title("普通用户错误密码登录失败")
def test_user_login_with_wrong_pwd(user_factory,ecommerce_login_api):
    user = user_factory()
    payload = {"username":user["username"],"password":"123"}#正确密码是123456
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 401, "密码错误")
    assert_json(response, detail="账号或密码错误")

@allure.id("ecommerce_login_user_003")
@allure.title("普通用户账号不存在登录失败")
def test_login_db_without_user(ecommerce_login_api):
    payload = {"username":"user002","password":"123456"}
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 401, "用户不存在")
    assert_json(response, detail="账号或密码错误")

@allure.id("ecommerce_login_user_004")
@allure.title("账号密码为空登录失败")
def test_login_with_empty_payloay(ecommerce_login_api):
    response = ecommerce_login_api.get_login()
    assert_status(response, 422, "缺少请求体")

@allure.id("ecommerce_login_user_005")
@allure.title("账号前有空格，后端 strip 后登录成功")
def test_login_empty_ahead_name(user_factory,ecommerce_login_api):
    user = user_factory()
    payload = {"username":" "+user["username"],"password":"123456"}
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 200, "用户名带空格（预期 strip 后成功）")
