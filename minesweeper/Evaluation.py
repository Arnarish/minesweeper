
import itertools
import numpy as np
import numpy.linalg as la
import copy
class Evaluation:
    def __init__(self,numberedSquares,minesLeft,grid,gridWidth,gridHeight):
        self.numberedSquares = numberedSquares #map where x,y is the key and the number is the value
        self.minesLeft = minesLeft #int number of mines
        self.grid = grid #the grid right now
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.flags = []

    def init(self, numberedSquares, minesLeft, grid, gridWidth, gridHeight):
        self.numberedSquares = numberedSquares #map where x,y is the key and the number is the value
        self.minesLeft = minesLeft #int number of mines
        self.grid = grid #the grid right now
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.flags = []

    def setGrid(self, grid):
        self.grid = grid

    def setMines(self, mines):
        self.minesLeft = mines

    def getAdjacent(self,x,y):
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
                elif -1 < (x + i) < self.gridHeight and -1 < (y + j) < self.gridWidth:
                    #print(x+i,y+j,"is not out of bounds")
                    #if its an unopened square
                   # print(grid[x+i][y+j])
                    if self.grid[x+i][y+j] == None:
                        #print(grid[x+i][y+j])
                        neighbours.append((x + i, y + j))
                        #print(x+i,y+j," is a neighbour  of ",x,y)
                

        #return the adjacent squares
        return neighbours

    def listOfZeros(self,n,m):
        #makes a list of lists of zeros of length n where each list contains m zeros
        return [[0]*m] * n

    def getEquations(self,neighbours,variables,matrixA):
        #print("VARIABLES: ",variables)
        #print("NEIGHBOURS: ",neighbours)
       
        #if I didn't make a copy of matrixA, when changing the 0's to 1's there was a conflict
        #where the matrix would end up full of 1's
        matrixB = np.array(matrixA)
        print(matrixB)
        for i in range(0,len(neighbours)):
            for j in range(0,len(variables)):
                if variables[j] in neighbours[i] :
                    print(variables[j]," is in ",neighbours[i])
                    print("changing position ",i,j," on the list")
                    matrixB[i][j] = 1
            if self.isSingular(matrixB[i]):
               tmp = matrixB.tolist()
               tmp.remove(tmp[i])
               matrixB = np.array(tmp)
        #if the variable is an adjacent to the numbered square then it counts towards its equation 
        print(matrixB)

        return matrixB

    def isSingular(self, list):
        count = 0
        if list.all() == 0:
            return True
        for x in list:
            if x==1:
                count += 1
        if count == 1:
            return True
        return False

    def removeDuplicates(self, matrix, r):
        tmp = np.unique(matrix,axis=0)
        #tmp = matrix.tolist()
        return tmp, r

    def removeSingularOnes(self, matrix,r):
        """
        for x in range(0,len(matrix)):
            if matrix[x].count(1) == 1: 
                matrix.remove(matrix[x])
                r.remove(r[x])
        """
        return matrix, r



    def equationSolver(self):
        #to make an equation of the form x0,x1,...,xn; n will be the highest 
        #number of adjacent squares from a numberedSquare 
        listOfNeighbours = []
        matrixA = []
        variables = [] #variables for the equations (every existing adjacent for each numberedsquare, no duplicates)
        # 1. get foreach the list of adjacent squares for each numbered square->getAdjacent(x,y)
        results = []
        for key, val in self.numberedSquares.items():
            #print("Get adjacent of: ",item[0],item[1])
            temp = self.getAdjacent(key[0],key[1])
            #print(item[0],item[1]," has ",len(temp)," neighbours")
            if temp not in listOfNeighbours:
                listOfNeighbours.append(temp)
                results.append(val)
        # 2. make a list of variables for the equations
        variables = list(dict.fromkeys(itertools.chain(*listOfNeighbours)))
        print("Variables: ",variables)
        # 3. create a list of lists, where the inner lists are filled with 0s -> listOfZeros(n)
        matrixA = self.listOfZeros(len(listOfNeighbours),len(variables))
        print("Matrix A: ",matrixA)
        # 4. fill the corresponding list with 1s where the 1s are the adjacent squares
        # and are of length of n (list1)
        matrixA = self.getEquations(listOfNeighbours,variables,matrixA)
        print("Matrix A: ",matrixA)
        # 5. the squares value goes into a seperate list (list2)
        print("RESULTS: ",results)
        # 6. calculate the np.linalg.solve(list1,list2)
        #print(matrixA)
        #print(results)
        """
        results = [2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1]
        matrixA = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0],  
                    [0, 1, 1, 1, 0, 0, 0, 0, 0],   
                    [0, 0, 1, 1, 1, 0, 0, 0, 0],    
                    [0, 0, 0, 0, 0, 1, 1, 1, 0],   
                    [0, 0, 0, 0, 0, 0, 1, 1, 0],   
                    [0, 0, 0, 0, 0, 0, 0, 1, 0],   
                    [0, 0, 0, 0, 0, 0, 0, 1, 0],   
                    [1, 0, 0, 0, 0, 0, 0, 0, 0],    
                    [1, 1, 0, 0, 0, 0, 0, 0, 0],   
                    [1, 0, 0, 0, 0, 0, 0, 0, 0],   
                    [0, 0, 0, 1, 1, 1, 1, 0, 1]])
        """
        #matrixA, results = self.removeDuplicates(matrixA, results)
        #matrixA, results = self.removeSingularOnes(matrixA, results)
        print("2. Matrix A: ",matrixA)
        print("2. RESULTS: ",results)

        minesSolved = np.linalg.solve(matrixA,results)
        # 7. where there is a 1, means that:
        print("Mines: ",minesSolved)
        """for k in range(0, len(minesSolved)):
            if minesSolved[k] == 1:
                self.flags.append(variables[k])"""
        # E.G. if we have only 3 adjacent squares ([1,0,0][0,1,0][0,0,1])
        # and the result is [1,0,0] then that means the first square has a bomb, rest don't  
        #print("MINES: "+flags)
        return self.flags

"""
numberedSquares =  {(2, 0): 1, (2, 1): 2, (2, 2): 1, (0, 3): 1, (1, 3): 1, (2, 3): 1}
#print(numberedSquares.get((0,2)))
minesLeft = 10
#[[0 0,0 1],[1 0,1 1],[2 0,2 1],[3 0,3 1]]
grid = [[0, 0, 0, 1, None, None, None, None], 
 [0, 0, 0, 1, None, None, None, None], 
 [1, 2, 1, 1, None, None, None, None], 
 [None, None, None, None, None, None, None, None], 
 [None, None, None, None, None, None, None, None], 
 [None, None, None, None, None, None, None, None], 
 [None, None, None, None, None, None, None, None], 
 [None, None, None, None, None, None, None, None]]
gridWidth = 8 
gridHeight = 8

Eval1 = Evaluation(numberedSquares,minesLeft,grid,gridWidth,gridHeight)
#print(Eval1.getAdjacent(0,0))
#print(Eval1.listOfZeros(2,3))
#print(Eval1.equationSolver())

matrix = [[1,1,1,0,0,0,0,0],
[0,1,1,1,0,0,0,0],
[0,0,0,0,1,1,0,0],
[0,0,0,0,1,1,1,0],
[0,0,1,1,0,1,1,1]]
matrix[0][0] = 1
print(matrix)

print(Eval1.equationSolver())
"""