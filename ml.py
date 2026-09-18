import os
from pathlib import Path


def print_directory_tree(
        root_dir: str,
        ignore_dirs: list = None,
        ignore_files: list = None,
        prefix: str = "",
        is_last: bool = True
) -> None:
    """
    递归打印目录树形结构

    Args:
        root_dir: 要遍历的根目录路径
        ignore_dirs: 要忽略的目录名列表
        ignore_files: 要忽略的文件名/后缀列表
        prefix: 用于格式化输出的前缀字符串
        is_last: 当前节点是否是最后一个子节点
    """
    # 设置默认忽略项
    if ignore_dirs is None:
        ignore_dirs = [
            "__pycache__", ".git", ".vscode", "venv", "env",
            ".idea", "node_modules", ".pytest_cache"
        ]
    if ignore_files is None:
        ignore_files = [".pyc", ".pyo", ".log", ".DS_Store"]

    # 转换为Path对象，增强路径处理能力
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"错误：目录 {root_dir} 不存在！")
        return

    # 区分目录和文件，按名称排序
    entries = sorted(os.listdir(root_path))
    dirs = []
    files = []
    for entry in entries:
        entry_path = root_path / entry
        # 过滤忽略的目录
        if entry_path.is_dir() and entry not in ignore_dirs:
            dirs.append(entry)
        # 过滤忽略的文件
        elif entry_path.is_file():
            # 检查文件后缀是否在忽略列表中
            ignore = False
            for ext in ignore_files:
                if entry.endswith(ext):
                    ignore = True
                    break
            if not ignore:
                files.append(entry)

    # 合并目录和文件（目录在前，文件在后）
    all_entries = dirs + files
    total = len(all_entries)

    for index, entry in enumerate(all_entries):
        entry_path = root_path / entry
        is_last_entry = index == total - 1

        # 打印前缀和当前条目
        connector = "└── " if is_last_entry else "├── "
        print(f"{prefix}{connector}{entry}")

        # 递归处理子目录
        if entry_path.is_dir():
            # 计算子目录的前缀
            new_prefix = prefix + ("    " if is_last_entry else "│   ")
            print_directory_tree(
                str(entry_path),
                ignore_dirs,
                ignore_files,
                new_prefix,
                is_last_entry
            )


if __name__ == "__main__":
    # 替换为你的项目根目录路径
    # 示例：Windows路径 "C:/Users/xxx/handwriting-recognition"
    #       Mac/Linux路径 "/Users/xxx/handwriting-recognition"
    PROJECT_ROOT = "./"  # 当前目录，可自行修改

    print(f"项目目录结构: {PROJECT_ROOT}")
    print("=" * 50)
    print_directory_tree(PROJECT_ROOT)