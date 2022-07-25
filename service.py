import numpy as np

from multiConnectionServer import *


def generate_default_tiles(height: int, width: int, ship_name_default, bool_shot_default):
    """
    Function generates a list of height x width tiles. The list will contain tuples
    ('shipName', boolShot) set to their (default_value).

    default_value -> boolean which tells what the value to set to
    returns the list of tuples
    """
    default_tiles = np.full((height, width), (ship_name_default, bool_shot_default))

    return default_tiles


def check_revealed_tile(board, tile):
    """
    Function checks if a tile location contains a ship piece.

    board -> the tiled board either a ship piece or none
    tile -> location of tile
    returns True if ship piece exists at tile location
    """
    return board[tile[0]][tile[1]] is not None


def check_for_win(board):
    """
    Function checks if the current board state is a winning state.

    board -> the board which contains the ship pieces
    revealed -> list of revealed tiles
    returns True if all the ships are revealed
    """
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            # check if every board with a ship is revealed, return false if not
            loc = board[tilex][tiley]
            if loc[0] is not None and not loc[1]:
                return False
    return True











