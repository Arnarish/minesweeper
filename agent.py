import random
from abc import ABCMeta, abstractmethod
import pdb
from minesweeper import *
from bokeh.plotting import figure, show, output_file
import numpy as np
from itertools import compress
import matplotlib.pyplot as plt
from minesweeper.Evaluation import Evaluation

class Agent(GameAI):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.exposedSquares = set()
        self.flags = []


    def init(self, config):
        """
        Initialize an AI to play a new game
        config is a GameConfig object
        return is void
        """
        self.width = config.width
        self.height = config.height
        self.exposedSquares = set()
        self.exposedSquares.clear()
        self.flags.clear()



    def next(self):
        """
        Returns the next move as a tuple of (x,y)
        """
        print(game.get_state())        
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.exposedSquares:
                break
        #print('selecting point ({0},{1})'.format(x, y))
        return x, y

    def update(self, result):
        """
        Notify the AI of the result of the previous move
        result is a MoveResult object
        return is void
        """
        for position in result.new_squares:
            self.exposedSquares.add((position.x, position.y))
        #print(self.exposedSquares)

    def get_flags(self):
        """
        Return a list of coordinates for known mines. The coordinates are 2d tuples.
        """
        return self.flags



GAMES_COUNT=10
WIDTH =8
HEIGHT=8
MINES_COUNT=10

ai = Agent()
config = GameConfig(width=WIDTH, height=HEIGHT, num_mines=MINES_COUNT)
game = Game(config)
viz = GameVisualizer(2)

counter=0
lstSteps=[]
counterWins=0

while counter <GAMES_COUNT:
    stepsCount=0
    game = Game(config)
    ai.init(config)
    ai.game= game
    if viz: viz.start(game)
    while not game.is_game_over():
        coords = ai.next()
        result = game.select(*coords)
        if result is None:
            continue
        if not result.explosion:
            stepsCount+=1
            ai.update(result)
            game.set_flags(ai.get_flags())
            if game.num_exposed_squares == game.num_safe_squares:
                print("HORRRRRRRRRRRAAAY")
                if viz: viz.update(game)
                counterWins+=1
        else:
            lstSteps.append(stepsCount)
            print("EXPLOSION")
        #print(np.asarray(game.get_state()))
        #print("\n")
        if viz: viz.update(game)
    if viz: viz.finish()
    counter+=1


# plt.hist(lstSteps,normed=0,bins=np.max(lstSteps),edgecolor='black')
# plt.show()
# TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
# p1 = figure(tools=TOOLS, toolbar_location="above",
#     title="Trained Agent 1mMem (GAMES_COUNT: ) "+str(GAMES_COUNT)+" . " +str(counterWins) +" Wins.",
#     logo="grey",background_fill_color="#E8DDCB")
# hist, edges = np.histogram(np.asarray(lstSteps), density=False, bins=np.max(lstSteps))
# p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],fill_color="#036564", line_color="#033649")
# p1.legend.location = "center_right"
# p1.legend.background_fill_color = "darkgrey"


# show(p1)
