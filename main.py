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
base.set_background_color(0, 0, 0, 1)
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
environment_node = base.render.attach_new_node("Environment")
world_model = base.loader.load_model("assets/models/test_scene.egg")
world_tex = base.loader.loadTexture("assets/textures/proto_texture.png")
world_tex.set_format(core.Texture.F_srgb_alpha)
world_model.set_texture(world_tex)

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
world_nodepath = environment_node.attach_new_node(world_node)
world_nodepath.set_collide_mask(core.BitMask32.bit(colgroups.ENV_GROUP))
world_nodepath.set_z(-5)
# world_nodepath.set_p(90)
# world_model.set_color(150/255, 123/255, 182/255, 1)
world_model.reparentTo(world_nodepath)

base.world.attach_rigid_body(world_node)

# Set up the bullet debug renderer so we can see what's happening
# debug_node = bullet.BulletDebugNode()
# debug_node.show_wireframe(True)
# debug_node.show_normals(False)
# debug_node.show_bounding_boxes(False)
# debug_node.show_constraints(False)
# base.render.attach_new_node(debug_node).show()
# base.world.set_debug_node(debug_node)

player = Player()
player.add_to_world()
#player.node.set_kinematic(True)

world_material = core.Material()
world_material.set_shininess(50.0) #Make this material shiny
white = core.LColor(1, 1, 1, 1)
# world_material.set_base_color((150/255, 123/255, 182/255, 1))
#world_material.setAmbient((150/255, 123/255, 182/255, 1))
world_model.set_material(world_material)
print(world_material.get_specular())

player_material = core.Material()
player_material.set_shininess(100.0)
player_material.set_diffuse((0,0,0,1))
player_material.set_specular((1,1,1,1))
# player_material.set_base_color((0.7, 0.7, 0.7, 1))
player.model_node.set_material(player_material)

light = core.PointLight("Light")
light.set_color(core.Vec3(1, 1, 1))
light.set_attenuation((1, 0.045, 0.0075))
light.set_shadow_caster(True, 512, 512)
# light.set_max_distance()
light_np = base.render.attach_new_node(light)
light_np.set_pos(0, 0, -2)
base.render.set_light(light_np)

alight = core.AmbientLight('alight')
alight.setColor(core.VBase4(0.2, 0.2, 0.2, 1))
alnp = environment_node.attachNewNode(alight)
environment_node.setLight(alnp)

shader: core.Shader = core.Shader.load(core.Shader.SL_GLSL, vertex="assets/shaders/vertex.glsl", fragment="assets/shaders/fragment.glsl")
base.render.set_shader_input("cam_pos", base.camera.get_pos())
base.render.set_shader(shader)

def physics_update(task):
    global shadowbuf
    # Progress the physics world every frame
    dt = globalClock.get_dt()
    base.world.do_physics(dt)

    return task.cont

base.task_mgr.add(physics_update, "physics_update", sort=2)
base.task_mgr.add(player.process_inputs, "input_update", sort=1)

base.game_state.go_ingame()

# Kick off the game loop
base.run()
