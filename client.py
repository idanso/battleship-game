import json
import sys
import socket
import selectors
import types
from time import sleep
import pygame
from client_service import *
from pygame.locals import *
from shared import *

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]


def check_events_pygame(elem_dict, mousex, mousey):
    # Set the title in the menu bar to 'Battleship'
    mouse_clicked = False
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            elem_dict["DISPLAYSURF"] = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        if event.type == MOUSEBUTTONUP:
            if elem_dict["HELP_RECT"].collidepoint(event.pos):  # if the help button is clicked on
                elem_dict["DISPLAYSURF"].fill(BGCOLOR)
                show_help_screen(elem_dict)  # Show the help screen
            elif elem_dict["NEW_RECT"].collidepoint(event.pos):  # if the new game button is clicked on
                pass
                #todo: new game button
                #run_game('127.0.0.1', 1233, elem_dict)  # goto main, which resets the game
            else:  # otherwise
                mousex, mousey = event.pos  # set mouse positions to the new position
                mouse_clicked = True  # mouse is clicked but not on a button
        elif event.type == MOUSEMOTION:  # Detected mouse motion
            mousex, mousey = event.pos  # set mouse positions to the new position
    return mousex, mousey, mouse_clicked


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


def set_socket(server_addr):
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


# start_connections('127.0.0.1', 1233)
def run_game(host, port, elem_dict):
    server_addr = (host, port)
    sock = set_socket(server_addr)
    run = True
    try:
        game = ClientGamesHandler()
        send_message(sock, {"Action": "start_game"})
        # get board
        recv_data = receive_message(sock)
        game.set_boards(recv_data["Board_1"], recv_data["Board_2"])
        #operation_mapper(elem_dict, game, recv_data)
        mousex, mousey = 0, 0  # location of mouse
        counter = []  # counter to track number of shots fired
        xmarkers, ymarkers = set_markers(
            game.get_board_of_opponent())  # The numerical markers on each side of the board

        elem_dict["DISPLAYSURF"] = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE)

        while run:
            init_elements(counter, elem_dict)
            # Draw the tiles onto the board and their respective markers
            draw_board(game.get_board_of_opponent(), elem_dict, False)
            draw_markers(xmarkers, ymarkers, elem_dict)
            pygame.display.update()

            run = check_for_quit()

            mousex, mousey, mouse_clicked = check_events_pygame(elem_dict, mousex, mousey)
            # Check if the mouse is clicked at a position with a ship piece
            tilex, tiley = get_tile_at_pixel(mousex, mousey)

            if tilex is not None and tiley is not None:
                if not game.get_if_opponent_reveled_tile([tilex, tiley]):  # if the tile the mouse is on is not revealed
                    draw_highlight_tile(tilex, tiley, elem_dict)  # draws the hovering highlight over the tile
                if not game.get_if_opponent_reveled_tile(
                        [tilex, tiley]) and mouse_clicked:  # if the mouse is clicked on the not revealed tile
                    send_message(sock, {"Action": "attack", "Hitted_player": game.opponent_number(),
                                        "Location": [tilex, tiley]})
                    game.hit_on_board(tilex, tiley)  # turn opponent board on position to revealed
                    operation_mapper(elem_dict, game, receive_message(sock))
                    counter.append((tilex, tiley))

    finally:
        data_dict = dict({"Action": "close_connection"})
        send_message(data_dict)
        print("socket closed")
        sock.close()


# todo delete this comment when socket will work

# my_board = generate_default_tiles(10, 10)  # for test
# # add ships to board
# # send_data(ships,sock)
# ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
#              'destroyer3', 'submarine1', 'submarine2', 'submarine3',
#              'submarine4']  # List of the ships available
# my_board = add_ships_to_board(my_board, ship_objs)  # call add_ships_to_board to add the list of ships to the main_board


elem_dict = {"DISPLAYSURF": None, "FPSCLOCK": None, "BASICFONT": None, "HELP_SURF": None, "HELP_RECT": None,
             "NEW_SURF": None, \
             "NEW_RECT": None, "SHOTS_SURF": None, "SHOTS_RECT": None, "BIGFONT": None, "COUNTER_SURF": None, \
             "COUNTER_RECT": None, "HBUTTON_SURF": None, "EXPLOSION_IMAGES": None}
elem_dict = set_window(elem_dict)

run_game('127.0.0.1', 1233, elem_dict)
