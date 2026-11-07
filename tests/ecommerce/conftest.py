import time
import uuid

import pytest

from api.ecommerce_item_api import eCommerceItemApi
from api.ecommerce_login_api import eCommerceLoginApi
from common.assertions import assert_status


# 🛠️ 用户数据工厂：造一个真实用户，并登记起来，跑完统一回收
@pytest.fixture
def user_factory(api_client, run_id, created_data):
    """
    调用一次，就在数据库里真实注册一个用户，并返回账号信息。

    两点改进：
    1. 用户名带 run_id 前缀 —— 库里一眼能看出是哪次运行造的；
    2. 注册后登记到 created_data —— 会话结束统一删除，不再只增不减。
    """

    def _create_user(role="user"):
        # run_id(24) + "_u" + 6 位随机，长度约 32，不会超过 username 的 50 字符上限
        unique_name = f"{run_id}_u{uuid.uuid4().hex[:6]}"
        password = "123456"
        reg_payload = {
            "username": unique_name,
            "password": password,
        }
        register_response = api_client.post(f"{api_client.base_url}/register", json=reg_payload)
        assert_status(register_response, 200, f"注册用户 {unique_name}")

        created_data["usernames"].append(unique_name)   # ← 登记，等待回收

        return {
            "username": unique_name,
            "password": password,
        }

    return _create_user


@pytest.fixture
def user_headers_factory(api_client, user_factory):
    def _create_headers():
        user = user_factory()
        payload = {"username": user["username"], "password": user["password"]}
        response = api_client.post(f"{api_client.base_url}/login", json=payload)
        assert_status(response, 200, f"登录用户 {user['username']}")
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _create_headers


# 再封装一个动态创造商品数据的夹具
@pytest.fixture
def item_payload_factory(run_id):
    """商品数据工厂：既支持自动生成唯一名字，又支持手动传参覆盖"""

    def _create(name=None, price=18.5):
        # run_id(24) + "_item_" + 13 位毫秒，长度约 43，不会超过 name 的 50 字符上限
        unique_name = name if name is not None else f"{run_id}_item_{int(time.time() * 1000)}"
        return {"name": unique_name, "price": price}

    return _create


@pytest.fixture
def ecommerce_login_api(api_client):
    return eCommerceLoginApi(api_client)


@pytest.fixture
def ecommerce_item_api(api_client, created_data):
    """在原有接口封装外面加一层"记账"。

    只要发布成功（200 且返回 item_id），就把 id 记到 created_data 里，
    会话结束时统一删除。

    这样做的好处：用例代码一行都不用改，而且能覆盖"名字来自 YAML / AI 数据"的场景
    （那些名字不能随便加前缀，加了会破坏 50 字符边界的测试意图）。
    """
    api = eCommerceItemApi(api_client)

    # 先保存原始方法，再替换成"调用原始方法 + 记录结果"
    original_post_items = api.post_items

    def post_items_and_record(item_payload=None, **kwargs):
        response = original_post_items(item_payload, **kwargs)
        if response.status_code == 200:
            item_id = response.json().get("item_id")
            if item_id is not None:
                created_data["item_ids"].append(item_id)
        return response

    api.post_items = post_items_and_record
    return api
