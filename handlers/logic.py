import math


def w2s(camera: dict, actor: dict) -> tuple:
    try:
        # Ножно сделать получение фов
        fov = 90

        temp_matrix = viev_matrix(camera)
        # print(temp_matrix)

        v_axis_x = (temp_matrix[0][0], temp_matrix[0][1], temp_matrix[0][2])
        v_axis_y = (temp_matrix[1][0], temp_matrix[1][1], temp_matrix[1][2])
        v_axis_z = (temp_matrix[2][0], temp_matrix[2][1], temp_matrix[2][2])

        v_delta = (actor['cordinate_x'] - camera['localPlayer_x'],
                   actor['cordinate_y'] - camera['localPlayer_y'],
                   actor['cordinate_z'] - camera['localPlayer_z'])

        v_transformed = [dot(v_delta, v_axis_y),
                         dot(v_delta, v_axis_z),
                         dot(v_delta, v_axis_x)]

        if v_transformed[2] < 1.0:
            return False

        # Нужно сделать получение размера окна игры
        screen_center_x = 1920 / 2
        screen_center_y = 1080 / 2

        tmp_fov = math.tan(fov * math.pi / 360)

        x = screen_center_x + v_transformed[0] * (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if x > 1920 or x < 0:
            return False
        y = screen_center_y - v_transformed[1] * \
            (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if y > 1080 or y < 0:
            return False

        return int(x), int(y)

    except Exception as _error:
        print(_error)


def viev_matrix(camera):
    rad_pitch = (camera['camera_x'] * math.pi / 180)
    rad_yaw = (camera['camera_y'] * math.pi / 180)
    rad_roll = (camera['camera_z'] * math.pi / 180)

    sin_pitch = math.sin(rad_pitch)
    cos_pitch = math.cos(rad_pitch)
    sin_yaw = math.sin(rad_yaw)
    cos_yaw = math.cos(rad_yaw)
    sin_roll = math.sin(rad_roll)
    cos_roll = math.cos(rad_roll)

    matrix = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    matrix[0][0] = cos_pitch * cos_yaw
    matrix[0][1] = cos_pitch * sin_yaw
    matrix[0][2] = sin_pitch

    matrix[1][0] = sin_roll * sin_pitch * cos_yaw - cos_roll * sin_yaw
    matrix[1][1] = sin_roll * sin_pitch * sin_yaw + cos_roll * cos_yaw
    matrix[1][2] = -sin_roll * cos_pitch

    matrix[2][0] = -(cos_roll * sin_pitch * cos_yaw + sin_roll * sin_yaw)
    matrix[2][1] = cos_yaw * sin_roll - cos_roll * sin_pitch * sin_yaw
    matrix[2][2] = cos_roll * cos_pitch

    return matrix


def dot(array_1: tuple, array_2: tuple):
    if array_2[0] == 0 and array_2[1] == 0 and array_2[2] == 0:
        return 0.0

    return array_1[0] * array_2[0] + array_1[1] \
        * array_2[1] + array_1[2] * array_2[2]


def get_actor_distance(local_player_cords, actor_cords) -> int:
    return int(math.sqrt(
        (actor_cords['cordinate_x'] - local_player_cords['localPlayer_x']) ** 2 + (actor_cords['cordinate_y'] - local_player_cords['localPlayer_y']) ** 2 + (actor_cords['cordinate_z'] - local_player_cords['localPlayer_z']) ** 2))
