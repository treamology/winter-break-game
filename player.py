from panda3d import core, bullet
from direct.task import Task

from controls import FORWARD_BIND, BACKWARD_BIND, LEFT_BIND, RIGHT_BIND, FIRE_BIND
from controls import control_state

from projectile import Projectile

from math import sin, cos, radians, asin, sqrt

import colgroups
import mouse
from camera import CameraControl

class Player(object):

    ground_accel: float = 90
    slowdown_rate: float = 45
    stop_threshold: float = 0.5
    max_speed: float = 20

    bullet_speed: float = 80
    fire_rate: float = 0.2

    fire_accum: float = 0

    def __init__(self):
        self.shape = bullet.BulletSphereShape(1)

        self.node = bullet.BulletRigidBodyNode("Player")
        self.node.set_mass(1)
        self.node.add_shape(self.shape)

        # We're controlling the acceleration ourselves, we don't want friction interfering
        self.node.set_friction(0)

        self.nodepath = core.NodePath(self.node)
        self.nodepath.set_collide_mask(core.BitMask32.bit(colgroups.PLAYER_GROUP))

        self.model_node: core.NodePath = base.loader.load_model("models/smiley.egg")
        self.model_node.reparent_to(self.nodepath)

        self.cam_control = CameraControl(self.nodepath)
        self.cam_control.take_camera_control()

    def add_to_world(self):
        base.world.attach_rigid_body(self.node)
        self.nodepath.reparent_to(base.render)

    def process_inputs(self, task: Task) -> int:
        if not mouse.mouse_captured:
            return task.cont

        total_force = core.Vec3(0, 0, 0)

        if control_state[FORWARD_BIND] != 0:
            total_force.x += control_state[FORWARD_BIND] * self.ground_accel * sin(radians(self.cam_control.cam_heading))
            total_force.y += control_state[FORWARD_BIND] * self.ground_accel * cos(radians(self.cam_control.cam_heading))
        if control_state[BACKWARD_BIND] != 0:
            total_force.x += control_state[BACKWARD_BIND] * -self.ground_accel * sin(radians(self.cam_control.cam_heading))
            total_force.y += control_state[BACKWARD_BIND] * -self.ground_accel * cos(radians(self.cam_control.cam_heading))
        if control_state[LEFT_BIND] != 0:
            total_force.x += control_state[LEFT_BIND] * -self.ground_accel * cos(radians(self.cam_control.cam_heading))
            total_force.y += control_state[LEFT_BIND] * self.ground_accel * sin(radians(self.cam_control.cam_heading))
        if control_state[RIGHT_BIND] != 0:
            total_force.x += control_state[RIGHT_BIND] * self.ground_accel * cos(radians(self.cam_control.cam_heading))
            total_force.y += control_state[RIGHT_BIND] * -self.ground_accel * sin(radians(self.cam_control.cam_heading))

        if total_force != core.Vec3.zero() and not self.node.is_active():
            self.node.set_active(True)

        linvel = self.node.get_linear_velocity()

        # If the velocity is below a certain point, just stop it.
        if linvel.get_xy().length() < self.stop_threshold:
            vel = core.Vec3()
            vel.set_z(linvel.get_z())
            self.node.set_linear_velocity(vel)
        # Limit the velocity if we're going too fast
        elif linvel.get_xy().length() > self.max_speed:
            prev_length = linvel.length()
            linvel.normalize()
            linvel.set_x(self.max_speed * linvel.get_x())
            linvel.set_y(self.max_speed * linvel.get_y())
            linvel.set_z(linvel.get_z() * prev_length)
            self.node.set_linear_velocity(linvel)
        # Nothing is being input, so slow down the sphere so it doesn't roll off to infinity
        elif total_force == core.Vec3.zero():
            total_force = -self.node.get_linear_velocity()
            total_force.normalize()
            total_force *= self.slowdown_rate
            total_force.set_z(0)

        self.node.apply_central_force(total_force)

        # Rotate the sphere to make it look like it's rolling
        angular_velocity = self.node.get_linear_velocity() / self.shape.get_radius()  # v = ωr
        angular_velocity.set_z(0)
        x_vel = angular_velocity.get_x()
        angular_velocity.set_x(-angular_velocity.get_y())
        angular_velocity.set_y(x_vel)

        self.node.set_angular_velocity(angular_velocity)

        if control_state[FIRE_BIND] == 1:
            if self.fire_accum >= self.fire_rate:
                # fire_angle is calculated using a kinematic equation, the goal
                # is to have the ball's apex be where the crosshairs are aiming.
                grav = base.world.get_gravity().get_z()
                pitch = self.cam_control.cam_pitch
                height = self.cam_control.cam_hover_distance
                fire_angle = asin(sqrt((-2*grav*cos(radians(pitch))*height)/(self.bullet_speed * self.bullet_speed))) \
                    + radians(self.cam_control.cam_pitch)

                # Calculate the real velocity using the way the player is facing,
                # the angle upwards the ball should be shot, and the player's current
                # linear velocity.
                bullet_velocity = core.Vec3(
                    sin(radians(self.cam_control.cam_heading))*cos(fire_angle),
                    cos(radians(self.cam_control.cam_heading))*cos(fire_angle),
                    sin(fire_angle)
                ) * self.bullet_speed
                bullet_velocity += linvel

                projectile = Projectile()
                projectile.fire(self.nodepath.get_pos(), bullet_velocity)

                self.fire_accum = 0

        # I don't know if it's actually possible to overflow this number, but
        # just to be safe...
        if self.fire_accum < self.fire_rate:
            self.fire_accum += globalClock.get_dt()

        return task.cont
