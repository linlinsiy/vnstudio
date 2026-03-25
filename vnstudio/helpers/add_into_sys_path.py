from python_path import python_root, python_scripts_root
from win_env_path import add_to_sys_path


def main():
    add_to_sys_path(python_root)
    add_to_sys_path(python_scripts_root)


if __name__ == "__main__":
    main()
