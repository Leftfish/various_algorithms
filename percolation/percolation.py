from math import sqrt
from random import randint
from statistics import mean, stdev


class WeightedQuickUniondouble_virtual_UF:
    def __init__(self, n) -> None:
        self.data = [i for i in range(n)]
        self.size = [1 for i in range(n)]
        self.components = n

    def __repr__(self) -> str:
        return f"{str(self.data)} and tree sizes {str(self.size)}. Total components: {self.components}."

    def find(self, i) -> int:
        while self.data[i] != i:
            self.data[i] = self.data[self.data[i]]  # path compression
            i = self.data[i]
        return i

    def union(self, p, q) -> None:
        i, j = self.find(p), self.find(q)

        if i == j:
            return

        if self.data[p] != self.data[q]:
            if self.size[i] < self.size[j]:
                self.data[i] = j
                self.size[j] += self.size[i]
            else:
                self.data[j] = i
                self.size[i] += self.size[j]
            self.components -= 1


class Percolation:
    NEIGHBORS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, n=5) -> None:
        if n <= 0:
            raise ValueError("Width of the matrix (n) must be an int > 0.")

        self.WIDTH = n
        self.VTOP = 0
        self.VBOTTOM = n**2 + 1

        self.number_of_open_sites = 0
        self.double_virtual_UF = WeightedQuickUniondouble_virtual_UF(self.VBOTTOM + 1)
        self.single_virtual_UF = WeightedQuickUniondouble_virtual_UF(self.VBOTTOM)
        self.open_sites = [[False for x in range(n)] for y in range(n)]

        for i in range(1, n + 1):
            self.double_virtual_UF.union(self.VTOP, i)
            self.single_virtual_UF.union(self.VTOP, i)
            self.double_virtual_UF.union(self.VBOTTOM, n * (n-1) + i)

    def __repr__(self) -> str:
        open_sites_to_str = ''
        for row in self.open_sites:
            row_to_str = ' '.join(['_' if c else 'X' for c in row])
            open_sites_to_str += row_to_str
            open_sites_to_str += '\n'
        return f"UF grid with virtual top & bottom:\n{str(self.double_virtual_UF)}\n\nOpen sites:\n{open_sites_to_str}\nPercolates: {self.percolates()}"

    def _convert_2D_to_1D(self, row, col) -> int:
        return row * self.WIDTH + col + 1

    def _is_in_matrix_range(self, row, col) -> bool:
        return row >= 0 and row < self.WIDTH and col >= 0 and col < self.WIDTH

    def is_open(self, row, col) -> bool:
        if self._is_in_matrix_range(row, col):
            return self.open_sites[row][col]
        else:
            raise ValueError

    def is_full(self, row, col) -> bool:
        if self._is_in_matrix_range(row, col):
            location = self._convert_2D_to_1D(row, col)
            return self.is_open(row, col) and self.single_virtual_UF.find(location) == self.single_virtual_UF.find(self.VTOP)
        else:
            raise ValueError

    def open(self, row, col) -> None:
        location = self._convert_2D_to_1D(row, col)
        if self._is_in_matrix_range(row, col) and not self.is_open(row, col):
            self.open_sites[row][col] = True
            self.number_of_open_sites += 1

            for neighbour_coords in self.NEIGHBORS:
                neighbour_col = row + neighbour_coords[0]
                neighbour_row = col + neighbour_coords[1]

                if self._is_in_matrix_range(neighbour_col, neighbour_row) and self.is_open(neighbour_col, neighbour_row):
                    neighbour_location = self._convert_2D_to_1D(neighbour_col, neighbour_row)
                    self.double_virtual_UF.union(location, neighbour_location)
                    self.single_virtual_UF.union(location, neighbour_location)

    def count_open_sites(self) -> int:
        return self.number_of_open_sites

    def percolates(self) -> bool:
        return self.double_virtual_UF.find(self.VTOP) == self.double_virtual_UF.find(self.VBOTTOM)


class PercolationStats:
    SIGMA = 1.96

    def __init__(self, n, trials) -> None:
        if n <= 0 or trials <= 0:
            raise ValueError

        self.trials = trials
        self.results = []

        for _ in range(trials):
            percolation = Percolation(n)
            while not percolation.percolates():
                new_row, new_col = randint(0, n-1), randint(0, n-1)
                percolation.open(new_row, new_col)
            open_sites_ratio = percolation.number_of_open_sites/n**2
            self.results.append(open_sites_ratio)

        self.sample_mean = mean(self.results)
        self.sample_stdev = stdev(self.results)

    def mean(self) -> float:
        return self.sample_mean

    def stdev(self) -> float:
        return self.sample_stdev

    def confidence_intervals(self) -> tuple:
        lo = self.sample_mean - self.SIGMA * self.sample_stdev / sqrt(self.trials)
        hi = self.sample_mean + self.SIGMA * self.sample_stdev / sqrt(self.trials)
        return (lo, hi)


def print_percolation_stats(w, trials) -> None:
    stats = PercolationStats(w, trials)
    lo, hi = stats.confidence_intervals()
    print(f"Mean:\t\t\t{stats.mean()}\nStdDev:\t\t\t{stats.stdev()}")
    print(f"Conf. intervals 95%:\t[{lo}-{hi}]")


if __name__ == "__main__":
    w, trials = 50, 100
    print(f"Simulating threshold for a {w}x{w} grid with {trials} trials...")
    print("-" * 100)
    print_percolation_stats(w, trials)
    print("-" * 100)
