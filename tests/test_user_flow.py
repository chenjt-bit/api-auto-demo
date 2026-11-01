# 这个测试用例是测用户注册->用户登录->用户查询个人信息的业务测试
#因为是测试用例，使用pytest框架，所以需要导入pytest库
import pytest

#给整个文件打上标签mark
pytestmark = pytest.mark.user

#编写测试用例：
#1、登录的测试用例,因为需要发送请求，所以需要使用到coftest中的夹具api_client
def test_login(api_client,setup_test_user):
    #登录就需要获取对应的所需信息：用户名以及密码
    payload = setup_test_user#这里需要确定参数名的准确性
    #使用api_client发送请求并获取响应结果
    response = api_client.post(url=f"{api_client.base_url}/login",json=payload)
    #断言响应状态码是不是200，判断请求是否成功发送
    assert response.status_code == 200

#2、故意不带token的鉴权测试
def test_get_user_without_token(api_client):
    # 这个请求里我们故意不传headers（请求头）
    response = api_client.get(f"{api_client.base_url}/users/me")

    # 断言：服务器必须觉得“你不安全”，打回 401
    # 这就相当于你不刷门禁卡直接推门，警报必须响
    assert response.status_code == 401

#3、带着token的正常访问
def test_get_user_with_token(api_client,auth_token):
    #此时请求发送需要带上请求头
    # HTTP 协议规定：认证凭证必须放在 Header（请求头）里
    # 格式固定为：{"Authorization": "Bearer <真实的token>"}
    # 注意：Bearer 后面必须有一个英文空格！这是协议死规定。
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 🚨 加上这行！看看发送给服务器的到底是什么鬼
    print(f"\n==== 我发送的请求头是: {headers} ====")
    
    response = api_client.get(f"{api_client.base_url}/users/me",headers = headers)

    #断言一：请求发送成功：响应状态码是200
    assert response.status_code == 200
    #断言二：查出来的用户，必须就是刚才登录的那位
    assert response.json()["username"] == "ceshi001"

#覆盖异常测试
#注册异常覆盖（接口参数校验）目标：测空密码或者空用户名
def test_register_with_empty_pwd(api_client):
    #发送注册请求post：需要请求体数据json
    payload = {"username":"ceshi002","password":""}
    response = api_client.post(f"{api_client.base_url}/register",json=payload)
    #断言响应结果应该是422：字段不符合要求
    assert response.status_code == 422

def test_register_with_empty_name(api_client):
    payload = {"username":"","password":"123456"}
    response = api_client.post(f"{api_client.base_url}/register",json=payload)
    assert response.status_code == 422

#2、登录异常覆盖：测试密码错误
def test_login_with_error_pwd(api_client):
    payload = {"username":"ceshi001","password":"12345"}#正确密码是123456
    response = api_client.post(f"{api_client.base_url}/login",json=payload)
    # 在mock_server.py中，如果用户名与密码不匹配则无法在数据库中查询到数据，判断结果是返回状态码401
    assert response.status_code == 401
    assert response.json()["detail"] == "账号或密码错误"

#3、数据隔离与持久化（结合数据库断言）：使用随机数据注册，查库验证，杜绝重复运行报错
import time
import sqlite3

def test_register_and_db_verify(api_client):
    unique_name = f"user_{int(time.time())}"# 时间戳生成唯一名字
    payload = {"username":unique_name,"password":"123456"}

    #1、请求注册
    response = api_client.post(f"{api_client.base_url}/register",json=payload)
    assert response.status_code == 200

    #2、查数据库，请求返回状态码200表示请求成功不代表数据真的写进数据库
    conn = sqlite3.connect("mock_server/test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?",(unique_name,))
    db_result = cursor.fetchone()#fetchone抓取一条数据
    conn.close()

    #3、断言
    assert db_result is not None
    assert db_result[1] == unique_name
