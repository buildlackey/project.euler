from typing import TypeVar, List

import numpy as np

from enum import Enum, auto



class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    DIAG_UP_RIGHT = auto()
    DIAG_DOWN_RIGHT = auto()
    DIAG_UP_LEFT = auto()
    DIAG_DOWN_LEFT = auto()

    @staticmethod
    def all():
        return [dir for dir in Direction]


T = TypeVar('T')


class SquareMatrix:
    def __init__(self, elements: List[T], span: int):
        if len(elements) != span ** 2:
            raise ValueError("Size of the array does not match the specified number of rows and columns.")

        self.elements = elements
        self.span = span

    def validate_indices(self, row: int, col: int):
        if row < 0 or row >= self.span or col < 0 or col >= self.span:
            raise ValueError(f"Invalid row or column index: ({row},{col})")

    def cell(self, row: int, col: int) -> T:
        self.validate_indices(row, col)
        index = row * self.span + col
        return self.elements[index]

    def find_largest_product(self, span_length: int):

        def multiply_cells(slice) -> int:
            return np.prod([self.cell(x,y) for (x,y) in slice])

        cell_to_prod_map = dict()
        max_prod = -1
        for row in range(0, self.span):
            for col in range(0, self.span):
                slices = self.get_slices(row, col, span_length)
                print(f"for ({row},{col}) slices are: {slices}")

                for slice in slices:
                    slice_prod = multiply_cells(slice)
                    if (slice_prod > max_prod):
                        print(f"replacing {max_prod} w/ new max for ({row},{col}). update to ->{slice_prod}")
                        cell_to_prod_map[(row, col)] = slice_prod
                        max_prod = slice_prod
                    else:
                        print(f"NOT replacing max_prod {max_prod} w/ product for ({row},{col}) =   {slice_prod}")

        sorted_key_value_pairs = sorted(cell_to_prod_map.items(), key=lambda item: item[1], reverse=True)
        print(f"sorted_key_value_pairs: {sorted_key_value_pairs}")

        result = sorted_key_value_pairs
        print(f"result: {result}")
        return result[0][1]


    '''
    Given a cell position -- i.e. (row/col coordinates) -- find all of the valid
    horizontal, vertical and diagonal slices that end or begin with that
    cell position.
    '''
    def get_slices(self, row: int, col: int, span: int) -> List[T]:
        slices = []
        for dir in Direction.all():
            slice = self.slice(row, col, dir, span)
            if (slice):
                slices.append(slice)

        print(f"slices: {slices}")
        return slices

    def slice(self, start_row: int, start_col: int, direction: Direction, hops: int) -> List[T]:
        self.validate_indices(start_row, start_col)
        if (hops > self.span or hops <= 0):
            raise ValueError(f"Invalid number of hops: {hops}.")

        def room_down(int: start_row, hops: int) -> bool:  # is there room in downwards direction?
            return start_row + hops <= self.span

        def room_up(int: start_row, hops: int) -> bool:
            return start_row >= hops - 1

        def room_right(int: start_col, hops: int) -> bool:
            return start_col + hops <= self.span

        def room_left(int: start_col, hops: int) -> bool:
            return start_col >= hops - 1

        vert = []
        horiz = []
        if (direction == Direction.UP and room_up(start_row, hops)):
            vert = range(start_row, start_row - hops, -1)
            horiz = [start_col] * hops
        elif (direction == Direction.DOWN and room_down(start_row, hops)):
            vert = range(start_row, start_row + hops, 1)
            horiz = [start_col] * hops
        elif (direction == Direction.RIGHT and room_right(start_row, hops)):
            vert = [start_row] * hops
            horiz = range(start_col, start_col + hops, 1)
        elif (direction == Direction.LEFT and room_left(start_row, hops)):
            vert = [start_row] * hops
            horiz = range(start_col, start_col - hops, -1)
        elif (direction == Direction.DIAG_UP_RIGHT) and room_up(start_row, hops) and room_right(start_row, hops):
            vert = range(start_row, start_row - hops, -1)
            horiz = range(start_col, start_col + hops, 1)
        elif (direction == Direction.DIAG_UP_LEFT) and room_up(start_row, hops) and room_left(start_row, hops):
            vert = range(start_row, start_row - hops, -1)
            horiz = range(start_col, start_col - hops, -1)
        elif (direction == Direction.DIAG_DOWN_RIGHT) and room_down(start_row, hops) and room_right(start_row, hops):
            vert = range(start_row, start_row + hops, 1)
            horiz = range(start_col, start_col + hops, 1)
        elif (direction == Direction.DIAG_DOWN_LEFT) and room_down(start_row, hops) and room_left(start_row, hops):
            vert = range(start_row, start_row + hops, 1)
            horiz = range(start_col, start_col - hops, -1)

        retval = list(zip(vert, horiz))
        print(f"for dir {direction} - zip elements-> {retval}")
        return retval
