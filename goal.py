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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    # TODO: Recheck

    # Randomly select an x to select which goal to use
    x = random.randint(1, 2)
    result = []
    colours = COLOUR_LIST.copy()
    random.shuffle(colours)

    if x == 1:
        for _ in range(num_goals):
            colour = colours.pop()
            goal = PerimeterGoal(colour)
            result.append(goal)

    else:
        for _ in range(num_goals):
            colour = colours.pop()
            goal = BlobGoal(colour)
            result.append(goal)

    return result


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    # TODO: Recheck

    num_cells = 2 ** (block.max_depth - block.level)

    result = []

    if len(block.children) == 0:

        for i in range(num_cells):
            row = []
            for j in range(num_cells):
                row.append(block.colour)
            result.append(row)

    else:
        upper_right = _flatten(block.children[0])
        upper_left = _flatten(block.children[1])
        lower_left = _flatten(block.children[2])
        lower_right = _flatten(block.children[3])

        # Making result the board that will be appended with the correct values
        for i in range(num_cells):
            row = []
            for j in range(num_cells):
                row.append(None)
            result.append(row)

        quadrant_size = num_cells // 2

        for i in range(num_cells):
            for j in range(num_cells):

                if (i < quadrant_size) and (j < quadrant_size):
                    # Considering top left quadrant now
                    result[i][j] = upper_left[i][j]

                elif i < quadrant_size <= j:
                    # Considering the lower left quadrant now
                    result[i][j] = lower_left[i][j - quadrant_size]

                elif i >= quadrant_size > j:
                    # Considering the upper right quadrant now
                    result[i][j] = upper_right[i - quadrant_size][j]

                elif (i >= quadrant_size) and (j >= quadrant_size):
                    # Considering the lower right quadrant now
                    result[i][j] = \
                        lower_right[i - quadrant_size][j - quadrant_size]

    return result


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """Goal where the score is calculated based on the number of cells on
     the perimeter with target colour
     """

    def score(self, board: Block) -> int:
        """Scores the grid based on the rules of a perimeter goal"""

        # TODO: Recheck
        # We need to score according to the the number of unit cells
        # on the outer edges of the Block object <board>
        total_score = 0
        flat_version = _flatten(board)
        # We will compare the flattened version
        # with the desired colour of the block.

        n = len(flat_version)

        for i in range(n):
            # First, checking the upper edge
            if flat_version[i][0] == self.colour:
                # Keeping j constant to 0, ie: we're at the top!
                total_score += 1

            if flat_version[i][n - 1] == self.colour:
                # Keeping j constant at (n - 1) to get the last
                # column, and varying i to find .
                total_score += 1

            if flat_version[0][i] == self.colour:
                # Keeping x constant to check the sides, here - left-most.
                total_score += 1

            if flat_version[n - 1][i] == self.colour:
                # Similarly, right-most edge.
                total_score += 1

        return total_score

    def description(self) -> str:
        # TODO: Make shorter
        colour = colour_name(self.colour)

        result = f'Get points for colour: {colour} ' \
                 f'on the perimeter of the board'

        return result


class BlobGoal(Goal):
    """A type of goal where score is calcualted by the largest blob of
    target colour.
    """

    def score(self, board: Block) -> int:
        """Returns the score for the blob goal"""
        # TODO: Recheck

        # First flatten the board to make life easier
        flattened_board = _flatten(board)
        n = len(flattened_board)

        visited = []

        # iterating through the cells in the flattened tree, and finding out,
        # for each cell, what size of blob is it a part
        # of (if it is part of a blob of the target colour).
        for _ in range(n):
            row = []
            for __ in range(n):
                row.append(-1)
            visited.append(row)

        score_list = []
        for x in range(n):
            for y in range(n):

                # check if the current cell is in the largest connected blob
                score = self._undiscovered_blob_size((x, y),
                                                     flattened_board,
                                                     visited)
                score_list.append(score)

        return max(score_list)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        # TODO: Recheck
        # Assign x and y coordinates of position to variables to simplify code
        x = pos[0]
        y = pos[1]

        board_length = len(board)

        if x >= board_length or y >= board_length or x < 0 or y < 0 or \
                visited[x][y] != -1:
            # Checks if out of bounds or visited before (visited[x][y] == -1)
            return 0

        elif board[x][y] != self.colour:
            # From the previous if statement,
            # We know position is in bounds and is not visited before.

            visited[x][y] = 0
            return 0

        else:
            # Since the else says that the cell has not been
            # visited, and has just been discovered it should be set to 1
            visited[x][y] = 1

            # Target colour matches and the cell has been visited.
            total = 1

            # Traverse up.
            total += self._undiscovered_blob_size((x, y - 1), board, visited)

            # Traverse down
            total += self._undiscovered_blob_size((x, y + 1), board, visited)

            # Traverse left
            total += self._undiscovered_blob_size((x - 1, y), board, visited)

            # Traverse right
            total += self._undiscovered_blob_size((x + 1, y), board, visited)

            return total

    def description(self) -> str:
        # TODO: Make shorter
        colour = colour_name(self.colour)

        result = f'Connect as many blocks of colour: {colour} touching sides' \
                 f' (not corners).'

        return result


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
