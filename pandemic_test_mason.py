import random
import time

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


MAX_STATE = 32
SHOWING_SYMPTOMS = (1.0-1e-8, "#C6FC60")
COLOR_GRADIENT = [(0.0, "black"), (1e-8, "#FFD9C2"), SHOWING_SYMPTOMS, (1.0, "#819073")]
zombie_map = LinearSegmentedColormap.from_list("zombies", COLOR_GRADIENT, N=MAX_STATE)
mpl.colormaps.register(zombie_map)

# Infection parameters:
TICK_RATE = 0.1
INFECTION_CHANCE = 0.05
INCUBATION_RATE = 1

# Cell states:
EMPTY = 0
CLEAN = 1
ZOMBIE = MAX_STATE


class Board :
    def __init__(self, num_rows, num_cols) :
        print("board created")
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.board = np.zeros((self.num_rows, self.num_cols), dtype=int)

    def update_board(self, board) :
        self.board = board

    def print_board(self) :
        print(self.board)

    def get_board(self) :
        return self.board


class Gui :
    def __init__(self) :
        print("gui started")
        plt.ion()
        self.open = True
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('close_event', self.on_close)

    def update_display(self, board, tick_rate) :
        self.ax.clear()
        plt.axis('off')
        self.ax.imshow(board, cmap="zombies", vmin=0, vmax=MAX_STATE)
        self.fig.canvas.draw_idle()

    def on_close(self, event):
        print("Stopping")
        self.open = False


class Pandemic :
    def __init__(self) :
        print("hello world")
        self.num_rows = 32
        self.num_cols = 32
        self.population_percent = 30

        self.board = Board(self.num_rows, self.num_cols)
        self.gui = Gui()


    def create_first_board(self, patients=1):
        """Randomly places people, then infects 'patients' of them.

        If there are fewer people than 'patients', everyone is infected.
        """
        board = np.zeros((self.num_rows, self.num_cols), dtype=int)
        for i in range(self.board.num_rows):
            for j in range(self.board.num_cols):
                if random.randrange(0, 100) < self.population_percent :
                    board[i][j] = CLEAN

        people = np.argwhere(board != EMPTY)
        num_to_infect = min(patients, len(people))
        for y, x in random.sample(list(people), num_to_infect):
            board[y, x] = 2
        return board


    def move_people(self, board):
        """Each person tries one random step, wrapping at the edges.

        A blocked step means the person stays in place.
        """
        new_board = board.copy()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if board[i][j] != EMPTY:
                    dir1 = random.choice([0, 1])
                    dir2 = 1 - dir1
                    step_y = dir1 * random.choice([1, -1])
                    step_x = dir2 * random.choice([1, -1])
                    y_next = (i + step_y) % self.num_rows
                    x_next = (j + step_x) % self.num_cols
                    # Take random step
                    # If step is blocked it will stay still.
                    if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                        new_board[y_next, x_next] = board[i, j]
                        new_board[i, j] = EMPTY
        return new_board


    def get_neighbors(self, board, i, j):
        """Returns a cell's neighbors."""
        return [
            board[(i - 1) % self.num_rows, j],
            board[(i + 1) % self.num_rows, j],
            board[i, (j - 1) % self.num_cols],
            board[i, (j + 1) % self.num_cols],
        ]


    def spread_infection(self, board):
        """Clean people next to zombies may become infected.

        Incubating people tick one step closer to being zombies, and they
        progress faster the more infected neighbors they have.
        """
        new_board = board.copy()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Read from the old board so infections don't
                # compound in a single tick.
                state = board[i, j]
                if state == CLEAN:
                    neighbors = self.get_neighbors(board, i, j)
                    zombie_neighbors = neighbors.count(ZOMBIE)
                    if zombie_neighbors > 0:
                        # The chance of infection increases based off a
                        # persons number of zombie neighbors.
                        p = 1 - (1 - INFECTION_CHANCE) ** zombie_neighbors
                        if random.random() < p:
                            new_board[i, j] = 2
                elif 2 <= state < ZOMBIE:
                    neighbors = self.get_neighbors(board, i, j)
                    infected_neighbors = sum(n >= 2 for n in neighbors)
                    increase = 1 + INCUBATION_RATE * infected_neighbors
                    new_board[i, j] = min(ZOMBIE, state + increase)
        return new_board


    def count_states(self, board):
        """Return (clean, infected, zombie) counts."""
        num_clean = np.count_nonzero(board == CLEAN)
        num_zombie = np.count_nonzero(board == ZOMBIE)
        num_infected = np.count_nonzero(board) - num_clean - num_zombie
        return num_clean, num_infected, num_zombie


    def start(self) :
        print("game started")
        board = self.create_first_board()
        self.board.update_board(board)
        self.board.print_board()
        self.gui.update_display(board, TICK_RATE)
        plt.pause(0.5)

        #start game loop
        start_time = time.time()
        while self.gui.open:
            board = self.move_people(board)
            board = self.spread_infection(board)

            self.board.update_board(board)
            self.gui.update_display(board, TICK_RATE)

            #Count Cell Types
            clean, infected, zombie = self.count_states(board)
            total = clean + infected + zombie
            print(f"Clean: {clean},  Infected: {infected}, Zombie: {zombie}, Total: {total}")

            #reset time
            plt.pause(TICK_RATE - (time.time() - start_time))
            start_time = time.time()

        plt.ioff()
        plt.show()


if __name__ == "__main__" :
    game = Pandemic()
    game.start()