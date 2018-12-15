from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d.core import Vec3, loadPrcFile
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

from player import Player
import controls

loadPrcFile("config.prc")

# Initialize ShowBase and some basic options.
base = ShowBase()
base.disable_mouse()

# Set the camera to a test location
base.camera.set_pos(0, -30, 15)
base.camera.set_p(-30)

# Set up control bindings
controls.setup_controls()

# Initialize the physics world
base.world = BulletWorld()
base.world.set_gravity(Vec3(0, 0, -9.81))

# Set up the ground, which is an infinite plane (for now)
ground_node = BulletRigidBodyNode("Ground")
ground_node.add_shape(BulletPlaneShape(Vec3(0, 0, 1), 1)) # normal, const)
ground_nodepath = base.render.attach_new_node(ground_node)
ground_nodepath.set_z(-10)
base.world.attach_rigid_body(ground_node)

# Set up the bullet debug renderer so we can see what's happening
debug_node = BulletDebugNode()
debug_node.show_wireframe(True)
render.attach_new_node(debug_node).show()
base.world.set_debug_node(debug_node)

player = Player()
player.add_to_world()

def physics_update(task):
	# Progress the physics world every frame
	dt = globalClock.get_dt()
	base.world.do_physics(dt)
	
	return task.cont

base.task_mgr.add(physics_update, "phsyics_update")
base.task_mgr.add(player.process_inputs, "input_update")

# Kick off the game loop
base.run()
