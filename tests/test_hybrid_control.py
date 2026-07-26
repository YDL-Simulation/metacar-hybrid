import ast
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

from pydantic import TypeAdapter

import metacar_hybrid
from metacar_hybrid import SceneAPI, VehicleControl, __version__
from metacar_hybrid.models import Code4, SimCarMsg


BASIC_EXAMPLE_PATH = Path("examples/main_hybrid_basic.py")
BASIC_EXAMPLE = runpy.run_path(str(BASIC_EXAMPLE_PATH))
get_delta_time = BASIC_EXAMPLE["get_delta_time"]
get_keyboard_delta = BASIC_EXAMPLE["get_keyboard_delta"]
resolve_delta_time = BASIC_EXAMPLE["resolve_delta_time"]
run_basic_control = BASIC_EXAMPLE["run_basic_control"]


class CapturingSocket:
    def __init__(self):
        self.data = None
        self.type_ = None

    def send(self, data, type_):
        self.data = data
        self.type_ = type_


class FakeKeyboard:
    def __init__(self, pressed: set[str]):
        self.pressed = pressed
        self.added_hotkeys: list[str] = []
        self.removed_hotkeys: list[object] = []

    def is_pressed(self, key: str) -> bool:
        return key in self.pressed

    def add_hotkey(self, key: str, callback):
        self.added_hotkeys.append(key)
        return (key, callback)

    def remove_hotkey(self, handle) -> None:
        self.removed_hotkeys.append(handle)


class FakeBasicAPI:
    def __init__(self, messages: list[SimCarMsg]):
        self.messages = messages
        self.connected = False
        self.sent: list[tuple[float, float, float | None]] = []
        self.retry_count = 0
        self.skip_count = 0

    def connect(self, status_callback=None) -> None:
        if status_callback is not None:
            status_callback("[连接完成] 测试连接")
        self.connected = True

    def get_scene_static_data(self):
        return SimpleNamespace(route=[], roads=[], sub_scenes=[])

    def main_loop(self):
        for message in self.messages:
            yield message, []

    def set_hybrid_delta(self, dx: float, dy: float, dt: float | None = None):
        self.sent.append((dx, dy, dt))

    def retry_level(self) -> None:
        self.retry_count += 1

    def skip_level(self) -> None:
        self.skip_count += 1


def make_api_without_network() -> tuple[SceneAPI, CapturingSocket]:
    api = SceneAPI.__new__(SceneAPI)
    socket = CapturingSocket()
    api._model_socket = socket
    api._move_to_start = 0
    api._move_to_end = 0
    return api, socket


def captured_json(socket: CapturingSocket) -> dict:
    assert socket.data is not None
    assert socket.type_ is Code4
    encoded = TypeAdapter(socket.type_).dump_json(socket.data, by_alias=True)
    return json.loads(encoded)


def test_package_uses_independent_stable_version():
    assert __version__ == "0.1.0"


def test_package_uses_independent_import_namespace():
    assert metacar_hybrid.__name__ == "metacar_hybrid"


def test_incoming_model_declares_optional_hybrid_control_alias():
    field = SimCarMsg.model_fields["hybrid_control"]
    assert field.alias == "HybridControl"
    assert field.default is None


def test_public_basic_example_reads_delta_time():
    message = SimCarMsg.model_construct(hybrid_control={"deltaTime": 0.02})
    assert get_delta_time(message) == 0.02


def test_public_basic_example_falls_back_to_bounded_local_delta_time():
    message = SimCarMsg.model_construct(hybrid_control=None)

    assert resolve_delta_time(message, 0.04) == 0.04
    assert resolve_delta_time(message, 0.5) == 0.1
    assert resolve_delta_time(message, float("nan")) == 0.02


def test_public_basic_example_normalizes_diagonal_keyboard_input():
    dx, dy = get_keyboard_delta(0.5, FakeKeyboard({"w", "a"}))
    assert dx == dy
    assert round((dx**2 + dy**2) ** 0.5, 6) == 0.5


def test_public_basic_example_reverses_with_s_at_limited_speed():
    assert get_keyboard_delta(0.5, FakeKeyboard({"s"})) == (-0.25, 0.0)


def test_public_basic_example_ignores_down_key():
    assert get_keyboard_delta(0.5, FakeKeyboard({"down"})) == (0.0, 0.0)


def test_public_basic_program_connects_runs_and_sends_keyboard_delta():
    message = SimCarMsg.model_construct(hybrid_control={"deltaTime": 0.02})
    api = FakeBasicAPI([message])
    keyboard = FakeKeyboard({"w"})
    output: list[str] = []

    run_basic_control(
        api,
        keyboard,
        status_interval_s=0.0,
        output=output.append,
        clock=iter([0.0, 0.02]).__next__,
    )

    assert api.connected is True
    assert api.sent == [(0.02, 0.0, 0.02)]
    assert keyboard.added_hotkeys == ["space", "n"]
    assert len(keyboard.removed_hotkeys) == 2
    assert any("场景已正常结束" in line for line in output)


def test_connect_reports_each_handshake_stage_in_order():
    events: list[str] = []

    class FakeSocket:
        def __init__(self, name: str, received=None):
            self.name = name
            self.received = received

        def accept(self) -> None:
            events.append(f"accept:{self.name}")

        def recv(self, _type):
            events.append(f"recv:{self.name}")
            return self.received

    code1 = object()
    api = SceneAPI.__new__(SceneAPI)
    api._model_socket = FakeSocket("model", code1)
    api._streaming_socket = FakeSocket("stream")
    api._load_static_data = lambda received: events.append(
        f"load:{received is code1}"
    )

    api.connect(status_callback=events.append)

    assert events == [
        "[连接 1/3] 等待场景接入控制端口 127.0.0.1:5061 ...",
        "accept:model",
        "[连接 2/3] 控制端口已连接，等待视频端口 127.0.0.1:5063 ...",
        "accept:stream",
        "[连接 3/3] 视频端口已连接，等待场景初始化数据 ...",
        "recv:model",
        "load:True",
        "[连接完成] 场景初始化数据已加载",
    ]


def test_main_hybrid_basic_file_is_directly_runnable(capsys):
    message = SimCarMsg.model_construct(
        hybrid_control={"deltaTime": 0.02},
        pose_gnss=SimpleNamespace(pos_x=1.0, pos_y=2.0),
    )
    api = FakeBasicAPI([message])
    keyboard = FakeKeyboard({"d"})
    clock = iter([0.0, 0.02]).__next__
    namespace = runpy.run_path(str(BASIC_EXAMPLE_PATH))
    main_globals = namespace["main"].__globals__
    main_globals["SceneAPI"] = lambda: api
    main_globals["load_keyboard_module"] = lambda: keyboard
    main_globals["monotonic"] = clock

    namespace["main"]()

    assert api.connected is True
    assert api.sent == [(0.0, -0.02, 0.02)]
    assert "[已连接]" in capsys.readouterr().out


def test_main_hybrid_basic_does_not_override_installed_package_path():
    source = BASIC_EXAMPLE_PATH.read_text(encoding="utf-8")

    assert "sys.path" not in source
    assert "REPO_ROOT" not in source


def test_main_hybrid_basic_only_imports_stable_package_api():
    source = BASIC_EXAMPLE_PATH.read_text(encoding="utf-8")
    module = ast.parse(source)
    package_imports = [
        (node.module, [alias.name for alias in node.names])
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom)
        and node.module is not None
        and node.module.startswith("metacar_hybrid")
    ]

    assert package_imports == [("metacar_hybrid", ["SceneAPI"])]


def test_package_does_not_install_basic_example_command():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert "metacar-hybrid-basic" not in pyproject
    assert "metacar_hybrid.hybrid_basic" not in pyproject
    assert not Path("metacar_hybrid/hybrid_basic.py").exists()


def test_set_hybrid_delta_serializes_expected_payload():
    api, socket = make_api_without_network()

    api.set_hybrid_delta(dx=0.25, dy=-0.5, dt=0.02)

    payload = captured_json(socket)
    assert payload["code"] == 4
    assert payload["SimCarMsg"]["HybridControl"] == {
        "Delta": {"dx": 0.25, "dy": -0.5},
        "deltaTime": 0.02,
    }


def test_set_hybrid_delta_omits_delta_time_when_not_provided():
    api, socket = make_api_without_network()

    api.set_hybrid_delta(dx=1.0, dy=2.0)

    hybrid_control = captured_json(socket)["SimCarMsg"]["HybridControl"]
    assert hybrid_control == {"Delta": {"dx": 1.0, "dy": 2.0}}


def test_original_vehicle_control_api_remains_available():
    api, socket = make_api_without_network()

    api.set_vehicle_control(VehicleControl(throttle=0.4, steering=-0.2))

    sim_car_msg = captured_json(socket)["SimCarMsg"]
    assert sim_car_msg["HybridControl"] is None
    assert sim_car_msg["VehicleControl"]["throttle"] == 0.4
    assert sim_car_msg["VehicleControl"]["steering"] == -0.2
