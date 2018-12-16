PLAYER_GROUP = 0
ENV_GROUP = 1
PLAYER_BULLET_GROUP = 2
CAMERA_GROUP = 3

base.world.set_group_collision_flag(PLAYER_GROUP, PLAYER_BULLET_GROUP, False)
base.world.set_group_collision_flag(PLAYER_BULLET_GROUP, PLAYER_BULLET_GROUP, False)

base.world.set_group_collision_flag(ENV_GROUP, PLAYER_GROUP, True)
base.world.set_group_collision_flag(ENV_GROUP, PLAYER_BULLET_GROUP, True)
base.world.set_group_collision_flag(ENV_GROUP, CAMERA_GROUP, True)