import os
from itertools import cycle
from time import sleep

UP = ("U", -1, 0)
LEFT = ("L", 0, -1)
DOWN = ("D", 1, 0)
RIGHT = ("R", 0, 1)

WALL = 1
END = 9

PIC_WALL = '\033[34m' + '#'
PIC_RUNNER = '\033[35m' + '@'
PIC_PATH = '\033[37m' + '*'
PIC_START = '\033[33m' + 'X'
PIC_END = '\033[32m' + '$'

ANIMATION_PAUSE = 0.05


class MazeRunner:
    def __init__(self, start: tuple, maze: list) -> None:
        self.directions = cycle([UP, LEFT, DOWN, RIGHT])
        self.direction = next(self.directions)
        self.maze = maze
        self.start = start
        self.x, self.y = start[0], start[1]

        if self.maze[self.x][self.y] == WALL:
            raise ValueError("Cannot start inside a wall!")

        self.path = []

        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == END:
                    self.end = (i, j)

    def __repr__(self) -> str:
        return f"Position: {self.x}-{self.y}. Direction: {self.direction[0]}"

    def print_maze(self) -> None:
        maze_copy = [row[:] for row in self.maze]

        for coord in self.path:
            maze_copy[coord[0]][coord[1]] = PIC_PATH

        maze_copy[self.start[0]][self.start[1]] = PIC_START
        maze_copy[self.x][self.y] = PIC_RUNNER
        maze_copy[self.end[0]][self.end[1]] = PIC_END

        for row in maze_copy:
            print("".join(map(str, row)).replace("1", PIC_WALL).replace("0", " "))

    def is_way_forward(self) -> bool:
        new_x = self.x + self.direction[1]
        new_y = self.y + self.direction[2]

        return new_x >= 0 and new_x < len(self.maze) and new_y >= 0 and new_y < len(self.maze[0]) and self.maze[new_x][new_y] != WALL

    def turn_left(self) -> None:
        self.direction = next(self.directions)

    def turn_right(self) -> None:
        for _ in range(3):
            self.direction = next(self.directions)

    def step(self) -> None:
        self.x += self.direction[1]
        self.y += self.direction[2]
        self.path.append((self.x, self.y))

    def is_hand_on_right_wall(self) -> bool:
        if self.direction[0] == 'U':
            return self.y + 1 < len(self.maze[0]) and self.maze[self.x][self.y+1] == WALL

        elif self.direction[0] == 'D':
            return self.y - 1 >= 0 and self.maze[self.x][self.y-1] == WALL

        elif self.direction[0] == 'L':
            return self.x - 1 >= 0 and self.maze[self.x-1][self.y] == WALL

        elif self.direction[0] == 'R':
            return self.x + 1 < len(self.maze) and self.maze[self.x+1][self.y] == WALL

        return False

    def is_at_finish(self) -> bool:
        return self.maze[self.x][self.y] == END

    def is_any_wall_around(self) -> bool:
        if self.y + 1 < len(self.maze[0]) and self.maze[self.x][self.y+1] == WALL:
            return True

        elif self.y - 1 >= 0 and self.maze[self.x][self.y-1] == WALL:
            return True

        elif self.x - 1 >= 0 and self.maze[self.x-1][self.y] == WALL:
            return True

        elif self.x + 1 < len(self.maze) and self.maze[self.x+1][self.y] == WALL:
            return True

        return False

    def find_any_wall(self) -> None:
        if not self.is_any_wall_around():
            while self.is_way_forward():
                self.step()
            self.turn_left()

    def move(self) -> None:
        if self.is_hand_on_right_wall() and self.is_way_forward():
            self.step()

        elif self.is_hand_on_right_wall() and not self.is_way_forward():
            self.turn_left()

        elif not self.is_hand_on_right_wall():
            self.turn_right()
            if self.is_way_forward():
                self.step()

    def run_maze(self, animate=True) -> None:
        self.find_any_wall()
        while not self.is_at_finish():
            self.move()

            if animate:
                M.print_maze()
                sleep(ANIMATION_PAUSE)
                if not self.is_at_finish():
                    os.system("cls") if os.name == "nt" else os.system("clear")

def make_maze(maze: str) -> list:
    return [list(map(int, line)) for line in maze_solvable.splitlines()]

maze_solvable = '''111111111111111111111111111111111111111111111111111111
101110000000000111111001111111110111111110111000001111
101111101111011111100000001111110111101110111011011111
101101101100011111101101100000000111101110111011011011
101101101111011111101101101111011111100000000011011011
101000000011011110101111001111011111101111111111011009
101101110111011110111110001111000001101110111111011011
101101110111011110111100011111011011101111111111011011
101101110011011000000000011111011000000000111111011011
100000010111011110111111011011111011011111111000011011
101111110111000000000111001011111111000000001110111011
101110000110011110111111100000001111011111111110000011
111111111111111111111111111111111111111111111111111111'''

maze_unsolvable = '''111111111111111111111111111111111111111111111111111111
101110000000000111111001111111110111111110111000001111
101111101111011111100000001111110111101110111011011111
101101101100011111101101100000000111101110111011011011
101101101111011111101101101111011111100000000011011011
101000000011011110101111001111011111101009000111011001
101101110111011110111110001111000001101000000111011011
101101110111011110111100011111011011101111111111011011
101101110011011000000000011111011000000000111111011011
100000010111011110111111011011111011011111111000011011
101111110111000000000111001011111111000000001110111011
101110000110011110111111100000001111011111111110000011
111111111111111111111111111111111111111111111111111111'''

M = MazeRunner((1,1), make_maze(maze_solvable))
M.run_maze()
