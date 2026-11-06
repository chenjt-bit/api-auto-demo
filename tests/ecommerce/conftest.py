import pytest
import time
import uuid  # 确保顶部引入了 uuid
from api.ecommerce_item_api import eCommerceItemApi
from api.ecommerce_login_api import eCommerceLoginApi
#🛠️ 企业级改造：把用户夹具变成“超级兵工厂”
@pytest.fixture
def user_factory(api_client):
    """
    🌟 企业级用户数据工厂
    调用一次，就在数据库里真实注册一个用户，并返回账号信息
    """
    def _create_user(role="user"):
        # 毫秒时间戳 + uuid 前8位，绝对不可能重复
        unique_name = f"user_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        password = "123456"
        reg_payload = {
            "username":unique_name,
            "password":password
        }
        register_response = api_client.post(f"{api_client.base_url}/register",json=reg_payload)
        assert register_response.status_code == 200,f"注册失败，原因是：{register_response.text}"
        # 返回一个包含用户信息
        return {
            "username":unique_name,
            "password":password,
        }

    return _create_user

@pytest.fixture
def user_headers_factory(api_client,user_factory):
    def _create_headers():
        user = user_factory()
        payload = {"username": user["username"], "password": user["password"]}
        response = api_client.post(f"{api_client.base_url}/login", json=payload)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _create_headers

# 再封装一个动态创造商品数据的夹具
@pytest.fixture
def item_payload_factory():
    """商品数据工厂：既支持自动生成唯一名字，又支持手动传参覆盖"""
    def _create(name=None, price=18.5):
        unique_name = name if name is not None else f"toyBear_{int(time.time() * 1000)}"
        return {"name": unique_name, "price": price}
    return _create

@pytest.fixture
def ecommerce_login_api(api_client):
    return eCommerceLoginApi(api_client)

@pytest.fixture
def ecommerce_item_api(api_client):
    return eCommerceItemApi(api_client)