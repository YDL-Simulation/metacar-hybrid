# 是否发布新包：判断与操作流程

本文档是 MetaCar Hybrid 每次修改后的第一判断入口，用来决定：

1. 是否需要发布新的 PyPI `metacar-hybrid` 版本；
2. 需要发布时如何完成版本、测试、Release 和 PyPI 验证；
3. 不需要发布时如何只更新 GitHub 仓库。

完整的双仓库边界见 [MAINTENANCE.md](MAINTENANCE.md)，具体发布操作和一次性配置见
[RELEASING.md](RELEASING.md)。

## 一句话判断原则

如果修改会影响用户执行 `pip install metacar-hybrid` 后得到的代码、依赖、命令、
协议行为或包元数据，就必须使用新版本号重新发布；如果修改只影响 GitHub 上的
示例、开发文档、测试或维护配置，通常只需合并到 `main`，不需要发布新包。

PyPI 已发布的版本不可覆盖。例如 `0.1.0a4` 已发布后，任何需要进入安装包的修复
都必须使用 `0.1.0a5` 或更高的新版本。

## 快速判断表

| 修改范围 | 是否发布新包 | 原因或注意事项 |
| --- | --- | --- |
| `metacar_hybrid/**/*.py` | 是 | 这是用户安装后实际使用的 SDK 代码 |
| `metacar_hybrid/sceneapi.py`、`models.py`、`sockets.py` | 是 | 会改变通信、序列化、数据模型或公开 API |
| `metacar_hybrid/hybrid_basic.py` | 是 | 安装命令 `metacar-hybrid-basic` 运行的就是该模块 |
| `pyproject.toml` 的依赖、入口命令、Python 版本或构建配置 | 是 | 会改变 wheel/sdist 或安装行为 |
| 安装包需要携带的数据文件、许可证或类型信息 | 是 | 发布产物内容发生变化 |
| `examples/main_hybrid_basic.py` 单独修改 | 通常否 | 它是 GitHub 示例，不是 `metacar-hybrid-basic` 命令的实现 |
| `README.md`、`docs/`、维护手册单独修改 | 通常否 | 只更新 GitHub/文档；若必须更新 PyPI 页面展示内容，则随下一版本发布 |
| `tests/` 单独修改 | 否 | 只加强验证，不改变用户安装包行为 |
| `.github/`、Issue/PR 模板单独修改 | 否 | 只改变仓库自动化或协作流程 |
| `.gitignore`、代码格式配置、开发工具配置 | 通常否 | 不改变已安装 SDK；若改变构建产物则需要发布 |
| 内部仓库的完整 `examples/main_hybrid.py` | 不发布且不得公开 | 属于内部算法和测试策略，不能进入公开仓库历史 |
| 同步上游后只改文档或测试 | 否 | 没有安装包代码变化 |
| 同步上游后改到 `metacar_hybrid/` | 是 | 安装包代码和兼容基线发生变化 |

## 两个容易混淆的基础示例入口

以下两个入口不是同一个文件：

```text
python examples/main_hybrid_basic.py
        -> GitHub 仓库中的 examples/main_hybrid_basic.py

metacar-hybrid-basic
        -> PyPI 安装包中的 metacar_hybrid.hybrid_basic:main
```

因此：

- 只修改 `examples/main_hybrid_basic.py`，供克隆仓库的用户查看或运行时，不需要发布新包；
- 希望通过 `pip` 安装后执行 `metacar-hybrid-basic` 的用户也获得修改时，必须修改
  `metacar_hybrid/hybrid_basic.py`、补测试、增加版本号并发布新包；
- 两处包含相同逻辑时应同步修改，避免 GitHub 示例与安装命令表现不同；
- 尚未通过真实虚实结合场景验证的实验逻辑，先放在分支或示例中验证，不要立即发布 PyPI。

## 不需要发布新包时的流程

适用于示例、文档、测试、CI 或维护配置等不改变安装包行为的修改。

1. 从最新 `main` 创建普通修改分支。

   ```bash
   git switch main
   git pull --ff-only origin main
   git switch -c docs/<topic>
   ```

2. 完成修改，并确认没有意外改到安装包代码。

   ```bash
   git status --short
   git diff --name-only
   git diff
   ```

3. 根据影响范围运行检查。最低要求是相关测试和公开边界检查；示例逻辑应做真实场景验证。

   ```bash
   python scripts/check_public_repository.py
   python -m pytest
   ```

4. 使用详细中文提交说明，推送分支并创建 Pull Request。
5. 等待 GitHub Actions 全部通过后合并到 `main`。
6. 到此结束：

   - 不修改 `metacar_hybrid/__init__.py` 的版本号；
   - 不创建版本标签；
   - 不创建 GitHub Release；
   - 不触发 PyPI 发布；
   - 已有的 PyPI 版本保持不变。

如果修改暂时不发布但需要在下一版本告知用户，可以写在 `CHANGELOG.md` 的“未发布”部分。

## 必须发布新包时的流程

适用于 SDK、通信协议、数据模型、安装命令、依赖或构建产物发生变化的修改。

### 1. 先完成并验证产品改动

1. 从最新 `main` 创建功能或修复分支；
2. 修改 `metacar_hybrid/` 或相关打包配置；
3. 补充不会泄露内部策略的单元测试和公开文档；
4. 涉及连接、控制或协议时，必须在真实虚实结合场景中验证；
5. 先通过 Pull Request 合并产品改动，不要在未验证时创建发布标签。

### 2. 选择新版本号

当前仍处于 Alpha 阶段时，普通修复或小功能依次增加 Alpha 序号：

```text
0.1.0a4 -> 0.1.0a5 -> 0.1.0a6
```

进入稳定版以后：

- 兼容性 bug 修复：增加补丁版本，例如 `0.1.0 -> 0.1.1`；
- 向后兼容的新功能：增加次版本，例如 `0.1.1 -> 0.2.0`；
- 不兼容的公开 API/协议变更：增加主版本，并在发布说明中提供迁移方法。

不要因为上游 MetaCar 发布了某个版本，就机械使用相同的产品版本号。

### 3. 准备发布提交

1. 更新 `metacar_hybrid/__init__.py` 中的 `__version__`；
2. 将 `CHANGELOG.md` 的“未发布”内容整理为新版本和发布日期；
3. 如果同步过上游，更新 `UPSTREAM.md` 的上游标签、提交哈希和产品增量；
4. 确认 README、安装命令和示例中的版本说明正确；
5. 使用详细中文提交信息，通过 Pull Request 合并到 `main`。

### 4. 执行发布前检查

在公开仓库根目录执行：

```bash
python scripts/check_public_repository.py
python -m pytest
python -m build
python -m twine check --strict dist/*
python scripts/check_release_artifacts.py dist/*
sphinx-build -W -E -b html docs docs/_build/html
```

必须确认：

- 测试全部通过；
- wheel 和 sdist 构建成功；
- Twine 元数据检查通过；
- 发布产物隐私检查通过；
- 文档在 warnings-as-errors 模式下通过；
- wheel/sdist 中没有完整 `main_hybrid.py`、日志、地图、内部参数或密钥。

### 5. 创建标签和 GitHub Release

发布准备 Pull Request 合并且 `main` 全部检查通过后：

```bash
git switch main
git pull --ff-only origin main
git tag -a v<版本号> -m "MetaCar Hybrid <版本号>：中文发布摘要"
git push origin v<版本号>
```

然后在 GitHub 创建 Release：

- Tag 必须严格等于 `v` 加 `metacar_hybrid.__version__`，例如 `v0.1.0a5`；
- Alpha、Beta、RC 版本选择 **Pre-release**；
- Release notes 写明主要变化、上游基线、安装命令和兼容性；
- 发布 Release 后，`Upload Python Package` 工作流会通过 Trusted Publishing 自动上传 PyPI；
- 不需要创建或保存 PyPI API Token。

### 6. 监控并验证 PyPI

1. 等待 `release-build` 和 `pypi-publish` 两个任务成功；
2. 在干净虚拟环境安装准确版本，不要只测试开发仓库；
3. 验证版本、导入路径、公开 API 和命令入口。

Windows 示例：

```powershell
python -m venv verify-env
verify-env\Scripts\python -m pip install --no-cache --pre "metacar-hybrid[examples]==<版本号>"
verify-env\Scripts\python -c "import metacar_hybrid; print(metacar_hybrid.__version__, metacar_hybrid.__file__)"
verify-env\Scripts\metacar-hybrid-basic.exe
```

Linux/macOS 将 `verify-env\Scripts\` 替换为 `verify-env/bin/`。

## 发布后的重要规则

- PyPI 版本不可覆盖、替换或删除后复用；修复时增加版本号重新发布；
- 已发布的 Git 标签不得强制移动或重写；
- 不要为了更新一个 GitHub 示例或文档而频繁发布空的新包；
- 也不要在 SDK 已改变时只更新 GitHub 而忘记发布，否则 `main` 与 PyPI 用户行为会不同；
- GitHub `main` 可以包含尚未发布的改动，但 `CHANGELOG.md` 应放在“未发布”部分；
- 每次发布后都要用干净环境从 PyPI 安装验证，不能用本地 editable install 代替。

## 新对话的交接提示

以后新开 Codex 对话时，可以直接发送：

```text
请先完整阅读 metacar-hybrid 公开仓库中的 RELEASE_POLICY.md、
MAINTENANCE.md 和 RELEASING.md，再检查 git status、当前版本和最近标签。
按照 RELEASE_POLICY.md 判断本次修改是否需要发布 PyPI；不要自动复用旧版本号，
也不要把内部 main_hybrid.py 或内部策略提交到公开仓库。
```

只要这三个文件仍在仓库中，新对话就可以重新建立完整的维护和发布上下文。
