import numpy as np
import random
import time
import sys
#import scipy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


MAX_STATE = 32
SHOWING_SYMPTOMS = (1.0-1e-8, "#C6FC60")
COLOR_GRADIENT = [(0.0, "black"), (1e-8, "#FFD9C2"), SHOWING_SYMPTOMS, (1.0, "#819073")]
zombie_map = LinearSegmentedColormap.from_list("zombies", COLOR_GRADIENT, N=MAX_STATE)
mpl.colormaps.register(zombie_map)


TickRate = 0.1


class Board :
    def __init__(self, num_cols, num_rows) :
        print("board created")
        self.num_cols = num_cols
        self.num_rows = num_rows
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

    def update_display(self, board, tickRate) :
        #print("test")
        self.ax.clear()
        plt.axis('off')
        self.ax.imshow(board, cmap="zombies", vmin=0, vmax=MAX_STATE)
        self.fig.canvas.draw_idle()

    def on_close(self, event):
        print("Stopping")
        self.open = False
        sys.exit(0)

class Pandemic :
    def __init__(self) :
        print("hello world")
        self.board_x = 32
        self.board_y = 32
        self.population_percent = 10

        self.board = Board(self.board_x,self.board_y)
        self.gui = Gui()


    def start(self) :
        print("game started")
        gamerunning = True
        self.board.print_board()
        self.gui.update_display(self.board.get_board(), TickRate)
        plt.pause(.5)

        board = self.board.get_board().copy()

        #create initial board
        for i in range(0,self.board.num_rows) :
            for j in range(0,self.board.num_cols) :
                if random.randrange(0, 100) < self.population_percent :
                    board[i][j] = 1
                else :
                    board[i][j] = 0

        #start game loop
        start_time = time.time()
        while gamerunning :

            if self.gui.open == False :
                gamerunning = False

            new_board = board.copy()
            #Movement step happens first, followed by infection step
            #Movement
            for i in range(0,self.board_x) :
                for j in range(0,self.board_y) :
                    if board[i][j] != 0 :
                        #movement
                        dir1 = random.choice([0,1])
                        dir2 = 1 - dir1
                        y_next = (j + dir1 * random.choice([1,-1])) % self.board_y
                        x_next = (i + dir2 * random.choice([1,-1])) % self.board_x
                        #Take random step
                        #If step is blocked it will stay still.
                        if board[x_next, y_next] == 0 and new_board[x_next, y_next] == 0:
                            new_board[x_next, y_next] = board[i, j]
                            new_board[i, j] = 0

            #Infection
            for i in range(0,self.board.num_rows) :
                for j in range(0,self.board.num_cols) :
                    #infection
                    if new_board[i][j] < MAX_STATE and new_board[i][j] != 0 :
                        new_board[i][j] = new_board[i][j] + 1
                    elif new_board[i][j] == MAX_STATE :
                        new_board[i][j] = MAX_STATE - random.randrange(0,MAX_STATE)

            board = new_board
            self.board.update_board(board)
            self.gui.update_display(board,TickRate)

            #Count Cell Types
            num_clean = np.count_nonzero(board == 1)
            num_zombie = np.count_nonzero(board == MAX_STATE)
            num_infected = np.count_nonzero(board) - num_clean - num_zombie
            num_total = num_infected + num_zombie + num_clean
            print(f'Clean: {num_clean}, Zombie: {num_zombie}, Infected: {num_infected}, Total: {num_total}')

            #reset time
            plt.pause(TickRate - (time.time() - start_time))
            start_time = time.time()

        plt.ioff()
        plt.show()


if __name__ == "__main__" :
    game = Pandemic()
    game.start()

