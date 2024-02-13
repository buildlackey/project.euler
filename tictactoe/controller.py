from tictactoe.view import *



"""
Sets up the grid, prompts the external player for their name, preferred game symbol ('x' or 'o'), 
and whether to go first.   For each game round the controller will loop through process of getting players 
moves until a winning move or draw (no more positions open on board) is detected.  Upon conclusion of each game
the external player has the option of continuing for another round of play.
"""
class GameSessionController:

    def __init__(self):
        self.ui = UI()
        #self.state = self.ui.init_state_from_user_input()
        self.state = get_state()
        self.bot_strategy = MinMaxStrategy()

    def clear_grid(self):
        self.grid = GameBoard(3)

    def run(self):
        while True:
            self.clear_grid()

            while not self.state.winner():
                self.ui.render_board(self.state)
                player = self.state.get_next_player_to_move()
                if player.is_bot_player:
                    row, col = self.bot_strategy.get_next_move(self.state, player)
                    self.state.board.update_cell(row, col, player.symbol)
                    self.ui.announce_bot_player_move(player, row, col)  # shows move the AI chose
                else:
                    row, col = self.ui.prompt_for_coords_of_next_move(self.state.board, player)
                    self.state.board.update_cell(row, col, player.symbol)

                if self.state.game_done():
                    self.ui.announce_winner(self.state)
                    if (self.ui.get_users_yes_no_response("\nPlay again? (y/n)") == 'N'):
                        return


def get_state():
    board = GameBoard(3)
    player1 = Player("bob", O_CELL, True)
    player2 = Player("joe", X_CELL, False)
    players = [ player1, player2 ]
    state = GameState(board, 0, players)
    return state


if __name__ == "__main__":
    GameSessionController().run()

