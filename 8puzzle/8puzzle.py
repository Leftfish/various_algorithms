from queue import PriorityQueue


class Board:
    def __init__(self, tiles: list) -> None:
        self.size = len(tiles)
        self.tiles = [None] * self.size**2
        self.hamming_score = 0
        self.manhattan_score = 0
        self.blank_position = None

        # convert 2D tiles to 1D array
        for i in range(self.size):
            for j in range(self.size):
                position = i * self.size + j
                if tiles[i][j] == 0:
                    self.blank_position = position
                self.tiles[position] = tiles[i][j]

        # check each tile for wrong placement, calculate distances for tiles other than the blank space
        for i in range(len(self.tiles)):
            if self.tiles[i] != i+1 and self.tiles[i] != 0:
                self.manhattan_score += abs((self.tiles[i]-1) // self.size - i // self.size) + abs((self.tiles[i]-1) % self.size - i % self.size)
                self.hamming_score += 1

    def __repr__(self) -> str:
        i = 0
        j = self.size
        to_string = ''
        while j <= len(self.tiles):
            to_string += '\t'.join(map(str, self.tiles[i:j]))
            if j != len(self.tiles):
                to_string += '\n'
            i += self.size
            j += self.size
        return to_string

    def neighbors(self) -> list:
        neighboring_boards = []

        if self.blank_position % self.size: # left
            neighboring_boards.append(self._make_neighbor(self.blank_position - 1))

        if (self.blank_position + 1) % self.size: # right
            neighboring_boards.append(self._make_neighbor(self.blank_position + 1))

        if self.blank_position - self.size >= 0: # top
            neighboring_boards.append(self._make_neighbor(self.blank_position - self.size))

        if self.blank_position + self.size < len(self.tiles): # bottom
            neighboring_boards.append(self._make_neighbor(self.blank_position + self.size))

        return neighboring_boards

    def twin(self) -> object:
        # create a "twin" array by switching tiles @ either indexes 0-1, 0-2, 1-2 or 1-3
        swapped_tiles = self.tiles[:]
        index_to_swap, index_next_to_swap = 0, 1
        if swapped_tiles[0] == 0:
            index_to_swap += 1
            index_next_to_swap += 1
        if swapped_tiles[index_next_to_swap] == 0:
            index_next_to_swap += 1
        swapped_tiles[index_to_swap], swapped_tiles[index_next_to_swap] = swapped_tiles[index_next_to_swap], swapped_tiles[index_to_swap]

        # convert to 2D and return as Board
        return Board(self._make_2d_array(swapped_tiles))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Board):
            return self.tiles == o.tiles
        return NotImplemented

    def _make_2d_array(self, array_1d: list) -> list:
        return [[array_1d[i * self.size + j] for j in range(self.size)] for i in range(self.size)]

    def _make_neighbor(self, to_swap: int) -> object:
        swapped_tiles = self.tiles[:]
        swapped_tiles[to_swap], swapped_tiles[self.blank_position] = swapped_tiles[self.blank_position], swapped_tiles[to_swap]
        return Board(self._make_2d_array(swapped_tiles))


class Node:
    def __init__(self, board: object, previous_node: object) -> None:
        self.board = board
        self.previous_node = previous_node
        self.moves = self.previous_node.moves + 1 if previous_node else 0
        self.manhattan = board.manhattan_score
        self.priority = self.manhattan + self.moves

    def __repr__(self) -> str:
        to_string = f'Current board after {self.moves} moves:\n{self.board}\n'
        to_string += 'Manhattan: {self.manhattan}\nPriority: {self.priority}\nParent board: {self.previous_node}'
        return to_string

    def __lt__(self, o: object) -> bool:
        if isinstance(o, Node):
            if self.priority < o.priority:
                return True
            elif self.priority == o.priority:
                return self.board.manhattan_score < o.board.manhattan_score
            return False
        return NotImplemented

    def is_goal(self) -> bool:
        return self.manhattan == 0


class Solver:
    def __init__(self, initial: object) -> None:
        self.solvable = False
        self.solution = []

        main_queue = PriorityQueue()
        twin_queue = PriorityQueue()
        initial_board = Board(initial)

        main_queue.put(Node(initial_board, None))
        twin_queue.put(Node(initial_board.twin(), None))

        while True:
            current_node = main_queue.get()
            twin_node = twin_queue.get()

            if current_node.is_goal() or twin_node.is_goal():
                if current_node.is_goal():
                    self.solvable = True
                break

            for neighbor in current_node.board.neighbors():
                    if current_node.previous_node and neighbor == current_node.previous_node.board:
                        continue
                    new_node = Node(neighbor, current_node)
                    main_queue.put(new_node)

            for neighbor in twin_node.board.neighbors():
                    if twin_node.previous_node and neighbor == twin_node.previous_node.board:
                        continue
                    new_node = Node(neighbor, twin_node)
                    twin_queue.put(new_node)

        while current_node.previous_node:
            self.solution.append(current_node.board)
            current_node = current_node.previous_node
        self.solution.append(current_node.board)
        self.solution.reverse()

    def moves(self) -> int:
        if not self.solvable:
            return -1
        return len(self.solution) - 1


if __name__ == "__main__":
    print("Using A* tree search to solve 8-puzzle and similar NxN puzzles...")
    print("=" * 64)

    testboards = ([[1, 2, 3], [4, 5, 6], [8, 7, 0]], [[0, 1, 3], [4, 2, 5], [7, 8, 6]], [[1, 3, 2], [4, 5, 6], [8, 7, 0]], [[1, 2, 3, 4], [5, 7, 6, 8], [9, 10, 11, 12], [13, 15, 14, 0]])

    for board in testboards:
        S = Solver(board)
        print(f"Trying to solve this {len(board)}x{len(board)} puzzle:\n{Board(board)}\n")
        if not S.solvable:
            print(f"Puzzle not solvable! (Solver.moves() returns {S.moves()})")
        else:
            print(f"Minimum number of moves to solve: {S.moves()}")
            print()
            for board in S.solution:
                print(f"{board}\n")
        print("-" * 24)
