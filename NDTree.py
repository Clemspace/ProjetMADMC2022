 
import numpy as np
import itertools
from collections import defaultdict
from scipy.spatial import distance
from math import dist 

class NDTree(object):

    def __init__(self, nbDims, maxNodeSize = 20, root=None, nodes=[], numberOfSplits = 2):
        self.root = root
        self.nodes = nodes
        self.nbDims = nbDims
        self.maxNodeSize = maxNodeSize
        self.numberOfSplits = numberOfSplits
        
    def Update(self, candidate):
        if self.root is None:
            self.root = Node(nbDims = self.nbDims,solution = candidate,maxNodeSize = self.maxNodeSize, numberOfSplits = self.numberOfSplits)
            return True
        else:
            updated = self.root.UpdateNode(candidate)
            if updated:
                self.root.Insert(candidate)
            return updated
    
    def getSolutions(self):
        return self.root.getSolutions()
    
    def getPoints(self):
        return self.root.getPoints()
    
    def getSize(self):
        if self.root is not None:
            return self.root.getSizeSubtree()
        else:
            return 0
        
class Node(object):
        
    def __init__(self, nbDims, solution, maxNodeSize,children = [], parent = None, numberOfSplits = 2):
        self.points = solution
        self.approxNadir = list(self.points.values())[0]
        self.approxIdeal = list(self.points.values())[0]
        self.nbDims = nbDims
        self.parent = parent
        self.children = children
        self.maxNodeSize = maxNodeSize
        self.numberOfSplits = numberOfSplits
        
    
    def removePoint(self, point):
        r = dict(self.points)
        del r[list(point.keys())[0] ]
        self.points = r
        
        
    def distance(self, candidate):
        #retourne la distance entre un point candidat et centre de gravité estimé d'un noeud
        s = 0
        middle = [(self.approxIdeal[i] + self.approxNadir[i]) /2 for i in range(self.nbDims)]
        return dist(middle,candidate[1])    
         
    def findClosestChild(self, candidate):
        if self.isLeaf():
            return self
        
        closestChild = self.children[0]
        minDistance = self.children[0].distance(candidate)
        
        for i in self.children:
            newDist = i.distance(candidate)
            if newDist <= minDistance:
                minDistance = newDist
                closestChild = i
        return closestChild
         
    def findMostIsolatedPoint(self):
        
        
        if len(self.points) == 1:
            
            return self.points.items()[0]
        else:
            z = None
            maxAvgDist = 0

            
            
            for i,j in self.points.items():
                
                cpt = 0
                distn = 0
                for k,l in self.points.items():
                    
                    if i == k:
                        
                        continue
                    
                    else:
                        cpt+=1
                        distn+= dist(j,l)
                        
                if maxAvgDist < distn :
                    maxAvgDist = distn
                    z = i
                        
                    
            return {z:self.points[z]}
          
            
    def getSolutions(self):
        if self.isLeaf():
            return set(self.points.keys())
        else:
            res = set()
            for child in self.children:
            
                res.union(child.getSolutions())
        return res
    
    def getEvaluations(self):
        return list(self.points.values())
    
    def getSolutionsAndEvaluations(self):
        return self.points.items()
    
    def isLeaf(self):
        return self.children == []
    
    def isRoot(self):
        return self.parent == None
    
    def isInternal(self):
        return not self.isLeaf()
    
    def addChild(self, child):
        self.children.append(child)
        child.parent = self
    
    def removeChild(self, child):
        pass
    
    def isEmpty(self):
        if self.isLeaf():
            return len(self.points) == 0
        else:
            size = 0
            for child in self.children:
                size += child.getSizeSubtree()
            return size == 0
                
    def getSizeSubtree(self):
        
        if self.isLeaf():
            return len(self.points)
        else:
            size = 0
            for child in self.children:
                    size+= child.getSizeSubtree()
        return size
        
    def getPoints(self):
        if self.isLeaf():
            return self.points
        else:
            res = dict()
            for child in self.children:
            
             res = {**res, **child.getPoints()}
        return res
    
    def deleteSubtree(self):
        
        if not self.isLeaf():
            for child in self.children:
                child.delete_subtree()
        if self.isLeaf():
            self.points =dict()
            return True
        if not self.isRoot():
            self.parent.children.remove(self)#hmm à méditer
        self.parent = None

        return True
        
    def UpdateIdealNadir(self, candidate):
        changed = False
        candi = list(candidate.values())[0]
        for i in range(self.nbDims): #on met à jour les valeurs approx. Nadir & Idéales locales
            if (candi[i] > self.approxIdeal[i]):
                self.approxIdeal[i] = candi[i]
                changed = True
            if (candi[i] < self.approxNadir[i]):
                self.approxNadir[i] = candi[i]
                changed = True
        if changed: #si il y a eu maj et qu'on est pas à la racine, on propage au parent
            if self.parent is not None: 
                UpdateIdealNadir(self.parent, candidate)
        
        return changed
    
    def Insert(self, candidate):
        
        if self.isLeaf(): #Si on est dans une feuille
            if not list(candidate.keys())[0] in list(self.points.keys()): #si le candidat n'est pas déjà présent dans le noeud
                
                self.points.update(candidate)
                self.UpdateIdealNadir(candidate)

                return True
            else:
                return False
            
            if len(self.points) > self.maxNodeSize: #si le noeud contient trop de valeurs:
                self.Split()
            return True
        else:
            nprime = self.findClosestChild(candidate)
            return nprime.Insert(candidate)

            
    
    def UpdateNode(self, candidate):
        
        candi = list(candidate.values())[0]
        if self.Property1(candi):
            return False
        elif self.Property2(candi):
            #dans ce cas on supprime n et tous ses sous arbres #TODO
            self.deleteSubtree()
        
        elif Dominates(self.approxIdeal,candi) or Dominates(candi, self.approxNadir):
            #si le candidat est dominé par l'idéal et domine le point nadir
            
            if self.isLeaf():
                for point in self.Points.items():
                    if Dominates(point.value(),candi):
                        return False
                    if strictlyDominates(candi,point):
                        self.removePoint(point)
            else:
                for child in self.children:
                    if not child.UpdateNode():
                        return False
                    else:
                        if child.getSizeSubtree() == 0:
                            child.delete_subtree()
                if len(self.children) == 1:
                   #remplace le noeud par son seul fils
                    self.prent.children.append(self.children[0])
                    self.parent =None
                    self.parent.children.remove(self)
        else:
            #propriété 3
            pass
        return True
        
    def Property1(self, candidate):
        return Dominates(self.approxNadir,candidate)
      
    def Property2(self, candidate):
        return Dominates(candidate, self.approxIdeal)
    
    
    

        
    def Split(self):
        splits = 0        
        z = self.findMostIsolatedPoint()
        print(z)
        newChild = Node(nbDims = self.nbDims, solution = z, maxNodeSize = self.maxNodeSize, numberOfSplits = self.numberOfSplits, parent = self)
        self.removePoint(z)
        splits+=1
        
        while splits < self.numberOfSplits:
            z = self.findMostIsolatedPoint()
            newChild = Node(nbDims = self.nbDims, solution = z, maxNodeSize = self.maxNodeSize, numberOfSplits = self.numberOfSplits, parent = self)
            self.addChild(newChild)
            self.removePoint(z)
            splits+=1
            
        while len(self.points) > 0:
            z = self.points.popitem()
            closest = self.findClosestChild(z)
            closest.Insert(z)
            #normalement la maj nadir/ideal se fait dans le Insert
        
        
def avg_distance(point, others):
    dist = 0
    for i in others:
        dist+= dist(point,i)
    return dist/len(others)

def Dominates(point, candidate):
    return sum([point[x] >= candidate[x] for x in range(len(point))]) == len(point) 

def StrictlyDominates(point, candidate):
    return sum([point[x] > candidate[x] for x in range(len(point))]) == len(point) 

def arraytoString(array):
    return ''.join(array)
