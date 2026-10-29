# import requests
import pytest# 导入pytest，使用其框架
from jsonschema import validate #这个是用来校验返回的数据字段结构的
import yaml 
from api.posts_api import PostsApi # 导入PostsApi类

# 定义体检单（规则）
POST_SCHEMA = {
    "type":"object",
    "required":["userId","id","title","body"],
    "properties":{
        "userId":{"type":"integer"},
        "id":{"type":"integer"},
        "title":{"type":"string"},
        "body":{"type":"string"}
    }
}

# 2、创建一个“服务员”：实例化PostsApi类
# 选择使用夹具fixture的方式，因为测试函数调用时，pytest会自动到fixture找所需资源
@pytest.fixture
def posts_api(api_client):
    return PostsApi(api_client)

#3、正常测试路径
def test_get_single_post(posts_api):
    response = posts_api.get_post(1)# 发送查询第一篇文章的get请求
    # 状态码断言
    assert response.status_code == 200
    assert response.json()["id"] == 1

# 4、异常路径测试
def test_get_nonexistent_post(posts_api):
    response = posts_api.get_post(9999)
    assert response.status_code == 404

# 5、结构校验测试
def test_post_structure(posts_api):
    #我需要校验结构，也就是要使用到jsonschema其中的validate
    #使用validate是：validate(instance = body,schema = POSTS_SCHEMA)
    #也就是intance = 响应的json（）数据，还有schema = 定义的结构
    response = posts_api.get_post(1)
    body = response.json()
    validate(instance=body,schema=POST_SCHEMA)

# 6、数据驱动测试（YAML 读取+封装）
@pytest.mark.parametrize("posts_data",
                         yaml.safe_load(open("data/posts_data.yaml","r",encoding="utf-8"))
                         )

def test_multiple_posts_from_yaml(posts_api,posts_data):
    post_id = posts_data["id"]
    response = posts_api.get_post(post_id)
    assert response.status_code == 200
    assert response.json()["id"] == post_id


# 执行删除请求
def test_delete_post(posts_api):
    response = posts_api.delete_post(1)
    assert response.status_code == 200
    # assert response.status_code == 404