FORWARD_BIND = "w"
BACKWARD_BIND = "s"
LEFT_BIND = "a"
RIGHT_BIND = "d"

control_state = {
	FORWARD_BIND: 0,
	BACKWARD_BIND: 0,
	LEFT_BIND: 0,
	RIGHT_BIND: 0
}

def _change_control_state(control, state):
	control_state[control] = state

def setup_controls():
	for control in control_state:
		base.accept(control, _change_control_state, [control, 1])
		base.accept(control + "-up", _change_control_state, [control, 0])
