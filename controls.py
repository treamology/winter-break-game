from typing import Dict

FORWARD_BIND = "w"
BACKWARD_BIND = "s"
LEFT_BIND = "a"
RIGHT_BIND = "d"
FIRE_BIND = "mouse1"
JUMP_BIND = "space"

control_state: Dict[str, float] = {
	FORWARD_BIND: 0,
	BACKWARD_BIND: 0,
	LEFT_BIND: 0,
	RIGHT_BIND: 0,
	FIRE_BIND: 0,
	JUMP_BIND: 0,
}

def _change_control_state(control: str, state: float):
	control_state[control] = state

def setup_controls():
	for control in control_state:
		base.accept(control, _change_control_state, [control, 1])
		base.accept(control + "-up", _change_control_state, [control, 0])
