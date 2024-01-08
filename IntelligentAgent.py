"""
IntelligentAgent.py
Fall 2023 - AI
Author: Roey Elmelech
UNI: re2431
"""
from BaseAI import BaseAI
import time


class IntelligentAgent(BaseAI):
    def getMove(self, grid):
        max_depth = 0
        moveset = grid.getAvailableMoves()  # returns a list of tuples of move ([UP, DOWN, LEFT, RIGHT]) and the grid
        state, _ = self.maximize(grid, max_depth, float('-inf'), float('inf'), time.process_time())
        return state if moveset else None

    def maximize(self, grid, max_depth, alpha, beta, start):
        """
        Essentially, the player's best move
        :param grid: the current grid
        :param max_depth: IDS
        :param alpha: largest value for max
        :param beta: lowest value for min
        :param start: start time
        :return: the move and its utility
        """
        if (time.process_time() - start > 0.2) or (max_depth > 3):
            return None, self.eval(grid)

        max_child, max_utility = None, float('-inf')
        available_moves = grid.getAvailableMoves()
        available_moves.reverse()  # UP is the least desired move, reversing the order improves heuristics

        if not available_moves:  # Ed post 746
            return grid, self.eval(grid)

        for child, state in available_moves:
            _, utility = self.minimize(state, max_depth + 1, alpha, beta, start)
            if utility > max_utility:
                max_child, max_utility = child, utility
            if max_utility >= beta:
                break
            if max_utility > alpha:
                alpha = max_utility

        return max_child, max_utility

    def minimize(self, grid, max_depth, alpha, beta, start):
        """
        Essentially, the computer's response to the move
        :param grid: the current grid
        :param max_depth: IDS
        :param alpha: largest value for max
        :param beta: lowest value for min
        :param start: start time
        :return: the move and its utility
        """
        if (time.process_time() - start > 0.2) or (max_depth > 3):
            return None, self.eval(grid)

        min_child, min_utility = None, float('inf')
        available_cells = grid.getAvailableCells()

        for cell in available_cells:
            two = grid.clone()
            four = grid.clone()
            two.insertTile(cell, 2)
            four.insertTile(cell, 4)
            _, two_util = self.maximize(two, max_depth + 1, alpha, beta, start)
            _, four_util = self.maximize(four, max_depth + 1, alpha, beta, start)
            utility = (two_util * 0.9) + (four_util * 0.1)
            if utility < min_utility:
                min_child, min_utility = grid, utility
            if min_utility <= alpha:
                break
            if min_utility < beta:
                beta = min_utility

        return min_child, min_utility

    def monotonicity(self, grid):
        """
        This heuristic tries to ensure that the values of the tiles are all either
        increasing or decreasing along both the left/right and up/down directions
        :param grid: the current grid
        :return: an integer value
        """
        monotonicity = 0
        for cell in range(grid.size):
            local_monotonicity = 0
            for i in range(grid.size - 1):
                if grid.map[cell][i] >= grid.map[cell][i + 1]:
                    local_monotonicity += 1
            monotonicity += local_monotonicity / (grid.size - 1)

        return monotonicity

    def possible_mergers(self, grid):
        """
        A heuristic that checks how many possible mergers are there
        :param grid: the current grid
        :return: an integer value
        """
        possible_mergers = 0

        for neighbor1 in range(grid.size):
            for neighbor2 in range(grid.size):
                tile_value = grid.map[neighbor1][neighbor2]

                # check if the current tile has a value
                if tile_value > 0:
                    # Check adjacent tiles (up, down, left, and right)
                    neighbors = [(neighbor1 + neighbor3, neighbor2 + neighbor4)
                                 for neighbor3, neighbor4 in [(0, 1), (0, -1), (1, 0), (-1, 0)]]

                    for n1, n2 in neighbors:
                        if 0 <= n1 < grid.size and 0 <= n2 < grid.size:
                            neighbor_value = grid.map[n1][n2]

                            # If the neighbor has the same value, it's a possible merger
                            if neighbor_value == tile_value:
                                possible_mergers += 1

        return possible_mergers

    def eval(self, grid):
        """
        Calculates utilities based on heuristics
        :param grid: the current grid
        :return: the utility
        """
        tile_sum = sum(grid.map[x][y] for x in range(grid.size) for y in range(grid.size))
        empty_cells = len(grid.getAvailableCells())
        max_tile = grid.getMaxTile()
        monotonicity = self.monotonicity(grid)

        possible_mergers = self.possible_mergers(grid)

        smoothness = 0  # measures the value difference between neighboring tiles
        for x in range(grid.size):
            for y in range(grid.size):
                value = grid.map[x][y]
                neighbors = [(x + dx, y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]
                for nx, ny in neighbors:
                    if 0 <= nx < grid.size and 0 <= ny < grid.size:
                        neighbor_value = grid.map[nx][ny]
                        if neighbor_value:
                            smoothness -= abs(value - neighbor_value)

        weights = {
            'tile_sum': 3.0,
            'empty_cells': 2.0,
            'max_tile': 4.0,
            'smoothness': 0.1,
            'monotonicity': 1.0,
            'possible_mergers': 2.0
        }

        # calculates the overall utility based on the weighted sum of heuristics
        utility = (
                weights['tile_sum'] * tile_sum +
                weights['empty_cells'] * empty_cells +
                weights['max_tile'] * max_tile +
                weights['smoothness'] * smoothness +
                weights['monotonicity'] * monotonicity +
                weights['possible_mergers'] * possible_mergers
        )

        return utility
