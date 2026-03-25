import winreg
from typing import List

from path_utils import is_same_file

type_mapper = {str: winreg.REG_SZ, int: winreg.REG_DWORD, bytes: winreg.REG_BINARY}
sys_reg_root = winreg.HKEY_LOCAL_MACHINE
sys_reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

user_reg_root = winreg.HKEY_CURRENT_USER
user_reg_path = r"Environment"


def get_key(root, path: str, key: str):
    try:
        with winreg.OpenKey(root, path) as k:
            val, reg_type = winreg.QueryValueEx(k, key)
            return val
    except WindowsError:
        return None


def set_key(root, path: str, key: str, val: any):
    with winreg.CreateKey(root, path) as k:
        reserved = 0
        winreg.SetValueEx(k, key, reserved, type_mapper[type(val)], val)


def get_sys_path() -> List[str]:
    path: str = get_key(sys_reg_root, sys_reg_path, "Path")
    return path.split(';') if path else []


def set_sys_path(new_value: List[str]):
    set_key(sys_reg_root, sys_reg_path, "Path", ";".join(new_value))


def get_user_path() -> List[str]:
    path: str = get_key(user_reg_root, user_reg_path, "Path")
    return path.split(';') if path else []


def set_user_path(new_value: List[str]):
    set_key(user_reg_root, user_reg_path, "Path", ";".join(new_value))


def add_to_user_path(new_path: str, ):
    """
    Add **one** path into PATH of current user
    """
    assert ';' not in new_path
    old_fixed_paths = get_user_path()
    for p in old_fixed_paths:
        if is_same_file(p, new_path):
            return
    old_paths = get_user_path()
    return set_user_path([new_path, *old_paths])


def add_to_sys_path(new_path: str):
    """
    Add **one** path into PATH of SYSTEM
    """
    assert ';' not in new_path
    old_fixed_paths = get_sys_path()
    for p in old_fixed_paths:
        if is_same_file(p, new_path):
            return
    old_paths = get_sys_path()
    return set_sys_path([new_path, *old_paths])


def remove_from_user_path(path: str):
    """
    Remove **one** path from PATH of current user
    """
    assert ';' not in path
    old_paths = get_user_path()
    new_paths = [i for i in old_paths if not is_same_file(i, path)]
    if new_paths != old_paths:
        return set_user_path(new_paths)


def remove_from_sys_path(path: str):
    """
    Remove **one** path from PATH of SYSTEM
    """
    assert ';' not in path
    old_paths = get_sys_path()
    new_paths = [i for i in old_paths if not is_same_file(i, path)]
    if new_paths != old_paths:
        return set_sys_path(new_paths)
