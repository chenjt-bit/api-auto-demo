# config/settings.py
# 全项目唯一读环境变量的地方

import os
from dotenv import load_dotenv

# 项目根目录：config 的上一级
# __file__ 是当前文件路径，abspath 转绝对路径，dirname 取上级，两次就到项目根
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VALID_ENVS = ["dev", "test", "prod"]

# 缓存变量：第一次读完后存在这里，之后直接返回，不用重复读文件
_settings = None


def _read_env_file(env):
    """读 .env.dev / .env.test，返回文件路径；文件不存在就返回 None"""
    env_file = os.path.join(BASE_DIR, ".env." + env)
    if not os.path.exists(env_file):
        return None
    # override=False：已经存在的环境变量优先，不允许被文件覆盖
    load_dotenv(env_file, override=False)
    return env_file


def _get(name, default):
    """读环境变量；没设置、或设置了空字符串，都用默认值"""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _build():
    """真正组装配置的私有函数，只在第一次调用时执行"""
    env = _get("ENV", "dev").lower()
    if env not in VALID_ENVS:
        raise ValueError("未知环境 ENV=" + env + "，可选：" + str(VALID_ENVS))

    env_file = _read_env_file(env)

    return {
        "env": env,
        "env_file": env_file,
        "base_url": _get("BASE_URL", "http://127.0.0.1:8081"),
        "connect_timeout": float(_get("CONNECT_TIMEOUT", "3")),
        "read_timeout": float(_get("READ_TIMEOUT", "10")),
        "db_config": {
            "host": _get("DB_HOST", "127.0.0.1"),
            "port": int(_get("DB_PORT", "3307")),
            "user": _get("DB_USER", "root"),
            "password": _get("DB_PASSWORD", "123456"),
            "database": _get("DB_NAME", "ecommerce"),
            "charset": "utf8mb4",
        },
        "admin_username": _get("ADMIN_USERNAME", "admin"),
        "admin_password": _get("ADMIN_PASSWORD", "admin123"),
    }


def get_settings():
    """对外唯一入口：返回一个字典"""
    global _settings          # 声明我要改的是外面那个全局变量
    if _settings is None:     # 第一次调用才真正去读
        _settings = _build()
    return _settings


def reload_settings():
    """清空缓存重新读。改了环境变量之后要调用它"""
    global _settings
    _settings = None
    return get_settings()