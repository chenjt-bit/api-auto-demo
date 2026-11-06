import json
import pytest
import allure
import os


# 1. 读取 AI 生成的 JSON 文件
def load_ai_data():
    file_path = "data/ai_generated_items.json"
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@allure.feature("电商-商品模块")
@allure.story("AI 生成的极限异常测试")
class TestAIItems:

    # 2. 将 AI 数据直接传给 parametrize
    @pytest.mark.parametrize("ai_data", load_ai_data())
    @allure.title("AI 用例: {ai_data[case_name]}")
    def test_create_item_with_ai_data(self, ecommerce_item_api, user_headers_factory, ai_data):
        # 3. 提取 AI 生成的数据
        name = ai_data["name"]
        price = ai_data["price"]
        # 注意：AI 预估的状态码可能不准确，我们先记录下来
        ai_expected_code = ai_data["expected_code"]

        payload = {"name": name, "price": price}

        with allure.step(f"发送商品数据，名称长度: {len(name)}，价格: {price}"):
            response = ecommerce_item_api.post_items(payload, headers=user_headers_factory())

            # 🌟 企业级思维：不盲信 AI 的预测！
            # 这里我们不直接用 assert response.status_code == ai_expected_code
            # 我们把实际结果和 AI 的预测都打印出来，由测试工程师来判断
            print(f"\n👉 AI 预期状态码: {ai_expected_code} | 实际状态码: {response.status_code}")
            print(f"👉 后端返回: {response.text}")

            # 合法数据返回 200，非法边界返回 422。只要不是这两个，就是后端出了严重故障！
            assert response.status_code in [200, 422], f"后端发生了未知故障，状态码: {response.status_code}"