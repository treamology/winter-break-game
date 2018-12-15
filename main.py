from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d.core import Vec3
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletSphereShape, BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

# Keep track of the gameplay keys being used
keyboard_state = {"w": False, "a": False, "s": False, "d": False, "spacebar": False}
def keyboard_input(key, state):
	keyboard_state[key] = state

# Initialize ShowBase and some basic options.
base = ShowBase()
base.disable_mouse()
base.set_frame_rate_meter(True)

# Bind the movement keys
base.accept("w", keyboard_input, ["w", True])
base.accept("a", keyboard_input, ["a", True])
base.accept("s", keyboard_input, ["s", True])
base.accept("d", keyboard_input, ["d", True])
base.accept("space", keyboard_input, ["spacebar", True])
base.accept("w-up", keyboard_input, ["w", False])
base.accept("a-up", keyboard_input, ["a", False])
base.accept("s-up", keyboard_input, ["s", False])
base.accept("d-up", keyboard_input, ["d", False])
base.accept("space-up", keyboard_input, ["spacebar", False])

# Set the camera to a test location
base.camera.set_pos(0, -30, 15)
base.camera.set_p(-30)

# Initialize the physics world
world = BulletWorld()
world.set_gravity(Vec3(0, 0, -9.81))

# Set up the ground, which is an infinite plane (for now)
ground_node = BulletRigidBodyNode("Ground")
ground_node.add_shape(BulletPlaneShape(Vec3(0, 0, 1), 1)) # normal, const)
ground_node.set_friction(10)
ground_nodepath = base.render.attach_new_node(ground_node)
ground_nodepath.set_z(-10)
world.attach_rigid_body(ground_node)

# Progress the physics world every frame
def bullet_update(task):
	dt = globalClock.get_dt()
	world.do_physics(dt)
	return task.cont
base.task_mgr.add(bullet_update, 'update')

# Set up the bullet debug renderer so we can see what's happening
debug_node = BulletDebugNode()
debug_node.show_wireframe(True)
render.attach_new_node(debug_node).show()
world.set_debug_node(debug_node)

# Attach a physics object to the world for the player
player_shape = BulletSphereShape(1)
player_bullet_node = BulletRigidBodyNode("Player")
player_bullet_node.set_mass(1)
player_bullet_node.add_shape(player_shape)
player_bullet_node.set_friction(10)
player_bullet_nodepath = render.attach_new_node(player_bullet_node)
world.attach_rigid_body(player_bullet_node)

# Load a test smiley model for the player
player_node = base.loader.load_model("models/smiley.egg")
player_node.reparent_to(player_bullet_nodepath)

def controls(task):
	if keyboard_state["spacebar"]:
		player_bullet_node.set_linear_velocity(Vec3(0, 0, 10))

	total_torque = Vec3(0, 0, 0)
	if keyboard_state["w"]:
		total_torque.x = -30
	if keyboard_state["s"]:
		total_torque.x = 30
	if keyboard_state["a"]:
		total_torque.y = -30
	if keyboard_state["d"]:
		total_torque.y = 30

	player_bullet_node.apply_torque(total_torque)
	return task.cont
base.task_mgr.add(controls, 'update')

# Kick off the game loop
base.run()
