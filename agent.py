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
        self.exposedSquares.clear()
        self.numberedSquares = {}
        self.numberedSquares.clear()
        self.flags = []
        self.flags.clear()
        self.currGrid = game.get_state()
        #self.currGrid.clear()
        self.mines = []
        self.mines.clear()
        self.mineCount = config.num_mines
        self.minesLeft = self.mineCount
        self.safeSquareCount = game.num_safe_squares
        self.exploredSquares = 0
        self.safeSquares = []
        self.certainBombs = []
        self.forbiddenSquares = []
        self.nonExposedSquares = []
        self.getNonExposed()
       

    def checkForCertainBombs(self):
        for x in range(0,self.width-1):
            for y in range(0,self.height-1):
                #print("X,Y:",x,y)
                if self.currGrid[x][y] == None and self.isLonely(x,y):
                    self.certainBombs.append((x,y))


    def isLonely(self,x,y):
        #lonely means only numbered squares for adjacent squares or out of the adjacent 1 is nonexposed and res is numbered
        friendsCount = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                #so we don't go out of bounds...
                elif -1 < (x + i) < self.height and -1 < (y + j) < self.width:
                    if self.currGrid[x+i][y+j] == None:
                        friendsCount+= 1
                    if friendsCount > 1:
                        return False
        #print(x,y," is a loner!")
        return True

    def adjacent(self,x,y):
        #to be an adjacent square it MUST be an unopened square and be:
        # (x-1,y+1) (x,y+1) (x+1,y+1)
        # (x-1,y)   (x,y)   (x+1,y)
        # (x-1,y-1) (x,y-1) (x+1,y-1)
        neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                #so we don't go out of bounds...
                elif -1 < (x + i) < self.height and -1 < (y + j) < self.width:
                    #print(x+i,y+j,"is not out of bounds")
                    #if its an unopened square
                    if self.currGrid[x+i][y+j] == None:
                        neighbours.append((x + i, y + j))
                        #print(x+i,y+j," is a neighbour  of ",x,y)
        #return the adjacent squares
        if len(neighbours) == self.numberedSquares.get((x,y)):
            for n in neighbours:
                self.certainBombs.append(n)
            return []
        return neighbours

    def next(self):
        """
        Returns the next move as a tuple of (x,y)
        """
        #print(self.currGrid)
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
         
        self.adjSafeSquares(allNeighbours)
        inCommon = []
        #number of numberedsquares that have neighbours in common with other numberedsquares
        counter = 0
        #keep track of the indexes of the squares in allNeighbours
        i = 0
        #create a temporary nested list that = allNeighbours except l
        #see if l has any neighbours in common with the rest of the lists
        #else we send in the numbered squares that share adjacents with at least one square in the exposed ones
        #so we calculate the mines
        for l in allNeighbours:
            temp = copy.deepcopy(allNeighbours)
            temp.remove(l)
            temp = [val for sublist in temp for val in sublist]
            if not set(l).isdisjoint(temp):
                counter+=1
                inCommon.append(i)
                
            i+=1
        #print("ALL NEIGHBOURS:",allNeighbours)
        #print("isCommon:",inCommon)
        #Find and update the known mines
        #Only required if we do not know of all mines
        self.findMines(inCommon)
        self.clean()
        self.forbiddenSquares = self.mineNeighbours()
        #No mines known, selecting a random point with some logic
        if len(self.safeSquares) != 0:
            print("Selecting safe square: ", self.safeSquares[-1])
            self.exploredSquares +=1
            return self.safeSquares.pop() 

        elif len(self.flags) == 0:
            self.exploredSquares +=1   
            return self.selectSafe()

        #Game ongoing, using some logic to choose a point and gain more information on the board
        elif self.minesLeft >=0:
            self.exploredSquares +=1
            return self.selectSafe()

        else:
            self.exploredSquares +=1
            return self.selectSafe()
    def selectSafe(self):
        length = len(self.nonExposedSquares)-1
        while True:
            i = random.randint(0,length)
            xy = self.nonExposedSquares[i]
            if xy not in self.exposedSquares and xy not in self.flags and xy not in self.forbiddenSquares:
                print("XY is: ",xy)
                break
        return xy
        """
        for n in self.nonExposedSquares:
            if n not in self.exposedSquares and n not in self.flags and n not in self.forbiddenSquares:
                return n"""
                
        

    def getNonExposed(self):
        self.nonExposedSquares = []
        for x in range(0,self.width):
            for y in range(0,self.height):
                if self.currGrid[x][y] == None:
                    self.nonExposedSquares.append((x,y))


    def findMines(self, inCommon):
        #print("getting flags for...")
        #print("NUMBERED SQUARES: ",self.numberedSquares)
        #print("CURRENT GRID: ",self.currGrid)
        i = 0
        relevantNumberedSquares = {}
        for k,v in self.numberedSquares.items():
            if i in inCommon:
                relevantNumberedSquares.update({k : v})
            i+=1
        self.minesLeft = self.mineCount - len(self.flags)
        eval1 = Evaluation(relevantNumberedSquares,self.minesLeft,self.currGrid,self.width,self.height)
        tempFlags = eval1.equationSolver()
        #print("TEMP FLAGS: ", tempFlags)

        self.checkForCertainBombs()
        self.flags = tempFlags
        for c in self.certainBombs:
            if c not in self.flags:
                self.flags.append(c)
        self.minesLeft = self.mineCount - len(self.flags)
        #print("MINES TO GO: ",self.minesLeft)
        #print("MINES:", self.flags)

    def clean(self):
        for x in self.safeSquares:
            if x in self.flags:
                #print("Removing ",x," from safe squares as it's a mine")
                self.safeSquares.remove(x)

    def adjSafeSquares(self, neighbours):
        i = 0
        #get the number of neighbours that are bombs
        #if that number is equal to the val of the numbered square
        #we mark the rest of the squares as safe
        #remove the numbered square because the mines have all been found
        toDelete = []
        for key, val in self.numberedSquares.items():
            countNeighbours = 0
            possibleSafe = []
            #print(neighbours[i])
            for n in neighbours[i]:
                if(n in self.flags):
                    countNeighbours += 1
                else:
                    possibleSafe.append(n)
            if countNeighbours == val:
                toDelete.append(key)
                for p in possibleSafe:
                    self.safeSquares.append(p)
            i +=1
        if len(toDelete) > 0:
            for t in toDelete:
                self.numberedSquares.pop(t)

    def mineNeighbours(self):
        #print("Finding mine neighbours")
        if len(self.flags) == 0:
            return []
        mineNeighbours = []
        for mine in self.flags:
            #print(mine)
            tmp = self.adjacent(mine[0],mine[1])
            for pos in tmp:
                mineNeighbours.append(pos)
        return tuple(mineNeighbours)

    def update(self, result):
        """
        Notify the AI of the result of the previous move
        result is a MoveResult object
        return is void
        """
        self.currGrid = game.get_state()
        self.getNonExposed()
        for position in result.new_squares: 
            self.exposedSquares.update( {(position.x, position.y) : self.currGrid[position.x][position.y]} )
        for key,value in self.exposedSquares.items():
            if value > 0:
                self.numberedSquares.update({key : value})
       
                
    def get_flags(self,inCommon):
        """
        Return a list of coordinates for known mines. The coordinates are 2d tuples.
        """
        #getting the numbered squares only, value = 0 means that its just a safe unlocked square
        #print("NUMBERED SQUARES: ",self.numberedSquares)
        #numberedSquares,minesLeft,grid,gridWidth,gridHeight
        
        return self.flags



GAMES_COUNT=5
WIDTH =9
HEIGHT=9
MINES_COUNT=10

ai = Agent()
config = GameConfig(width=WIDTH, height=HEIGHT, num_mines=MINES_COUNT)
game = Game(config)
viz = None#GameVisualizer(2)

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
            game.set_flags(ai.flags)
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

print("Wins: ", counterWins)

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
