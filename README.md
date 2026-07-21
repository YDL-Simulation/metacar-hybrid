# MetaCar Hybrid - 虚实结合平台 Python API

MetaCar Hybrid 是面向智能网联汽车虚实结合场景的 Python API。本项目基于 [YDL-Simulation/autodrive_api_python](https://github.com/YDL-Simulation/autodrive_api_python) 开发，在保留原有场景通信、车辆状态和视频流能力的基础上，增加了 `HybridControl` 消息和 Delta 位移控制。

> 当前为 Alpha 版本，接口可能随虚实平台协议继续调整。

## 与原版 MetaCar 的关系

- PyPI 发行包名为 `metacar-hybrid`。
- Python 导入包名为 `metacar_hybrid`，与原版 `metacar` 明确区分。
- `metacar-hybrid` 与原版 `metacar` 可以安装在同一个 Python 环境中。
- 本产品使用独立版本号，并在 [UPSTREAM.md](UPSTREAM.md) 中记录对应的上游基线。

## 功能特性

- 与虚实结合平台进行 TCP 通信
- 解析 `HybridControl` 和 `deltaTime`
- 通过 `SceneAPI.set_hybrid_delta()` 发送 `dx` / `dy` 控制量
- 获取场景静态数据、车辆状态和传感器数据
- 摄像头视频流处理
- 保留原版油门、刹车、转向控制接口
- 提供不包含产品策略的基础键盘 Delta 控制示例

## 安装

建议在独立虚拟环境中安装：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --pre metacar-hybrid
```

安装运行示例所需的键盘和 GUI 依赖：

```bash
python -m pip install --pre "metacar-hybrid[examples]"
```

## 虚实结合控制

```python
from metacar_hybrid import SceneAPI

api = SceneAPI()
api.connect()

for sim_car_msg, frames in api.main_loop():
    hybrid_control = sim_car_msg.hybrid_control or {}
    dt = hybrid_control.get("deltaTime")

    # dx / dy 由上层轨迹跟踪或键盘算法计算
    api.set_hybrid_delta(dx=0.1, dy=0.0, dt=dt)
```

## 示例

仓库中包含：

- `examples/main_hybrid_basic.py` - 可直接连接虚实场景并运行的基础键盘 Delta 控制程序
- `examples/main.py` - 原有仿真控制示例
- `examples/gui.py` - 车辆状态与场景信息 GUI

安装示例依赖后，可以直接运行基础示例：

```bash
python -m pip install --pre "metacar-hybrid[examples]"
python examples/main_hybrid_basic.py
```

从源码开发时也可以运行：

```bash
python -m pip install --pre "metacar-hybrid[examples]"
cd examples
python -c "import metacar_hybrid; print(metacar_hybrid.__version__, metacar_hybrid.__file__)"
python main_hybrid_basic.py
```

仓库示例不会修改 Python 导入路径，使用的是当前 Python 环境中通过 `pip`
安装的 `metacar-hybrid`。上面的检查命令应显示当前虚拟环境下的
`site-packages/metacar_hybrid` 路径。

基础程序支持以下按键：

- `W` 或上方向键：前进
- `A`/`D` 或左/右方向键：横向移动
- 按住 `X`：发送零位移停车指令
- `Space`：重开当前关卡
- `N`：跳过当前关卡
- `Esc`：发送停车指令并安全退出

程序不依赖 GUI。它与原版 `main.py` 一样是 TCP 监听端：应先启动本程序，
再在平台中启动虚实结合场景，由场景主动连接本机的 `127.0.0.1:5061`
控制端口和 `127.0.0.1:5063` 视频端口。终端会分别显示控制端口连接、
视频端口连接和场景初始化三个阶段，并在握手完成后持续输出位置和控制状态。

完整轨迹控制和测试策略属于内部开发代码，不包含在 PyPI 的
wheel 和源码发布包中。

## 维护

本项目采用内部开发仓库与公开产品仓库分离的方式维护。上游同步、公开边界和发版步骤请参阅 [MAINTENANCE.md](MAINTENANCE.md)。

创建 GitHub Release 和发布 PyPI 前，请按照 [RELEASING.md](RELEASING.md) 完成版本、标签、Trusted Publisher 和安装验证。

## 本地开发与验证

```bash
python -m pip install -e ".[test,examples]" build twine
python -m pytest
python -m build
python -m twine check --strict dist/*
python scripts/check_release_artifacts.py dist/*
```

## 文档

本地构建 Sphinx 文档：

```bash
python -m pip install -r docs/requirements.txt
sphinx-build -W -b html docs docs/_build/html
```

## 版本策略

MetaCar Hybrid 独立发版：

- `0.1.0a1` - 首个 Alpha 测试版，使用旧导入名 `metacar`
- `0.1.0a2` - 使用独立导入名 `metacar_hybrid`，支持与原版共存
- `0.1.0a3` - 提供可直接运行的基础虚实结合键盘控制程序
- `0.1.0a4` - 对齐原版连接顺序并增加分阶段连接诊断
- `0.1.0rc1` - 首个发布候选版
- `0.1.0` - 首个稳定版

每次同步上游后，应在 `UPSTREAM.md` 和发布说明中记录上游标签及提交哈希。

## 许可证

本项目基于 MIT 许可证的上游项目开发，继续使用 MIT 许可证。详见 [LICENSE](LICENSE)。
