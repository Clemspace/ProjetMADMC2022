 
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
        if root is None:
            self.root = Node(self.nbDims, candidate,self.maxNodeSize, self.numberOfSplits)
            return True
        else:
            n = self.root
            updated = n.UpdateNode(candidate)
            if updated:
                n.insert(candidate)
            return updated

class Node(object):
        
    def __init__(self, nbDims, solution, maxNodeSize,children = [], parent = None, numberOfSplits = 2):
        self.points = dict(solution)
        self.approxNadir = self.points.values()[0]
        self.approxIdeal = self.points.values()[0]
        self.nbDims = nbDims
        self.parent = parent
        self.children = children
        self.maxNodeSize = maxNodeSize
        self.numberOfSPlits = numberOfSplits
        
    
    def removePoint(self, point):
        r = dict(self.points)
        del r[point.key()]
        self.Points = r
        
        
    def distance(self, candidate):
        #retourne la distance entre un point candidat et centre de gravité estimé d'un noeud
        s = 0
        middle = [(self.approxIdeal[i] + self.approxNadir[i]) /2 for i in range(self.nbDims)]
        return dist(middle,candidate.value())    
         
    def findCLosestChild(self, candidate):
        
        closestChild = self.children[0]
        minDistance = self.children[0].distance(candidate)
        
        for i in self.children:
            newDist = i.distance(candidate)
            if newDist < minDistance:
                minDistance = newDist
                closestChild = i
        return closestChild
         
    def findMostIsolatedPoint(self):
        
        for i in self.points.items():
            avgdist  = sum(dist(i.value(),j.value()) for j in self.points.items())/len(self.points)-1
            
        
        return z
          
            
    def getSolutions(self):
        return self.points.keys()
    
    def getEvaluations(self):
        return self.points.values()
    
    def getSoutionsAndEvaluations(self):
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
        size = 0
        for child in self.children:
                size+= child.getSizeSubtree()
        return size
        
    
    def delete_subtree(self):
        self.children.clear()
        self.parent =None
        self.parent.children.remove(self)#hmm à méditer
    
    def UpdateIdealNadir(self, candidate):
        changed = False
        for i in range(nbDims): #on met à jour les valeurs approx. Nadir & Idéales locales
            if (candidate.value()[i] > self.approxIdeal[i]):
                self.approxIdeal[i] = candidate.value()[i]
                changed = True
            if (candidate.value()[i] < self.approxNadir[i]):
                self.approxNadir[i] = candidate.value()[i]
                changed = True
        if changed: #si il y a eu maj et qu'one st pas à la racine, on propage au parent
            if self.parent is not None:
                UpdateIdealNadir(self.parent, candidate)
        
        return changed
    
    def Insert(self, candidate):
        if self.isLeaf(): #Si on est dans une feuille
            
            if not candidate in self.points: #si le candidat n'est pas déjà présent dans le noeud
                
                self.points.update(candidate)
                self.UpdateIdealNadir(candidate)

                
            if len(self.points > self.maxNodeSize): #si le noeud contient trop de valeurs:
                self.Split()
            return
        else:
            nprime = self.findClosestChild(candidate)
            nprime.Insert(candidate)
            return
            
    
    def UpdateNode(self, candidate):
        
        if self.Property1(candidate):
            return False
        elif self.Property2(candidate):
            #dans ce cas on supprime n et tous ses sous arbres #TODO
            self.deleteNode()
        
        elif Dominates(self.approxIdeal,candidate.value()) or dominates(candidate.value(), self.approxNadir):
            #si le candidat est dominé par l'idéal et domine le point nadir
            
            if self.isLeaf():
                for point in self.Points.items():
                    if Dominates(point.value(),candidate.value()):
                        return False
                    if StrictlyDominates(candidate.value(),point.value()):
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
        return Dominates(self.approxNadir,candidate.value())
      
    def Property2(self, candidate):
        return Dominates(candidate.value(), self.approxIdeal)
    
    
    

        
    def Split(self):
        splits = 0        
        z = self.findMostIsolatedPoint()
        
        newChild = Node(self.nbDims, z, self.maxNodeSize, self.NumberOfSplits, parent = self)
        self.removePoint(z)
        splits+=1
        
        while splits < self.NumberOfSplits:
            z = self.findMostIsolatedPoint()
            newChild = Node(self.nbDims, z, self.maxNodeSize, self.NumberOfSplits, parent = self)
            self.addChild(newChild)
            self.removePoint(z)
            splits+=1
            
        while len(self.Points) > 0:
            z = self.Points.popitem()
            closest = self.findCLosestChild(z)
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
    
