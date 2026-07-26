# 更新日志

本项目使用独立的 MetaCar Hybrid 版本号。上游兼容基线见 [UPSTREAM.md](UPSTREAM.md)。

## 0.1.0 - 2026-07-26

### 正式发布

- 将经过五个 Alpha 版本验证的 `metacar_hybrid` 独立命名空间、虚实结合通信模型和 `SceneAPI.set_hybrid_delta()` 作为首个稳定公开 API 发布。
- 确认发行包可与上游原版 `metacar` 安装在同一个 Python 环境中。
- 将项目稳定性元数据、安装命令和文档更新为正式版本。

### 示例

- 基础键盘控制示例保持与 SDK 发布包解耦，仅依赖稳定的 `SceneAPI`。
- `S` 键按参考控制逻辑生成负向纵向位移，并将后退速度限制为 `0.5 m/s`；下方向键保持不启用。

## 0.1.0a5 - 2026-07-21

### 调整

- 仓库基础示例不再修改 `sys.path`，统一使用当前 Python 环境中通过 `pip` 安装的 `metacar-hybrid`。
- 将时间步处理、键盘控制和运行循环完整迁移至 `examples/main_hybrid_basic.py`，示例只依赖稳定的 `SceneAPI`。
- 移除包内 `metacar_hybrid.hybrid_basic` 模块及 `metacar-hybrid-basic` 命令，解除示例更新与 SDK 发版的绑定。
- 移除尚未实现的 `S` 键和下方向键倒车行为。

## 0.1.0a4 - 2026-07-20

### 修复

- 将基础示例的热键注册、场景连接和静态数据读取顺序与上游 `main.py` 对齐。
- 连接过程分阶段显示控制端口、视频端口和场景初始化状态，便于定位客户端未接入的位置。
- 明确说明 Python 程序是监听端，必须由虚实结合场景主动连接 `127.0.0.1:5061/5063`。

## 0.1.0a3 - 2026-07-20

### 变更

- 将 `examples/main_hybrid_basic.py` 扩充为可直接连接场景并运行的完整基础程序。
- 增加 WASD/方向键移动、按住 X 停车、Space 重开、N 跳关和 Esc 安全退出。
- 平台未提供合法 `deltaTime` 时，使用经过上下限保护的本机循环时间作为回退。
- 增加基础程序连接、主循环、控制发送和示例文件直接运行测试。

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
