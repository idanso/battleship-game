import random
import uuid
import enum
import pickle
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk)

#### Globals ####
DEFAULT_SHIP_NAME = None
DEFAULT_BOOL_SHOT = False

FILE_NAME = "saved_data.pkl"

BOARD_WIDTH = 10  # Number of grids horizontally
BOARD_HEIGHT = 10  # Number of grids vertically


################

class GameStatus(enum.Enum):
    """
    Enum class for game status
    """
    ACTIVE = 1
    ENDED = 2


class User:
    """
    class User stores the players data with their name and overall score
    """
    def __init__(self, name: str):
        self.name = name
        self.score = {"win": 0, "lose": 0}

    def __cmp__(self, other: str):
        return self.name == other.name


class Game:
    """
    class Game  to store individual game between two players, their socket address from client, players boards and game status of the game
    """
    def __init__(self, address, players: [User, User]=None):
        self.id = uuid.uuid4()
        if players:
            self.players = players
        else:
            self.players = [None, None]
        self.address = address
        self.boards = [None, None]
        self.status = GameStatus.ACTIVE


    def init_auto_generated_boards(self, height=BOARD_HEIGHT, width=BOARD_WIDTH, ships_objs=None):
        """
        Function generate random boards for two players with custom or predefine ships and add them to the players board.

        :param height: int board height
        :param width: int board width
        :param ships_objs: list of names of ships to place on board
        """
        self.boards[0] = generate_default_tiles(height, width)
        self.boards[1] = generate_default_tiles(height, width)

        if ships_objs is None:
            ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
                         'destroyer3', 'submarine1', 'submarine2', 'submarine3',
                         'submarine4']  # List of the ships available

        self.boards[0] = add_ships_to_board(self.boards[0], ship_objs)
        self.boards[1] = add_ships_to_board(self.boards[1], ship_objs)

    def set_players(self, players: [User, User]):
        """
        Function set players to game

        :param players: list[2] of two players of object 'User'
        """
        self.players = players

    def set_boards(self, board1, board2):
        """
        Function set boards of players to game

        :param board1: list[][] 2D matrix of board for player 1, every elemet is tuple('shipName', boolShot)
        :param board2: list[][] 2D matrix of board for player 2, every elemet is tuple('shipName', boolShot)
        """
        self.boards[0] = board1
        self.boards[1] = board2


class ServerGamesHandler:
    def __init__(self):
        """
        Class for managing all games and server objects

        :attribute number_of_games: int count number of games stored
        :attribute games_lst: list of type 'Game' stores all games
        :attribute users: list of type 'User' stores all users
        :attribute readyPlayers: list[2] of type string stores names of players ready to enter game
        :attribute ready_thread: Thread stores the client thread of the game ready to start
        :attribute kill_server: bool to state if server need to exit
        """
        self.number_of_games = 0
        self.games_lst = []
        self.users = []
        self.readyPlayers = [None, None]
        self.ready_thread = None
        self.kill_server = False

    def add_user(self, user: User):
        """
        function for adding new user to users list

        :param user: User to append list
        """
        self.users.append(user)

    def add_game(self,game: Game):
        """
        function for adding new user to users list

        :param user: User to append list
        """
        self.games_lst.append(game)
        self.number_of_games += 1


    def start_game(self, address, players: [str, str]=None, boards=None, thread=None) -> Game:
        """
        create new game with  for each player and add it to the games list

        :param address: tuple containing port and address of client socket
        :param players: list[2] player's names of type trings
        :param boards: list[2] of board with list[][] 2D matrix of board, every element is tuple('shipName', boolShot)
        :param thread: Thread stores the client thread of the game

        :return: 'Game' object of the new created game
        """
        game = Game(address, thread)
        game.set_players([self.get_user_by_name(players[0]), self.get_user_by_name(players[1])])
        if boards:
            game.set_boards(boards[0], boards[1])
        else:
            game.init_auto_generated_boards()

        self.add_game(game)
        return game

    def get_game_by_address(self, game_address) -> Game:
        """
        Function get game with the given address(address, port)

        :param: game_address: tuple containing port and address of client socket
        :return: 'Game' object of the game with with the game address,
                if game not found return None
        """
        for game in self.games_lst:
            if game.status == GameStatus.ACTIVE and game.address[0] == game_address[0] and game.address[1] == game_address[1]:
                return game
        return None


    def get_ordered_best_players(self, reverse=True) -> list:
        """
        Function to get ordered best players with most or least wins

        :param: reverse: bool specify order of the sorted uesrs list
        :return: list of type 'User' sorted by wins count of each user
        """
        return sorted(self.users, key=lambda user: user.score["win"], reverse=reverse)

    def get_best_players_plot(self):
        best_players = self.get_ordered_best_players()
        wins_lst = list(map(lambda user: user.score["win"], best_players))
        players_lst = list(map(lambda user: user.name, best_players))
        plt.bar(players_lst, wins_lst)

    def get_ordered_most_games(self, reverse=True):
        return sorted(self.users, key=lambda user: user.score["win"] + user.score["lose"], reverse=reverse)

    def get_string_players_with_most_games(self):
        most_played_players = list(map(lambda user: [user.name, user.score["wins"] + user.score["lose"]], self.get_ordered_most_games()))
        out_str = "   Player Name   | Number Of Games |\n"
        out_str += "------------------------------------\n"
        for i, user in enumerate(most_played_players):
            out_str += str(str(i) + ") " + str(user[0])).ljust(17) + "|   " + str(user[1]).ljust(13)
        return out_str

    def get_user_by_name(self, name: str) -> User:
        """
        function get user by given name

        :param: name: str name of user to return
        :return: User with the name of the given name, if not found return None
        """
        for user in self.users:
            if user.name == name:
                return user
        return None

    def finish_all_games(self):
        """
        function change all games with status ACTIVE to ENDED
        """
        for game in self.games_lst:
            if game.status == GameStatus.ACTIVE:
                game.status = GameStatus.ENDED

    def reset_vars(self):
        """
        function init attributes readyPlayers, ready_thread to None and kill_server to False
        """
        self.readyPlayers = [None, None]
        self.ready_thread = None
        self.kill_server = False


class Game_handler_locker:
    """
    Class to keep 'ServerGamesHandler' object and manage access to by other threads
    """
    def __init__(self):
        self.game_handler = None

    def set_game_handler(self, game_handler):
        self.game_handler = game_handler

    def create_game_handler(self):
        self.game_handler = ServerGamesHandler()

    @property
    def get_game_handler(self):
        return self.game_handler

def save_data_to_file(game_handler, file_name=FILE_NAME):
    """
    Func save 'ServerGamesHandler' to file using pickle
    """
    with open(file_name, 'wb') as f:
        pickle.dump(game_handler, f)


def load_data_from_file(file_name=FILE_NAME) -> ServerGamesHandler:
    """
    Func load 'ServerGamesHandler' data from file using pickle
    :return: ServerGamesHandler object with data loaded from file
    """
    with open(file_name, 'rb') as f:
        game_handler = pickle.load(f)
    return game_handler


def generate_default_tiles(height: int, width: int, ship_name_default=DEFAULT_SHIP_NAME,
                           bool_shot_default=DEFAULT_BOOL_SHOT) -> list:
    """
    Function generates a list of height x width tiles. The list will contain list
    ('shipName', boolShot) set to their (default_value).

    :param: height: set the height of board matrix
    :param: width: set the width of board matrix
    :param: ship_name_default: which tells what the value to set to as ship name
    :param: bool_shot_default: which tells what the value to set to as shot value

    :returns: list[][] 2D matrix of board, every element is tuple('shipName', boolShot)
    """
    default_tiles = [[[ship_name_default, bool_shot_default] for _ in range(width)] for _ in range(height)]
    return default_tiles


def check_revealed_tile(board, tile):
    """
    Function checks if a tile location contains a ship piece.

    :param: board: the tiled board either a ship piece or none
    :param: tile: location of tile
    :returns: True if ship piece exists at tile location
    """
    if board[tile[0]][tile[1]][0] is None:
        return False
    return True


def check_for_win(board):
    """
    Function checks if the current board state is a winning state.

    :param: board: the board which contains the ship pieces
    :returns: True if all the ships are revealed
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

    :param: board: list of board tiles
    :returns: the 2 lists of markers with number of ship pieces in each row (xmarkers)
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

    :param: board: list of board tiles
    :param: ships: list of ships to place on board
    :returns: list of board tiles with ships placed on certain tiles
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

    :param: board: list of board tiles
    :param: xPos: x-coordinate of first ship piece
    :param: yPos: y-coordinate of first ship piece
    :param: isHorizontal: True if ship is horizontal
    :param: length: length of ship
    :returns: tuple True if ship position is valid and list ship coordinates
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
    Function checks if a ship has adjacent ships

    :param: board -> list of board tiles
    :param: xPos: x-coordinate of first ship piece
    :param: yPos: y-coordinate of first ship piece
    :param: ship: the ship being checked for adjacency
    :returns: true if there are adjacent ships and false if there are no adjacent ships
    """
    for x in range(x_pos - 1, x_pos + 2):
        for y in range(y_pos - 1, y_pos + 2):
            if (x in range(10)) and (y in range(10)) and \
                    (board[x][y][0] not in (ship, None)):
                return True
    return False

