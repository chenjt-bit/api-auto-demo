import os
import json
import re  # 🌟 引入正则表达式库，用于提取 JSON
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


def generate_test_data():
    print("🤖 正在请求 AI 生成测试数据...")

    prompt = """
    你是一个资深的电商接口测试工程师。
    我们的商品发布接口接收两个参数：
    - name (商品名称，字符串，正常长度1-50)
    - price (价格，浮点数，正常大于0)

    请帮我生成 5 条极端的异常测试数据，包含以下场景：
    1. 超长字符（用 100 个 'A' 表示即可，千万别太长）
    2. 空字符串
    3. SQL 注入语句
    4. 包含特殊表情符号
    5. 负数价格

    ⚠️ 极其严格的要求：
    1. 请严格以 JSON 数组格式返回，不要包含任何解释性文字。
    2. 不要使用 ```json 和 ``` 这种 Markdown 代码块标记。
    3. 格式必须完全符合：[{"case_name": "场景名称", "name": "商品名", "price": 10.0, "expected_code": 422}]
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个只输出纯净 JSON 格式的测试数据生成器，绝对不输出任何废话。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    raw_content = response.choices[0].message.content
    print(f"\n📄 AI 原始返回内容:\n{raw_content}\n")

    # 🌟 核心防弹衣：用正则强行提取 [ 到 ] 之间的内容
    try:
        # 清理 markdown 标记
        clean_content = raw_content.replace("```json", "").replace("```", "").strip()

        # 如果 AI 废话太多，我们用正则强行抠出 JSON 数组
        match = re.search(r'\[.*\]', clean_content, re.DOTALL)
        if match:
            clean_content = match.group(0)

        data_list = json.loads(clean_content)

        print("✅ 解析成功！AI 生成的数据如下：")
        for item in data_list:
            print(f"👉 [{item['case_name']}] Name: {item['name'][:20]}... | Price: {item['price']}")

        # 保存文件
        os.makedirs("data", exist_ok=True)
        with open("data/ai_generated_items.json", "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        print("\n💾 数据已保存至 data/ai_generated_items.json")

    except json.JSONDecodeError as e:
        print(f"❌ 解析失败，即使穿了防弹衣也没拦住。错误信息：{e}")
        print("请检查大模型返回的内容是否真的符合 JSON 格式。")


if __name__ == "__main__":
    generate_test_data()