from panda3d import core, bullet

import colgroups

class Projectile(object):
	def __init__(self):
		self.shape = bullet.BulletSphereShape(0.2)

		self.node = bullet.BulletRigidBodyNode("Projectile")
		self.node.add_shape(self.shape)
		self.node.set_mass(0.1)

		self.nodepath = core.NodePath(self.node)
		self.nodepath.set_collide_mask(core.BitMask32.bit(colgroups.PLAYER_BULLET_GROUP))

		self.model: core.NodePath = base.loader.load_model("models/smiley.egg")
		self.model.set_color(1, 0, 0, 1)
		self.model.set_scale(0.2)
		self.model.reparentTo(self.nodepath)

	def fire(self, from_pos: core.Vec3, vector: core.Vec3):
		base.world.attach_rigid_body(self.node)
		self.nodepath.reparentTo(base.render)
		self.nodepath.set_pos(from_pos)
		self.node.set_linear_velocity(vector)
