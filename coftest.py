import pytest
import request
from config.settings import BASE_URL,CONNECT_TIMEOUT,READ_TIMEOUT,accounts

#api_client:api（接口）client（用户端）：这个夹具负责所有接口请求的发送
@pytest.fixture(scope="session")
def api_client():
    # 1. 准备阶段：创建一个 Session 对象
    session = request.Session()
    session.headers.update({"Accept": "application/json"})
    
    session.base_url = BASE_URL
    # 💡 核心技巧：给 session 统一配置超时
    # 这是一个元组 (连接超时时间, 读取超时时间)
    session.timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)

    # 2. 把准备好的东西交出去
    yield session

    # 3. 清理阶段：测试跑完后，关掉连接
    session.close()