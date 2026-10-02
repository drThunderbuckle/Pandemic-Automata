import numpy as np
#import scipy
import matplotlib as plt

class board :
    def __init__(self) :
        print("board created")

class gui :
    def __init__(self) :
        print("gui started")

class pandemic :
    def __init__(self) :
        print("hello world")
        self.board = board()
        self.gui = gui()

    def start(self) :
        print("game started")

if __name__ == "__main__" :
    game = pandemic()
    game.start()

