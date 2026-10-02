import numpy as np
#import scipy
import matplotlib.pyplot as plt

class board :

    def __init__(self, num_cols, num_rows) :
        print("board created")
        self.num_col = num_cols
        self.num_row = num_rows
        self.board = np.zeros((self.num_col,self.num_row),int)

    def updateBoard(self, board) :
        self.board = board

    def printBoard(self) :
        print(self.board)

    def getBoard(self) :
        return self.board

class gui :

    def __init__(self) :
        print("gui started")
        self.fig, self.ax = plt.subplots()

    def createDisplay(self, board) :

        self.ax.imshow(board,cmap='vanimo')
        print(board)
        plt.show()
        

    def updateDisplay(self, board) :
        #print("test")
        self.ax.clear()
        self.ax.imshow(board,cmap='vanimo')
        plt.show()


class pandemic :

    def __init__(self) :
        print("hello world")
        self.board = board(2,2)
        self.gui = gui()

    def start(self) :
        print("game started")
        self.board.printBoard()
        self.gui.createDisplay(self.board.getBoard())
        new_board = self.board.getBoard()
        new_board[0][0] = 1
        new_board[1][0] = 2
        self.board.updateBoard(new_board)
        self.board.printBoard()
        self.gui.updateDisplay(new_board)

if __name__ == "__main__" :
    game = pandemic()
    game.start()

