import numpy as np
import random
import time
#import scipy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


MAX_STATE = 64
COLOR_GRADIENT = [(0.0, "black"), (1e-8, "#FFD9C2"), (1.0-1e-8, "#C6FC60"), (1.0, "#819073")]
zombie_map = LinearSegmentedColormap.from_list("zombies", COLOR_GRADIENT, N=MAX_STATE)
mpl.colormaps.register(zombie_map)


TickRate = 0.01


class Board :
    def __init__(self, num_cols, num_rows) :
        print("board created")
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.board = np.zeros((self.num_cols,self.num_rows), dtype=int)

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
        self.fig, self.ax = plt.subplots()

    def update_display(self, board) :
        #print("test")
        self.ax.clear()
        plt.axis('off')
        self.ax.imshow(board, cmap="zombies", vmin=0, vmax=MAX_STATE)
        self.fig.canvas.draw_idle()
        plt.pause(0.05)


class Pandemic :
    def __init__(self) :
        print("hello world")
        self.board = Board(20,20)
        self.gui = Gui()
        self.population_percent = 50

    def start(self) :
        print("game started")
        gamerunning = True;
        self.board.print_board()
        self.gui.update_display(self.board.get_board())
        plt.pause(.5)

        new_board = self.board.get_board().copy()
        new_board[0][1] = 1
        new_board[1][0] = 16
        new_board[1][1] = 32

        #create initial board
        for i in range(0,self.board.num_cols) :
            for j in range(0,self.board.num_cols) :
                if random.randrange(0, 100) < self.population_percent :
                    new_board[i][j] = 1
                else :
                    new_board[i][j] = 0

        #start game loop
        start_time = time.time()
        while gamerunning :
            if not (time.time() - start_time < TickRate) :

                #game logic
                for i in range(0,self.board.num_cols) :
                    for j in range(0,self.board.num_cols) :
                        if new_board[i][j] < MAX_STATE and new_board[i][j] != 0 :
                            new_board[i][j] = new_board[i][j] + 1
                        elif new_board[i][j] == MAX_STATE :
                            new_board[i][j] = MAX_STATE - random.randrange(0,MAX_STATE)


                self.board.update_board(new_board)
                self.board.print_board()
                self.gui.update_display(new_board)

                #reset time
                start_time = time.time()

        plt.ioff()
        plt.show()


if __name__ == "__main__" :
    game = Pandemic()
    game.start()

