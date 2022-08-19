import pygame as pg

BORDER = (0, 0, 0)

COVERED = (200, 200, 200)
MISS = (255, 50, 50)
SHIP = (50, 50, 255)

Tile = tuple[int, int, int]


class Board(pg.Surface):
    def __init__(self, width: float, tile_count: int = 10):
        super().__init__(size=(width, width))

        self.tile_width = width / tile_count
        self.tile_count = tile_count

        self.state: list[list[Tile]] = [[COVERED for _ in range(tile_count)] for _ in range(tile_count)]
        self.ships: list[list[bool]] = [[False for _ in range(tile_count)] for _ in range(tile_count)]

        # TODO self.is_active

        self._tiles: list[list[pg.Rect]] = [
            [
                pg.Rect(
                    self.tile_width * tile_idx,
                    self.tile_width * row_idx,
                    self.tile_width,
                    self.tile_width
                ) for tile_idx in range(tile_count)
            ] for row_idx in range(tile_count)
        ]
        self._left = 0
        self._top = 0

    def draw(self):
        # TODO draw border around entire board to be even with the inner grid

        for row_idx, row in enumerate(self.state):
            for tile_idx, tile in enumerate(row):
                pg.draw.rect(
                    surface=self,
                    color=tile,
                    rect=self._tiles[row_idx][tile_idx]
                )
                pg.draw.rect(
                    surface=self,
                    color=BORDER,
                    rect=self._tiles[row_idx][tile_idx],
                    width=1
                )

    def blit_onto(self, target: pg.Surface, left: float, top: float):
        target.blit(self, dest=(left, top))

        self._left = left
        self._top = top


class OpponentBoard(Board):
    def handle(self, event: pg.event.Event):
        if event.type == pg.MOUSEBUTTONUP:
            x, y = pg.mouse.get_pos()

            for row_idx, row in enumerate(self._tiles):
                for tile_idx, tile in enumerate(row):

                    # if this tile was pressed
                    if tile.collidepoint((x - self._left, y - self._top)):

                        # if there is a ship there
                        if self.ships[row_idx][tile_idx] is True:
                            self.state[row_idx][tile_idx] = SHIP
                        else:
                            self.state[row_idx][tile_idx] = MISS
