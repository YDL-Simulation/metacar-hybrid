# 更新日志

本项目使用独立的 MetaCar Hybrid 版本号。上游兼容基线见 [UPSTREAM.md](UPSTREAM.md)。

## 0.1.0a2 - 2026-07-19

### 变更

- 将 Python 导入包从 `metacar` 重命名为 `metacar_hybrid`。
- 支持与上游原版 `metacar` 安装在同一个 Python 环境中。
- 更新 CLI、示例、测试、Sphinx API 引用和发布隐私门禁以使用独立命名空间。

### 迁移

`0.1.0a1` 用户需要修改导入语句：

```python
# 0.1.0a1
from metacar import SceneAPI

# 0.1.0a2 及以后
from metacar_hybrid import SceneAPI
```

## 0.1.0a1 - 2026-07-19

### 新增

- 增加接收数据中的 `HybridControl` 解析。
- 增加 `SceneAPI.set_hybrid_delta()` Delta 位移控制接口。
- 增加可公开的基础键盘 Delta 控制示例。
- 增加发布产物隐私检查，阻止完整内部测试策略进入 PyPI 压缩包。
- 增加 MetaCar Hybrid 安装、协议和上游基线文档。
- 增加 Python 3.10-3.13 自动化测试和 PyPI Trusted Publishing 发布校验。
- 增加公开仓库 Git 历史门禁、严格文档构建、Pull Request 隐私清单和首发操作手册。

### 兼容性

- 基于上游 MetaCar `v0.4.0`。
- 保留原有 `SceneAPI.set_vehicle_control()` 接口。
- PyPI 发行包名改为 `metacar-hybrid`，Python 导入包名保留为 `metacar`。
