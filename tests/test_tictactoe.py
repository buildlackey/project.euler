from  src.tictactoe.model import *
from  src.tictactoe.view import *

from pprint import pprint

import pytest


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

def test_tracking_of_user_moves():
    state = get_state()
    saw_victory = False
    for row in range(0,3):
        for col in range(0,3):
            UI().render_board(state)
            state.update_board(row, col, state.peek_next_player_to_move())
            if (state.game_won()):
                assert(state.winner() == state.get_player_who_moved_last())
            saw_victory = True
            state.get_next_player_to_move()     # bump
    assert(saw_victory)

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



def test_minimax_finds_winning_move():
    state = get_state()
    for row in range(0,2):
        for col in range(0,3):
            state.update_board(row, col, state.peek_next_player_to_move())
            state.get_next_player_to_move()     # bump


    UI().render_board(state)


    who=state.peek_next_player_to_move()
    pprint(who.__repr__())

    best_next_move = MinMaxStrategy().get_next_move(state)
    print(f"best_next_move: {best_next_move}")


def test_minimax_finds_winning_move2():
    state = get_state()
    for row in range(0,3):
        for col in range(0,3):
            if (row,col) != (2,2):
                state.update_board(row, col, state.peek_next_player_to_move())
                state.get_next_player_to_move()     # bump


    UI().render_board(state)


    who=state.peek_next_player_to_move()
    pprint(who.__repr__())

    best_next_move = MinMaxStrategy().get_next_move(state)
    assert (best_next_move == (2,2))
