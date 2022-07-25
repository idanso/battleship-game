import numpy as np


def generate_default_tiles(height: int, width: int, ship_name_default, bool_shot_default):
    """
    Function generates a list of height x width tiles. The list will contain tuples
    ('shipName', boolShot) set to their (default_value).

    default_value -> boolean which tells what the value to set to
    returns the list of tuples
    """
    default_tiles = np.full((height, width), (ship_name_default, bool_shot_default))

    return default_tiles

