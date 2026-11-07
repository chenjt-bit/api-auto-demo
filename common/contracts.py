# common/contracts.py
"""接口契约校验：JSON Schema 的加载与断言。

与 common/assertions.py 的分工：
- assertions.py：断言"这次 HTTP 交互对不对"（状态码、字段值、失败现场）
- contracts.py ：断言"响应结构对不对"（字段类型、必填项、额外字段）

用法：
    from common.contracts import assert_schema

    assert_schema(response, "item_created.schema.json")
"""

import json
import os

import jsonschema

from common.assertions import dump
from config.settings import BASE_DIR

# 契约文件目录：锚定项目根，不依赖启动目录
SCHEMA_DIR = os.path.join(BASE_DIR, "tests", "schemas")


def load_schema(filename):
    """读取 tests/schemas/ 下的契约文件。"""
    with open(os.path.join(SCHEMA_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def assert_schema(response, filename):
    """用 JSON Schema 校验响应体；失败时给出字段路径与完整响应。"""
    try:
        jsonschema.validate(instance=response.json(), schema=load_schema(filename))
    except jsonschema.ValidationError as exc:
        raise AssertionError(f"响应契约不符（{filename}）：{exc.message}\n\n{dump(response)}")
