import pygame as pg

BORDER = (0, 0, 0)

COVERED = (200, 200, 200)
MISS = (255, 50, 50)
SHIP = (50, 50, 255)
SHIP_PLACEMENT = (50, 50, 200)
SHIP_CONFLICT = (80, 50, 50)

SHIP_SIZES = [5, 4, 3, 3, 2]

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
    def handle_event(self, event: pg.event.Event):
        if event.type != pg.MOUSEBUTTONUP:
            return

        x, y = pg.mouse.get_pos()

        for row_idx, row in enumerate(self._tiles):
            for tile_idx, tile in enumerate(row):

                # if this tile was not pressed
                if not tile.collidepoint((x - self._left, y - self._top)):
                    continue

                # if there is a ship there
                if self.ships[row_idx][tile_idx] is True:
                    self.state[row_idx][tile_idx] = SHIP
                else:
                    self.state[row_idx][tile_idx] = MISS


class CreateBoard(Board):
    def __init__(self, width: float, tile_count: int = 10):
        super().__init__(width, tile_count=tile_count)

        self.current_horizontal: bool = True
        self.next_sizes: list[int] = []
        self.current_size: int = 0

        self.clear()

    def clear(self):
        self.current_horizontal = True
        self.next_sizes = SHIP_SIZES.copy()
        self.current_size = self.next_sizes.pop(0)
        self.ships = [[False for _ in range(self.tile_count)] for _ in range(self.tile_count)]
        self.state_from_ships()

    def state_from_ships(self):
        for row in range(self.tile_count):
            for col in range(self.tile_count):
                if self.ships[row][col] is True:
                    self.state[row][col] = SHIP
                else:
                    self.state[row][col] = COVERED

    def exists_horizontal(self, row: int, col_a: int, col_b: int) -> bool:
        assert col_a < col_b

        for col_idx in range(col_a, col_b):
            if self.ships[row][col_idx] is True:
                return True

        return False

    def insert_horizontal(self, row: int, col_a: int, col_b: int):
        assert col_a < col_b

        for col_idx in range(col_a, col_b):
            self.ships[row][col_idx] = True

    def draw_horizontal(self, row: int, col_a: int, col_b: int):
        assert col_a < col_b

        for col_idx in range(col_a, col_b):
            if self.ships[row][col_idx] is False:
                self.state[row][col_idx] = SHIP_PLACEMENT
            else:
                self.state[row][col_idx] = SHIP_CONFLICT

    def exists_vertical(self, col: int, row_a: int, row_b: int) -> bool:
        assert row_a < row_b

        for row_idx in range(row_a, row_b):
            if self.ships[row_idx][col] is True:
                return True

        return False

    def insert_vertical(self, col: int, row_a: int, row_b: int):
        assert row_a < row_b

        for row_idx in range(row_a, row_b):
            self.ships[row_idx][col] = True

    def draw_vertical(self, col: int, row_a: int, row_b: int):
        assert row_a < row_b

        for row_idx in range(row_a, row_b):
            if self.ships[row_idx][col] is False:
                self.state[row_idx][col] = SHIP_PLACEMENT
            else:
                self.state[row_idx][col] = SHIP_CONFLICT

    def handle_event(self, event: pg.event.Event):
        if self.current_size is None:
            return

        if event.type == pg.KEYDOWN:
            pressed_keys = pg.key.get_pressed()

            if pressed_keys[pg.K_r] is True:
                self.current_horizontal = not self.current_horizontal

            if pressed_keys[pg.K_c] is True:
                self.clear()

        x, y = pg.mouse.get_pos()

        self.state_from_ships()

        for row_idx, row in enumerate(self._tiles):
            for col_idx, col in enumerate(row):

                # if this tile was not hovered
                if not col.collidepoint((x - self._left, y - self._top)):
                    continue

                # if the tile is too close to the edge
                if (self.current_horizontal and col_idx + self.current_size > self.tile_count) or (
                        (not self.current_horizontal) and row_idx + self.current_size > self.tile_count):
                    continue

                if self.current_horizontal:
                    self.draw_horizontal(row_idx, col_idx, col_idx + self.current_size)

                    # if tried to place ship, and no ships exist in the spaces
                    if event.type == pg.MOUSEBUTTONUP and not self.exists_horizontal(row_idx, col_idx,
                                                                                     col_idx + self.current_size):
                        # actually set ship
                        self.insert_horizontal(row_idx, col_idx, col_idx + self.current_size)

                        self.state_from_ships()

                        # go to next ship
                        if len(self.next_sizes) > 0:
                            self.current_size = self.next_sizes.pop(0)
                        else:
                            self.current_size = None

                else:
                    self.draw_vertical(col_idx, row_idx, row_idx + self.current_size)

                    # if tried to place ship, and no ships exist in the spaces
                    if event.type == pg.MOUSEBUTTONUP and not self.exists_vertical(col_idx, row_idx,
                                                                                   row_idx + self.current_size):
                        # actually set ship
                        self.insert_vertical(col_idx, row_idx, row_idx + self.current_size)

                        self.state_from_ships()

                        # go to next ship
                        if len(self.next_sizes) > 0:
                            self.current_size = self.next_sizes.pop(0)
                        else:
                            self.current_size = None
