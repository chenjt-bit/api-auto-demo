# 接口自动化测试框架实战：真实电商业务流

## 📌 项目简介
本项目是一个基于 `Python + Pytest + Requests` 搭建的企业级接口自动化测试框架。
项目摒弃了市面上的“假接口”演示，采用 `FastAPI + SQLite` 自主构建了一个高仿真的电商后端靶机。测试用例覆盖了真实业务中的**多角色鉴权、JWT Token 接口关联、发布商品业务流**，并深度结合了**数据库落库断言**。同时，项目已接入 `GitHub Actions` 实现云端 CI/CD 持续集成。

## 🛠️ 技术栈
*   **核心语言**：Python 3.12
*   **测试框架**：Pytest
*   **网络请求**：Requests (Session 复用与超时控制)
*   **数据校验**：jsonschema (接口契约校验)
*   **数据驱动**：YAML
*   **数据库**：SQLite3 (直连数据库进行底层数据断言)
*   **CI/CD**：GitHub Actions

## 📂 核心架构与分域设计
项目采用了清晰的**分层架构**与**业务分域**，严格隔离测试数据与业务逻辑，目录结构如下：

```text
api-auto-demo/
├── .github/workflows/    # GitHub Actions CI/CD 流水线配置
├── api/                  # 接口封装层 (如 posts_api.py)
├── config/               
|    |——settings          # 全局配置层 (环境地址、账号池等)
├── data/                 # 数据驱动层 (YAML 测试数据)
├── mock_server/          # 真实后端靶机 (FastAPI + SQLite)
│   ├── real_server.py    # 电商业务 API 源码
│   └── ecommerce.db      # 真实测试数据库
├── tests/                # 测试用例层
│   ├── conftest.py       # 全局 Fixture (Session、动态测试账号生成等)
│   ├── practice/         # 【练习区】历史爬坑练习用例，已通过 pytest.ini 忽略
│   └── ecommerce/        # 【电商项目】真实业务实战测试用例
│       ├──test_ecommerce.py
|       |——test_login.py
│       └── test_items.py
├── pytest.ini            # Pytest 全局配置文件
└── README.md
核心亮点与测试维度
动态前置数据准备（Fixture）：使用时间戳动态注册唯一测试账号，彻底解决自动化测试中“数据污染”和“重复执行报错”的痛点。
复杂的鉴权与越权防护测试：不仅测试正常的 JWT 鉴权流转，还专门设计了垂直越权用例（普通用户强制访问管理员接口，断言返回 403 Forbidden）。
接口 + 数据库双重断言：拒绝“接口返回 200 就代表成功”的表面测试。测试发布商品后，通过 sqlite3 直连底层数据库，验证 item 数据是否真正持久化落库。

企业级 CI/CD 流水线：通过 .github/workflows/test.yml 配置，实现代码 Push 后，云端自动安装依赖、后台启动靶机服务、执行健康检查探测（curl），最后全量运行测试。
⚙️ 本地运行指南
1. 安装依赖
bash
# 建议在虚拟环境下运行
pip install -r requirements.txt
2. 启动真实靶机服务器
bash
cd mock_server
uvicorn real_server:app --reload --port 8081
(注意：请保持该终端窗口开启，靶机正在 8081 端口提供服务)
3. 执行自动化测试
打开一个新的终端（在项目根目录下）：
bash
# 运行全量测试（会自动跳过 practice 目录）
pytest
# 仅运行电商核心业务流测试
pytest tests/ecommerce/ -v
💡 该项目为个人进阶学习实战项目，持续迭代中。
