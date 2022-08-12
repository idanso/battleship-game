import json
import sys
import socket
import selectors
import types
from time import sleep

import pygame
from client_service import *
from server_service import *

from pygame.locals import *

DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE)
sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]


# def start_connections(host, port):
#     server_addr = (host, port)
#     #change order of while and try catch to get socket out?
#     while True:
#         try:
#             print(f"Starting connection to {server_addr}")
#             sock = set_socket(server_addr)
#             #get board
#             #my_board = receive_data(sock)
#             my_board = generate_default_tiles(10,10)#for test
#             #add ships to board
#             #send_data(ships,sock)
#             ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
#                          'destroyer3', 'submarine1', 'submarine2', 'submarine3',
#                          'submarine4']  # List of the ships available
#             my_board = add_ships_to_board(my_board,ship_objs)  # call add_ships_to_board to add the list of ships to the main_board
#             mousex, mousey = 0, 0  # location of mouse
#             counter = []  # counter to track number of shots fired
#             xmarkers, ymarkers = set_markers(my_board)  # The numerical markers on each side of the board
#
#
#             send_data = json.dumps({"name": usr_input})
#             sock.send(send_data.encode())
#             recv_data = sock.recv(1024)  # Should be ready to read
#
#             print("data recived from server: " + str(json.loads(bytes(recv_data).decode())))
#             sleep(1000)
#         finally:
#             print("socket closed")
#             sock.close()

def receive_data(sock):#made def incase we want to make difrent situations
    recv_data = sock.recv(1024)
    decoded_data = str(json.loads(bytes(recv_data).decode()))
    return decoded_data


def send_data(data, sock):
    send_data = json.dumps(data)
    sock.send(send_data.encode())

def set_socket(server_addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.settimeout(5)
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

# start_connections('127.0.0.1', 1233)
def run_game(host, port):
    server_addr = (host, port)
    sock = set_socket(server_addr)
    run = True
    try:
        set_window()
        # get board
        # my_board = receive_data(sock)
        my_board = generate_default_tiles(10, 10)  # for test
        # add ships to board
        # send_data(ships,sock)
        # ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
        #              'destroyer3', 'submarine1', 'submarine2', 'submarine3',
        #              'submarine4']  # List of the ships available
        # my_board = add_ships_to_board(my_board,
        #                               ship_objs)  # call add_ships_to_board to add the list of ships to the main_board
        mousex, mousey = 0, 0  # location of mouse
        counter = []  # counter to track number of shots fired
        xmarkers, ymarkers = set_markers(my_board)  # The numerical markers on each side of the board


        while run:
                # server_addr = (host, port)
                # sock_player1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # sock.setblocking(False)
                # sock_player2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # sock.setblocking(False)
                # counter display (it needs to be here in order to refresh it)
                COUNTER_SURF = BASICFONT.render(str(len(counter)), True, WHITE)
                COUNTER_RECT = SHOTS_SURF.get_rect()
                COUNTER_RECT.topleft = (WINDOWWIDTH - 680, WINDOWHEIGHT - 570)

                # Fill background
                DISPLAYSURF.fill(BGCOLOR)

                # draw the buttons
                DISPLAYSURF.blit(HELP_SURF, HELP_RECT)
                DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
                DISPLAYSURF.blit(SHOTS_SURF, SHOTS_RECT)
                DISPLAYSURF.blit(COUNTER_SURF, COUNTER_RECT)

                # Draw the tiles onto the board and their respective markers
                draw_board(my_board)
                draw_markers(xmarkers, ymarkers)

                mouse_clicked = False


                # Set the title in the menu bar to 'Battleship'
                for event in pygame.event.get():
                    if event.type == pygame.VIDEORESIZE:
                        window_W = event.w
                        window_H = event.h
                        DISPLAYSURF = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
    finally:
        print("socket closed")
        sock.close()

def set_window():
    window_H = WINDOWHEIGHT
    window_W = WINDOWWIDTH

    global DISPLAYSURF, FPSCLOCK, BASICFONT, HELP_SURF, HELP_RECT, NEW_SURF, \
        NEW_RECT, SHOTS_SURF, SHOTS_RECT, BIGFONT, COUNTER_SURF, \
        COUNTER_RECT, HBUTTON_SURF, EXPLOSION_IMAGES
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    # Fonts used by the game

    BASICFONT = pygame.font.Font('freesansbold.ttf', 20)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 50)

    # Create and label the buttons
    HELP_SURF = BASICFONT.render("HELP", True, WHITE)
    HELP_RECT = HELP_SURF.get_rect()
    HELP_RECT.topleft = (window_W - 180, window_H - 350)
    NEW_SURF = BASICFONT.render("NEW GAME", True, WHITE)
    NEW_RECT = NEW_SURF.get_rect()
    NEW_RECT.topleft = (window_W - 200, window_H - 200)

    # The 'Shots:' label at the top
    SHOTS_SURF = BASICFONT.render("Shots: ", True, WHITE)
    SHOTS_RECT = SHOTS_SURF.get_rect()
    SHOTS_RECT.topleft = (window_W - 750, window_H - 570)

    # Load the explosion graphics from the /img folder
    # EXPLOSION_IMAGES = [
    #     pygame.image.load("img/blowup1.png"), pygame.image.load("img/blowup2.png"),
    #     pygame.image.load("img/blowup3.png"), pygame.image.load("img/blowup4.png"),
    #     pygame.image.load("img/blowup5.png"), pygame.image.load("img/blowup6.png")]

set_window()
run_game('127.0.0.1', 1233)
