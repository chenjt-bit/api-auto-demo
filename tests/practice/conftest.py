import pytest

# 创建token的夹具形象
@pytest.fixture(scope="session")
def auth_token(api_client, setup_test_user):
    # 获取token的方式：给登录接口发送登录请求，对响应结果进行筛选
    # 1. 登录
    payload = setup_test_user
    # 注意：为了防止没注册就登录，这里可能要先调注册接口(真实业务里注册通常不会在每次跑测试都调，这里为了方便直接用固定账号)
    # ... 假设已经注册成功 ...
    response = api_client.post(f"{api_client.base_url}/login", json=payload)

    # 2. 防御性断言：如果连登录都失败，后面的测试不用跑了，直接报错
    assert response.status_code == 200, "前置登录失败，拿不到Token！"

    # 3. 提取 token
    token = response.json()["access_token"]
    return token


# 创建一个注册的夹具，将注册时用到的数据信息发送出去
@pytest.fixture(scope="session")
def setup_test_user(api_client):
    """
    自动前置准备：在测试开始前，确保数据库有这个账号
    """
    payload = {"username": "ceshi001", "password": "123456"}
    response = api_client.post(f"{api_client.base_url}/register", json=payload)

    # 企业级断言：要么注册成功(200)，要么报“用户名已存在”(400)
    # 只要是这两个结果，都说明环境是正常的，前置准备算成功
    if response.status_code == 200:
        print("\n✅ 测试前置：新用户注册成功")
    elif response.status_code == 400 and "已存在" in response.text:
        print("\nℹ️ 测试前置：用户已存在，直接复用")
    else:
        # 如果是别的报错（比如 500 服务器崩了），必须让测试直接 ERROR！
        pytest.fail(f"❌ 测试前置失败！注册接口异常，状态码: {response.status_code}")

    return payload