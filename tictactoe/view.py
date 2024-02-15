import re
import logging

from tictactoe.model import *

"""
Acquires user input, writes current state of game board to console, and announces the status of the
game (winning plays, draws, etc).
"""


class UI:
    def render_board(self, state: GameState) -> str:
        aligned_strings = []
        for row in range(state.board.span):
            row_values = []
            for col in range(state.board.span):
                cell = state.board.grid[row, col]
                row_values.append(str(reverse_mapping[cell]).rjust(state.board.span))
            aligned_strings.append(" ".join(row_values))
        result = "\n\n".join(aligned_strings)
        print(f"\n{result}")
        print("\n")
        return result

    def announce_winner(self, state: GameState):
        assert (state.game_done())

        if state.game_won():
            print(f"\nGame has been won by {state.get_next_player_to_move()}. Congratulations!\n")
        else:
            print(f"\nGame resulted in a draw\n")
        self.render_board(state)

    def get_user_input(self, prompt, input_validator):
        while True:
            response = input(prompt).upper()
            if input_validator(response):
                break
            else:
                print(prompt)

        return response

    def get_restricted_input(self, prompt, valid_responses) -> str:
        def validator(string):
            return string in valid_responses

        return self.get_user_input(prompt, validator)

    def get_nonnull_input(self, prompt):
        def validator(string):
            return len(string) > 0

        return self.get_user_input(prompt, validator)

    def get_users_yes_no_response(self, prompt):
        def y_n_validator(string):
            return (str(string).upper() == 'Y' or str(string).upper() == 'N')

        return self.get_user_input(prompt, y_n_validator)

    def init_state_from_user_input(self) -> GameState:
        player_name = self.get_nonnull_input("Please input your player name: ")
        symbol = self.get_restricted_input("Please choose letter representing your moves ('X' or 'O'): ", ["X", "O"])
        goes_first = self.get_restricted_input("Do you want to go first? (Y/N): ", ["Y", "N"])

        if goes_first:
            next_player_to_move = 1
        else:
            next_player_to_move = 0

        opponent = Player(player_name, symbol_mapping[symbol])
        if (symbol == X_CELL):
            opponent_symbol  = O_CELL
        else:
            opponent_symbol  = X_CELL
        bot = Player("game_bot", opponent_symbol, True)
        state = GameState(GameBoard(3), next_player_to_move, [opponent, bot])

        return state

    def display_game_grid(self, grid):
        print(f"\nGame Board:\n{grid.r()}")

    """
    Prompts player to enter the coordinates of a free cell where they wish to make their next move,

    Args:
        grid:  the grid where the move needs to be chosen
        player: the player making the move.

    Invariants:  the game grid must have available moves, and no established winner

    Returns: The cell with player's chosen coordinates.
    """

    def prompt_for_coords_of_next_move(self, board: GameBoard, player: Player) -> Tuple[int, int]:
        def parse_input(input_str):
            # Define a regular expression pattern to match two integers separated by non-numeric characters
            pattern = r'[^0-9]*([0-9]+)[^0-9]+([0-9]+)[^0-9]*'

            match = re.match(pattern, input_str)
            if match:
                row = int(match.group(1))
                col = int(match.group(2))
                if (row >= 0 and row < board.span and col >= 0 and col < board.span):
                    if board.grid[row, col] == OPEN_CELL:
                        return [row, col]
            return None

        def get_coords(string_input):
            return parse_input(string_input) is not None

        msg = f"\nYour move, {player.name},  Enter x,y coordinates of free cell (each coord >= 0 and < {board.span}): "
        input = self.get_user_input(msg, get_coords)
        coords = parse_input(input)
        logging.debug(f"for next move position, player {player} selected coords: {coords}")
        return (coords[0], coords[1])

    def announce_bot_player_move(self, player, row, col):
        print(f"\nPlayer {player.name}  claimed  ({row},{col}) with {reverse_mapping[player.symbol]}")


