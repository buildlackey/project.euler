from tictactoe.model import *
from tictactoe.view import *


def test_board_full():
    board = GameBoard(3)
    assert not board.full()
    assert len(board.available_moves()) == 9
    for col in range(0,3):
        for row in range(0,3):
            board.grid[row, col] =  X_CELL
    assert board.full()
    assert board.available_moves() == []


def get_state():            # return state for users bob the bot, and joe,  bob goes first
    board = GameBoard(3)
    player1 = Player("bob", O_CELL, True)
    player2 = Player("joe", X_CELL, False)
    players = [ player1, player2 ]
    return GameState(board, 0, players)

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
    state = get_state().\
        claim_cell_for_curr_player(0, 0, True).\
        claim_cell_for_curr_player(1, 2, True)
    UI().render_board(state)

    state = state.\
        claim_cell_for_curr_player(1, 1, True). \
        claim_cell_for_curr_player(0, 2, True). \
        claim_cell_for_curr_player(2, 2, True)
    UI().render_board(state)

    game_won, score= Score(state.board).value()
    assert(score == -6 and game_won)    # -6, not -3 because diagonal is 'hottest'


def test_minimax_blocks_opponent_win_on_diagonal():
    state = get_state(). \
        claim_cell_for_curr_player(1, 2, True). \
        claim_cell_for_curr_player(2, 2, True)
    UI().render_board(state)

    state = state. \
        claim_cell_for_curr_player(0, 2, True). \
        claim_cell_for_curr_player(1, 1, True)
    UI().render_board(state)


    pp = state.get_next_player_to_move()
    print(f"next up: {pp}")

    best_next_move = MinMaxStrategy().get_next_move(state)
    assert (best_next_move == (0,0))


def test_minimax_finds_winning_move_at_center():
    state = get_state()
    UI().render_board(state)
    best_next_move = MinMaxStrategy().get_next_move(state)
    assert (best_next_move == (1,1))




def test_minimax_finds_winning_move_at_center2():
    state = get_state()
    UI().render_board(state)



def test_minimax_finds_winning_move_with_3_moves_left():

    state = get_state()
    pp = state.get_next_player_to_move()
    print(f"next up: {pp}")

    
    state = state. \
        claim_cell_for_curr_player(1, 2, True). \
        claim_cell_for_curr_player(2, 2, True)
    UI().render_board(state)

    state = state. \
        claim_cell_for_curr_player(0, 2, True). \
        claim_cell_for_curr_player(1, 1, True)
    UI().render_board(state)

    state = state. \
        claim_cell_for_curr_player(0, 0, True). \
        claim_cell_for_curr_player(1, 0, True)
    UI().render_board(state)


    best_next_move = MinMaxStrategy().get_next_move(state, True)
    assert (best_next_move == (0,1))
