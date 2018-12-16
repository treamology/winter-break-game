from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import PandaNode, NodePath, Vec3
import math, colgroups

class CameraControl(object):

	prev_mouse_x = None
	prev_mouse_y = None

	cam_hover_distance = 2
	dist_from_player = 25

	cam_heading = 0
	cam_pitch = 0

	mouse_sens = 20

	def __init__(self, player_node):
		self.mw = base.mouseWatcherNode
		self.player_node = player_node

		self.rot_origin = NodePath(PandaNode("rot_origin"))
		self.rot_origin.reparent_to(self.player_node)
		self.rot_origin.set_compass()

		self.cam_origin = NodePath(PandaNode("cam_origin"))
		self.cam_origin.reparent_to(self.rot_origin)
		self.cam_origin.set_pos(0, -self.dist_from_player, 0)

	def take_camera_control(self):
		base.camera.reparent_to(self.cam_origin)
		base.camera.set_pos(0, 0, self.cam_hover_distance)
		base.task_mgr.add(self.camera_update, "camera_update")

	def camera_update(self, task):
		if not self.mw.has_mouse():
			return

		if self.prev_mouse_x is not None and self.prev_mouse_y is not None:
			dx = self.mw.get_mouse_x() - self.prev_mouse_x	
			dy = self.mw.get_mouse_y() - self.prev_mouse_y

			self.cam_heading += dx * self.mouse_sens
			self.cam_pitch += dy * self.mouse_sens

			self.cam_pitch = max(-90, min(self.cam_pitch, 60))

		self.rot_origin.set_h(-self.cam_heading)
		self.rot_origin.set_p(self.cam_pitch)

		self.prev_mouse_x = self.mw.get_mouse_x()
		self.prev_mouse_y = self.mw.get_mouse_y()

		global_cam_pos = self.cam_origin.get_net_transform().get_pos()
		global_player_pos = self.player_node.get_net_transform().get_pos()
		cam_origin_dir_vec = global_cam_pos - global_player_pos
		cam_origin_dir_vec.normalize()
		cam_origin_dir_vec *= self.dist_from_player
		global_max_cam_extension = global_player_pos + cam_origin_dir_vec

		result = base.world.ray_test_closest(global_player_pos, global_max_cam_extension)

		hit_frac = 1
		if result.has_hit():
			hit_frac = result.get_hit_fraction()

		self.cam_origin.set_y(-self.dist_from_player * hit_frac)

		return task.cont
	
