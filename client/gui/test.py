import pygame as pg
from pygame.locals import *

from board import OpponentBoard, CreateBoard

S_WIDTH = 1000
S_HEIGHT = 600


def main():
    pg.init()
    pg.font.init()
    pg.mixer.init()

   # pg.mixer.music.load("../../soundfile/start.mp3")
   # pg.mixer.music.play()

    font = pg.font.SysFont("Ariel", 24, bold=True)

    create_board_title = font.render("My Board", True, (0, 0, 0))

    display = pg.display.set_mode(
        size=(S_WIDTH, S_HEIGHT),
        depth=32
    )
    opp_board = OpponentBoard(width=400)
    opp_board.ships[0][0], opp_board.ships[0][1], opp_board.ships[0][2] = True, True, True

    create_board = CreateBoard(width=400)

    while True:
        display.fill((255, 255, 255))

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                exit()

            opp_board.handle_event(event)
            create_board.handle_event(event)

        opp_board.draw()
        opp_board.blit_onto(display, 525, 100)

        create_board.draw()
        create_board.blit_onto(display, 75, 100)

        display.blit(create_board_title, (240, 75))

        pg.display.flip()


if __name__ == '__main__':
    main()
