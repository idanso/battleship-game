import json
import sys
import socket
import selectors
import types
from time import sleep
import pygame
# from client_service import *
from server_service import *
from pygame.locals import *


# Set variables, like screen width and height
# globals
FPS = 30 #Determines the number of frames per second
REVEALSPEED = 8 #Determines the speed at which the squares reveals after being clicked
WINDOWWIDTH = 800 #Width of game window
WINDOWHEIGHT = 600 #Height of game window
TILESIZE = 40 #Size of the squares in each grid(tile)
MARKERSIZE = 40 #Size of the box which contatins the number that indicates how many ships in this row/col
BUTTONHEIGHT = 20 #Height of a standard button
BUTTONWIDTH = 40 #Width of a standard button
TEXT_HEIGHT = 25 #Size of the text
TEXT_LEFT_POSN = 10 #Where the text will be positioned
BOARDWIDTH = 10 #Number of grids horizontally
BOARDHEIGHT = 10 #Number of grids vertically
DISPLAYWIDTH = 200 #Width of the game board
EXPLOSIONSPEED = 10 #How fast the explosion graphics will play

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * TILESIZE) - DISPLAYWIDTH - MARKERSIZE) / 2) #x-position of the top left corner of board
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * TILESIZE) - MARKERSIZE) / 2) #y-position of the top left corner of board

#Colours which will be used by the game
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (  0, 204,   0)
GRAY    = ( 60,  60,  60)
BLUE    = (  0,  50, 255)
YELLOW  = (255, 255,   0)
DARKGRAY =( 40,  40,  40)

#Determine what to colour each element of the game
BGCOLOR = GRAY
BUTTONCOLOR = GREEN
TEXTCOLOR = WHITE
TILECOLOR = GREEN
BORDERCOLOR = BLUE
TEXTSHADOWCOLOR = BLUE
SHIPCOLOR = YELLOW
HIGHLIGHTCOLOR = BLUE

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

                DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE)

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

























def blowup_animation(coord):
    """
    Function creates the explosition played if a ship is shot.

    coord -> tuple of tile coords to apply the blowup animation
    """
    for image in EXPLOSION_IMAGES:  # go through the list of images in the list of pictures and play them in sequence
        # Determine the location and size to display the image
        image = pygame.transform.scale(image, (TILESIZE + 10, TILESIZE + 10))
        DISPLAYSURF.blit(image, coord)
        pygame.display.flip()
        FPSCLOCK.tick(EXPLOSIONSPEED)  # Determine the delay to play the image with


def draw_tile_covers(board, tile, coverage):
    """
    Function draws the tiles according to a set of variables.

    board -> list; of board tiles
    tile -> tuple; of tile coords to reveal
    coverage -> int; amount of the tile that is covered
    """
    left, top = left_top_coords_tile(tile[0][0], tile[0][1])
    if check_revealed_tile(board, tile):
        pygame.draw.rect(DISPLAYSURF, SHIPCOLOR, (left, top, TILESIZE,
                                                  TILESIZE))
    else:
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, TILESIZE,
                                                TILESIZE))
    if coverage > 0:
        pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left, top, coverage,
                                                  TILESIZE))

    pygame.display.update()
    FPSCLOCK.tick(FPS)


def reveal_tile_animation(board, tile_to_reveal):
    """
    Function creates an animation which plays when the mouse is clicked on a tile, and whatever is
    behind the tile needs to be revealed.

    board -> list of board tile tuples ('shipName', boolShot)
    tile_to_reveal -> tuple of tile coords to apply the reveal animation to
    """
    for coverage in range(TILESIZE, (-REVEALSPEED) - 1, -REVEALSPEED):  # Plays animation based on reveal speed
        draw_tile_covers(board, tile_to_reveal, coverage)


def draw_board(board):
    """
    Function draws the game board.

    board -> list of board tiles
    revealed -> list of revealed tiles
    """
    # draws the grids depending on its state
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            left, top = left_top_coords_tile(tilex, tiley)
            if not board[tilex][tiley][1]:
                pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left, top, TILESIZE,
                                                          TILESIZE))
            else:
                if board[tilex][tiley][0] is not None:
                    pygame.draw.rect(DISPLAYSURF, SHIPCOLOR, (left, top,
                                                              TILESIZE, TILESIZE))
                else:
                    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top,
                                                            TILESIZE, TILESIZE))
    # draws the horizontal lines
    for x in range(0, (BOARDWIDTH + 1) * TILESIZE, TILESIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x + XMARGIN + MARKERSIZE,
                                                 YMARGIN + MARKERSIZE), (x + XMARGIN + MARKERSIZE,
                                                                         WINDOWHEIGHT - YMARGIN))
    # draws the vertical lines
    for y in range(0, (BOARDHEIGHT + 1) * TILESIZE, TILESIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (XMARGIN + MARKERSIZE, y +
                                                 YMARGIN + MARKERSIZE), (WINDOWWIDTH - (DISPLAYWIDTH + MARKERSIZE *
                                                                                        2), y + YMARGIN + MARKERSIZE))

def check_for_quit():
    """
    Function checks if the user has attempted to quit the game.
    """
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()


def set_markers(board):
    """
    Function creates the lists of the markers to the side of the game board which indicates
    the number of ship pieces in each row and column.

    board: list of board tiles
    returns the 2 lists of markers with number of ship pieces in each row (xmarkers)
        and column (ymarkers)
    """
    xmarkers = [0 for i in range(BOARDWIDTH)]
    ymarkers = [0 for i in range(BOARDHEIGHT)]
    # Loop through the tiles
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            if board[tilex][tiley][0] is not None:  # if the tile is a ship piece, then increment the markers
                xmarkers[tilex] += 1
                ymarkers[tiley] += 1

    return xmarkers, ymarkers

def draw_markers(xlist, ylist):
    """
    Function draws the two list of markers to the side of the board.

    xlist -> list of row markers
    ylist -> list of column markers
    """
    for i in range(len(xlist)): #Draw the x-marker list
        left = i * MARKERSIZE + XMARGIN + MARKERSIZE + (TILESIZE / 3)
        top = YMARGIN
        marker_surf, marker_rect = make_text_objs(str(xlist[i]),
                                                    BASICFONT, TEXTCOLOR)
        marker_rect.topleft = (left, top)
        DISPLAYSURF.blit(marker_surf, marker_rect)
    for i in range(len(ylist)): #Draw the y-marker list
        left = XMARGIN
        top = i * MARKERSIZE + YMARGIN + MARKERSIZE + (TILESIZE / 3)
        marker_surf, marker_rect = make_text_objs(str(ylist[i]),
                                                    BASICFONT, TEXTCOLOR)
        marker_rect.topleft = (left, top)
        DISPLAYSURF.blit(marker_surf, marker_rect)


def left_top_coords_tile(tilex, tiley):
    """
    Function calculates and returns the pixel of the tile in the top left corner

    tilex -> int; x position of tile
    tiley -> int; y position of tile
    returns tuple (int, int) which indicates top-left pixel coordinates of tile
    """
    left = tilex * TILESIZE + XMARGIN + MARKERSIZE
    top = tiley * TILESIZE + YMARGIN + MARKERSIZE
    return (left, top)


def get_tile_at_pixel(x, y):
    """
    Function finds the corresponding tile coordinates of pixel at top left, defaults to (None, None) given a coordinate.

    x -> int; x position of pixel
    y -> int; y position of pixel
    returns tuple (tilex, tiley)
    """
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            left, top = left_top_coords_tile(tilex, tiley)
            tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tile_rect.collidepoint(x, y):
                return (tilex, tiley)
    return (None, None)


def draw_highlight_tile(tilex, tiley):
    """
    Function draws the hovering highlight over the tile.

    tilex -> int; x position of tile
    tiley -> int; y position of tile
    """
    left, top = left_top_coords_tile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR,
                     (left, top, TILESIZE, TILESIZE), 4)


def show_help_screen():
    """
    Function display a help screen until any button is pressed.
    """
    line1_surf, line1_rect = make_text_objs('Press a key to return to the game',
                                            BASICFONT, TEXTCOLOR)
    line1_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT)
    DISPLAYSURF.blit(line1_surf, line1_rect)

    line2_surf, line2_rect = make_text_objs(
        'This is a battleship puzzle game. Your objective is ' \
        'to sink all the ships in as few', BASICFONT, TEXTCOLOR)
    line2_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 3)
    DISPLAYSURF.blit(line2_surf, line2_rect)

    line3_surf, line3_rect = make_text_objs('shots as possible. The markers on' \
                                            ' the edges of the game board tell you how', BASICFONT, TEXTCOLOR)
    line3_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 4)
    DISPLAYSURF.blit(line3_surf, line3_rect)

    line4_surf, line4_rect = make_text_objs('many ship pieces are in each' \
                                            ' column and row. To reset your game click on', BASICFONT, TEXTCOLOR)
    line4_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 5)
    DISPLAYSURF.blit(line4_surf, line4_rect)

    line5_surf, line5_rect = make_text_objs('the "New Game" button.',
                                            BASICFONT, TEXTCOLOR)
    line5_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 6)
    DISPLAYSURF.blit(line5_surf, line5_rect)

    while check_for_keypress() == None:  # Check if the user has pressed keys, if so go back to the game
        pygame.display.update()
        FPSCLOCK.tick()


def check_for_keypress():
    """
    Function checks for any key presses by pulling out all KEYDOWN and KEYUP events from queue.

    returns any KEYUP events, otherwise return None
    """
    for event in pygame.event.get([KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
        if event.type in (KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
            continue
        return event.key
    return None


def make_text_objs(text, font, color):
    """
    Function creates a text.

    text -> string; content of text
    font -> Font object; face of font
    color -> tuple of color (red, green blue); colour of text
    returns the surface object, rectangle object
    """
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def show_gameover_screen(shots_fired):
    """
    Function display a gameover screen when the user has successfully shot at every ship pieces.

    shots_fired -> the number of shots taken before game is over
    """
    DISPLAYSURF.fill(BGCOLOR)
    titleSurf, titleRect = make_text_objs('Congrats! Puzzle solved in:',
                                          BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs('Congrats! Puzzle solved in:',
                                          BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs(str(shots_fired) + ' shots',
                                          BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2 + 50))
    DISPLAYSURF.blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs(str(shots_fired) + ' shots',
                                          BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2 + 50) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = make_text_objs(
        'Press a key to try to beat that score.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while check_for_keypress() == None:  # Check if the user has pressed keys, if so start a new game
        pygame.display.update()
        FPSCLOCK.tick()





























set_window()
run_game('127.0.0.1', 1233)

