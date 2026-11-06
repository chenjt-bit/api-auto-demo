import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB  # 🌟 1. 导入连接池
import time
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel,Field
from jose import jwt

app = FastAPI(title="真实电商靶机")
# 🌟 2. 初始化全局连接池
# 这个池子会在服务器启动时只执行一次
POOL = PooledDB(
    creator=pymysql,      # 指定用哪个库建连接
    maxconnections=20,    # 最大连接数（超出这个数，后面的请求会排队等）
    mincached=5,          # 初始化时，先建 5 个空连接备用
    blocking=True,        # 连接池满了之后，是否阻塞等待（True = 排队，False = 直接报错）
    ping=1,               # 每次借出连接时，先 ping 一下，保证连接是活的
    host="127.0.0.1",     # 👈 注意换成你自己的 MySQL 配置
    port=3307,
    user="root",
    password="123456",
    database="ecommerce",
    cursorclass=DictCursor
)
#🌟 新增：每次服务启动时，自动建库建表！
def init_db():
    try:
        # 先连一个空的库，用来建库
        conn = pymysql.connect(host="127.0.0.1", port=3307, user="root", password="123456")
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ecommerce DEFAULT CHARSET utf8mb4;")
        cursor.execute("USE ecommerce;")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(50),
                role VARCHAR(20)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50),
                price FLOAT,
                owner_id INT
            )
        ''')

        # 预置 admin（用 INSERT IGNORE 防止重复报错）
        cursor.execute("INSERT IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


# 启动时执行初始化
init_db()

# 封装一个获取数据库连接的函数，方便复用
def get_db():
    # 🌟 3. 不再新建连接，而是从池子里“借”一个
    return POOL.connection()

# ================= 数据模型 =================
class UserBase(BaseModel):
    username: str
    password: str


class ItemBase(BaseModel):
    # 限制名字不能为空，且最长 50
    name: str = Field(..., min_length=1, max_length=50)
    # 限制价格必须大于 0
    price: float = Field(..., gt=0)


# ================= 鉴权工具 =================
SECRET_KEY = "super_secret_key"

def verify_token(token: str = Header(None)):
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Token无效")


# ================= 接口路由 =================

# 1. 注册（默认注册为普通用户）
@app.post("/register")
def register(user: UserBase):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")

    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (user.username, user.password))
    conn.commit()
    conn.close()
    return {"msg": "注册成功"}


# 2. 登录（生成 Token）
@app.post("/login")
def login(user: UserBase):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username = %s AND password = %s", (user.username, user.password))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 把用户 ID 和角色（role）加密进 Token
    token = jwt.encode({"user_id": db_user["id"], "role": db_user["role"]}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# 3. 发布商品（任何登录用户都能发）
@app.post("/items")
def create_item(item: ItemBase, token_info: str = Header(None, alias="Authorization")):
    user_data = verify_token(token_info)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price, owner_id) VALUES (%s, %s, %s)",
                   (item.name, item.price, user_data["user_id"]))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"msg": "发布成功", "item_id": new_id}

# 4、查询商品（显示全部商品）
@app.get("/items")
def get_items(token_info: str = Header(None, alias="Authorization")):
    #鉴权token,没登录不给查
    user_data = verify_token(token_info)
    # 连接数据库
    conn = get_db()
    cursor = conn.cursor()

    # 2. 核心 SQL：联表查询（JOIN）
    # 这里我们把 items 表和 users 表连起来，查出商品信息和发布者的名字
    sql = """
            SELECT items.id, items.name, items.price, users.username AS owner 
            FROM items 
            JOIN users ON items.owner_id = users.id
            ORDER BY items.id DESC
        """
    cursor.execute(sql)
    # 3. 获取所有数据（因为你配置了 DictCursor，这里直接返回的就是字典列表）
    items_list = cursor.fetchall()

    cursor.close()
    conn.close()

    # 4. 返回 JSON 响应
    return {"code": 200, "msg": "查询成功", "data": items_list}

# 5.根据商品id删除指定商品
@app.delete("/items/{item_id}")
def delete_item(item_id: int, token_info: str = Header(None, alias="Authorization")):
    #鉴权token并解析当前登录的人的id
    user_data = verify_token(token_info)
    current_user_id = user_data["user_id"]
    user_role = user_data["role"]

    conn = get_db()
    cursor = conn.cursor()

    # 2. 先查一下这个商品到底存不存在
    cursor.execute("SELECT owner_id FROM items WHERE id = %s", (item_id,))
    item = cursor.fetchone()

    if not item:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="商品不存在")

    # 3. 核心防越权逻辑：判断商品的主人，是不是当前登录人
    # 注意：如果是管理员 (admin)，则允许删除任何商品（企业级常见逻辑）
    if item["owner_id"] != current_user_id and user_role != "admin":
        cursor.close()
        conn.close()
        # 如果不是自己的，也不是管理员，直接拒绝（403）
        raise HTTPException(status_code=403, detail="越权警告：你没有权限删除别人的商品！")

    # 4. 权限校验通过，执行删除
    cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return {"code": 200, "msg": "删除成功"}

# 6. 查所有用户（只有 admin 能查，测试垂直越权！）
@app.get("/admin/users")
def get_all_users(token_info: str = Header(None, alias="Authorization")):
    user_data = verify_token(token_info)
    if user_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="普通用户无权访问，必须是管理员！")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = [{"id": u["id"], "username": u["username"], "role": u["role"]} for u in cursor.fetchall()]
    conn.close()
    return users

