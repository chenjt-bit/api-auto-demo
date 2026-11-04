#封装添加商品的请求
class eCommerceItemApi:
    def __init__(self,api_client):
        self.client = api_client
        self.endpoint = "/items"

    #添加商品的请求函数
    def post_items(self,item_payload=None,**kwargs):
        url = f"{self.client.base_url}{self.endpoint}"
        if item_payload == None:
            return self.client.post(url,**kwargs)
        return self.client.post(url,json=item_payload,**kwargs)