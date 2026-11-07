# common/assertions.py
"""统一的响应断言：失败时自动带上"发了什么请求、收到什么响应"。

裸写 assert response.status_code == 200 的问题：
失败时只看到 "500 != 200"，看不到请求体、响应体和业务错误信息，
只能复跑 + 打日志 + 猜，排查成本很高。

用法：
    from common.assertions import assert_json, assert_status

    assert_status(response, 200, "发布商品")
    assert_json(response, msg="发布成功")
"""

import json

import allure


def _pretty(response):
    """响应体转可读文本：JSON 格式化，非 JSON 原样返回。"""
    try:
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except ValueError:
        return response.text or "<empty>"


def dump(response):
    """把请求/响应整理成文本，并挂到 Allure 报告。"""
    request = response.request
    body = request.body
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")

    text = (
        f"{request.method} {request.url}\n"
        f"\n[请求体]\n{body or '<empty>'}\n"
        f"\n[响应状态码] {response.status_code}\n"
        f"\n[响应体]\n{_pretty(response)}"
    )
    allure.attach(text, name="失败现场", attachment_type=allure.attachment_type.TEXT)
    return text


def assert_status(response, expected=200, note=""):
    """断言状态码；不通过时把请求/响应写进报错信息。"""
    if response.status_code != expected:
        prefix = f"{note}：" if note else ""
        raise AssertionError(
            f"{prefix}状态码不符，期望 {expected}，实际 {response.status_code}\n\n"
            f"{dump(response)}"
        )


def assert_json(response, **expected):
    """断言响应 JSON 的字段值；不通过时给出字段级差异。"""
    data = response.json()
    for key, value in expected.items():
        actual = data.get(key)
        if actual != value:
            raise AssertionError(
                f"字段 {key} 不符，期望 {value!r}，实际 {actual!r}\n\n{dump(response)}"
            )
