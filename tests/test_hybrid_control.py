import json

from pydantic import TypeAdapter

from metacar import SceneAPI, VehicleControl, __version__
from metacar.hybrid_basic import get_delta_time, get_keyboard_delta
from metacar.models import Code4, SimCarMsg


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

    def is_pressed(self, key: str) -> bool:
        return key in self.pressed


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
    assert __version__ == "0.1.0a1"


def test_incoming_model_declares_optional_hybrid_control_alias():
    field = SimCarMsg.model_fields["hybrid_control"]
    assert field.alias == "HybridControl"
    assert field.default is None


def test_public_basic_example_reads_delta_time():
    message = SimCarMsg.model_construct(hybrid_control={"deltaTime": 0.02})
    assert get_delta_time(message) == 0.02


def test_public_basic_example_normalizes_diagonal_keyboard_input():
    dx, dy = get_keyboard_delta(0.5, FakeKeyboard({"w", "a"}))
    assert dx == dy
    assert round((dx**2 + dy**2) ** 0.5, 6) == 0.5


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
