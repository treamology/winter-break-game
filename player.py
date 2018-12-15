from panda3d.core import NodePath, Vec3
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape

from controls import FORWARD_BIND, BACKWARD_BIND, LEFT_BIND, RIGHT_BIND
from controls import control_state

class Player(object):

	ground_torque_speed = 30

	def __init__(self):
		self.shape = BulletSphereShape(1)

		self.node = BulletRigidBodyNode("Player")
		self.node.set_mass(1)
		self.node.add_shape(self.shape)
		self.node.set_friction(10)
		# self.node.deactivation_enabled = False

		self.nodepath = NodePath(self.node)

		self.model_node = base.loader.load_model("models/smiley.egg")
		self.model_node.reparent_to(self.nodepath)

	def add_to_world(self):
		base.world.attach_rigid_body(self.node)
		self.nodepath.reparent_to(base.render)

	def process_inputs(self):
		total_torque = Vec3(0, 0, 0)

		total_torque.x += control_state[FORWARD_BIND] * -self.ground_torque_speed
		total_torque.x += control_state[BACKWARD_BIND] * self.ground_torque_speed
		total_torque.y += control_state[LEFT_BIND] * -self.ground_torque_speed
		total_torque.y += control_state[RIGHT_BIND] * self.ground_torque_speed

		if (total_torque != Vec3.zero() and not self.node.is_active()):
			self.node.set_active(True)			

		self.node.apply_torque(total_torque)