from random import random

import numpy as np
import uuid

from multiConnectionServer import *
from client_service import *


#### Globals ####
DEFAULT_SHIP_NAME = None
DEFAULT_BOOL_SHOT = False

BOARD_WIDTH = 10  # Number of grids horizontally
BOARD_HEIGHT = 10  # Number of grids vertically
################


class Player:
    def __init__(self, connection, address):
        self.id = uuid.uuid4()
        self.connection = connection
        self.address = address
        self.score = {"win": 0, "lose": 0}


class Game:
    def __init__(self, player_1: Player, player_2: Player):
        self.id = uuid.uuid4()
        self.players = [player_1, player_2]
        self.score = [0, 0]
        self.boards = {player_1.id: None, player_2.id: None}
        self.active = True

    def init_boards(self, height=BOARD_HEIGHT, width=BOARD_WIDTH, ships_objs=None):
        player_1 = self.players[0].id
        player_2 = self.players[1].id
        self.boards[player_1] = generate_default_tiles(height, width)
        self.boards[player_2] = generate_default_tiles(height, width)

        if ships_objs is None:
            ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
                         'destroyer3', 'submarine1', 'submarine2', 'submarine3', 'submarine4']  # List of the ships available

        self.boards[player_1] = add_ships_to_board(self.boards[player_1], ship_objs)
        self.boards[player_2] = add_ships_to_board(self.boards[player_2], ship_objs)


class GamesHandler:
    def __init__(self):
        self.number_of_games = 0
        self.games_lst = []

    def add_game(self, game: Game):
        self.games_lst.append(game)
        self.number_of_games += 1

    def start_game(self, player_1: Player, player_2: Player):
        """
        create new game with initialized random boards for each player and add it to the games list
        :param: two players who will take park of the game
        :return: the game id
        """
        game = Game(player_1, player_2)
        game.init_boards()
        self.add_game(game)
        return game.id

    def get_player_and_game_by_port(self, player_port: int):
        """
        :param: player_port: the socket port of the player
        :return: id of active game of the player with player_port, id of player
                if player not found return None
        """
        for game in self.games_lst:
            if game.active:
                for player in game.players:
                    if player.address[1] == player_port:
                        return game.id, player.id
        return None


def generate_default_tiles(height: int, width: int, ship_name_default=DEFAULT_SHIP_NAME, bool_shot_default=DEFAULT_BOOL_SHOT):
    """
    Function generates a list of height x width tiles. The list will contain tuples
    ('shipName', boolShot) set to their (default_value).

    default_value -> boolean which tells what the value to set to
    :returns: the list of tuples
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
    for tilex in range(board.size[1]):
        for tiley in range(board.size[0]):
            # check if every board with a ship is revealed, return false if not
            loc = board[tilex][tiley]
            if loc[0] is not None and not loc[1]:
                return False
    return True


def set_markers(board):
    """
    Function creates the lists of the markers to the side of the game board which indicates
    the number of ship pieces in each row and column.

    board: list of board tiles
    returns the 2 lists of markers with number of ship pieces in each row (xmarkers)
        and column (ymarkers)
    """
    xmarkers = [0 for i in range(board.size[1])]
    ymarkers = [0 for i in range(board.size[0])]
    # Loop through the tiles
    for tilex in range(board.size[1]):
        for tiley in range(board.size[0]):
            if board[tilex][tiley][0] is not None:  # if the tile is a ship piece, then increment the markers
                xmarkers[tilex] += 1
                ymarkers[tiley] += 1

    return xmarkers, ymarkers


def add_ships_to_board(board, ships):
    """
    Function goes through a list of ships and add them randomly into a board.

    board -> list of board tiles
    ships -> list of ships to place on board
    returns list of board tiles with ships placed on certain tiles
    """
    new_board = board[:]
    ship_length = 0
    for ship in ships:  # go through each ship declared in the list
        # Randomly find a valid position that fits the ship
        valid_ship_position = False
        while not valid_ship_position:
            xStartpos = random.randint(0, 9)
            yStartpos = random.randint(0, 9)
            isHorizontal = random.randint(0, 1)  # vertical or horizontal positioning
            # Type of ship and their respective length
            if 'battleship' in ship:
                ship_length = 4
            elif 'cruiser' in ship:
                ship_length = 3
            elif 'destroyer' in ship:
                ship_length = 2
            elif 'submarine' in ship:
                ship_length = 1

            # check if position is valid
            valid_ship_position, ship_coords = make_ship_position(new_board,
                                                                  xStartpos, yStartpos, isHorizontal, ship_length, ship)
            # add the ship if it is valid
            if valid_ship_position:
                for coord in ship_coords:
                    new_board[coord[0]][coord[1]][0] = ship
    return new_board


def make_ship_position(board, x_pos, y_pos, isHorizontal, length, ship):
    """
    Function makes a ship on a board given a set of variables

    board -> list of board tiles
    xPos -> x-coordinate of first ship piece
    yPos -> y-coordinate of first ship piece
    isHorizontal -> True if ship is horizontal
    length -> length of ship
    returns tuple: True if ship position is valid and list ship coordinates
    """
    ship_coordinates = []  # the coordinates the ship will occupy
    if isHorizontal:
        for i in range(length):
            if (i + x_pos > 9) or (board[i + x_pos][y_pos][0] is not None) or \
                    has_adjacent(board, i + x_pos, y_pos, ship):  # if the ship goes out of bound, hits another ship, or is adjacent to another ship
                return False, ship_coordinates  # then return false
            else:
                ship_coordinates.append((i + x_pos, y_pos))
    else:
        for i in range(length):
            if (i + y_pos > 9) or (board[x_pos][i + y_pos][0] is not None) or \
                    has_adjacent(board, x_pos, i + y_pos, ship):  # if the ship goes out of bound, hits another ship, or is adjacent to another ship
                return False, ship_coordinates  # then return false
            else:
                ship_coordinates.append((x_pos, i + y_pos))
    return True, ship_coordinates  # ship is successfully added


def has_adjacent(board, x_pos, y_pos, ship):
    """
    Funtion checks if a ship has adjacent ships

    board -> list of board tiles
    xPos -> x-coordinate of first ship piece
    yPos -> y-coordinate of first ship piece
    ship -> the ship being checked for adjacency
    returns true if there are adjacent ships and false if there are no adjacent ships
    """
    for x in range(x_pos - 1, x_pos + 2):
        for y in range(y_pos - 1, y_pos + 2):
            if (x in range(10)) and (y in range(10)) and \
                    (board[x][y][0] not in (ship, None)):
                return True
    return False








