import random
import time

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.widgets import Button, Slider

MAX_STATE = 32
POPULATION = 50  # population in percent from 0-100
BOARD_SIZE = 10
SHOWING_SYMPTOMS = (1.0 - 1e-8, "#C6FC60")
COLOR_GRADIENT = [(0.0, "black"), (1e-8, "#FFD9C2"), SHOWING_SYMPTOMS, (1.0, "#819073")]
zombie_map = LinearSegmentedColormap.from_list("zombies", COLOR_GRADIENT, N=MAX_STATE)
mpl.colormaps.register(zombie_map)

# Infection parameters:
TICK_RATE = 0.1  # Simulation speed
ZOMBIE_INFECTION_CHANCE = 0.3  # Chance of infection per zombie neighbor per tick
INFECTED_INFECTION_CHANCE = ZOMBIE_INFECTION_CHANCE / 4  # Chance of infection per infected neighbor per tick,
# (1/4 of the chance of a zombie neighbor).
INCUBATION_RATE = 1  # Rate at which infected people progress towards becoming zombies per tick,
# multiplied by the number of infected neighbors.
QUARANTINE_THRESHOLD = 0.8  # Infected Level at which cured cells begin treating infected as a zombie and infected isolate themselves

# Cell states:
EMPTY = 0  # Board cell.
CLEAN = 1  # Healthy person.
QUARANTINE = int(MAX_STATE * QUARANTINE_THRESHOLD)
ZOMBIE = MAX_STATE  # Completely infected person, who cannot be cured.

'''
Features to possibly add

zombies chase clean/infected

clean/infected run away from zombies

    create a movement direction opposite of the average relative position of neighboring zombies

clean/infected run away from eachother if difference in infection level is high enough

isolated infected can have infection go down and become cured.

isolated will distance themselves from all other cells to avoid spreading infection

'''


class Board:
    def __init__(self, num_rows, num_cols):
        print("board created")
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.board = np.zeros((self.num_rows, self.num_cols), dtype=int)

    def update_board(self, board):
        self.board = board

    def print_board(self):
        print(self.board)

    def get_board(self):
        return self.board


class Gui:
    SLIDERS = [
        # attr, label, min, max, step, format
        ("tick_rate", "Speed", 0.01, 1.0, 0.01, "%.2f"),
        ("zombie_infection_chance", "Infection chance", 0.0, 1.0, 0.01, "%.2f"),
        ("incubation_rate", "Infection rate", 0.0, 5.0, 0.1, "%.1f"),
        ("quarantine_threshold", "Quarantine threshold", 0.0, 1.0, 0.01, "%.2f"),
        ("population_percent", "Population", 1, 100, 1, "%d"),
        ("board_size", "Size", 8, 64, 1, "%d"),
    ]

    def __init__(self):
        print("gui started")
        plt.ion()
        self.open = True
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        self.buttons = {}
        self.sliders = {}
        for name, label, x in [
            ("play", "Play", 0.15),
            ("reset", "Reset", 0.35),
            ("random", "Random", 0.55),
            ("quit", "Quit", 0.75)
        ]:
            ax = self.fig.add_axes([x, 0.925, 0.12, 0.05])
            self.buttons[name] = Button(ax, label)
        #self.buttons["play"].on_clicked(self.toggle_play)
        #self.buttons["reset"].on_clicked(self.on_reset)
        #self.buttons["random"].on_clicked(self.on_random)
        #self.buttons["quit"].on_clicked(self.on_quit)

        # Sliders

    def update_display(self, board, tick_rate):
        self.ax.clear()
        plt.axis('off')
        self.ax.imshow(board, cmap="zombies", vmin=0, vmax=MAX_STATE)
        self.fig.canvas.draw_idle()

    def on_close(self, event):
        print("Stopping")
        self.open = False

    # def toggle_play(self):

    #def on_reset(self):
        #self.create_first_board()

    #def on_random(self):


    #def on_quit(self):


class Pandemic:
    def __init__(self):
        print("hello world")
        self.num_rows = BOARD_SIZE
        self.num_cols = BOARD_SIZE
        self.population_percent = POPULATION

        self.board = Board(self.num_rows, self.num_cols)
        self.gui = Gui()

    def create_first_board(self, patients=1):
        """Randomly places people, then infects 'patients' of them.

        If there are fewer people than 'patients', everyone is infected.
        """
        board = np.zeros((self.num_rows, self.num_cols), dtype=int)
        for i in range(self.board.num_rows):
            for j in range(self.board.num_cols):
                if random.randrange(0, 100) < self.population_percent:
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

                    # Cured Movement
                    if board[i][j] == CLEAN:

                        direction, _ = self.get_neighbors(board, i, j, radius=3, target=QUARANTINE)

                        step_y = -direction[0]
                        step_x = -direction[1]

                        # Take Random Step
                        if direction == [0, 0]:
                            dir1 = random.choice([0, 1])
                            dir2 = 1 - dir1
                            step_y = dir1 * random.choice([1, -1])
                            step_x = dir2 * random.choice([1, -1])

                        y_next = int((i + step_y) % self.num_rows)
                        x_next = int((j + step_x) % self.num_cols)

                        # If step is blocked it will try another random step and then stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

                    # Infected Movement
                    elif CLEAN < board[i][j] < QUARANTINE:

                        direction, _ = self.get_neighbors(board, i, j, radius=3, target=QUARANTINE)
                        step_y = -direction[0]
                        step_x = -direction[1]

                        # Take Random Step
                        if direction == [0, 0]:
                            dir1 = random.choice([0, 1])
                            dir2 = 1 - dir1
                            step_y = dir1 * random.choice([1, -1])
                            step_x = dir2 * random.choice([1, -1])

                        y_next = int((i + step_y) % self.num_rows)
                        x_next = int((j + step_x) % self.num_cols)

                        # If step is blocked it will try another random step and then stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

                    # Quarantined Movement
                    elif QUARANTINE <= board[i][j] < ZOMBIE:

                        direction, _ = self.get_neighbors(board, i, j, radius=3, target=1)

                        step_y = -direction[0]
                        step_x = -direction[1]

                        # Take Random Step
                        if direction == [0, 0]:
                            dir1 = random.choice([0, 1])
                            dir2 = 1 - dir1
                            step_y = dir1 * random.choice([1, -1])
                            step_x = dir2 * random.choice([1, -1])

                        y_next = int((i + step_y) % self.num_rows)
                        x_next = int((j + step_x) % self.num_cols)

                        # If step is blocked it will try another random step and then stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

                    # Zombie Movement
                    elif board[i][j] == ZOMBIE:
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

    def get_neighbors(self, board, i, j, radius=1, target=ZOMBIE):
        """Returns a cell's neighbors."""

        neighbors = []
        i1 = i
        j1 = j

        target_x = 0
        target_y = 0

        # Direction in [x,y]
        direction = [0, 0]

        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if (i != 0) or (j != 0):
                    check_i = (i1 + i) % self.num_rows
                    check_j = (j1 + j) % self.num_cols
                    neighbors.append(board[check_i, check_j])

                    if board[check_i, check_j] >= target:
                        target_x += i
                        target_y += j

        if (target_x != 0) and (target_y != 0):
            if abs(target_x) > abs(target_y):
                direction = [target_x / abs(target_x), 0]
            else:
                direction = [0, target_y / abs(target_y)]

        return direction, neighbors

    def spread_infection(self, board):
        """Clean people next to zombies or infected people may become infected.

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
                    _, neighbors = self.get_neighbors(board, i, j)
                    zombie_neighbors = neighbors.count(ZOMBIE)
                    clean_neighbors = neighbors.count(CLEAN)
                    board_spots = neighbors.count(EMPTY)
                    infected_neighbors = len(neighbors) - zombie_neighbors - clean_neighbors - board_spots
                    if zombie_neighbors > 0:
                        # The chance of infection increases based off a
                        # persons number of zombie neighbors.
                        p_z = 1 - (1 - ZOMBIE_INFECTION_CHANCE) ** zombie_neighbors
                        if random.random() < p_z:
                            new_board[i, j] = 2
                    if infected_neighbors > 0:
                        # The chance of infection increases based off a
                        # persons number of infected neighbors.
                        p_i = 1 - (1 - INFECTED_INFECTION_CHANCE) ** infected_neighbors
                        if random.random() < p_i:
                            new_board[i, j] = 2
                elif CLEAN < state < ZOMBIE:
                    _, neighbors = self.get_neighbors(board, i, j)
                    infected_neighbors = sum(n >= 2 for n in neighbors)
                    increase = 1 + INCUBATION_RATE * infected_neighbors
                    if (len(neighbors) - neighbors.count(EMPTY)) == 0:
                        increase = -1
                    new_board[i, j] = min(ZOMBIE, state + increase)
        return new_board

    def count_states(self, board):
        """Return (clean, infected, zombie) counts."""
        num_clean = np.count_nonzero(board == CLEAN)
        num_zombie = np.count_nonzero(board == ZOMBIE)
        num_infected = np.count_nonzero(board) - num_clean - num_zombie
        return num_clean, num_infected, num_zombie

    def start(self):
        print("game started")
        board = self.create_first_board()
        self.board.update_board(board)
        self.board.print_board()
        self.gui.update_display(board, TICK_RATE)
        plt.pause(0.5)

        # start game loop
        start_time = time.time()
        buffer_max = 20  # buffer to allow a set number of frames after board is fully clean or zombified
        buffer = 0
        while self.gui.open:
            board = self.move_people(board)
            board = self.spread_infection(board)

            self.board.update_board(board)
            self.gui.update_display(board, TICK_RATE)

            # Count Cell Types
            clean, infected, zombie = self.count_states(board)
            total = clean + infected + zombie
            print(f"Clean: {clean},  Infected: {infected}, Zombie: {zombie}, Total: {total}")

            if zombie == total or clean == total:

                if buffer < buffer_max:
                    buffer += 1
                else:
                    board = self.create_first_board()
                    buffer = 0

            # reset time
            if (TICK_RATE - (time.time() - start_time)) > 0:
                plt.pause(TICK_RATE - (time.time() - start_time))
            else:
                plt.pause(0.01)
            start_time = time.time()

        plt.ioff()
        plt.show()


if __name__ == "__main__":
    game = Pandemic()
    game.start()