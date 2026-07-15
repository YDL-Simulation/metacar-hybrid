"""可公开的 MetaCar Hybrid 基础键盘控制示例。"""

from __future__ import annotations

import math

from .models import SimCarMsg
from .sceneapi import SceneAPI


CONTROL_SPEED_MPS = 1.0


def get_delta_time(sim_car_msg: SimCarMsg) -> float | None:
    """从平台下发的 HybridControl 中读取 deltaTime。"""
    hybrid_control = sim_car_msg.hybrid_control
    if not isinstance(hybrid_control, dict):
        return None

    value = hybrid_control.get("deltaTime")
    if value is None:
        return None

    try:
        delta_time = float(value)
    except (TypeError, ValueError):
        return None

    return delta_time if delta_time > 0 else None


def get_keyboard_delta(
    delta_time: float | None,
    keyboard_module,
) -> tuple[float, float]:
    """将 WASD / 方向键转换为世界坐标系下的 Delta 位移。"""
    if delta_time is None:
        return 0.0, 0.0

    direction_x = 0.0
    direction_y = 0.0

    if keyboard_module.is_pressed("w") or keyboard_module.is_pressed("up"):
        direction_x += 1.0
    if keyboard_module.is_pressed("s") or keyboard_module.is_pressed("down"):
        direction_x -= 1.0
    if keyboard_module.is_pressed("a") or keyboard_module.is_pressed("left"):
        direction_y += 1.0
    if keyboard_module.is_pressed("d") or keyboard_module.is_pressed("right"):
        direction_y -= 1.0

    length = math.hypot(direction_x, direction_y)
    if length == 0:
        return 0.0, 0.0

    distance = CONTROL_SPEED_MPS * delta_time
    return direction_x / length * distance, direction_y / length * distance


def main():
    try:
        import keyboard
    except ModuleNotFoundError as exc:
        raise SystemExit(
            '请先安装示例依赖: python -m pip install "metacar-hybrid[examples]"'
        ) from exc

    api = SceneAPI()
    api.connect()

    print("[MetaCar Hybrid] WASD / 方向键：发送基础 Delta 控制")

    for sim_car_msg, _frames in api.main_loop():
        delta_time = get_delta_time(sim_car_msg)
        dx, dy = get_keyboard_delta(delta_time, keyboard)
        api.set_hybrid_delta(dx=dx, dy=dy, dt=delta_time)


if __name__ == "__main__":
    main()
