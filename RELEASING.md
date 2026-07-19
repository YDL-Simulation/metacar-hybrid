# 发布手册

本文档用于发布独立产品 `metacar-hybrid`。Python 导入名为 `metacar_hybrid`，产品版本号不跟随上游 MetaCar。

## 首次发布前的一次性设置

### 1. GitHub 仓库

在 `YDL-Simulation` 组织下创建公开空仓库 `metacar-hybrid`，不要初始化 README、`.gitignore` 或 License。将本地仓库推送后，在仓库设置中创建名为 `pypi` 的 Environment。

建议由组织管理员完成：

- 授予维护者仓库 Admin 权限，以便维护 Actions、Environment 和发布设置。
- 保护 `main` 分支，要求 `Python tests` 中的测试、构建、文档和公开边界检查通过。
- 禁止强制推送和删除 `main` 分支。
- 开启 GitHub 的私密漏洞报告功能。

### 2. PyPI Trusted Publisher

登录 PyPI 后打开账号的 Publishing 设置，创建 Pending Trusted Publisher：

| 字段 | 值 |
| --- | --- |
| PyPI project name | `metacar-hybrid` |
| GitHub owner | `YDL-Simulation` |
| Repository name | `metacar-hybrid` |
| Workflow name | `python-publish.yml` |
| Environment name | `pypi` |

Pending Publisher 允许尚不存在的 PyPI 项目由指定 GitHub Actions 工作流完成首次创建。仓库、工作流文件名和 Environment 必须完全匹配。

## 每次发布

1. 从最新 `main` 创建发布准备分支。
2. 更新 `metacar_hybrid/__init__.py` 中的 `__version__`。
3. 把 `CHANGELOG.md` 对应版本从“未发布”改为发布日期。
4. 检查并更新 `UPSTREAM.md` 的上游标签和提交哈希。
5. 运行发布前检查：

   ```bash
   python scripts/check_public_repository.py
   python -m pytest
   python -m build
   python -m twine check --strict dist/*
   python scripts/check_release_artifacts.py dist/*
   sphinx-build -W -E -b html docs docs/_build/html
   ```

6. 合并 Pull Request，等待 `main` 的全部检查通过。
7. 在 GitHub 创建新 Release，标签必须严格等于 `v` 加包版本，例如 `v0.1.0a2`。
8. 发布 Release 后，`Upload Python Package` 工作流会重新测试、构建并通过 Trusted Publishing 上传 PyPI。
9. 在干净环境验证：

   ```bash
   python -m venv verify-env
   verify-env/Scripts/python -m pip install --pre metacar-hybrid
   verify-env/Scripts/python -c "import metacar_hybrid; print(metacar_hybrid.__version__)"
   ```

Linux 或 macOS 将 `verify-env/Scripts/python` 改为 `verify-env/bin/python`。

## 发布失败或版本有误

- PyPI 上已经使用的版本号不能覆盖上传，也不要尝试复用。
- 修复代码后增加版本号，例如从 `0.1.0a1` 改为 `0.1.0a2`，重新走完整流程。
- 如果 GitHub Release 的标签与 `metacar_hybrid.__version__` 不一致，工作流会在上传前失败。
- 如果公开仓库或发布包包含完整内部测试代码，门禁会在上传前失败。
