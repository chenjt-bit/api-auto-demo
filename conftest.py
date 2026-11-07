# 在这个文件中创建pytest的钩子函数
# 实现在命令行切换pytest时的环境
import pytest
import os

# 钩子函数是固定命名：pytest_addoption
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "test", "prod"],  # ← 新增这行
        help="指定测试环境：dev,test,prod"
    )

# 🌟 新增这个钩子：在框架初始化时，把参数写进环境变量
def pytest_configure(config):
    # 获取命令行传入的 --env 参数
    env = config.getoption("--env")
    # 将其写入系统环境变量
    os.environ["ENV"] = env
    print(f"\n 正在启动测试，当前环境切换为: {env}")


# ==================== 用例 ID 追溯 ====================

DOC_URL = "https://github.com/chenjt-bit/api-auto-demo/tree/main/docs"


def pytest_collection_modifyitems(config, items):
    """把 @allure.id 的用例编号同步成 testCaseId 标签与用例链接。

    allure.id("x") 实际写入的是 allure_label(label_type="as_id")；
    这里再补一个通用的 testCaseId 标签，方便报告展示与结果检索，
    并加上指向 docs/ 的链接，报告里点一下就能回到用例设计文档。

    同时强制：每条用例都必须带 @allure.id，否则收集阶段直接失败，
    避免新增用例时忘记登记编号。
    """
    missing = []

    for item in items:
        case_id = None
        for marker in item.iter_markers("allure_label"):
            if marker.kwargs.get("label_type") == "as_id" and marker.args:
                case_id = marker.args[0]
                break

        if not case_id:
            missing.append(item.nodeid)
            continue

        item.add_marker(pytest.mark.allure_label(case_id, label_type="testCaseId"))
        item.add_marker(pytest.mark.allure_link(DOC_URL, name=case_id, link_type="tms"))

    if missing:
        raise pytest.UsageError(
            "以下用例缺少 @allure.id(\"用例编号\")，请先在 docs/用例追溯表.md 登记：\n  "
            + "\n  ".join(missing)
        )