"""
这个测试用例集是测试real_server的
用你学过的 Fixture 夹具，写出完整的业务自动化：
随机注册一个普通用户。
登录普通用户，拿到 Token1。
登录 admin，拿到 Token2。
测试越权：用 Token1 去请求 /admin/users，断言状态码为 403。
测试正常：用 Token2 去请求 /admin/users，断言状态码为 200。
数据库断言：用 sqlite3 连上 ecommerce.db，去查一下刚才那个普通用户发布商品的数据是否真的落库了。
"""
import pytest
import sqlite3# 连上ecommerce.db数据库
import time
from jsonschema import validate
from config.settings import accounts,db_path

pytestmark = pytest.mark.ecommerce
# 1、测试登录普通用户
def test_login_user(api_client):
    #获取登录数据
    payload = accounts["user"]
    response = api_client.post(f"{api_client.base_url}/login",json=payload)
    #断言响应状态码，登录成功会获取token，断言token数据类型
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert isinstance(token,str) and len(token)>0
    
#2、测试登录admin管理员
def test_login_admin(api_client):
    payload = accounts["admin"]
    response = api_client.post(f"{api_client.base_url}/login",json=payload)

    assert response.status_code == 200

# 3、测试用 Token1 去请求 /admin/users，断言状态码为 403。
def test_user_token_get_users(api_client,user_headers):
    headers = user_headers

    response = api_client.get(f"{api_client.base_url}/admin/users",headers=headers)
    assert  response.status_code == 403
    
# 4、测试用Token2去请求/admin/users，断言状态码为200
def test_admin_get_users(api_client,admin_headers):
    headers = admin_headers
    response = api_client.get(f"{api_client.base_url}/admin/users",headers = headers)
    assert response.status_code == 200


@pytest.fixture
def register_login_get_token(api_client):
    # 可以先进行注册+登录操作：获取已登录的token
    unique_name = f"user_{int(time.time())}"  # 时间戳生成唯一名字
    user_payload = {"username": unique_name, "password": "123456"}
    register_response = api_client.post(f"{api_client.base_url}/register", json=user_payload)
    login_response = api_client.post(f"{api_client.base_url}/login", json=user_payload)
    assert login_response.status_code == 200
    # 获取token
    token = login_response.json()["access_token"]
    return token

@pytest.fixture
def insert_item(api_client,register_login_get_token):
    token = register_login_get_token
    # 发布商品
    item_payload = {"name": "toyBear", "price": 18.5}
    headers = {"Authorization": f"Bearer {token}"}
    item_response = api_client.post(f"{api_client.base_url}/items", json=item_payload, headers=headers)
    assert item_response.status_code == 200
    return "toyBear"

# 5、测试数据库内容：使用普通用户发布商品
def test_check_user_db(api_client,insert_item):
    published_item = insert_item
    #开始连接数据库判断数据库是否添加了商品
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items JOIN users ON owner_id = users.id WHERE items.name = ?",
        (published_item,))
    db_result = cursor.fetchone()
    cursor.close()
    conn.close()

    # 3、断言
    assert db_result is not None
    assert db_result[1] == "toyBear"
    assert db_result[2] == 18.5
    