"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    # TODO: Recheck
    total_num = num_human + num_random + len(smart_players)
    result = []
    goals = generate_goals(total_num)

    for i in range(num_human):
        goal = goals[i]
        player = HumanPlayer(i, goal)

        result.append(player)

    for i in range(num_human, num_human + num_random):
        goal = goals[i]
        player = RandomPlayer(i, goal)

        result.append(player)

    for i in range(len(smart_players)):
        x = num_human + num_random + i
        goal = goals[x]
        difficulty = smart_players[i]

        player = SmartPlayer(x, goal, difficulty)
        result.append(player)

    return result


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    # TODO: Implement me
    location_x = location[0]
    location_y = location[1]

    position_x = block.position[0]
    position_y = block.position[1]
    size = block.size

    # position_x and position_y is left_most and top_most of the range
    if position_x <= location_x < (position_x + size) and \
            position_y <= location_y < (position_y + size):

        if len(block.children) == 0:
            # Represents the case where it is a leaf before desired level
            # or max_depth is reached (this is deepest block)
            return block

        elif block.level == level:
            # Desired depth is reached
            return block

        # Now we need to recursively call on a child block. This means we have
        # to figure out which quadrant contains location and only search for the
        # corresponding child block.
        # We can do so by using a for loop over children with an if condition
        else:
            for child in block.children:
                child_x = child.position[0]
                child_y = child.position[1]

                if child_x <= location_x < (child_x + child.size) and \
                        child_y <= location_y < (child_y + child.size):
                    return _get_block(child, location, level)

    else:
        return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """Player type that makes random moves"""
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def _get_valid_moves(self, board: Block) -> \
            List[Optional[Tuple[str, Optional[int], Block], int]]:
        """Return a list of valid moves for the board with what score they have
        """
        valid_moves = []

        if board.create_copy().rotate(ROTATE_CLOCKWISE[1]):
            valid_moves.append(((ROTATE_CLOCKWISE[0],
                                 ROTATE_CLOCKWISE[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().rotate(ROTATE_COUNTER_CLOCKWISE[1]):
            valid_moves.append(((ROTATE_COUNTER_CLOCKWISE[0],
                                 ROTATE_COUNTER_CLOCKWISE[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().swap(SWAP_HORIZONTAL[1]):
            valid_moves.append(((SWAP_HORIZONTAL[0],
                                 SWAP_HORIZONTAL[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().swap(SWAP_VERTICAL[1]):
            valid_moves.append(((SWAP_VERTICAL[0],
                                 SWAP_VERTICAL[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().smash():
            valid_moves.append(((SMASH[0],
                                 SMASH[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().paint(self.goal.colour):
            valid_moves.append(((PAINT[0],
                                 PAINT[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().combine():
            valid_moves.append(((COMBINE[0],
                                 COMBINE[1], board),
                                self.goal.score(board.create_copy())))

        return valid_moves

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        valid_moves = self._get_valid_moves(board)

        if len(valid_moves) > 0:
            # tup contains (move, score)
            tup = random.choice(valid_moves)
            move = tup[0]

        else:
            move = (PASS[0], PASS[1], board)

        self._proceed = False  # Must set to False before returning!
        return move


class SmartPlayer(Player):
    """Player type that makes educated moves"""
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def _get_valid_moves(self, board: Block) -> \
            List[Optional[Tuple[str, Optional[int], Block], int]]:
        """Return a list of valid moves for the board with what score they have
        """
        valid_moves = []

        if board.create_copy().rotate(ROTATE_CLOCKWISE[1]):
            valid_moves.append(((ROTATE_CLOCKWISE[0],
                                 ROTATE_CLOCKWISE[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().rotate(ROTATE_COUNTER_CLOCKWISE[1]):
            valid_moves.append(((ROTATE_COUNTER_CLOCKWISE[0],
                                 ROTATE_COUNTER_CLOCKWISE[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().swap(SWAP_HORIZONTAL[1]):
            valid_moves.append(((SWAP_HORIZONTAL[0],
                                 SWAP_HORIZONTAL[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().swap(SWAP_VERTICAL[1]):
            valid_moves.append(((SWAP_VERTICAL[0],
                                 SWAP_VERTICAL[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().smash():
            valid_moves.append(((SMASH[0],
                                 SMASH[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().paint(self.goal.colour):
            valid_moves.append(((PAINT[0],
                                 PAINT[1], board),
                                self.goal.score(board.create_copy())))

        if board.create_copy().combine():
            valid_moves.append(((COMBINE[0],
                                 COMBINE[1], board),
                                self.goal.score(board.create_copy())))

        return valid_moves

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        # TODO: Recheck

        if not self._proceed:
            return None  # Do not remove

        valid_moves = self._get_valid_moves(board)

        if len(valid_moves) > 0:
            random.shuffle(valid_moves)
            to_pick = []
            for _ in range(self._difficulty):
                to_pick.append(valid_moves.pop())

            best_score = self.goal.score(board)
            best_move = (PASS[0], PASS[1], board)

            for move, score in valid_moves:
                if score > best_score:
                    best_score = score
                    best_move = move

            self._proceed = False  # Must set to False before returning!
            return best_move

        else:
            self._proceed = False
            return PASS[0], PASS[1], board


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
