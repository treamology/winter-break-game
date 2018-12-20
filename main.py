from panda3d import core, bullet
from direct.showbase.ShowBase import ShowBase

import controls
import mouse
import colgroups
from player import Player

from lui.LUIRegion import LUIRegion

import os

class GameState(object):
	"""Some state that applies globally"""
	ingame: bool = False

	def go_ingame(self):
		"""Allows mouse to be captured and released"""
		base.accept("escape", mouse.toggle_mouse)

	def leave_ingame(self):
		"""Undoes whatever was done by `go_ingame()`"""
		pass

core.loadPrcFile(os.path.abspath("./config.prc"))

# Initialize ShowBase and some basic options.
base = ShowBase()
base.disable_mouse()
base.game_state: GameState = GameState()

# Set up LUI
base.lui_region: LUIRegion = LUIRegion.make("HUD", base.win)

# Set up control bindings
controls.setup_controls()

# Initialize the physics world
base.world = bullet.BulletWorld()
base.world.set_gravity(core.Vec3(0, 0, -9.81))

# Set mouse to relative mode for camera movement
mouse.capture_mouse()

# Now that we have the basic stuff set up, we can continue importing things that
# depend on it existing.
colgroups.init()

# Create the world mesh and collision solid
world_model = base.loader.load_model("assets/models/world.egg")

geom = None
for geom_np in world_model.findAllMatches('**/+GeomNode'):
	geom_node = geom_np.node()
	geom = geom_node.get_geom(0)
	break

mesh = bullet.BulletTriangleMesh()
mesh.add_geom(geom)

mesh_shape = bullet.BulletTriangleMeshShape(mesh, dynamic=False)
world_node = bullet.BulletRigidBodyNode("World")
world_node.add_shape(mesh_shape)
world_nodepath = base.render.attach_new_node(world_node)
world_nodepath.set_collide_mask(core.BitMask32.bit(colgroups.ENV_GROUP))
world_nodepath.set_z(-5)
world_nodepath.set_p(270)
world_model.set_color(150/255, 123/255, 182/255, 1)
world_model.reparentTo(world_nodepath)

base.world.attach_rigid_body(world_node)

# Add some lighting
# light = PointLight("Light")
# light.set_color(Vec3(1, 1, 1))
# light_np = base.render.attach_new_node(light)
# light_np.set_pos(0, 0, 50)
# base.render.set_light(light_np)

# world_mat = Material()
# world_mat.set_diffuse((150/255, 123/255, 182/255, 1))
# world_model.set_material(world_mat)

# Set up the bullet debug renderer so we can see what's happening
debug_node = bullet.BulletDebugNode()
debug_node.show_wireframe(True)
base.render.attach_new_node(debug_node).show()
base.world.set_debug_node(debug_node)

player = Player()
player.add_to_world()

def physics_update(task):
	# Progress the physics world every frame
	dt = globalClock.get_dt()
	base.world.do_physics(dt)
	
	return task.cont

base.task_mgr.add(physics_update, "physics_update", sort=2)
base.task_mgr.add(player.process_inputs, "input_update", sort=1)

base.game_state.go_ingame()

# Kick off the game loop
base.run()
