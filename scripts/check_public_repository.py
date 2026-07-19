"""检查公开仓库当前文件和 Git 历史是否包含内部测试代码。"""

from __future__ import annotations

import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATHS = {
    "examples/main_hybrid.py",
}
REQUIRED_PATHS = {
    "examples/main_hybrid_basic.py",
    "metacar_hybrid/hybrid_basic.py",
    "scripts/check_release_artifacts.py",
}
PRIVATE_CODE_MARKERS = (
    "get_delta_from_trajectory",
    "TURN_FORCE",
    "TURN_COMMIT",
    "PHASE_",
    "emergency_stop",
)
CODE_DIRECTORIES = ("metacar_hybrid/", "examples/", "tests/")


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def normalized_paths(output: str) -> set[str]:
    return {
        line.strip().replace("\\", "/")
        for line in output.splitlines()
        if line.strip()
    }


def check_tracked_paths() -> set[str]:
    tracked = normalized_paths(git("ls-files"))
    leaked = sorted(FORBIDDEN_PATHS & tracked)
    if leaked:
        raise RuntimeError(f"公开仓库跟踪了私有文件: {', '.join(leaked)}")

    legacy_package = sorted(
        path for path in tracked if path == "metacar" or path.startswith("metacar/")
    )
    if legacy_package:
        raise RuntimeError(
            "当前版本仍跟踪旧 metacar 导入包: " + ", ".join(legacy_package)
        )

    missing = sorted(REQUIRED_PATHS - tracked)
    if missing:
        raise RuntimeError(f"公开仓库缺少必要文件: {', '.join(missing)}")

    return tracked


def check_history() -> None:
    historical = normalized_paths(
        git("log", "--all", "--format=", "--name-only", "--diff-filter=ACMR")
    )
    leaked = sorted(FORBIDDEN_PATHS & historical)
    if leaked:
        raise RuntimeError(
            "私有文件曾进入 Git 历史，不能直接公开此仓库: " + ", ".join(leaked)
        )


def check_private_markers(tracked: set[str]) -> None:
    candidates = sorted(
        path
        for path in tracked
        if path.endswith(".py") and path.startswith(CODE_DIRECTORIES)
    )
    leaked: list[str] = []

    for relative_path in candidates:
        content = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for marker in PRIVATE_CODE_MARKERS:
            if marker in content:
                leaked.append(f"{relative_path}: {marker}")

    if leaked:
        raise RuntimeError("发现内部策略标记:\n" + "\n".join(leaked))


def main() -> None:
    tracked = check_tracked_paths()
    check_history()
    check_private_markers(tracked)
    print("公开仓库文件、历史和内部策略标记检查通过")


if __name__ == "__main__":
    main()
