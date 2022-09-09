import selectors
import socket
import time
import pygame
import shared
import types
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
import client_service as cs
import logging

BOARD_SIZE = 10
TILE_WIDTH = 4
TILE_HEIGHT = 2
BUTTON_WIDTH = 10
BUTTON_HEIGHT = 1

BLACK = "#000000"
GREEN = "#33FF33"
YELLOW = "#FFFF00"
BLUE = "#0080FF"
RED = "#FF0000"
GREY = "#C0C0C0"

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]


def set_socket(server_addr):
    """
        this function is used to create the socket
        :param server_addr: Tuple that contains the ip address and port of the server

        :return: socket
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.settimeout(200)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        msg_total=sum(len(m) for m in messages),
        recv_total=0,
        messages=messages.copy(),
        outb=b"",
    )
    sel.register(sock, events, data=data)
    return sock


class client_window(tk.Tk):
    """
    client_window represents a client with it's screen and data
    """

    def __init__(self, server_addr):
        """
        init of a client
        """
        super().__init__()
        # some screen settings
        self.attributes("-topmost", True)
        self.title('Battleship')
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.font = Font(family='Arial', size=14, weight='normal')

        # Main frame so button be at middle under the boards
        self.main_frame = Frame(self, padx=5, pady=5)
        self.main_frame.pack(side=TOP)
        # Makes the frame for each side so player label will always be in the center of board no matter if we resize
        self.left_frame = Frame(self.main_frame, padx=5, pady=5)
        self.left_frame.pack(side=LEFT, padx=25, pady=10)
        self.right_frame = Frame(self.main_frame, padx=5, pady=5)
        self.right_frame.pack(side=RIGHT, padx=25, pady=10)

        # create the frames for the players boards
        self.myframe = Frame(self.right_frame, padx=5, pady=5)
        self.myframe.pack(side=BOTTOM, padx=0, pady=0)
        self.opponent_frame = Frame(self.left_frame, padx=5, pady=5)
        self.opponent_frame.pack(side=BOTTOM, padx=0, pady=0)

        # create the boards on the display by using buttons
        self.create_boards()

        self.game = cs.ClientGamesHandler()
        self.sock = set_socket(server_addr)
        self.game_ended = False
        cs.start_new_game(self.game, self.sock, logging, self)

        self.update_colors()
        pygame.mixer.init()
        # make player board name labels
        self.my_name_label = Label(self.right_frame, text=self.game.get_my_name(), font=self.font)
        self.my_name_label.pack(side=TOP, pady=5, padx=200)
        self.opponent_name_label = Label(self.left_frame, text=self.game.get_opponent_name(), font=self.font)
        self.opponent_name_label.pack(side=TOP, pady=5, padx=200)

        # new game button
        self.new_game_button = Button(self, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text="New Game", font=self.font,
                                      bg=GREY, command = self.new_game)
        self.new_game_button.pack(side=BOTTOM, padx=25, pady=20)

    def change_name_lbl(self, won=False):
        if won:
            self.my_name_label.config(text=self.game.get_my_name() + " Has Won!")
        else:
            self.my_name_label.config(text=self.game.get_my_name())
            self.opponent_name_label.config(text=self.game.get_opponent_name())

    def new_game(self):
        """
        reinstate the state of the buttons on the opponent board to work and send the server that we want to start a new
        game and get the new boards
        """
        if self.game_ended:
            self.enable_opponent_board_button()
        cs.start_new_game(self.game, self.sock, logging, self, quit=not self.game_ended)
        self.game_ended = False
        self.update_colors()

    def enable_opponent_board_button(self):
        """ reinstate the state of the buttons on the opponent board to work """
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.opponent_frame.grid_slaves(row=i, column=j)[0].config(state="normal")

    def disable_opponent_board_button(self):
        """ disable the state of the buttons on the opponent board so they wont work """
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.opponent_frame.grid_slaves(row=i, column=j)[0].config(state="disable")

    def create_boards(self):
        """
        this function creates the buttons that serve as tile in the playing board, the opponent playing board is
        disabled so the buttons cant be pressed
        """
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                button = Button(self.opponent_frame, width=TILE_WIDTH, height=TILE_HEIGHT)
                button.bind("<Button-1>", lambda temp=0, x=row, y=col: self.click(x, y))
                button.grid(row=row, column=col)

                button_opponent = Button(self.myframe, width=TILE_WIDTH, height=TILE_HEIGHT, state="disable")
                button_opponent.grid(row=row, column=col, sticky="nsew")

    def update_colors(self):
        """
            this function updates the board colors according to the ships state and the player who is currently playing
        """

        my_board = self.game.get_my_board()
        board_opponent = self.game.get_board_of_opponent()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if my_board[i][j][0]:  # if there is a ship in this tile
                    if my_board[i][j][1]:  # the ship was hit
                        self.myframe.grid_slaves(row=i, column=j)[0].configure(bg=RED)
                    else:
                        self.myframe.grid_slaves(row=i, column=j)[0].configure(bg=GREEN)
                else:
                    self.myframe.grid_slaves(row=i, column=j)[0].configure(bg=BLUE)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board_opponent[i][j][1]:  # if there is a ship in this tile and the ship was hit
                    if board_opponent[i][j][0]:
                        self.opponent_frame.grid_slaves(row=i, column=j)[0].configure(bg=RED)
                    else:
                        self.opponent_frame.grid_slaves(row=i, column=j)[0].configure(bg=BLACK)
                else:
                    self.opponent_frame.grid_slaves(row=i, column=j)[0].configure(bg=BLUE)

    def click(self, row, col):
        """
            Function that do all the necessary action upon clicking a tile on the board
            :param row: int; x position of tile
            :param col: int; y position of tile
        """
        if self.game.get_board_of_opponent()[row][col][1]:
            pass
        else:
            time.sleep(0.2)
            shared.send_message(self.sock, {"Action": "attack", "Hitted_player": self.game.opponent_number(),
                                            "Location": [row, col]}, logging)
            self.game.hit_on_board(row, col)  # turn opponent board on position to revealed
            cs.operation_mapper(game=self.game, received_data=shared.receive_message(self.sock, logging),
                                sock=self.sock,
                                logger=logging, client_win=self)

    def on_closing(self):
        """ Function that do all the necessary action upon closing the window"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            data_dict = dict({"Action": "close_connection"})
            shared.send_message(self.sock, data_dict, logging)
            self.sock.close()
            logging.info("socket closed")
            self.destroy()


def start_client_gui():
    """function that start the client gui and connect to the server"""
    temp = client_window(('127.0.0.1', 1233))
    temp.mainloop()
