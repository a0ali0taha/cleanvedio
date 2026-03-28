"""Unified app/resource/data directory resolution (dev, frozen bundle, env overrides)."""
import os
import sys


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_app_root() -> str:
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_root() -> str:
    if is_frozen():
        return getattr(sys, "_MEIPASS", get_app_root())
    return get_app_root()


def get_data_root() -> str:
    env_root = os.environ.get("CLEANVEDIO_DATA_DIR")
    if env_root:
        return os.path.abspath(env_root)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return os.path.join(local_app_data, "CleanVedio")
    return get_app_root()


def ensure_data_root() -> str:
    root = get_data_root()
    os.makedirs(root, exist_ok=True)
    return root
