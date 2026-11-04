# 测试添加商品模块的自动化测试用例

import pytest
import sqlite3
import time
import yaml
from config.settings import db_path
from api.ecommerce_item_api import eCommerceItemApi

pytestmark = pytest.mark.ecommerce_items

# 创建一个调用数据库的夹具，返回想查的数据库数据
@pytest.fixture
def db_message():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    yield cursor
    cursor.close()
    conn.close()

@pytest.fixture
def ecommerce_item_api(api_client):
    return eCommerceItemApi(api_client)

# ecommerce_items_001:有效Token成功发布商品
def test_items_check_token(ecommerce_item_api,user_headers,db_message):
    # 准备商品数据
    unique_name = f"toyBear_{int(time.time())}"
    payload = {"name":unique_name,"price":18.5}
    response = ecommerce_item_api.post_items(payload)

    assert response.status_code == 200
    #检查数据库
    db_message.execute("select id,name,price from items where name = ?",(unique_name,))
    db_result = db_message.fetchone()
    #断言数据库查询结果不是空的
    assert db_result is not None
    assert db_result[1] == unique_name
    assert db_result[2] == payload["price"]
    
#测试参数化
# 读取yaml数据文件
item_test_data = yaml.safe_load(open("data/ecommerce_items.yaml","r",enconding="utf-8"))
@pytest.mark.parametrize("data",item_test_data)
def test_create_item_with_different_price(ecommerce_item_api,user_headers,data):
    payload = {
        "name":f"{data["name"]}_{int(time.time())}",
        "price":data["price"]
    }
    response = ecommerce_item_api.post_items(payload)
    
    assert response.status_code == data["expected_code"]