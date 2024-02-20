from typing import TypeVar, List
from typing import Tuple
from typing_extensions import Self


import copy
import numpy as np
import sys

#  Cell and game states
#
X_CELL = 1          # internal integer code value for cell marked by player 'x'
O_CELL = -1         # internal integer code value for cell marked by player 'o'
OPEN_CELL = 0       # internal integer code value for cell open to be marked by either player

symbol_char_to_code_map = {
    "X": X_CELL,
    "O": O_CELL
}

symbol_code_to_char_map = {
    X_CELL: "X",
    O_CELL: "O",
    0: "_"
}



COUNT = 1  # marked by player 'x'
def incr():
    global COUNT
    COUNT = COUNT + 1
    return COUNT


verbose = False

def check_verbose():
    print(f"verbose: {verbose}")

def set_verbose():
    global verbose
    verbose = True

def dbg(msg: str):
    if (verbose):
        sprint(msg)


def sprint(msg):        # had issues with pycharm output, so this logs to a file so i can debug
    if (verbose):
        log_file_path = "/tmp/log"
        try:
            # Open the file in append mode (a) to add new messages without overwriting existing content
            with open(log_file_path, 'a') as log_file:
                # Write the message to the log file
                log_file.write(msg + "\n")
                log_file.flush()
                print(msg)
                sys.stdout.flush()
        except Exception as e:
            sprint(f"Error logging message: {e}")



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


class Player:

    def __init__(self, name: str, symbol: int, is_bot_player=False):
        self.name = name
        self.symbol = symbol
        self.is_bot_player = is_bot_player
        self.opposing_player: Player


    def set_opposing_player(self, opponent: Self):
        self.opposing_player = opponent


    def get_opposing_player(self):
        return self.opposing_player

    def opponent_symbol(self):
        return self.get_opposing_player().symbol


    # Determines 'worst case' board value for this opponent (used in minimax search)
    def init_best_score(self):
        if (self.symbol == X_CELL):
            return -sys.maxsize - 1     # minimum int value
        else:
            return sys.maxsize          # maximum int value


    # Determine if alternative score is 'better'. For X_CELL player, prefer highest, for O_CELL, seek lowest possible
    def prefer_updated_score(self, current: int, proposed_update: int):
        if (self.symbol == X_CELL):
            return current <= proposed_update        # proposed score is higher, so better for X_CELL player
        else:
            return current > proposed_update        # proposed score is lower, so better for O_CELL player

    def __repr__(self):
        name = f"name={repr(self.name)}"
        symbol = f"symbol={repr(symbol_code_to_char_map[self.symbol])}/{repr(self.symbol)}"
        init_board_val = f"init_board_val {self.init_best_score() }:"
        return f"Player({name}, {symbol} is_bot={repr(self.is_bot_player)}, {init_board_val} )"


class GameState:
    def __init__(self, board: GameBoard, next_to_move: int, players: List[Player]):
        self.board = board
        self.players = players
        self.players[0].set_opposing_player(self.players[1])
        self.players[1].set_opposing_player(self.players[0])
        self.current_player = self.players[next_to_move]


    # Update state to set current player to be the opponent of the previous current player
    def next_players_turn(self) -> Self:
        dup = copy.deepcopy(self)
        dup.current_player = dup.current_player.get_opposing_player()
        return dup

    # Returns player whose turn it is to move. This will not change until next_players_turn is called
    def get_next_player_to_move(self) -> Player:
        return self.current_player


    # Update board so that given cell position is marked using symbol of current player
    def claim_cell_for_curr_player(self, row: int, col: int) -> Self:
        if (self.board.grid[row, col] != OPEN_CELL):
            raise ValueError(f"attempt to update non-open cell: ({row},{col})")
        dup = copy.deepcopy(self)
        dup.board.grid[row, col] = dup.current_player.symbol
        return dup

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



class Score:
    def __init__(self, board: GameBoard):
        sp = board.span
        self.board = board

    # returns a tuple indicating 1) whether game has been won yet, and 2) the game score
    def value(self):

        # returns a tuple indicating 1) whether sequence of cells has owner, and 2) the score for sequence
        def sequence_score(cells: List[Tuple[int, int]]) -> Tuple[bool, int]:

            def edge_cell_bump_value():     # bump score for more attractive board positions
                on_edge = any( (row == self.board.span-1 or col == self.board.span-1) for (row,col) in cells)
                if (on_edge):
                    value = self.board.grid[(cells[0][0]), (cells[0][1])]
                    return 1 * value  # convert to positive or negative 'bonus value'
                else:
                    return 0

            def center_cell_bump_value():     # bump score for more attractive board positions
                mid_point = self.board.span // 2
                on_center = any( (row == mid_point or col == mid_point) for (row,col) in cells)
                if (on_center ):
                    return 2 * self.board.grid[mid_point,mid_point]  # convert to positive or negative 'bonus value'
                else:
                    return 0

            cell_values = [self.board.grid[row, col] for row, col in cells]
            cell_sum = sum(cell_values)
            dbg(f"sequence_score for {list(cells)}: {cell_sum}")
            is_winning_sequence = abs(cell_sum) == self.board.span

            if (is_winning_sequence):                # bump score for center and edge squares
                cell_sum = cell_sum + edge_cell_bump_value() + center_cell_bump_value()
            return is_winning_sequence, cell_sum


        best_score = 0

        # check horizontal sequence of cells for each row
        for row in self.board.ycoords:
            has_owner, score = sequence_score([(row, col) for col in self.board.xcoords])
            if (has_owner and  abs(score)  > abs(best_score)):
                best_score = score

        # check vertical sequence of cells for each column
        for col in self.board.xcoords:
            has_owner, score = sequence_score([(row, col) for row in self.board.ycoords])
            if (has_owner and  abs(score)  > abs(best_score)):
                best_score = score

        # check on diagonal down and to right
        diag_to_right_coords = [(index, index) for index in self.board.ycoords]
        has_owner, score = sequence_score(diag_to_right_coords)
        if (has_owner and  abs(score)  > abs(best_score)):
            best_score = score

        # check on diagonal down and to left
        has_owner, score = sequence_score(
            [(row, self.board.span - row - 1) for row in self.board.ycoords])
        dbg(f"diagonal down and to left: {has_owner} {score}")
        if (has_owner and  abs(score)  > abs(best_score)):
            best_score = score

        return (best_score != 0 , best_score)


class Move:
    pass


class MinMaxStrategy:

    def __init__(self):
        import sys
        self.max_size = sys.maxsize
        self.min_size = -sys.maxsize - 1


    def __find_best_score_and_move__(self, state: GameState, alpha: int, beta: int) -> Tuple[Tuple[int,int],int]:
        moves_to_try = state.board.available_moves()
        best_move_value = state.current_player.init_best_score()    # initialize to extreme 'worst' value
        padlen = 9 - len(moves_to_try)
        padstr =  " " * padlen                                      # this is for debugging
        inc = incr()
        sprint(f"{padstr}Checking at {inc} for {state.current_player} : init_best: {best_move_value} {moves_to_try}")

        optimal_row = -1
        optimal_col = -1
        for row, col in moves_to_try:
            sprint(f"{padstr}Trying {row}/{col} with curr best {best_move_value}  available_moves:   {len(moves_to_try)} |  {moves_to_try}")
            board_value = self.__recurse__(state.claim_cell_for_curr_player(row, col)) # check score assuming curr player owns row/col
            sprint(f"{padstr}CELL:{row}/{col} candidate best move value: {board_value} with remaining = {moves_to_try}")
            if (state.current_player.prefer_updated_score(best_move_value, board_value)):
                sprint(f"{padstr}CELL:{row}/{col} candidate {board_value} better than {best_move_value}")
                best_move_value = board_value
                optimal_row = row
                optimal_col = col


        sprint(f"{padstr}Returning {optimal_row}/{optimal_col} for {moves_to_try}")
        return  (optimal_row, optimal_col), best_move_value


    def __recurse__(self, state: GameState, alpha, beta) -> int:
        if (state.game_done()):
            return  Score(state.board).value()[1]

        # recursively enter best score search while setting current player to opponent
        return self.__find_best_score_and_move__(state.next_players_turn(), alpha, beta)[1]


    def get_next_move(self, state: GameState, disable_game_won_check = False) -> Tuple[int, int]:
        dbg(f"get_next_move for starting")
        assert (not state.board.full())
        assert (disable_game_won_check or not state.game_won())     # can turn off this check for testing
        assert (state.current_player.is_bot_player)

        midpoint = state.board.span // 2                            # simple heuristic: grab center position if open
        if state.board.grid[midpoint, midpoint] == OPEN_CELL:
            return (midpoint, midpoint)

        (row,col),score = self.__find_best_score_and_move__(state)
        dbg(f"get_next_move for {state.current_player} resulted in: {row}/{col} -> {score}")
        return row,col



if __name__ == "__main__":
   check_verbose()
   set_verbose()
   check_verbose()

