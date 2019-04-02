import random
from abc import ABCMeta, abstractmethod
import pdb
from minesweeper import *
from bokeh.plotting import figure, show, output_file
import numpy as np
from itertools import compress
import matplotlib.pyplot as plt
from minesweeper.Evaluation import Evaluation
import copy

class Agent(GameAI):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.exposedSquares = {}
        self.flags = []
        self.currGrid = []
        self.numberedSquares = {}

    def init(self, config):
        """
        Initialize an AI to play a new game
        config is a GameConfig object
        return is void
        """
        self.width = config.width
        self.height = config.height
        self.exposedSquares = {}
        self.numberedSquares = {}
        self.currGrid = []
        self.get_flags()

    def adjacent(self,x,y):
        #to be an adjacent square it MUST be an unopened square and be:
        # (x-1,y+1) (x,y+1) (x+1,y+1)
        # (x-1,y)   (x,y)   (x+1,y)
        # (x-1,y-1) (x,y-1) (x+1,y-1)
        neighbours = []
        #print(self.grid)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                #so we don't go out of bounds...
                elif -1 < (x + i) < HEIGHT and -1 < (y + j) < WIDTH:
                    #print(x+i,y+j,"is not out of bounds")
                    #if its an unopened square
                    if self.currGrid[x+i][y+j] == None:
                        neighbours.append((x + i, y + j))
                        #print(x+i,y+j," is a neighbour  of ",x,y)
                

        #return the adjacent squares
        return neighbours

    def next(self):
        """
        Returns the next move as a tuple of (x,y)
        """
        #TODO: CHANGE THIS TO ACTUALLY SELECT A SAFE SQUARE
        #if the length of exposed squares is 1
        #or if the squares exposed don't have neighbours in common
        #-> we choose any square at random that is not a neighbor of the revealed
        allNeighbours = []
        for k in self.numberedSquares:
            #print("Getting adj of :",k[0],k[1])
            allNeighbours.append(self.adjacent(k[0],k[1]))
            #print("ALL NEIGHBOURS: ",allNeighbours) 
        #squares that have neighbours in common with other squares, each number corresponds to the index in the numberedsquares 
        inCommon = []
        #number of numberedsquares that have neighbours in common with other numberedsquares
        counter = 0
        #keep track of the indexes of the squares in allNeighbours
        i = 0
        for l in allNeighbours:
            temp = copy.deepcopy(allNeighbours)
            temp.remove(l)
            temp = [val for sublist in temp for val in sublist]
            if not set(l).isdisjoint(temp):
                counter+=1
                inCommon.append(i)
            i+=1

        if counter == 0:
            print("NO NEIGHBOURS IN COMMON") 
        else:
            print("THERE ARE NEIGHBOURS IN COMMON")   
        #create a temporary nested list that = allNeighbours except l
        #see if l has any neighbours in common with the rest of the lists
        #else we send in the numbered squares that share adjacents with at least one square in the exposed ones
        #so we calculate the mines 
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
        self.currGrid = game.get_state()
        for position in result.new_squares: 
            self.exposedSquares.update( {(position.x, position.y) : self.currGrid[position.x][position.y]} )
        for key,value in self.exposedSquares.items():
            if value > 0:
                self.numberedSquares.update({key : value})
    def get_flags(self):
        """
        Return a list of coordinates for known mines. The coordinates are 2d tuples.
        """
        
       
        #getting the numbered squares only, value = 0 means that its just a safe unlocked square
        
        

        print("NUMBERED SQUARES: ",self.numberedSquares)
        #numberedSquares,minesLeft,grid,gridWidth,gridHeight
        #eval1 = Evaluation(numberedSquares,MINES_COUNT,self.currGrid,WIDTH,HEIGHT)
        #flags = eval1.equationSolver()
        #print("MINES:", flags)
        return []



GAMES_COUNT=5
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
            ai.get_flags()
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
