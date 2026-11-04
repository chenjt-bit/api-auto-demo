# 测试添加商品模块的自动化测试用例
import allure
import pytest
import time
import yaml
from config.settings import DB_PATH
from api.ecommerce_item_api import eCommerceItemApi

pytestmark = pytest.mark.ecommerce_items

@pytest.fixture
def ecommerce_item_api(api_client):
    return eCommerceItemApi(api_client)

# 1. 标记它属于哪个大业务模块
@allure.feature("电商-商品模块")
# 2. 标记它属于哪个子场景
@allure.story("正向业务流")
# 3. 标记它的严重级别（Blocker最严重，Minor最轻微）
@allure.severity(allure.severity_level.CRITICAL)
# 4. 覆盖原生的英文函数名，改成极其专业的中文标题
@allure.title("验证有效 Token 能成功发布商品，并校验数据库落库")
# ecommerce_items_001:有效Token成功发布商品
def test_items_check_token(ecommerce_item_api,user_headers,db_message):
    # 准备商品数据
    unique_name = f"toyBear_{int(time.time())}"
    payload = {"name":unique_name,"price":18.5}
    # 5. 给操作步骤加上“剧本台词”
    with allure.step("步骤1：发送 POST 请求发布商品"):
        response = ecommerce_item_api.post_items(payload, headers=user_headers)
        assert response.status_code == 200

    #检查数据库
    with allure.step("步骤2：连接数据库，断言商品是否真实落库"):
        db_message.execute("select id,name,price from items where name = %s", (unique_name,))
        db_result = db_message.fetchone()
        # 断言数据库查询结果不是空的
        assert db_result is not None
        assert db_result["name"] == unique_name
        assert db_result["price"] == payload["price"]

    
#测试参数化
# 读取yaml数据文件
item_test_data = yaml.safe_load(open("data/ecommerce_items.yaml","r",encoding="utf-8"))
@pytest.mark.parametrize("data",item_test_data)
def test_create_item_with_different_price(ecommerce_item_api,user_headers,data):
    payload = {
        "name":f"{data["name"]}_{int(time.time())}",
        "price":data["price"]
    }
    response = ecommerce_item_api.post_items(payload,headers=user_headers)
    
    assert response.status_code == data["expected_code"]