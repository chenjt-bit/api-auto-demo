#在这个文件中封装电商项目ecommerce的登录模块的请求

class eCommerceLoginApi:
    def __init__(self,api_client):
        self.client = api_client
        self.endpoint = "/login"

    #封装用户登录的请求
    def get_login(self,login_payload=None,**kwargs):
        url = f"{self.client.base_url}{self.endpoint}"

        if login_payload == None:
            return self.client.post(url,**kwargs)

        return self.client.post(url,json = login_payload,**kwargs)
        