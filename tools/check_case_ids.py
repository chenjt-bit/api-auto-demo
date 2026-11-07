# -*- coding: utf-8 -*-
"""用例 ID 追溯检查（可直接作为 CI 门禁）。

检查四件事：
1. tests/ 下每个 test_* 函数必须带 @allure.id("...")；
2. 用例 ID 不能重复；
3. 代码里的 ID 必须登记在 docs/用例追溯表.md；
4. 追溯表里标记为 ✅ 的 ID，代码中必须能找到对应实现。

用法：
    python tools/check_case_ids.py

退出码 0 表示通过；1 表示存在问题（CI 里会让流水线变红）。
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
DOC = ROOT / "docs" / "用例追溯表.md"

MARK_DONE = "✅"


def case_id_of(decorator):
    """识别 @allure.id("xxx")，返回其中的字符串；不是这种装饰器则返回 None。"""
    if not isinstance(decorator, ast.Call):
        return None
    func = decorator.func
    if not (isinstance(func, ast.Attribute) and func.attr == "id"):
        return None
    if not (isinstance(func.value, ast.Name) and func.value.id == "allure"):
        return None
    if decorator.args and isinstance(decorator.args[0], ast.Constant):
        return decorator.args[0].value
    return None


def scan_code():
    """扫描测试文件，返回 (带 ID 的用例列表, 缺少 ID 的用例列表)。"""
    found, missing = [], []
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue
            ids = [case_id_of(d) for d in node.decorator_list]
            ids = [i for i in ids if i]
            if not ids:
                missing.append(f"{rel}::{node.name}")
                continue
            found.append((ids[0], rel, node.name))
    return found, missing


def load_doc():
    """解析追溯表，返回 {用例ID: 自动化状态}。"""
    doc = {}
    if not DOC.exists():
        return doc
    for line in DOC.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ecommerce_"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5:
            doc[cells[0]] = cells[4]
    return doc


def main():
    found, missing = scan_code()
    doc = load_doc()

    errors = []
    seen = {}

    for case_id, rel, func in found:
        place = f"{rel}::{func}"
        if case_id in seen:
            errors.append(f"ID 重复：{case_id} 同时用于 {seen[case_id]} 和 {place}")
        seen[case_id] = place

    for case_id, rel, func in found:
        if case_id not in doc:
            errors.append(f"未登记：{case_id}（{rel}::{func}）不在 docs/用例追溯表.md 中")

    for case_id, state in doc.items():
        if MARK_DONE in state and case_id not in seen:
            errors.append(f"文档标记已自动化，但代码中找不到：{case_id}")

    for item in missing:
        errors.append(f"缺少 @allure.id：{item}")

    total_done = sum(1 for s in doc.values() if MARK_DONE in s)
    print(f"代码侧用例 ID：{len(found)} 个（去重后 {len(seen)} 个）")
    print(f"追溯表登记：{len(doc)} 条（其中标记已自动化 {total_done} 条）")
    print(f"缺少 ID 的用例：{len(missing)} 个")

    if errors:
        print(f"\n发现 {len(errors)} 个问题：")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n检查通过：ID 唯一、全部已登记、文档与代码一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
