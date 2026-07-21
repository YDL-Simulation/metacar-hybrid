"""MetaCar Hybrid 可直接运行的基础键盘控制示例。

运行前：

1. 安装 ``python -m pip install --pre \"metacar-hybrid[examples]\"``。
2. 启动虚实结合场景。
3. 执行 ``python examples/main_hybrid_basic.py``。

该示例只演示连接、接收状态和发送基础 Delta 控制，不包含轨迹跟踪、
转弯状态机、GUI 或其他内部产品策略。
"""

from __future__ import annotations

from time import monotonic

from metacar_hybrid import SceneAPI
from metacar_hybrid.hybrid_basic import (
    CONTROL_SPEED_MPS,
    get_keyboard_delta,
    resolve_delta_time,
)


def load_keyboard_module():
    """延迟加载可选的键盘依赖，并给出明确安装提示。"""
    try:
        import keyboard
    except ModuleNotFoundError as exc:
        raise SystemExit(
            '请先安装示例依赖: python -m pip install --pre "metacar-hybrid[examples]"'
        ) from exc
    return keyboard


def remove_hotkeys(keyboard_module, handles: list[object]) -> None:
    for handle in handles:
        try:
            keyboard_module.remove_hotkey(handle)
        except (KeyError, ValueError):
            pass


def main() -> None:
    keyboard = load_keyboard_module()
    api = SceneAPI()

    print("[等待] 请在平台中启动虚实结合场景；本程序作为服务端等待场景主动接入")
    print(
        "[按键] W/↑ 前进，A/D/←/→ 横向移动，按住 X 停车，"
        "Space 重开，N 跳关，Esc 退出"
    )

    loop = None
    hotkey_handles: list[object] = []
    connected = False
    last_delta_time = 0.02

    try:
        hotkey_handles = [
            keyboard.add_hotkey("space", api.retry_level),
            keyboard.add_hotkey("n", api.skip_level),
        ]
        api.connect(status_callback=print)
        connected = True
        static_data = api.get_scene_static_data()
        print(
            "[已连接] 场景握手完成 "
            f"(路线点 {len(static_data.route)}，道路 {len(static_data.roads)}，"
            f"子场景 {len(static_data.sub_scenes)})"
        )
        print("[控制] 开始接收车辆状态并发送 HybridControl.Delta")

        previous_tick = monotonic()
        last_status = previous_tick - 1.0
        loop = api.main_loop()

        for sim_car_msg, _frames in loop:
            now = monotonic()
            elapsed_s = now - previous_tick
            previous_tick = now
            delta_time = resolve_delta_time(sim_car_msg, elapsed_s)
            last_delta_time = delta_time

            if keyboard.is_pressed("esc"):
                api.set_hybrid_delta(dx=0.0, dy=0.0, dt=delta_time)
                print("[退出] 已发送停车指令")
                break

            stopped = keyboard.is_pressed("x")
            if stopped:
                dx, dy = 0.0, 0.0
            else:
                dx, dy = get_keyboard_delta(
                    delta_time,
                    keyboard,
                    speed_mps=CONTROL_SPEED_MPS,
                )

            api.set_hybrid_delta(dx=dx, dy=dy, dt=delta_time)

            if now - last_status >= 1.0:
                pose = sim_car_msg.pose_gnss
                mode = "STOP" if stopped else "RUN"
                print(
                    f"[运行] mode={mode} dt={delta_time:.3f}s "
                    f"dx={dx:.3f} dy={dy:.3f} "
                    f"pos=({pose.pos_x:.2f}, {pose.pos_y:.2f})"
                )
                last_status = now
        else:
            print("[结束] 场景已正常结束")
    except KeyboardInterrupt:
        print("[退出] 收到 Ctrl+C")
        if connected:
            try:
                api.set_hybrid_delta(dx=0.0, dy=0.0, dt=last_delta_time)
            except Exception:
                pass
    finally:
        if loop is not None:
            loop.close()
        remove_hotkeys(keyboard, hotkey_handles)


if __name__ == "__main__":
    main()
