from python_path import python_root, python_scripts_root
from win_env_path import remove_from_sys_path


def main():
    remove_from_sys_path(python_root)
    remove_from_sys_path(python_scripts_root)


if __name__ == "__main__":
    main()
