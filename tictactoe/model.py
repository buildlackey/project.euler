from typing import TypeVar, List
from typing import Tuple

import copy
import numpy as np

#  Cell and game states
#
X_CELL = 1  # marked by player x
O_CELL = -1  # marked by player x
OPEN_CELL = 0  # open to be marked by either player

symbol_mapping = {
    "X": X_CELL,
    "0": O_CELL
}

reverse_mapping = {
    X_CELL: "X",
    O_CELL: "0",
    0: "_"
}

UNDEFINED_SCORE = -9
NO_WINNER_YET = -10


class GameBoard:

    def __init__(self, span: int):
        self.span: int = span
        self.grid = np.full(((span), (span)), OPEN_CELL, int)
        self.xcoords = list(range(0, self.span))
        self.ycoords = self.xcoords
        self.reverse_coords = list(reversed(self.xcoords))

    def full(self) -> bool:
        return self.available_moves() == []

    def empty(self) -> bool:
        return len(self.available_moves()) == self.span**2

    def available_moves(self) -> List[Tuple[int, int]]:
        moves = []
        for i in range(0, self.span):
            for j in range(0, self.span):
                if (self.grid[i, j] == OPEN_CELL):
                    moves.append((i, j))
        return moves

    def update_cell(self, row, col, symbol):
        if (self.grid[row, col] != OPEN_CELL):
            raise ValueError(f"attempt to update non-open cell: ({row},{col})")
        else:
            self.grid[row, col] = symbol


class Player:
    def __init__(self, name: str, symbol: str, is_bot_player=False):
        self.name = name
        self.symbol = symbol
        self.is_bot_player = is_bot_player

    def opponent_symbol(self):
        if (self.symbol == X_CELL):
            return O_CELL
        else:
            return X_CELL

    def __repr__(self):
        return f"Player(name={repr(self.name)}, symbol={repr(self.symbol)}, is_bot={repr(self.is_bot_player)})"


class GameState:
    def __init__(self, board: GameBoard, next_to_move: int, players: List[Player]):
        self.board = board
        self.next_to_move = next_to_move
        self.players = players

    # Returns next player 'p', and resets  'next player' pointer to point to the opponent of player 'p'
    def get_next_player_to_move(self) -> Player:
        next = self.next_to_move
        self.next_to_move = (self.next_to_move + 1) % 2
        return self.players[next]

    # Returns next player to move 'p'. Unline get_next_player_to_move, has no side effects (no reset of next pointer)
    def peek_next_player_to_move(self) -> Player:
        return self.players[self.next_to_move]

    def get_player_who_moved_last(self) -> Player:
        if (self.board.empty()):
            raise ValueError("illegal call to get_player_who_moved_last - no one moved yet")

        index = (self.next_to_move + 1) % 2
        return self.players[index]

    # Update given cell position using symbol of 'player_doing_update'
    def update_board(self, row: int, col: int, player_doing_update: Player):
        assert (player_doing_update == self.peek_next_player_to_move())

        self.board.update_cell(row, col, player_doing_update.symbol)

    def game_won(self):
        has_won, score = Score(self.board).value()
        return has_won

    def winner(self):
        has_won, score = Score(self.board).value()
        if (not has_won):
            return False
        if (score > 0):  # negative score 'O' player wins, else 'X' player
            if (self.players[0] == X_CELL):
                return self.players[0]
            else:
                return self.players[1]
        else:
            if (self.players[0] == O_CELL):
                return self.players[0]
            else:
                return self.players[1]

    def game_done(self):
        return self.board.full() or self.game_won()


verbose = False


def dbg(msg: str):
    if (verbose):
        print(msg)


class Score:
    def __init__(self, board: GameBoard):
        sp = board.span
        self.board = board
        pass

    # returns a tuple indicating 1) whether game has been won yet, and 2) the game score
    def value(self):

        # returns a tuple indicating 1) whether sequence of cells has owner, and 2) the score for sequence
        def sequence_score(cells: List[Tuple[int, int]]) -> Tuple[bool, int]:
            cell_values = [self.board.grid[row, col] for row, col in cells]
            cell_sum = sum(cell_values)
            dbg(f"sequence_score for {list(cells)}: {cell_sum}")
            i = abs(cell_sum)
            span = self.board.span
            dbg(f"span: {span}")
            return i == span, cell_sum

        # check horizontal sequence of cells for each row
        for row in self.board.ycoords:
            has_owner, score = sequence_score([(row, col) for col in self.board.xcoords])
            if (has_owner):
                return (True, score)

        # check vertical sequence of cells for each column
        for col in self.board.xcoords:
            has_owner, score = sequence_score([(row, col) for row in self.board.ycoords])
            if (has_owner):
                return (True, score)

        # check on diagonal down and to right
        diag_to_right_coords = [(index, index) for index in self.board.ycoords]
        has_owner, score = sequence_score(diag_to_right_coords)
        if (has_owner):
            return (True, score)

        # check on diagonal down and to left
        has_owner, score = sequence_score(
            [(row, self.board.span - row - 1) for row in self.board.ycoords])
        dbg(f"diagonal down and to left: {has_owner} {score}")
        if (has_owner):
            return (True, score)

        return (False, UNDEFINED_SCORE)


class Move:
    pass


class MinMaxStrategy:

    def __init__(self):
        import sys
        self.max_size = sys.maxsize
        self.min_size = -sys.maxsize - 1

    def search(self, state: GameState) -> Tuple[Tuple[int, int], int]:
        working_state = copy.deepcopy(state)
        next_up_player = working_state.get_next_player_to_move()
        symbol = next_up_player.symbol
        remaining_moves = working_state.board.available_moves()

        if (len(remaining_moves) == 1):     # return the only move available, and board score with this move
            move = remaining_moves[0]
            working_state.board.update_cell(move[0], move[1], symbol)
            return (move, Score(state.board).value()[1])

        if (state.game_done()):
            return ((-1, -1), Score(state.board).value()[1])

        dbg(f"search for {next_up_player} trying remaining_moves: {remaining_moves}")

        best_move_found = (-1, -1)
        if (next_up_player.is_bot_player):  # can prob refactor this chunk...
            best_move_value = self.max_size
            for row, col in remaining_moves:
                working_state.board.update_cell(row, col, symbol)
                best_move, board_value = self.search(working_state)
                if (board_value < best_move_value):
                    best_move_value = board_value
                    best_move_found = (row, col)
        else:
            best_move_value = self.min_size
            best_move_found = (-1, -1)
            for row, col in remaining_moves:
                working_state.board.update_cell(row, col, symbol)
                best_move, board_value = self.search(working_state)
                if (board_value > best_move_value):
                    best_move_value = board_value
                    best_move_found = (row, col)

        return (best_move_found, best_move_value)

    def get_next_move(self, state: GameState, player: Player, disable_game_won_check = False) -> Tuple[int, int]:
        assert (not state.board.full())
        assert (disable_game_won_check or not state.game_won())     # can turn off this check for testing
        assert (player.is_bot_player)
        best_next_move, _ = self.search(copy.deepcopy(state))
        return best_next_move
