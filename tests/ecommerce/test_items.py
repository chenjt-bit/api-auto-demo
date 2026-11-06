# 测试添加商品模块的自动化测试用例
import allure
import pytest
import time
import yaml

pytestmark = pytest.mark.ecommerce_items

# 1. 标记它属于哪个大业务模块
@allure.feature("电商-商品模块")
# 2. 标记它属于哪个子场景
@allure.story("正向业务流")
# 3. 标记它的严重级别（Blocker最严重，Minor最轻微）
@allure.severity(allure.severity_level.CRITICAL)
# 4. 覆盖原生的英文函数名，改成极其专业的中文标题
@allure.title("验证有效 Token 能成功发布商品，并校验数据库落库")
# ecommerce_items_001:正向成功发布商品
def test_items_check_token(ecommerce_item_api,user_headers_factory,db_message,item_payload_factory):
    # 准备商品数据
    unique_name = item_payload_factory()["name"]
    payload = item_payload_factory()
    headers = user_headers_factory()
    # 5. 给操作步骤加上“剧本台词”
    with allure.step("步骤1：发送 POST 请求发布商品"):
        response = ecommerce_item_api.post_items(payload, headers=headers)
        assert response.status_code == 200
        assert response.json()["msg"] == "发布成功"

    #检查数据库
    with allure.step("步骤2：连接数据库，断言商品是否真实落库"):
        db_message.execute("select id,name,price from items where name = %s", (unique_name,))
        db_result = db_message.fetchone()
        # 断言数据库查询结果不是空的
        assert db_result is not None
        assert db_result["name"] == unique_name
        assert db_result["price"] == payload["price"]
#----------------------------------------------------------------------------------------------------------------------

@allure.feature("电商-商品模块")
@allure.story("正常业务流")
@allure.title("用户A成功删除自己发布的商品，断言200")
def test_user_delete_own_item_success(ecommerce_item_api, user_headers_factory, db_message,item_payload_factory):
    # 1. 用户A 发商品
    headers = user_headers_factory()
    payload = item_payload_factory()
    post_res = ecommerce_item_api.post_items(payload, headers=headers)
    item_id = post_res.json()["item_id"]

    # 2. 用户A 删自己的商品
    delete_res = ecommerce_item_api.delete_item(item_id=item_id, headers=headers)
    assert delete_res.status_code == 200

    # 3. 查库验证：商品真的被删除了（查不到）
    db_message.execute("SELECT id FROM items WHERE id = %s", (item_id,))
    assert db_message.fetchone() is None
#--------------------------------------------------------------------------------------------------------------------------
    
# 测试参数化
# 读取yaml数据文件
def item_test_data():
    with open("data/ecommerce_items.yaml","r",encoding="utf-8") as file:
        return yaml.safe_load(file)

@pytest.mark.parametrize(
    "data",
    item_test_data()
)
@allure.feature("电商-商品模块")
@allure.story("发布商品参数校验")
def test_create_item_with_different_price(ecommerce_item_api,user_headers_factory,data):
    headers = user_headers_factory()
    payload = {
        "name":f"{data["name"]}_{int(time.time())}",
        "price":data["price"]
    }
    with allure.step(f"发送发布商品请求，价格：{data["price"]}"):
        response = ecommerce_item_api.post_items(payload, headers=headers)
        assert response.status_code == data["expected_code"]
#-----------------------------------------------------------------------------------------------------------------------

# 测试“端到端”全链路的验证：注册登录->发布商品->查询商品->校验数据库是否落库
@allure.feature("电商-商品模块")
@allure.story("端到端全链路验证")
def test_full_e2e_create_and_quary_item(ecommerce_item_api,user_headers_factory,db_message,item_payload_factory):
    #user_headers参数会调用夹具自动完成注册登录得到token，所以下面先发布商品
    with allure.step("1、动态创建商品数据然后发布并断言"):
        headers = user_headers_factory()
        item_payload = item_payload_factory()
        post_response = ecommerce_item_api.post_items(item_payload,headers=headers)
        assert post_response.status_code == 200
        assert post_response.json()["msg"] == "发布成功"
    #获取商品id
    item_id = post_response.json()["item_id"]
    
    with allure.step("2、发送查询商品请求并断言商品数据"):
        get_response = ecommerce_item_api.get_items(headers=headers)
        assert get_response.status_code == 200
        items_data = get_response.json()["data"]
        # 把列表里的所有商品名提取出来，变成一个新的列表
        item_names = [item["name"] for item in items_data]
        # 断言：刚发布的商品名，一定在这个列表里！
        assert item_payload["name"] in item_names
        
    with allure.step("3、断言数据库中是否真的落库刚刚发布的商品数据"):
        sql = "select id,name,price from items where id = %s"
        db_message.execute(sql,(item_id,))
        db_result = db_message.fetchone()
        assert db_result is not None
        assert db_result["name"] == item_payload["name"]
        assert db_result["id"] == item_id
#-----------------------------------------------------------------------------------------------------------------------

@allure.feature("电商-商品模块")
@allure.story("安全防御-水平越权")
@allure.title("用户B尝试删除用户A的商品，断言403拒绝")
def test_horizontal_privilege_escalation(ecommerce_item_api, user_headers_factory, db_message):
    # 🌟 变出两个不同的用户
    headers_a = user_headers_factory()
    headers_b = user_headers_factory()
    
    # 1. 用户A发布一个商品
    payload = {"name": f"A的宝贝_{int(time.time())}", "price": 99.9}
    post_res = ecommerce_item_api.post_items(payload, headers=headers_a)
    assert post_res.status_code == 200
    item_id = post_res.json()["item_id"]

    # 2. 用户B试图越权删除用户A的商品！
    with allure.step(f"用户B尝试越权删除商品ID: {item_id}"):
        delete_res = ecommerce_item_api.delete_item(item_id=item_id, headers=headers_b)

        # 断言：必须返回 403 拒绝
        assert delete_res.status_code == 403
        assert "越权警告" in delete_res.json()["detail"]

    # 3. 查库验证：A的商品安然无恙，没有被 B 删掉
    db_message.execute("SELECT id FROM items WHERE id = %s", (item_id,))
    assert db_message.fetchone() is not None