from locust import HttpUser, task, between
import time
import uuid  # 🌟 引入 UUID 库

class EcommerceUser(HttpUser):
    # 🌟 模拟真实用户的行为：每个请求之间随机等待 1~3 秒
    wait_time = between(1, 3)

    def on_start(self):
        """
        当每一个虚拟用户启动时，会执行一次 on_start
        这里我们为每个虚拟用户注册并登录，拿到专属的 Token
        """
        # 用 UUID 的前8位作为唯一后缀，绝对不会撞车
        unique_suffix = str(uuid.uuid4())[:8]
        self.username = f"locust_{unique_suffix}"
        self.password = "123456"

        # 1. 注册
        self.client.post("/register", json={"username": self.username, "password": self.password})

        # 2. 登录拿 Token
        res = self.client.post("/login", json={"username": self.username, "password": self.password})
        if res.status_code == 200:
            token = res.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    # 🌟 @task(3) 代表：在所有任务中，发布商品的概率是查询商品的 3 倍
    @task(3)
    def create_item(self):
        """模拟用户发商品"""
        payload = {
            "name": f"load_test_item_{int(time.time() * 1000)}",
            "price": 18.5
        }
        self.client.post("/items", json=payload, headers=self.headers)

    @task(1)
    def get_items(self):
        """模拟用户查询商品列表"""
        self.client.get("/items", headers=self.headers)