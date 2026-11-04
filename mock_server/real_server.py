import pymysql
from pymysql.cursors import DictCursor
import time
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from jose import jwt

app = FastAPI(title="真实电商靶机")

# 封装一个获取数据库连接的函数，方便复用
def get_db():
    return pymysql.connect(
        host="127.0.0.1", port=3307, user="root", password="123456",
        database="ecommerce", cursorclass=DictCursor
    )
# ================= 数据模型 =================
class UserBase(BaseModel):
    username: str
    password: str


class ItemBase(BaseModel):
    name: str
    price: float


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


# 4. 查所有用户（只有 admin 能查，测试垂直越权！）
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