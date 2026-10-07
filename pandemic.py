import numpy as np
import random
#import scipy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

COLOR_GRADIENT = [(0.0, "black"), (1e-8, "#FFD9C2"), (1.0, "#819073")]
zombie_map = LinearSegmentedColormap.from_list("zombies", COLOR_GRADIENT, N=256)
mpl.colormaps.register(zombie_map)

MAX_STATE = 256


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
        self.ax.imshow(board, cmap="zombies", vmin=0, vmax=MAX_STATE)
        self.fig.canvas.draw_idle()
        plt.pause(0.05)


class Pandemic :
    def __init__(self) :
        print("hello world")
        self.board = Board(20,20)
        self.gui = Gui()

    def start(self) :
        print("game started")
        self.board.print_board()
        self.gui.update_display(self.board.get_board())
        plt.pause(.5)

        new_board = self.board.get_board().copy()
        new_board[0][1] = 1
        new_board[1][0] = 128
        new_board[1][1] = 256
        for i in range(0,self.board.num_cols) :
            for j in range(0,self.board.num_cols) :
                new_board[i][j] = random.randrange(0,256)
        self.board.update_board(new_board)
        self.board.print_board()
        self.gui.update_display(new_board)

        plt.ioff()
        plt.show()


if __name__ == "__main__" :
    game = Pandemic()
    game.start()

