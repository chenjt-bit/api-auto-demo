# 在这个文件中创建关于api的类
# api/posts_api


#创建PostsApi类
class PostsApi:
    #1、__init__是初始化方法，每次创建类的时候这个方法都会调用
    def __init__(self,api_client):
        self.__client = api_client
        self.__endpoint = "/posts"# 把这个模块的公共路径抽出来
        #获取一下“超时时间”timeout
        self.__timeout = api_client.time_out

    # 2、封装“获取单篇文章”的请求
    def get_post(self,post_id):
        # 拼装url发送get请求
        url = f"{self.__client.base_url}{self.__endpoint}/{post_id}"
        return self.__client.get(url,timeout=self.__timeout)

    # 3、封装创建文章的请求（post）
    def create_post(self,data):
        # data是字典数据类型，requests发送post请求时会自动将字典转换为json数据类型
        url = f"{self.__client.base_url}{self.__endpoint}"
        return self.__client.post(url,json=data,timeout=self.__timeout)

    # 4、删除文章的请求
    def delete_post(self,post_id):
        url = f"{self.__client.base_url}{self.__endpoint}/{post_id}"
        return self.__client.delete(url,timeout=self.__timeout)