from tictactoe.model import *
from tictactoe.view import *


def test_board_full():
    board = GameBoard(3)
    assert not board.full()
    assert len(board.available_moves()) == 9
    for col in range(0,3):
        for row in range(0,3):
            board.update_cell(row, col, X_CELL)
    assert board.full()
    assert board.available_moves() == []


def get_state():
    board = GameBoard(3)
    player1 = Player("bob", O_CELL, True)
    player2 = Player("joe", X_CELL, False)
    players = [ player1, player2 ]
    state = GameState(board, 0, players)

    assert(state.get_next_player_to_move() == player1)   # bump pointer to other player
    assert(state.get_next_player_to_move() == player2)   # bump pointer to other player
    assert(state.peek_next_player_to_move() == player1)  # check with no bump

    return state

def test_getting_game_state_from_user_input(monkeypatch):
    responses = ["joe", "X", "Y"]

    def mock_input(prompt):
        nonlocal responses
        response = responses.pop(0)
        return response
    monkeypatch.setattr('builtins.input', mock_input)

    ui = UI()
    state = ui.init_state_from_user_input()

    assert(not state.board.full())
    assert(state.players[0].name == 'JOE')
    assert(not state.players[0].is_bot_player)
    assert(state.players[1].name == 'game_bot')
    assert(state.players[1].is_bot_player)



def test_correct_score_for_win_on_diagonal():
    state = get_state()
    state.update_board(0, 2, state.peek_next_player_to_move())
    state.update_board(1, 1, state.peek_next_player_to_move())
    state.update_board(2, 0, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump
    state.update_board(0, 0, state.peek_next_player_to_move())

    UI().render_board(state)
    game_won, score= Score(state.board).value()
    assert(score == -6 and game_won)    # -6, not -3 because diagonal is 'hottest'


def test_minimax_blocks_opponent_win_on_diagonal():
    state = get_state()
    state.update_board(0, 0, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    state.update_board(0, 1, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    state.update_board(2, 2, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    state.update_board(0, 2, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    UI().render_board(state)
    best_next_move = MinMaxStrategy().get_next_move(state, state.peek_next_player_to_move())
    assert (best_next_move == (1,1))


def test_minimax_finds_winning_move_at_center():
    state = get_state()
    state.update_board(0, 0, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    state.update_board(0, 1, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    state.update_board(2, 2, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    state.update_board(0, 2, state.peek_next_player_to_move())
    state.get_next_player_to_move()     # bump

    UI().render_board(state)
    best_next_move = MinMaxStrategy().get_next_move(state, state.peek_next_player_to_move())
    assert (best_next_move == (1,1))



def test_minimax_finds_winning_move_with_one_move_left():
    state = get_state()
    for row in range(0,3):
        for col in range(0,3):
            #if (row,col) != (2,2) and (row,col) != (2,0) :
            if (row,col) != (2,2):
                state.update_board(row, col, state.peek_next_player_to_move())
                state.get_next_player_to_move()     # bump

    player = state.peek_next_player_to_move()
    symbol = reverse_mapping[player.symbol]
    print(f"rendering board with next player up {player.name} using {symbol}")
    UI().render_board(state)

    best_next_move = MinMaxStrategy().get_next_move(state, state.peek_next_player_to_move(), True)
    assert (best_next_move == (2,2))
