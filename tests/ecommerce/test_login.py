#编写电商项目登录模块的自动化测试脚本（测试用例）

import pytest

from common.assertions import assert_json, assert_status

pytestmark = pytest.mark.ecommerce_login

# 测试普通用户正确账号与密码登录成功，断言状态码为200以及token
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

# 测试普通用户密码错误
def test_user_login_with_wrong_pwd(user_factory,ecommerce_login_api):
    user = user_factory()
    payload = {"username":user["username"],"password":"123"}#正确密码是123456
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 401, "密码错误")
    assert_json(response, detail="账号或密码错误")

# 测试用户不存在时登录失败
def test_login_db_without_user(ecommerce_login_api):
    payload = {"username":"user002","password":"123456"}
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 401, "用户不存在")
    assert_json(response, detail="账号或密码错误")

# 测试用户密码为空时登录失败，断言状态码为422：参数校验失败
def test_login_with_empty_payloay(ecommerce_login_api):
    response = ecommerce_login_api.get_login()
    assert_status(response, 422, "缺少请求体")

# 测试账号前后有空格
#@pytest.mark.xfail(reason="BUG-123 后端未对 username 做 strip，修复后移除本标记", strict=True)
def test_login_empty_ahead_name(user_factory,ecommerce_login_api):
    user = user_factory()
    payload = {"username":" "+user["username"],"password":"123456"}
    response = ecommerce_login_api.get_login(payload)
    assert_status(response, 200, "用户名带空格（预期 strip 后成功）")
