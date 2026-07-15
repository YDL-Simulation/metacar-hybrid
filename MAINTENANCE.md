# 双仓库维护手册

MetaCar Hybrid 使用两个职责明确的仓库维护：

- 内部开发仓库保存完整场景测试、轨迹跟踪算法、调试参数和未公开实验代码。
- `metacar-hybrid` 公开仓库只保存可发布的 SDK、基础示例、文档、测试和发布配置。

完整的 `examples/main_hybrid.py` 不得复制、提交或先提交后删除到公开仓库。Git 删除文件不会清除已经公开的提交历史。

## 远程仓库约定

公开仓库使用以下远程名称：

```text
origin    https://github.com/YDL-Simulation/metacar-hybrid.git
upstream  https://github.com/YDL-Simulation/autodrive_api_python.git
```

- `origin` 是 MetaCar Hybrid 自己的产品仓库，可以正常拉取和推送。
- `upstream` 只用于获取原版 MetaCar 更新，不向其推送。

首次创建远程仓库后执行：

```bash
git remote add origin https://github.com/YDL-Simulation/metacar-hybrid.git
git push -u origin main
```

## 同步原版 MetaCar 更新

不要把上游 `master` 直接覆盖到产品主分支。每次同步都从独立分支开始：

```bash
git fetch upstream --tags
git switch -c sync/upstream-<tag-or-commit>
git log --oneline --decorate HEAD..upstream/master
git diff HEAD...upstream/master -- metacar pyproject.toml
```

逐项判断上游改动：

1. 通用 bug、安全问题、通信协议和数据模型修复通常应同步。
2. 与 HybridControl 或 Delta 控制冲突的部分需要人工适配，不能机械覆盖。
3. 文档和示例只同步适合公开产品的内容。
4. 每次同步后更新 `UPSTREAM.md` 中的上游标签、提交哈希和兼容性结果。

完成适配后必须运行：

```bash
python -m pytest
python -m build
python -m twine check --strict dist/*
python scripts/check_release_artifacts.py dist/*
sphinx-build -W -E -b html docs docs/_build/html
```

测试通过后再通过 Pull Request 合并到 `main`。已发布的版本和主分支不要强制 rebase。

## 从内部仓库发布改动

内部功能完成后，只挑选真正属于公开 SDK 的改动移植到公开仓库。允许公开的典型范围包括：

- `metacar/` 中的通用 SDK 和协议实现
- `tests/` 中不包含内部场景参数的单元测试
- `docs/`、`README.md`、`CHANGELOG.md` 和 `UPSTREAM.md`
- `examples/main_hybrid_basic.py` 等最小示例
- 构建、CI 和发布配置

禁止公开的典型内容包括：

- 完整 `examples/main_hybrid.py`
- 内部轨迹、地图、场景数据和实验结果
- 转弯判定阈值、调度策略和调试参数
- 密钥、令牌、账号、内部地址和运行日志

提交前先检查公开仓库的待提交文件：

```bash
git status --short
git diff --staged --name-status
git diff --staged
```

## 版本与发布

MetaCar Hybrid 使用独立版本号，不跟随原版 MetaCar 的版本号递增。首个预发布版本为 `0.1.0a1`。

推荐发布流程：

1. 更新 `metacar/__init__.py`、`CHANGELOG.md` 和 `UPSTREAM.md`。
2. 运行全部测试、构建和隐私检查。
3. 创建版本标签，例如 `v0.1.0a1`。
4. 推送标签，由 GitHub Actions 和 PyPI Trusted Publisher 发布。
5. 在干净虚拟环境中使用 `pip install --pre metacar-hybrid` 做安装验证。

PyPI 包名为 `metacar-hybrid`，Python 导入名仍为 `metacar`。它不应与原版 `metacar` 安装在同一个 Python 环境中。
