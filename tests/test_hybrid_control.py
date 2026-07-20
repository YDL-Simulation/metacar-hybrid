import json
import runpy
from types import SimpleNamespace

from pydantic import TypeAdapter

import metacar_hybrid
from metacar_hybrid import SceneAPI, VehicleControl, __version__
from metacar_hybrid.hybrid_basic import (
    get_delta_time,
    get_keyboard_delta,
    resolve_delta_time,
    run_basic_control,
)
from metacar_hybrid.models import Code4, SimCarMsg


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

    def connect(self) -> None:
        self.connected = True

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


def test_package_uses_independent_alpha_version():
    assert __version__ == "0.1.0a3"


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


def test_main_hybrid_basic_file_is_directly_runnable(capsys):
    message = SimCarMsg.model_construct(
        hybrid_control={"deltaTime": 0.02},
        pose_gnss=SimpleNamespace(pos_x=1.0, pos_y=2.0),
    )
    api = FakeBasicAPI([message])
    keyboard = FakeKeyboard({"d"})
    clock = iter([0.0, 0.02]).__next__
    namespace = runpy.run_path("examples/main_hybrid_basic.py")
    main_globals = namespace["main"].__globals__
    main_globals["SceneAPI"] = lambda: api
    main_globals["load_keyboard_module"] = lambda: keyboard
    main_globals["monotonic"] = clock

    namespace["main"]()

    assert api.connected is True
    assert api.sent == [(0.0, -0.02, 0.02)]
    assert "[已连接]" in capsys.readouterr().out


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
