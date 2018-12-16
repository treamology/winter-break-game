from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d.core import Vec3, loadPrcFile, BitMask32, WindowProperties
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletBoxShape
from panda3d.bullet import BulletDebugNode

import controls

loadPrcFile("config.prc")

# Initialize ShowBase and some basic options.
base = ShowBase()
base.disable_mouse()

# Set up control bindings
controls.setup_controls()

# Initialize the physics world
base.world = BulletWorld()
base.world.set_gravity(Vec3(0, 0, -9.81))

# Set mouse to relative mode for camera movement
props = WindowProperties()
props.set_mouse_mode(WindowProperties.M_relative)
base.win.request_properties(props)

# Now that we have the basic stuff set up, we can continue importing things that
# depend on it existing.
import colgroups
from player import Player

# Set up the ground, which is an infinite plane (for now)
ground_node = BulletRigidBodyNode("Ground")
# ground_node.add_shape(BulletPlaneShape(Vec3(0, 0, 1), 0)) # normal, const)
box = BulletBoxShape(Vec3(100, 100, 2))
ground_node.add_shape(box)
ground_nodepath = base.render.attach_new_node(ground_node)
ground_nodepath.set_z(-10)
ground_nodepath.set_collide_mask(BitMask32.bit(colgroups.ENV_GROUP))
base.world.attach_rigid_body(ground_node)

wall = BulletBoxShape(Vec3(2, 100, 100))
wall_node = BulletRigidBodyNode("Wall")
wall_node.add_shape(wall)
wall_nodepath = base.render.attach_new_node(wall_node)
wall_nodepath.set_collide_mask(BitMask32.bit(colgroups.ENV_GROUP))
base.world.attach_rigid_body(wall_node)

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

base.task_mgr.add(physics_update, "phsyics_update", sort=2)
# base.task_mgr.add(camera.camera_update, "camera_update", extraArgs=[player.aim_node], sort=2, appendTask=True)
base.task_mgr.add(player.process_inputs, "input_update", sort=1)

base.accept("escape", quit)

# Kick off the game loop
base.run()
