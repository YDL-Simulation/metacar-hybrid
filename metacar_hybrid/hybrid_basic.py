"""可直接运行的 MetaCar Hybrid 基础键盘控制程序。"""

from __future__ import annotations

import math
from time import monotonic
from typing import Callable

from .models import SimCarMsg
from .sceneapi import SceneAPI


CONTROL_SPEED_MPS = 1.0
DEFAULT_DELTA_TIME_S = 0.02
MIN_DELTA_TIME_S = 0.001
MAX_DELTA_TIME_S = 0.1


def get_delta_time(sim_car_msg: SimCarMsg) -> float | None:
    """从平台下发的 ``HybridControl`` 中读取合法的 ``deltaTime``。"""
    hybrid_control = sim_car_msg.hybrid_control
    if not isinstance(hybrid_control, dict):
        return None

    value = hybrid_control.get("deltaTime")
    if value is None:
        value = hybrid_control.get("delta_time")
    if value is None:
        return None

    try:
        delta_time = float(value)
    except (TypeError, ValueError):
        return None

    return delta_time if math.isfinite(delta_time) and delta_time > 0 else None


def resolve_delta_time(sim_car_msg: SimCarMsg, elapsed_s: float) -> float:
    """优先使用平台时间步，缺失时退回到本机循环时间并限制异常值。"""
    delta_time = get_delta_time(sim_car_msg)
    if delta_time is None:
        delta_time = elapsed_s if math.isfinite(elapsed_s) else DEFAULT_DELTA_TIME_S
    if delta_time <= 0:
        delta_time = DEFAULT_DELTA_TIME_S
    return max(MIN_DELTA_TIME_S, min(delta_time, MAX_DELTA_TIME_S))


def get_keyboard_delta(
    delta_time: float | None,
    keyboard_module,
    speed_mps: float = CONTROL_SPEED_MPS,
) -> tuple[float, float]:
    """将前进和横向移动按键转换为世界坐标系下的 Delta 位移。"""
    if delta_time is None or delta_time <= 0:
        return 0.0, 0.0

    direction_x = 0.0
    direction_y = 0.0

    if keyboard_module.is_pressed("w") or keyboard_module.is_pressed("up"):
        direction_x += 1.0
    if keyboard_module.is_pressed("a") or keyboard_module.is_pressed("left"):
        direction_y += 1.0
    if keyboard_module.is_pressed("d") or keyboard_module.is_pressed("right"):
        direction_y -= 1.0

    length = math.hypot(direction_x, direction_y)
    if length == 0:
        return 0.0, 0.0

    distance = max(0.0, float(speed_mps)) * delta_time
    return direction_x / length * distance, direction_y / length * distance


def _remove_hotkeys(keyboard_module, hotkey_handles: list[object]) -> None:
    for handle in hotkey_handles:
        try:
            keyboard_module.remove_hotkey(handle)
        except (KeyError, ValueError):
            pass


def run_basic_control(
    api: SceneAPI,
    keyboard_module,
    *,
    speed_mps: float = CONTROL_SPEED_MPS,
    status_interval_s: float = 1.0,
    output: Callable[[str], None] = print,
    clock: Callable[[], float] = monotonic,
) -> None:
    """连接虚实结合场景并持续运行基础键盘 Delta 控制。"""
    output("[等待] 请在平台中启动虚实结合场景；本程序作为服务端等待场景主动接入")

    loop = None
    hotkey_handles: list[object] = []
    connected = False
    last_delta_time = DEFAULT_DELTA_TIME_S

    try:
        hotkey_handles = [
            keyboard_module.add_hotkey("space", api.retry_level),
            keyboard_module.add_hotkey("n", api.skip_level),
        ]
        api.connect(status_callback=output)
        connected = True
        static_data = api.get_scene_static_data()

        output(
            "[已连接] 场景握手完成 "
            f"(路线点 {len(static_data.route)}，道路 {len(static_data.roads)}，"
            f"子场景 {len(static_data.sub_scenes)})"
        )
        output(
            "[按键] W/↑ 前进，A/D/←/→ 横向移动，按住 X 停车，"
            "Space 重开，N 跳关，Esc 退出"
        )
        started_at = clock()
        previous_tick = started_at
        last_status = started_at - max(0.0, status_interval_s)
        loop = api.main_loop()

        for sim_car_msg, _frames in loop:
            now = clock()
            elapsed_s = now - previous_tick
            previous_tick = now
            delta_time = resolve_delta_time(sim_car_msg, elapsed_s)
            last_delta_time = delta_time

            if keyboard_module.is_pressed("esc"):
                api.set_hybrid_delta(dx=0.0, dy=0.0, dt=delta_time)
                output("[退出] 已发送停车指令")
                break

            stopped = keyboard_module.is_pressed("x")
            if stopped:
                dx, dy = 0.0, 0.0
            else:
                dx, dy = get_keyboard_delta(
                    delta_time,
                    keyboard_module,
                    speed_mps=speed_mps,
                )

            api.set_hybrid_delta(dx=dx, dy=dy, dt=delta_time)

            if now - last_status >= max(0.0, status_interval_s):
                pose = getattr(sim_car_msg, "pose_gnss", None)
                position = ""
                if pose is not None:
                    position = f" pos=({pose.pos_x:.2f}, {pose.pos_y:.2f})"
                mode = "STOP" if stopped else "RUN"
                output(
                    f"[运行] mode={mode} dt={delta_time:.3f}s "
                    f"dx={dx:.3f} dy={dy:.3f}{position}"
                )
                last_status = now
        else:
            output("[结束] 场景已正常结束")
    except KeyboardInterrupt:
        output("[退出] 收到 Ctrl+C")
        if connected:
            try:
                api.set_hybrid_delta(dx=0.0, dy=0.0, dt=last_delta_time)
            except Exception:
                pass
    finally:
        if loop is not None:
            close = getattr(loop, "close", None)
            if callable(close):
                close()
        _remove_hotkeys(keyboard_module, hotkey_handles)


def main() -> None:
    try:
        import keyboard
    except ModuleNotFoundError as exc:
        raise SystemExit(
            '请先安装示例依赖: python -m pip install --pre "metacar-hybrid[examples]"'
        ) from exc

    run_basic_control(SceneAPI(), keyboard)


if __name__ == "__main__":
    main()
