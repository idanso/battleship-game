import random, sys
import logging
import pygame
from shared import *

# Set variables, like screen width and height
#### Globals ####
BOARD_SIZE = 10


class ClientGamesHandler:

    def __init__(self):
        self.players_board = [None, None]
        self.players_name = [None, None]
        self.turn_of_player = random.randint(0, 1)
        self.last_attack = None

    def set_boards(self, board_1, board_2):
        """
            a function that set the two players board
            :param board_1: List; board of player 1
            :param board_2: List; board of player 2
        """
        self.players_board[0] = board_1
        self.players_board[1] = board_2

    def set_names(self, player_1_name, player_2_name):
        """
            a function that set the two players board
            :param player_1_name: String; name of player 1
            :param player_2_name: String; name of player 2
        """
        self.players_name[0] = player_1_name
        self.players_name[1] = player_2_name

    def hit_on_board(self, x, y):
        """
        a function that keep track of the last attack on the(x,y) position and make the necessary changes to the
        board and change the player turn

        :param x: int; x position of tile
        :param y: int; y position of tile
        """
        self.last_attack = [x, y]
        self.get_board_of_opponent()[x][y][1] = True

    def opponent_number(self):
        """
            :return: int; the number of the opponent
        """
        if self.turn_of_player == 0:
            return 1
        else:
            return 0

    def get_board_of_opponent(self):
        """
            :return: List; the board of the opponent
        """
        return self.players_board[self.turn_of_player - 1]

    def get_opponent_name(self):
        """
            :return: String; the name of the opponent
        """
        return self.players_name[self.turn_of_player - 1]

    def get_my_name(self):
        """
            :return: String; the name of the current player
        """
        return self.players_name[self.turn_of_player]

    def get_my_board(self):
        """
            :return: List; the board of the opponent
        """
        return self.players_board[self.turn_of_player]

    def get_if_opponent_reveled_tile(self, tile):
        """
            a function that check if the tile was already revealed on the opponent board

            :return: Boolean; if the tile was hit
        """
        return self.get_board_of_opponent()[tile[0]][tile[1]][1]

    def change_turn(self):
        """
            a function that change which player turn is it
        """
        if self.turn_of_player == 0:
            self.turn_of_player = 1
        else:
            self.turn_of_player = 0


def operation_mapper(game: ClientGamesHandler, received_data, logger, client_win=None, sock=None):
    """
    this function is used to map the different actions that were received from the server with there corresponding actions

    :param client_win: of type client_window, contain the tkinter display and the elements it needs to work
    :param game: of type ClientGamesHandler, is used to keep up with important things involving the game like board, player turn and
    etc...
    :param received_data: Dict that was received from the server
    :param sock: Socket object used to send data to the server
    :param logger: the logger object
    """

    if received_data["Action"] == "start_game":
        game.set_boards(received_data["Board_1"], received_data["Board_2"])
        if received_data["Restart"]:
            client_win.game_ended = False
        else:  # new game
            game.set_names(received_data["Players"][0], received_data["Players"][1])

    elif received_data["Action"] == "hit":
        # TODO: fix sound files maybe use pygame
        if received_data["Success"]:
            pygame.mixer.music.load('soundFiles\hit-water.wav')
            pygame.mixer.music.play(loops=0)
        else:
            pygame.mixer.music.load('soundFiles\sea-explosion.wav')
            pygame.mixer.music.play(loops=0)

        if received_data["Finished"]:
            client_win.game_ended = True
            client_win.disable_opponent_board_button()
            client_win.my_name_label.configure(text=game.get_my_name() + " Has Won!")

        else:  # if game didn't finished swap turns and update boards
            game.change_turn()
            client_win.my_name_label.configure(text=game.get_my_name())
            client_win.opponent_name_label.configure(text=game.get_opponent_name())
            client_win.update_colors()

            # TODO: show result screen

    elif received_data["Action"] == "ok":
        pass

    else:
        print("unknown Action: %s", received_data["Action"])
        # TODO: consider throwing error


def start_new_game(game: ClientGamesHandler, sock, logger, client_win, quit=False):
    """
    this function is used to send to the server that the client is starting a new game and receive from the server
    the new boards

    :param game: type ClientGamesHandler, is used to keep up with important things involving the game like board, player
    turn and etc...
    :param client_win: of type client_window, contain the tkinter display and the elements it needs to work
    :param logger: the logger object
    :param sock: Socket object used to send data to the server
    :param quit: boolean to tell the server which player pressed the new game button (Quit = None mean we just started the first game)
    """

    data = {"Action": "start_game"}
    if quit:
        data["Quit"] = game.turn_of_player
    else:
        data["Quit"] = None
        data["Players"] = game.players_name
    send_message(sock, data, logger)
    # get board
    recv_data = receive_message(sock, logger)
    operation_mapper(game=game, received_data=recv_data, logger=logger, client_win=client_win)
