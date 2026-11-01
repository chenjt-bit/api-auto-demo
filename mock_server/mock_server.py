# 这是一个靶机服务器，包含注册和登录接口
import sqlite3#python自带的一个轻量小型的数据库
#fastapi：目前 Python 最火的 Web 后端框架。它的特点是代码少、速度极快，而且自带一个极其漂亮的交互式接口文档。
from fastapi import FastAPI,HTTPException,Header
from pydantic import BaseModel
from jose import jwt#这个是用来生成token加密的

app = FastAPI()


# 1. 初始化真实的 SQLite 数据库（会在当前目录生成一个 test.db 文件）
def init_db():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()


init_db()


# 定义接收的数据格式
class UserBase(BaseModel):
    username: str
    password: str


# 2. 注册接口
@app.post("/register")
def register(user: UserBase):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    #对数据字段的内容格式进行一个校验
    if not user.username or not user.password:
        raise HTTPException(status_code=422, detail="账号或密码格式不对")

    # 🚨 新增：唯一性校验（先查一下库里有没有这个人）
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()  # 查完记得关连接
        # 返回 400 Bad Request，表示请求有误（业务规则冲突）
        raise HTTPException(status_code=400, detail="用户名已存在，请换一个")


    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
    conn.commit()
    conn.close()
    return {"msg": "注册成功"}


# 3. 登录接口（生成 Token）
@app.post("/login")
def login(user: UserBase):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user.username, user.password))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 生成一个 JWT Token (假密钥)
    token = jwt.encode({"sub": user.username}, "my_secret_key", algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# 4. 受保护的接口（必须带 Token 才能访问）
@app.get("/users/me")
def get_my_info(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Token")

    actual_token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(actual_token, "my_secret_key", algorithms=["HS256"])
        return {"username": payload["sub"], "message": "恭喜你，鉴权通过！"}
    except:
        raise HTTPException(status_code=401, detail="Token 无效")