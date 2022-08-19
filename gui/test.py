import pygame as pg
from pygame.locals import *

from board import OpponentBoard

S_WIDTH = 1000
S_HEIGHT = 600


def main():
    pg.init()

    display = pg.display.set_mode(
        size=(S_WIDTH, S_HEIGHT),
        depth=32
    )
    opp_board = OpponentBoard(width=400)
    opp_board.ships[0][0], opp_board.ships[0][1], opp_board.ships[0][2] = True, True, True

    while True:
        display.fill((255, 255, 255))

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                exit()

            opp_board.handle(event)

        opp_board.draw()
        opp_board.blit_onto(display, 300, 100)
        pg.display.flip()


if __name__ == '__main__':
    main()
