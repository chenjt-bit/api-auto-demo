import time
import uuid

import pymysql
import pytest
import requests
from pymysql.cursors import DictCursor

from config.settings import get_settings


# ==================== 基础资源 ====================

@pytest.fixture(scope="session")
def settings():
    """配置只取一次，整个会话共用。"""
    return get_settings()


# api_client: api（接口）client（客户端）：负责所有接口请求的发送
@pytest.fixture(scope="session")
def api_client(settings):
    # 1. 准备阶段：创建一个 Session 对象
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    session.base_url = settings["base_url"]
    # 给 session 统一配置超时：元组 (连接超时, 读取超时)
    session.timeout = (settings["connect_timeout"], settings["read_timeout"])

    # 2. 把准备好的东西交出去
    yield session

    # 3. 清理阶段：测试跑完后，关掉连接
    session.close()


@pytest.fixture(scope="session")
def db_conn(settings):
    """整个测试会话共用一条 MySQL 连接（作用域 session）。

    为什么把连接提到 session 级？
    - 每条用例新建连接 = 每条用例一次 TCP 握手 + 认证，慢且浪费；
    - 连接是"重"资源，游标是"轻"资源，所以连接共享、游标按用例新建（见 db_message）。

    autocommit=True：清理语句执行即生效，不用手工 commit。
    （用例只读数据，不存在事务隔离问题）
    """
    conn = pymysql.connect(
        **settings["db_config"],
        cursorclass=DictCursor,
        autocommit=True,
    )
    yield conn
    conn.close()


# 创建一个调用数据库的夹具，返回想查的数据库数据
@pytest.fixture
def db_message(db_conn):
    """单条用例使用的游标。

    游标是"有状态"的（记住上次执行到哪），所以不能跨用例共享，
    用例结束就关掉；底层连接由 db_conn 统一管理。
    """
    cursor = db_conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()


# ==================== 本次运行的数据登记与回收 ====================

@pytest.fixture(scope="session")
def run_id():
    """本次运行的唯一标识，写进数据名字里，方便识别与兜底清理。

    形如：run_20261106_2220_ab12
    """
    return time.strftime("run_%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:4]


@pytest.fixture(scope="session")
def created_data(db_conn):
    """登记本次运行造出来的数据，会话结束时统一回收。

    为什么不用下面两种"省事"的做法？
    1. TRUNCATE TABLE：测试库可能是多人共用的，一执行就清空别人的数据；
    2. DELETE WHERE id > 某个快照值：如果同时有压测/别人在写，会误删。
    只删"自己登记过的 id / 用户名"，才不会误伤。
    """
    data = {"item_ids": [], "usernames": []}

    yield data

    # 会话结束（无论用例成功还是失败）都会执行这里
    cursor = db_conn.cursor()
    deleted_items = 0
    deleted_users = 0
    try:
        # 先删商品、再删用户：保留父子顺序，将来加了外键也不会报错
        for item_id in data["item_ids"]:
            deleted_items += cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        for username in data["usernames"]:
            deleted_users += cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    finally:
        cursor.close()

    print(f"\n[cleanup] 回收 items {deleted_items} 条、users {deleted_users} 条")
