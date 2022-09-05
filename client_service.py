import random, sys, pygame

from shared import *
from pygame.locals import *
import board

# Set variables, like screen width and height
# globals


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
            elem_dict -> A dict that contains all the necessary element for the pygame display to make changes

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
        elem_dict -> A dict that contains all the necessary element for the pygame display to make changes

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

    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes

    coord -> tuple of tile coords to apply the blowup animation
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

    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
    tile -> tuple; of tile coords to reveal
    coverage -> int; amount of the tile that is covered
    hit -> did the tile contained a ship that was hit
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

    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
    tile_to_reveal -> tuple of tile coords to apply the reveal animation to
    hit -> did the tile contained a ship that was hit

    """
    for coverage in range(TILESIZE, (-REVEALSPEED) - 1, -REVEALSPEED):  # Plays animation based on reveal speed
        draw_tile_covers(tile_to_reveal, coverage, elem_dict, hit)


def draw_board(board, elem_dict, my_board: bool):
    """
    Function draws the game board.

    board -> list of board tiles
    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
    my_board -> bool that indicates if we need to cover the ships that still wasn't revealed
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


def draw_markers(xlist, ylist, elem_dict):
    """
    Function draws the two list of markers to the side of the board.

    xlist -> list of row markers
    ylist -> list of column markers
    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes

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


def draw_highlight_tile(tilex, tiley, elem_dict):
    """
    Function draws the hovering highlight over the tile.

    tilex -> int; x position of tile
    tiley -> int; y position of tile
    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
    """
    left, top = left_top_coords_tile(tilex, tiley)
    pygame.draw.rect(elem_dict["DISPLAYSURF"], HIGHLIGHTCOLOR,
                     (left, top, TILESIZE, TILESIZE), 4)


def show_help_screen(elem_dict):
    """
    Function display a help screen until any button is pressed.
    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
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


def show_gameover_screen(shots_fired, elem_dict):
    """
    Function display a gameover screen when the user has successfully shot at every ship pieces.

    shots_fired -> the number of shots taken before game is over
    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
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


class ClientGamesHandler:
    """
        A class that helps us keep track with all the actions and variables that involves in a game
        players_board -> variable that contains the players board
        turn_of_player -> variable that contains which player turn is currently running
        last_attack -> variable that contains in which tile was the last attack
    """
    def __init__(self):
        # Todo add name?
        self.players_board = [None, None]
        self.players_name = [None, None]
        self.turn_of_player = random.randint(0, 1)
        self.last_attack = None

    def set_boards(self, board_1, board_2):
        """
            a function that set the two players board
            board_1 -> board of player 1
            board_2 -> board of player 2
        """
        self.players_board[0] = board_1
        self.players_board[1] = board_2

    def set_boards(self, player_1_name, player_2_name):
        """
            a function that set the two players board
            board_1 -> board of player 1
            board_2 -> board of player 2
        """
        self.players_name[0] = player_1_name
        self.players_name[1] = player_2_name

    def hit_on_board(self, x, y):
        """
        a function that keep track of the last attack on the(x,y) position and make the necessary changes to the
        board and change the player turn
        """
        self.last_attack = [x, y]
        self.get_board_of_opponent()[x][y][1] = True
        self.change_turn()

    def opponent_number(self):
        """
            returns the number of the opponent
        """
        if self.turn_of_player == 0:
            return 1
        else:
            return 0

    def get_board_of_opponent(self):
        """
            return the board of the opponent
        """
        return self.players_board[self.turn_of_player - 1]

    def get_if_opponent_reveled_tile(self, tile):
        """
            a function that check if the tile was already revealed on the opponent board
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


    def encode(self):
        player_board = board.Board()
        opponent_board = board.Board()

        for i, row in enumerate(self.players_board[self.turn_of_player]):
            for c, tile in enumerate(row):
                if tile[0]:  # if ship exist
                    player_board.ships[i][c] = True
                    if tile[1]:  # if hitted
                        player_board.state[i][c] = board.SHIP_CONFLICT
                    else:
                        player_board.state[i][c] = board.COVERED
                else:
                    player_board.ships[i][c] = False
                    if tile[1]:  # if hitted
                        player_board.state[i][c] = board.MISS
                    else:
                        player_board.state[i][c] = board.COVERED

        for i, row in enumerate(self.get_board_of_opponent()):
            for c, tile in enumerate(row):
                if tile[0]:  # if ship exist
                    player_board.ships[i][c] = True
                    if tile[1]:  # if hitted
                        player_board.state[i][c] = board.SHIP_CONFLICT
                    else:
                        player_board.state[i][c] = board.COVERED
                else:
                    player_board.ships[i][c] = False
                    if tile[1]:  # if hitted
                        player_board.state[i][c] = board.MISS
                    else:
                        player_board.state[i][c] = board.COVERED




def operation_mapper(elem_dict, game: ClientGamesHandler, received_data, sock = None):
    """
    this function is used to map the different actions that were received from the server with there corresponding actions

    elem_dict -> A dict that contains all the necessary element for the pygame display to make changes
    game-> of type ClientGamesHandler, is used to keep up with important things involving the game like board, player turn and
    etc...
    received_data-> the dict that was received from the server
    sock -> the socket object used to send data to the server
    """
    if received_data["Action"] == "start_game":
        game.add_boards(received_data["Board_1"], received_data["Board_2"])

    elif received_data["Action"] == "hit":
        if received_data["Success"] == True:
            reveal_tile_animation(game.last_attack, elem_dict, True)
            left, top = left_top_coords_tile(game.last_attack[0], game.last_attack[1])
            blowup_animation((left, top), elem_dict)
        else:
            reveal_tile_animation(game.last_attack, elem_dict)

        if received_data["Finished"]:
            print("Game ended")
            start_new_game(game, sock)
            # TODO: show result screen
    elif received_data["Action"] == "ok":
        pass

    elif received_data["Action"] == "game finished":
        pygame.quit()
        sys.exit()
    else:
        print("unknown Action: %s", received_data["Action"])
        # TODO: consider throwing error


def start_new_game(game, sock, quit = False):
    """
    this function is used to send to the server that the client is starting a new game and receive from the server
    the new boards

    game-> of typeClientGamesHandler, is used to keep up with important things involving the game like board, player
    turn and etc...
    sock -> the socket object used to send data to the server
    quit -> to tell the server which player pressed the new game button (Quit = None mean we just started the first game)
    """
    data = {"Action": "start_game", "Player_name": game.players_name, "Board_1": game.players_board[0], "Board_2": game.players_board[1]}
    if quit:
        data["Quit"] = game.turn_of_player
    else:
        data["Quit"] = None
    send_message(sock, data)
    # get board
    recv_data = receive_message(sock)
    operation_mapper(recv_data)
