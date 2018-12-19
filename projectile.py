from panda3d.bullet import BulletSphereShape, BulletRigidBodyNode
from panda3d.core import NodePath, BitMask32

import colgroups

class Projectile(object):
	def __init__(self):
		self.shape = BulletSphereShape(0.2)

		self.node = BulletRigidBodyNode("Projectile")
		self.node.add_shape(self.shape)
		self.node.set_mass(0.1)

		self.nodepath = NodePath(self.node)
		self.nodepath.set_collide_mask(BitMask32.bit(colgroups.PLAYER_BULLET_GROUP))

		self.model = base.loader.load_model("models/smiley.egg")
		self.model.set_color(1, 0, 0, 1)
		self.model.set_scale(0.2)
		self.model.reparentTo(self.nodepath)

	def fire(self, from_pos, vector):
		base.world.attach_rigid_body(self.node)
		self.nodepath.reparentTo(base.render)
		self.nodepath.set_pos(from_pos)
		self.node.set_linear_velocity(vector)
