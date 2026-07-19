"""检查对外发布压缩包是否意外包含私有控制代码。"""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


FORBIDDEN_SUFFIXES = (
    "/examples/main_hybrid.py",
    "\\examples\\main_hybrid.py",
)
REQUIRED_SDIST_SUFFIX = "/examples/main_hybrid_basic.py"
REQUIRED_WHEEL_SUFFIX = "metacar_hybrid/hybrid_basic.py"


def archive_members(path: Path) -> list[str]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()

    if path.name.endswith(".tar.gz"):
        with tarfile.open(path, mode="r:gz") as archive:
            return archive.getnames()

    raise ValueError(f"不支持的发布文件: {path}")


def check_archive(path: Path) -> None:
    members = archive_members(path)
    leaked = [
        member
        for member in members
        if any(member.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)
    ]
    if leaked:
        raise RuntimeError(f"{path.name} 包含私有文件: {', '.join(leaked)}")

    if path.name.endswith(".tar.gz") and not any(
        member.endswith(REQUIRED_SDIST_SUFFIX) for member in members
    ):
        raise RuntimeError(f"{path.name} 缺少公开基础示例")

    if path.suffix == ".whl":
        legacy_package = [member for member in members if member.startswith("metacar/")]
        if legacy_package:
            raise RuntimeError(
                f"{path.name} 仍包含会与上游冲突的 metacar 导入包: "
                + ", ".join(legacy_package)
            )

    if path.suffix == ".whl" and not any(
        member.endswith(REQUIRED_WHEEL_SUFFIX) for member in members
    ):
        raise RuntimeError(f"{path.name} 缺少可安装的基础示例")

    print(f"{path.name}: 隐私检查通过")


def main(paths: list[str]) -> None:
    if not paths:
        raise SystemExit("请传入需要检查的 wheel 或 sdist")

    for value in paths:
        check_archive(Path(value))


if __name__ == "__main__":
    main(sys.argv[1:])
