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
    """

    Function for receiving data from the socket in json form.

    sock -> the socket object to recive data from

    return dictionary containing the data

    """
    recv_data = sock.recv(1024)
    decoded_data = str(json.loads(bytes(recv_data).decode()))
    return decoded_data


def send_data(data, sock):
    """

        Function for sending data from the socket in json form.

        sock -> the socket object to send data from

        data -> the data that should be sent

        """
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
def run_game(host, port, elem_dict):
    server_addr = (host, port)
    sock = set_socket(server_addr)
    run = True
    try:
        # get board
        # my_board = receive_data(sock)
        my_board = generate_default_tiles(10, 10)  # for test
        # add ships to board
        # send_data(ships,sock)
        ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
                      'destroyer3', 'submarine1', 'submarine2', 'submarine3',
                      'submarine4']  # List of the ships available
        my_board = add_ships_to_board(my_board, ship_objs)  # call add_ships_to_board to add the list of ships to the main_board
        mousex, mousey = 0, 0  # location of mouse
        counter = []  # counter to track number of shots fired
        xmarkers, ymarkers = set_markers(my_board)  # The numerical markers on each side of the board

        elem_dict["DISPLAYSURF"] = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE)

        while run:
            init_elements(counter, elem_dict)
            # Draw the tiles onto the board and their respective markers

            draw_board(my_board, elem_dict, False)
            draw_markers(xmarkers, ymarkers, elem_dict)
            pygame.display.update()

            mouse_clicked = False
            run = check_for_quit()

            # Set the title in the menu bar to 'Battleship'
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    window_W = event.w
                    window_H = event.h
                    DISPLAYSURF = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == MOUSEBUTTONUP:
                    if elem_dict["HELP_RECT"].collidepoint(event.pos):  # if the help button is clicked on
                        elem_dict["DISPLAYSURF"].fill(BGCOLOR)
                        show_help_screen(elem_dict)  # Show the help screen
                    elif elem_dict["NEW_RECT"].collidepoint(event.pos):  # if the new game button is clicked on
                        run_game('127.0.0.1', 1233, elem_dict)  # goto main, which resets the game
                    else:  # otherwise
                        mousex, mousey = event.pos  # set mouse positions to the new position
                        mouse_clicked = True  # mouse is clicked but not on a button
                elif event.type == MOUSEMOTION:  # Detected mouse motion
                    mousex, mousey = event.pos  # set mouse positions to the new position

            # Check if the mouse is clicked at a position with a ship piece
            tilex, tiley = get_tile_at_pixel(mousex, mousey)


            if tilex != None and tiley != None:
                if not my_board[tilex][tiley][1]:  # if the tile the mouse is on is not revealed
                    draw_highlight_tile(tilex, tiley, elem_dict)  # draws the hovering highlight over the tile
                if not my_board[tilex][tiley][1] and mouse_clicked:  # if the mouse is clicked on the not revealed tile
                    reveal_tile_animation(my_board, [(tilex, tiley)], elem_dict)
                    my_board[tilex][tiley][1] = True  # set the tile to now be revealed
                    if check_revealed_tile(my_board, (tilex, tiley)):  # if the clicked position contains a ship piece
                        left, top = left_top_coords_tile(tilex, tiley)
                        # blowup_animation((left, top))
                        if check_for_win(my_board):  # check for a win
                            counter.append((tilex, tiley))
                            return len(counter)  # return the amount of shots taken
                    counter.append((tilex, tiley))


    finally:
        print("socket closed")
        sock.close()























elem_dict = {"DISPLAYSURF": None, "FPSCLOCK": None, "BASICFONT": None, "HELP_SURF": None, "HELP_RECT": None, "NEW_SURF": None, \
    "NEW_RECT": None, "SHOTS_SURF": None, "SHOTS_RECT": None, "BIGFONT": None, "COUNTER_SURF": None, \
    "COUNTER_RECT": None, "HBUTTON_SURF": None, "EXPLOSION_IMAGES": None}
elem_dict = set_window(elem_dict)

run_game('127.0.0.1', 1233, elem_dict)

