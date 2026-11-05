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
    
    #封装查询商品的请求函数
    def get_items(self,headers=None,**kwargs):
        url = f"{self.client.base_url}{self.endpoint}"
        return self.client.get(url,headers=headers,**kwargs)

    #封装删除商品的请求函数
    def delete_item(self,item_id,headers=None,**kwargs):
        url = f"{self.client.base_url}{self.endpoint}/{item_id}"
        return self.client.delete(url,headers=headers,**kwargs)
            