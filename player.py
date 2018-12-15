from panda3d.core import NodePath, Vec3
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape

from controls import FORWARD_BIND, BACKWARD_BIND, LEFT_BIND, RIGHT_BIND
from controls import control_state

from math import copysign

class Player(object):

	ground_accel = 90
	slowdown_rate = 45
	stop_threshold = 0.5
	max_speed = 30

	def __init__(self):
		self.shape = BulletSphereShape(1)

		self.node = BulletRigidBodyNode("Player")
		self.node.set_mass(1)
		self.node.add_shape(self.shape)

		# We're controlling the acceleration ourselves, we don't want friction interfering
		self.node.set_friction(0)

		self.nodepath = NodePath(self.node)

		self.model_node = base.loader.load_model("models/smiley.egg")
		self.model_node.reparent_to(self.nodepath)

	def add_to_world(self):
		base.world.attach_rigid_body(self.node)
		self.nodepath.reparent_to(base.render)

	def process_inputs(self, task):
		total_force = Vec3(0, 0, 0)

		total_force.y += control_state[FORWARD_BIND] * self.ground_accel
		total_force.y += control_state[BACKWARD_BIND] * -self.ground_accel
		total_force.x += control_state[LEFT_BIND] * -self.ground_accel
		total_force.x += control_state[RIGHT_BIND] * self.ground_accel

		if total_force != Vec3.zero() and not self.node.is_active():
			self.node.set_active(True)

		linvel = self.node.get_linear_velocity()
		
		# If the velocity is below a certain point, just stop it.
		if linvel.get_xy().length() < self.stop_threshold:
			vel = Vec3()
			vel.set_z(linvel.get_z())
			self.node.set_linear_velocity(vel)
		# Limit the velocity if we're going too fast
		elif linvel.get_xy().length() > self.max_speed:
			vel = linvel
			linvel.normalize()
			vel.set_x(self.max_speed * linvel.get_x())
			vel.set_y(self.max_speed * linvel.get_y())
			self.node.set_linear_velocity(vel)
		# Nothing is being input, so slow down the sphere so it doesn't roll off to infinity
		elif total_force == Vec3.zero():
			total_force = -self.node.get_linear_velocity()
			total_force.normalize()
			total_force *= self.slowdown_rate
			total_force.set_z(0)

		self.node.apply_central_force(total_force)

		# Rotate the sphere to make it look like it's rolling
		angular_velocity = self.node.get_linear_velocity() / self.shape.get_radius() # v = ωr
		angular_velocity.set_z(0)
		x_vel = angular_velocity.get_x()
		angular_velocity.set_x(-angular_velocity.get_y())
		angular_velocity.set_y(x_vel)

		self.node.set_angular_velocity(angular_velocity)

		return task.cont