
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
        self.variables = []
        self.results = []
        self.mineCounter = -1

    def init(self, numberedSquares, minesLeft, grid, gridWidth, gridHeight):
        self.numberedSquares = numberedSquares #map where x,y is the key and the number is the value
        self.minesLeft = minesLeft #int number of mines
        self.grid = grid #the grid right now
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.flags = []
        self.flags.clear()
        self.results = []
        self.results.clear()
        self.mineCounter = self.minesLeft

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
        return np.array([[0]*m] * n)

    def getEquations(self,neighbours,matrixA):
        #print("self.variables: ",self.variables)
        #print("NEIGHBOURS: ",neighbours)
        #if I didn't make a copy of matrixA, when changing the 0's to 1's there was a conflict
        #where the matrix would end up full of 1's
        matrixB = np.array(matrixA)
        #print(matrixB)
        for i in range(0,len(neighbours)-1):
            for j in range(0,len(self.variables)-1):
                if self.variables[j] in neighbours[i]:
                    #print(self.variables[j]," is in ",neighbours[i])
                    #print("changing position ",i,j," on the list")
                    matrixB[i][j] = 1
         
        #if the variable is an adjacent to the numbered square then it counts towards its equation 
        return np.array(matrixB)
    def matrixValidation(self,matrixB):
        #print("NR OF MINES:",self.minesLeft)
        okay = ''            
        while okay != 't':
            #print("OKAY:",okay)
            if self.mineCounter == 0:
                return []
            okay = self.isOkay(matrixB)
            if len(self.variables) == 0 or len(self.results) == 0 or len(matrixB) < 2 or matrixB == np.array([]):
                return []
            else: 
                if okay == 'o':
                    matrixB = self.removeSingularOnes(matrixB)
                if okay == 'z':
                    matrixB = self.removeZeroOnes(matrixB)
                if okay == 'r':
                    matrixB = self.removeResultZero(matrixB)
                if okay == 'n':
                    return []   
            
        #print("MINES FOUND: ",self.flags)    
        #print("TEMP AFTER REMOVING",matrixB)    
        return matrixB
        
    def isOkay(self, matrix):
        count = 0
        if matrix == np.array([]):
            return 'n'
        matrix = np.array(matrix)
        temp = matrix.tolist()
        #all of these cases can result from removing one of the other cases so we must clear the matrix
        for l in temp:
            count+=1
            if l.count(0) == len(l):
                #there is a zero matrix
                return 'z'
            if l.count(1) == 1:
                #there is a singular matrix (e.g. 1 0 0 0)
                return 'o'
            if count < len(self.results) and self.results[count] <= 0:
                #there is a result 0
                return 'r'
        return 't'    

    def removeSingularOnes(self, matrix):
        if matrix == np.array([]):
            return []
        temp = matrix.tolist()
        #When we find a singular on (E.G an equation of the kind 1 0 0 = 1)
        #this means that the first variable is = 1; we then have to : 
        #print("INITIAL LENGTH: ",len(temp))
        for i in range(0,len(temp)):
            #print("CURR LENGTH: ",len(temp),i)
            #print(i)
            if i >= len(temp):
                break
            if temp[i].count(1)==1 and i<len(temp):
                #print(self.minesLeft)
                #print(temp[i], " IS A SINGULAR MATRIX, POINT ",self.variables[i]," is a mine")
                if True: #self.minesLeft > 0:
                #1. remove the equation from the matrix
                    temp.remove(temp[i])
                    #2. pop the result for that equation
                    if len(self.variables) == 0 or len(self.results) == 0:
                        return []
                    if i < len(self.variables) and i < len(self.results):
                        self.results.pop(i)
                        self.flags.append(self.variables.pop(i))
                    else:
                        return []
                    for j in range(0,len(temp)):
                    #3. remove the variable from each other equation and subtract the value in the result
                        #print(j,i)
                        if temp[j][i] == 1:
                            self.results[j]-=1
                        temp[j].pop(i)
                    i = 0   
                    self.mineCounter = self.minesLeft - len(self.flags)
                else: 
                    break
            #print("CURR LENGTH: ",len(temp),i)
        
        matrix = np.array(temp)
        return matrix


    def removeZeroOnes(self,matrix):
        if matrix == np.array([]):
            return []
        temp = matrix.tolist()
        #When we find a singular on (E.G an equation of the kind 1 0 0 = 1)
        #this means that the first variable is = 1; we then have to : 
        #print("INITIAL LENGTH: ",len(temp))
        for i in range(0,len(temp)):
        #print("CURR LENGTH: ",len(temp),i)
            if i >= len(temp):
                break
            if all(v == 0 for v in temp[i]) and i<len(temp):
                #some fields enter as pure zeroes, removing
                #print(temp[i], " IS A ZERO MATRIX, point:",self.variables[i])
                temp.remove(temp[i])
                if len(self.variables) == 0 or len(self.results) == 0:
                    return []
                if i < len(self.variables) and i < len(self.results):
                    self.results.pop(i)
                    self.variables.pop(i)
                else:
                    return []
                for j in range(0,len(temp)):
                    temp[j].pop(i)
                i = 0
                #print("Zero ones i: ",i)
        matrix = np.array(temp)
        return matrix

    def removeResultZero(self,matrix):
        temp = matrix.tolist()
        #print("removing zero result...")
        #When we find a singular on (E.G an equation of the kind 1 0 0 = 1)
        #this means that the first variable is = 1; we then have to : 
        #print("INITIAL LENGTH: ",len(temp))
        for i in range(0,len(temp)):
            if i >= len(temp):
                break
            if self.results[i] == 0 and i<len(temp):
                #print(" ZERO RESULT , point:",self.variables[i])
                #1. remove the equation from the matrix
                temp.remove(temp[i])
                #2. pop the result for that equation
                if len(self.variables) == 0 or len(self.results) == 0:
                    return []
                if i < len(self.variables) and i < len(self.results):
                    self.results.pop(i)
                    self.variables.pop(i)
                else:
                    return []
                for j in range(0,len(temp)):
                    if j >= len(temp):
                        break
                    #print(j,i)
                #3. remove the variable from each other equation and subtract the value in the result
                    temp[j].pop(i)
                #print("Remove result zero i: ",i)
        
        matrix = np.array(temp)
        return matrix
    def equationSolver(self):
        #to make an equation of the form x0,x1,...,xn; n will be the highest 
        #number of adjacent squares from a numberedSquare 
        listOfNeighbours = []
        matrixA = np.array([])
        #self.variables for the equations (every existing adjacent for each numberedsquare, no duplicates)
        # 1. get foreach the list of adjacent squares for each numbered square->getAdjacent(x,y)
        
        for key, val in self.numberedSquares.items():
            #print("Get adjacent of: ",item[0],item[1])
            temp = self.getAdjacent(key[0],key[1])
            #print(item[0],item[1]," has ",len(temp)," neighbours")                
            if temp not in listOfNeighbours:
                listOfNeighbours.append(temp)
                self.results.append(val)
        # 2. make a list of self.variables for the equations
        self.variables = list(dict.fromkeys(itertools.chain(*listOfNeighbours)))
        #print("self.variables: ",self.variables)
        # 3. create a list of lists, where the inner lists are filled with 0s -> listOfZeros(n)
        matrixA = self.listOfZeros(len(listOfNeighbours),len(self.variables))
        #print("Matrix A: ",matrixA)
        # 4. fill the corresponding list with 1s where the 1s are the adjacent squares
        # and are of length of n (list1)
        matrixA = self.getEquations(listOfNeighbours,matrixA)

        #print("INITIAL TEMP: ",matrixA)
        #print("INITIAL RESULTS: ",self.results)
        #print("VARIABLES: ",self.variables)
        matrixA = self.matrixValidation(matrixA)
        
        if matrixA ==[]:
            return self.flags
        #print("Matrix A: ",matrixA, " size: ", matrixA.size)
        # 5. the squares value goes into a seperate list (list2)
        #print("self.results: ",self.results)
        # 6. calculate the np.linalg.solve(list1,list2)
        #print(matrixA)
        #print(self.results)
        try:
            minesSolved = np.linalg.solve(matrixA,self.results)
        except:
            return self.flags
        
        # 7. where there is a 1, means that:
        #sprint("Mines: ",minesSolved)
        for k in range(0, len(minesSolved)):
            if minesSolved[k] == 1:
                self.flags.append(self.variables[k])
        # E.G. if we have only 3 adjacent squares ([1,0,0][0,1,0][0,0,1])
        # and the result is [1,0,0] then that means the first square has a bomb, rest don't  
        #print("MINES: "+flags)
        return self.flags, self.safe

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