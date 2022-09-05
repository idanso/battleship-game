import random

import uuid
import enum
import pickle
import client

#### Globals ####
DEFAULT_SHIP_NAME = None
DEFAULT_BOOL_SHOT = False

FILE_NAME = "saved_data"

BOARD_WIDTH = 10  # Number of grids horizontally
BOARD_HEIGHT = 10  # Number of grids vertically


################


class GameStatus(enum.Enum):
    ACTIVE = 1
    ENDED = 2
    READY = 3


class User:
    def __init__(self, name):
        self.name = name
        self.score = {"win": 0, "lose": 0}


class Game:
    def __init__(self, address, player1, player2):
        self.id = uuid.uuid4()
        self.players = [player1, player2]
        self.address = address
        # self.score = [0, 0]
        self.boards = [None, None]
        self.status = GameStatus.ACTIVE

    def init_auto_generated_boards(self, height=BOARD_HEIGHT, width=BOARD_WIDTH, ships_objs=None):
        self.boards[0] = generate_default_tiles(height, width)
        self.boards[1] = generate_default_tiles(height, width)

        if ships_objs is None:
            ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
                         'destroyer3', 'submarine1', 'submarine2', 'submarine3',
                         'submarine4']  # List of the ships available

        self.boards[0] = add_ships_to_board(self.boards[0], ship_objs)
        self.boards[1] = add_ships_to_board(self.boards[1], ship_objs)

    def set_players(self, players):
        self.players = players

    def set_boards(self, board1, board2):
        self.boards[board1, board2]


class ServerGamesHandler:
    def __init__(self):
        self.number_of_games = 0
        self.games_lst = []
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    def add_game(self, game: Game):
        self.games_lst.append(game)
        self.number_of_games += 1

    def start_game(self, address, players, boards=None): # TODO: update Doc
        """
        create new game with initialized random boards for each player and add it to the games list
        :param: two players who will take park of the game
        :return: the game id
        """
        game = Game(address)
        game.set_players(players)
        if boards:
            game.set_boards(boards)
        else:
            game.init_auto_generated_boards()

        self.add_game(game)
        return game

    def get_game_by_address(self, game_address) -> Game:
        """
        :param: player_port: the socket port of the player
        :return: id of active game of the player with player_port, id of player
                if player not found return None
        """
        for game in self.games_lst:
            if game.status == GameStatus.ACTIVE and game.address[0] == game_address[0] and game.address[1] == game_address[1]:
                return game
        return None

    def get_game_by_id(self, game_address):
        """
        :param: player_port: the socket port of the player
        :return: id of active game of the player with player_port, id of player
                if player not found return None
        """
        for game in self.games_lst:
            if game.status == GameStatus.ACTIVE and game.address[0] == game[0] and game.address[1] == game[1]:
                return tuple(game.id)
        return None

    def get_ordered_5_players(self, reverse=True):
        return sorted(self.users, key=lambda user: user.score["win"], reverse=reverse)[:5]

    def get_user_by_name(self, name):
        for user in self.users:
            if user.name == name:
                return user
        return None

    def finish_all_games(self):
        for game in self.games_lst:
            if game.status == GameStatus.ACTIVE:
                game.status = GameStatus.ENDED


def save_data_to_file(game_handler, file_name=FILE_NAME):
    with open(file_name, 'wb') as f:
        pickle.dump(game_handler, f)


def load_data_from_file(file_name=FILE_NAME):
    with open(file_name, 'rb') as f:
        game_handler = pickle.load(f)
    return game_handler


def generate_default_tiles(height: int, width: int, ship_name_default=DEFAULT_SHIP_NAME,
                           bool_shot_default=DEFAULT_BOOL_SHOT):
    """
    Function generates a list of height x width tiles. The list will contain list
    ('shipName', boolShot) set to their (default_value).

    default_value -> boolean which tells what the value to set to
    :returns: the list of tuples
    """
    default_tiles = [[[ship_name_default, bool_shot_default] for _ in range(width)] for _ in range(height)]
    #  TODO: delete if unnecessary
    # for x in range(height):
    #     for y in range(width):
    #         default_tiles[x][y] = (ship_name_default, bool_shot_default)
    # default_tiles = np.full((height, width), (ship_name_default, bool_shot_default), dtype='V,V')
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
    returns True if all the ships are revealed
    """
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
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
    size_col = len(board[1])
    size_rows = len(board[0])
    xmarkers = [0 for i in range(size_col)]
    ymarkers = [0 for i in range(size_rows)]
    # Loop through the tiles
    for tilex in range(size_col):
        for tiley in range(size_rows):
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
                    has_adjacent(board, i + x_pos, y_pos,
                                 ship):  # if the ship goes out of bound, hits another ship, or is adjacent to another ship
                return False, ship_coordinates  # then return false
            else:
                ship_coordinates.append((i + x_pos, y_pos))
    else:
        for i in range(length):
            if (i + y_pos > 9) or (board[x_pos][i + y_pos][0] is not None) or \
                    has_adjacent(board, x_pos, i + y_pos,
                                 ship):  # if the ship goes out of bound, hits another ship, or is adjacent to another ship
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

def start_client(players=('idan', 'shiran')):
    client.run_client('127.0.0.1', 1233)

