#!/usr/bin/env python3
"""把中文归档夹具复制到独立临时工作目录，恢复 Nuxt 约定的目录名称。"""
from pathlib import Path
import shutil
import sys


def main():
    source = Path(__file__).resolve().parent / "01-静态机制夹具"
    root = next(parent for parent in source.parents if (parent / "docs/README.md").is_file())
    destination = Path(sys.argv[1]).resolve()
    if destination == root or destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError("夹具工作目录须在项目外")
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copytree(source, destination)
    (destination / "01-应用").rename(destination / "app")
    (destination / "app/01-页面").rename(destination / "app/pages")
    (destination / "app/pages/01-游戏").rename(destination / "app/pages/games")
    print(destination)


if __name__ == "__main__":
    main()
