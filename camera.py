from panda3d import core
from direct.task import Task

from lui.LUISprite import LUISprite

import colgroups
import mouse

class CameraControl(object):

	prev_mouse_x: float = None
	prev_mouse_y: float = None

	cam_hover_distance: float = 0.5
	dist_from_player: float = 5

	cam_heading: float = 0
	cam_pitch: float = 0

	mouse_sens: float = 20

	def __init__(self, player_node: core.NodePath):
		self.mw = base.mouseWatcherNode
		self.player_node = player_node

		self.rot_origin = core.NodePath(core.PandaNode("rot_origin"))
		self.rot_origin.reparent_to(self.player_node)
		self.rot_origin.set_compass()

		self.cam_origin = core.NodePath(core.PandaNode("cam_origin"))
		self.cam_origin.reparent_to(self.rot_origin)
		self.cam_origin.set_pos(0, -self.dist_from_player, 0)

		self.abs_crosshair_tex: core.Texture = base.loader.load_texture("assets/ui/crosshair.png")
		self.abs_crosshair_tex.setMinfilter(core.SamplerState.FT_nearest)
		self.abs_crosshair_tex.setMagfilter(core.SamplerState.FT_nearest)
		self.abs_crosshair = LUISprite(base.lui_region.root, self.abs_crosshair_tex)
		self.abs_crosshair.set_centered(True, True)
		self.abs_crosshair.set_size(14, 14)

		self.cam_ray_bitmask: core.BitMask32 = core.BitMask32.bit(colgroups.ENV_GROUP)

	def take_camera_control(self):
		base.camera.reparent_to(self.cam_origin)
		base.camera.set_pos(0, 0, self.cam_hover_distance)
		base.task_mgr.add(self.camera_update, "camera_update")

	def camera_update(self, task: Task) -> int:
		if not self.mw.has_mouse() or not mouse.mouse_captured:
			return task.cont

		if self.prev_mouse_x is not None and self.prev_mouse_y is not None:
			dx = self.mw.get_mouse_x() - self.prev_mouse_x	
			dy = self.mw.get_mouse_y() - self.prev_mouse_y

			self.cam_heading += dx * self.mouse_sens
			self.cam_pitch += dy * self.mouse_sens

			# Limit the angles the camera can rotate vertically
			self.cam_pitch = max(-90, min(self.cam_pitch, 60))

		self.rot_origin.set_h(-self.cam_heading)
		self.rot_origin.set_p(self.cam_pitch)

		self.prev_mouse_x = self.mw.get_mouse_x()
		self.prev_mouse_y = self.mw.get_mouse_y()

		# To prevent the camera from entering the environment, we shoot a ray between the player and the camera's
		# default position. If the ray hits something, move the camera to the point on the ray it's being hit.
		global_cam_pos = self.cam_origin.get_net_transform().get_pos()
		global_player_pos = self.player_node.get_net_transform().get_pos()
		cam_origin_dir_vec = global_cam_pos - global_player_pos
		cam_origin_dir_vec.normalize()
		cam_origin_dir_vec *= self.dist_from_player
		global_max_cam_extension = global_player_pos + cam_origin_dir_vec

		result = base.world.ray_test_closest(global_player_pos, global_max_cam_extension, self.cam_ray_bitmask)

		hit_frac = result.get_hit_fraction() if result.has_hit() else 1

		if result.has_hit():
			base.col_notify.debug("Camera ray has collided with " + result.get_node().get_name() + " with fraction " + str(result.get_hit_fraction()))

		self.cam_origin.set_y(-self.dist_from_player * hit_frac)

		return task.cont
