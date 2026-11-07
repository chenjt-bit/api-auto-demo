import json
import os

import allure
import pytest

from common.assertions import assert_status
from config.settings import BASE_DIR

# 数据文件路径锚定到项目根目录，不依赖启动 pytest 时的工作目录
DATA_FILE = os.path.join(BASE_DIR, "data", "ai_generated_items.json")


# 1. 读取 AI 生成的 JSON 文件
def load_ai_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"AI 数据文件缺失: {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@allure.feature("电商-商品模块")
@allure.story("AI 生成的极限异常测试")
class TestAIItems:

    # ecommerce_ai_001
    @allure.id("ecommerce_ai_001")
    @pytest.mark.parametrize("ai_data", load_ai_data())
    @allure.title("AI 用例: {ai_data[case_name]}")
    def test_create_item_with_ai_data(self, ecommerce_item_api, user_headers_factory, ai_data):
        # 3. 提取 AI 生成的数据
        name = ai_data["name"]
        price = ai_data["price"]
        ai_expected_code = ai_data["expected_code"]

        payload = {"name": name, "price": price}

        with allure.step(f"发送商品数据，名称长度: {len(name)}，价格: {price}"):
            response = ecommerce_item_api.post_items(payload, headers=user_headers_factory())

            # 失败时 assert_status 会自动带上请求体、响应码与响应体，无需再 print
            assert_status(response, ai_expected_code, f"AI 数据：{name}")

            # 422 时进一步校验契约，而不是只看状态码
            if ai_expected_code == 422:
                assert isinstance(response.json().get("detail"), list)
