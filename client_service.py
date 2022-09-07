import random, sys, pygame
import logging
from shared import *
from playsound import playsound
from pygame.locals import *

#import board

# Set variables, like screen width and height
#### Globals ####
BOARD_SIZE = 10
DEFAULT_SHIP_NAME = None
DEFAULT_BOOL_SHOT = False

BOARD_WIDTH = 10  # Number of grids horizontally
BOARD_HEIGHT = 10  # Number of grids vertically

FPS = 30  # Determines the number of frames per second
REVEALSPEED = 8  # Determines the speed at which the squares reveals after being clicked
WINDOWWIDTH = 800  # Width of game window
WINDOWHEIGHT = 600  # Height of game window
TILESIZE = 40  # Size of the squares in each grid(tile)
MARKERSIZE = 40  # Size of the box which contatins the number that indicates how many ships in this row/col
BUTTONHEIGHT = 20  # Height of a standard button
BUTTONWIDTH = 40  # Width of a standard button
TEXT_HEIGHT = 25  # Size of the text
TEXT_LEFT_POSN = 10  # Where the text will be positioned
BOARDWIDTH = 10  # Number of grids horizontally
BOARDHEIGHT = 10  # Number of grids vertically
DISPLAYWIDTH = 200  # Width of the game board
EXPLOSIONSPEED = 10  # How fast the explosion graphics will play

XMARGIN = int((WINDOWWIDTH - (
            BOARDWIDTH * TILESIZE) - DISPLAYWIDTH - MARKERSIZE) / 2)  # x-position of the top left corner of board
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * TILESIZE) - MARKERSIZE) / 2)  # y-position of the top left corner of board

# Colours which will be used by the game
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 204, 0)
GRAY = (60, 60, 60)
BLUE = (0, 50, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)

# Determine what to colour each element of the game
BGCOLOR = GRAY
BUTTONCOLOR = GREEN
TEXTCOLOR = WHITE
TILECOLOR = GREEN
BORDERCOLOR = BLUE
TEXTSHADOWCOLOR = BLUE
SHIPCOLOR = YELLOW
HIGHLIGHTCOLOR = BLUE


def init_elements(counter: int, elem_dict):
    """
            do initialization to parameters involving pygame window that need to happen in every loop of the game
            :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes

            :return: elem_dict:Dict
    """

    # counter display (it needs to be here in order to refresh it)
    elem_dict["COUNTER_SURF"] = elem_dict["BASICFONT"].render(str(len(counter)), True, WHITE)
    elem_dict["COUNTER_RECT"] = elem_dict["SHOTS_SURF"].get_rect()
    elem_dict["COUNTER_RECT"].topleft = (WINDOWWIDTH - 680, WINDOWHEIGHT - 570)

    # Fill background
    elem_dict["DISPLAYSURF"].fill(BGCOLOR)

    # draw the buttons
    elem_dict["DISPLAYSURF"].blit(elem_dict["HELP_SURF"], elem_dict["HELP_RECT"])
    elem_dict["DISPLAYSURF"].blit(elem_dict["NEW_SURF"], elem_dict["NEW_RECT"])
    elem_dict["DISPLAYSURF"].blit(elem_dict["SHOTS_SURF"], elem_dict["SHOTS_RECT"])
    elem_dict["DISPLAYSURF"].blit(elem_dict["COUNTER_SURF"], elem_dict["COUNTER_RECT"])
    return elem_dict


def set_window(elem_dict):
    """
        do initialization to parameters involving pygame window that happens only once at start
        :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes

        :return: elem_dict:Dict

    """
    window_H = WINDOWHEIGHT
    window_W = WINDOWWIDTH

    pygame.init()

    elem_dict["FPSCLOCK"] = pygame.time.Clock()
    # Fonts used by the game

    elem_dict["BASICFONT"] = pygame.font.Font('freesansbold.ttf', 20)
    elem_dict["BIGFONT"] = pygame.font.Font('freesansbold.ttf', 50)

    # Create and label the buttons
    elem_dict["HELP_SURF"] = elem_dict["BASICFONT"].render("HELP", True, WHITE)
    elem_dict["HELP_RECT"] = elem_dict["HELP_SURF"].get_rect()
    elem_dict["HELP_RECT"].topleft = (window_W - 180, window_H - 350)
    elem_dict["NEW_SURF"] = elem_dict["BASICFONT"].render("NEW GAME", True, WHITE)
    elem_dict["NEW_RECT"] = elem_dict["NEW_SURF"].get_rect()
    elem_dict["NEW_RECT"].topleft = (window_W - 200, window_H - 200)

    # The 'Shots:' label at the top
    elem_dict["SHOTS_SURF"] = elem_dict["BASICFONT"].render("Shots: ", True, WHITE)
    elem_dict["SHOTS_RECT"] = elem_dict["SHOTS_SURF"].get_rect()
    elem_dict["SHOTS_RECT"].topleft = (window_W - 750, window_H - 570)

    # Load the explosion graphics from the /img folder
    elem_dict["EXPLOSION_IMAGES"] = [
        pygame.image.load("img/blowup1.png"), pygame.image.load("img/blowup2.png"),
        pygame.image.load("img/blowup3.png"), pygame.image.load("img/blowup4.png"),
        pygame.image.load("img/blowup5.png"), pygame.image.load("img/blowup6.png")]
    pygame.display.set_caption('Battleship')
    return elem_dict


def blowup_animation(coord, elem_dict):
    """
    Function creates the explosition played if a ship is shot.

    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes

    :param coord: tuple of tile coords to apply the blowup animation
    """
    for image in elem_dict[
        "EXPLOSION_IMAGES"]:  # go through the list of images in the list of pictures and play them in sequence
        # Determine the location and size to display the image
        image = pygame.transform.scale(image, (TILESIZE + 10, TILESIZE + 10))
        elem_dict["DISPLAYSURF"].blit(image, coord)
        pygame.display.flip()
        elem_dict["FPSCLOCK"].tick(EXPLOSIONSPEED)  # Determine the delay to play the image with


def draw_tile_covers(tile, coverage, elem_dict, hit= False):
    """
    Function draws the tiles according to a set of variables.

    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes
    :param tile: tuple; of tile coords to reveal
    :param coverage: int; amount of the tile that is covered
    :param hit: did the tile contained a ship that was hit
    """
    left, top = left_top_coords_tile(tile[0], tile[1])
    if hit:
        pygame.draw.rect(elem_dict["DISPLAYSURF"], SHIPCOLOR, (left, top, TILESIZE,
                                                               TILESIZE))
    else:
        pygame.draw.rect(elem_dict["DISPLAYSURF"], BGCOLOR, (left, top, TILESIZE,
                                                             TILESIZE))
    if coverage > 0:
        pygame.draw.rect(elem_dict["DISPLAYSURF"], TILECOLOR, (left, top, coverage,
                                                               TILESIZE))

    pygame.display.update()
    elem_dict["FPSCLOCK"].tick(FPS)


def reveal_tile_animation(tile_to_reveal, elem_dict, hit = False):
    """
    Function creates an animation which plays when the mouse is clicked on a tile, and whatever is
    behind the tile needs to be revealed.

    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes
    :param tile_to_reveal: tuple of tile coords to apply the reveal animation to
    :param hit: Boolean that indicate if the tile contained a ship that was hit

    """
    for coverage in range(TILESIZE, (-REVEALSPEED) - 1, -REVEALSPEED):  # Plays animation based on reveal speed
        draw_tile_covers(tile_to_reveal, coverage, elem_dict, hit)


def draw_board(board, elem_dict, my_board: bool):
    """
    Function draws the game board.

    :param board: list of board tiles
    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes
    :param my_board: Bool that indicates if we need to cover the ships that still wasn't revealed
    """
    # draws the grids depending on its state
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            left, top = left_top_coords_tile(tilex, tiley)
            if not board[tilex][tiley][1] and not my_board:
                pygame.draw.rect(elem_dict["DISPLAYSURF"], TILECOLOR, (left, top, TILESIZE,
                                                                       TILESIZE))
            else:
                if board[tilex][tiley][0] is not None:
                    pygame.draw.rect(elem_dict["DISPLAYSURF"], SHIPCOLOR, (left, top,
                                                                           TILESIZE, TILESIZE))
                else:
                    pygame.draw.rect(elem_dict["DISPLAYSURF"], BGCOLOR, (left, top,
                                                                         TILESIZE, TILESIZE))
    # draws the horizontal lines
    for x in range(0, (BOARDWIDTH + 1) * TILESIZE, TILESIZE):
        pygame.draw.line(elem_dict["DISPLAYSURF"], DARKGRAY, (x + XMARGIN + MARKERSIZE,
                                                              YMARGIN + MARKERSIZE), (x + XMARGIN + MARKERSIZE,
                                                                                      WINDOWHEIGHT - YMARGIN))
    # draws the vertical lines
    for y in range(0, (BOARDHEIGHT + 1) * TILESIZE, TILESIZE):
        pygame.draw.line(elem_dict["DISPLAYSURF"], DARKGRAY, (XMARGIN + MARKERSIZE, y +
                                                              YMARGIN + MARKERSIZE),
                         (WINDOWWIDTH - (DISPLAYWIDTH + MARKERSIZE *
                                         2), y + YMARGIN + MARKERSIZE))


def check_for_quit():
    """
    Function checks if the user has attempted to quit the game.

    :return: Boolean
    """
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()
        return False
    return True


def set_markers(board):
    """
    Function creates the lists of the markers to the side of the game board which indicates
    the number of ship pieces in each row and column.

    :param board: list of board tiles

    :return: 2 lists of markers with number of ship pieces in each row (xmarkers)
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


def draw_markers(xlist, ylist, elem_dict):
    """
    Function draws the two list of markers to the side of the board.

    :param xlist: list of row markers
    :param ylist: list of column markers
    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes

    """

    for i in range(len(xlist)):  # Draw the x-marker list
        left = i * MARKERSIZE + XMARGIN + MARKERSIZE + (TILESIZE / 3)
        top = YMARGIN
        marker_surf, marker_rect = make_text_objs(str(xlist[i]),
                                                  elem_dict["BASICFONT"], TEXTCOLOR)
        marker_rect.topleft = (left, top)
        elem_dict["DISPLAYSURF"].blit(marker_surf, marker_rect)
    for i in range(len(ylist)):  # Draw the y-marker list
        left = XMARGIN
        top = i * MARKERSIZE + YMARGIN + MARKERSIZE + (TILESIZE / 3)
        marker_surf, marker_rect = make_text_objs(str(ylist[i]),
                                                  elem_dict["BASICFONT"], TEXTCOLOR)
        marker_rect.topleft = (left, top)
        elem_dict["DISPLAYSURF"].blit(marker_surf, marker_rect)


def left_top_coords_tile(tilex, tiley):
    """
    Function calculates and returns the pixel of the tile in the top left corner

    :param tilex: int; x position of tile
    :param tiley: int; y position of tile

    :return: tuple (int, int) which indicates top-left pixel coordinates of tile
    """
    left = tilex * TILESIZE + XMARGIN + MARKERSIZE
    top = tiley * TILESIZE + YMARGIN + MARKERSIZE
    return (left, top)


def get_tile_at_pixel(x, y):
    """
    Function finds the corresponding tile coordinates of pixel at top left, defaults to (None, None) given a coordinate.

    :param x: int; x position of pixel
    :param y: int; y position of pixel

    :return: tuple (tilex, tiley)
    """
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            left, top = left_top_coords_tile(tilex, tiley)
            tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tile_rect.collidepoint(x, y):
                return (tilex, tiley)
    return (None, None)


def draw_highlight_tile(tilex, tiley, elem_dict):
    """
    Function draws the hovering highlight over the tile.

    :param tilex: int; x position of tile
    :param tiley: int; y position of tile
    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes
    """
    left, top = left_top_coords_tile(tilex, tiley)
    pygame.draw.rect(elem_dict["DISPLAYSURF"], HIGHLIGHTCOLOR,
                     (left, top, TILESIZE, TILESIZE), 4)


def show_help_screen(elem_dict):
    """
    Function display a help screen until any button is pressed.
    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes
    """
    line1_surf, line1_rect = make_text_objs('Press a key to return to the game',
                                            elem_dict["BASICFONT"], TEXTCOLOR)
    line1_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT)
    elem_dict["DISPLAYSURF"].blit(line1_surf, line1_rect)

    line2_surf, line2_rect = make_text_objs(
        'This is a battleship puzzle game. Your objective is ' \
        'to sink all the ships in as few', elem_dict["BASICFONT"], TEXTCOLOR)
    line2_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 3)
    elem_dict["DISPLAYSURF"].blit(line2_surf, line2_rect)

    line3_surf, line3_rect = make_text_objs('shots as possible. The markers on' \
                                            ' the edges of the game board tell you how', elem_dict["BASICFONT"],
                                            TEXTCOLOR)
    line3_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 4)
    elem_dict["DISPLAYSURF"].blit(line3_surf, line3_rect)

    line4_surf, line4_rect = make_text_objs('many ship pieces are in each' \
                                            ' column and row. To reset your game click on', elem_dict["BASICFONT"],
                                            TEXTCOLOR)
    line4_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 5)
    elem_dict["DISPLAYSURF"].blit(line4_surf, line4_rect)

    line5_surf, line5_rect = make_text_objs('the "New Game" button.',
                                            elem_dict["BASICFONT"], TEXTCOLOR)
    line5_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 6)
    elem_dict["DISPLAYSURF"].blit(line5_surf, line5_rect)

    while check_for_keypress() == None:  # Check if the user has pressed keys, if so go back to the game
        pygame.display.update()
        elem_dict["FPSCLOCK"].tick()


def check_for_keypress():
    """
    Function checks for any key presses by pulling out all KEYDOWN and KEYUP events from queue.

    :return: any KEYUP events, otherwise return None
    """
    for event in pygame.event.get([KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
        if event.type in (KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
            continue
        return event.key
    return None


def make_text_objs(text, font, color):
    """
    Function creates a text.

    :param text: string; content of text
    :param font: Font object; face of font
    :param color: tuple of color (red, green blue); colour of text

    :return: the surface object, rectangle object
    """
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def show_gameover_screen(shots_fired, elem_dict):
    """
    Function display a gameover screen when the user has successfully shot at every ship pieces.

    :param shots_fired: the number of shots taken before game is over
    :param elem_dict: Dict that contains all the necessary element for the pygame display to make changes
    """
    elem_dict["DISPLAYSURF"].fill(BGCOLOR)
    titleSurf, titleRect = make_text_objs('Congrats! Puzzle solved in:',
                                          elem_dict["BIGFONT"], TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    elem_dict["DISPLAYSURF"].blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs('Congrats! Puzzle solved in:',
                                          elem_dict["BIGFONT"], TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    elem_dict["DISPLAYSURF"].blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs(str(shots_fired) + ' shots',
                                          elem_dict["BIGFONT"], TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2 + 50))
    elem_dict["DISPLAYSURF"].blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs(str(shots_fired) + ' shots',
                                          elem_dict["BIGFONT"], TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2 + 50) - 3)
    elem_dict["DISPLAYSURF"].blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = make_text_objs(
        'Press a key to try to beat that score.', elem_dict["BASICFONT"], TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    elem_dict["DISPLAYSURF"].blit(pressKeySurf, pressKeyRect)

    while check_for_keypress() == None:  # Check if the user has pressed keys, if so start a new game
        pygame.display.update()
        elem_dict["FPSCLOCK"].tick()


def generate_default_tiles(height: int, width: int, ship_name_default=DEFAULT_SHIP_NAME,
                           bool_shot_default=DEFAULT_BOOL_SHOT):
    """
    Function generates a list of height x width tiles. The list will contain list
    ('shipName', boolShot) set to their (default_value).

    :param bool_shot_default: boolean which tells what the value to set if the ships where hit
    :param height: int; that tells the board height
    :param width: int; that tells the board width
    :param ship_name_default: List; containing the ships name

    :returns: list of tuples
    """
    default_tiles = [[[ship_name_default, bool_shot_default] for _ in range(width)] for _ in range(height)]
    #  TODO: delete if unnecessary
    # for x in range(height):
    #     for y in range(width):
    #         default_tiles[x][y] = (ship_name_default, bool_shot_default)
    # default_tiles = np.full((height, width), (ship_name_default, bool_shot_default), dtype='V,V')
    return default_tiles

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


def add_ships_to_board(board, ships):
    """
    Function goes through a list of ships and add them randomly into a board.

    :param board: list of board tiles
    :param ships: list of ships to place on board

    :return: list of board tiles with ships placed on certain tiles
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


class ClientGamesHandler:

    def __init__(self):
        # Todo add name?
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
        return self.players_board[self.turn_of_player - 1]

    def get_my_name(self):
        """
            :return: String; the name of the current player
        """
        return self.players_board[self.turn_of_player]

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

    def init_auto_generated_boards(self, height=BOARD_HEIGHT, width=BOARD_WIDTH, ships_objs=None):
        """
                    a function that generatets the default tiles

                    :param height: int; the board height
                    :param width: int; the board width
                    :param ships_objs: list; containing the ships names
                """
        self.players_board[0] = generate_default_tiles(height, width)
        self.players_board[1] = generate_default_tiles(height, width)

        if ships_objs is None:
            ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
                         'destroyer3', 'submarine1', 'submarine2', 'submarine3',
                         'submarine4']  # List of the ships available

        self.players_board[0] = add_ships_to_board(self.players_board[0], ship_objs)
        self.players_board[1] = add_ships_to_board(self.players_board[1], ship_objs)


def init_names_first_game(sock, game):
    """
        function that gets the players name from the server and send the boards after that

        :param game: of type ClientGamesHandler, is used to keep up with important things involving the game like board, player
        turn and etc...
        :param sock: the socket object used to send data to the server
    """

    send_message(sock, {"Action": "start_server"}, logging)
    received_data = receive_message(sock, logging)
    game.set_names(received_data["Players"][0], received_data["Players"][1])
    data = {"Action": "start_game", "Board_1": game.players_board[0], "Board_2": game.players_board[1], "Quit": None}
    send_message(sock, data, logging)


def operation_mapper(game: ClientGamesHandler, received_data, logger, client_win = None, sock = None):
    """
    this function is used to map the different actions that were received from the server with there corresponding actions

    :param client_win: of type client_window, contain the tkinter display and the elements it needs to work
    :param game: of type ClientGamesHandler, is used to keep up with important things involving the game like board, player turn and
    etc...
    :param received_data: Dict that was received from the server
    :param sock: Socket object used to send data to the server
    """
    # if received_data["Action"] == "start_game":
    #     if not received_data["Restart"]:
    #         game.set_names(received_data["Players"][0], received_data["Players"][1])


    if received_data["Action"] == "Init":
        game.set_names(received_data["Players"][0], received_data["Players"][1])

    elif received_data["Action"] == "start_game":
        game.set_boards(received_data["Board_1"],received_data["Board_2"])
        if received_data["restart"]:
            client_win.game_ended = False


    elif received_data["Action"] == "hit":
        #TODO: fix sound files maybe use pygame
        if received_data["Success"] == True:
            playsound('soundFiles\hit-water.wav')
        else:
            playsound('soundFiles\sea-explosion.wav')

        if received_data["Finished"]:
            client_win.game_ended = True
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE ):
                    client_win.opponent_frame.grid_slaves(row=i, column=j)[0].config(state="disable")
            if received_data["Winner"] == game.turn_of_player:
                client_win.my_name.set(game.get_my_name() + " Has Won!")
            else:
                client_win.opponent_name.set(game.get_opponent_name() + " Has Won!")
        else: # if game didn't finished swap turns and update boards
            game.change_turn()
            client_win.update_colors()


            # TODO: show result screen

    elif received_data["Action"] == "ok":
        pass

    elif received_data["Action"] == "game finished":
        pygame.quit()
        sys.exit()
    else:
        print("unknown Action: %s", received_data["Action"])
        # TODO: consider throwing error


def start_new_game(game, sock, logger, quit = False):
    """
    this function is used to send to the server that the client is starting a new game and receive from the server
    the new boards

    :param game: type ClientGamesHandler, is used to keep up with important things involving the game like board, player
    turn and etc...
    :param sock: Socket object used to send data to the server
    :param quit: boolean to tell the server which player pressed the new game button (Quit = None mean we just started the first game)
    """

    data = {"Action": "start_game"}
    if quit:
        data["Quit"] = game.turn_of_player
    else:
        data["Quit"] = None
    send_message(sock, data, logger)
    # get board
    recv_data = receive_message(sock)
    operation_mapper(game=game, received_data=recv_data ,logger=logger)
