import random as rand
import numpy as np


def read_from_file(path):
    """

    Parameters

    Returns:
        capacity
        nb_objects
        objects
    """
    capacity = 0
    nb_objects = 0
    objects = []

    with open(str(path)) as reader:
        for line in reader:
            if line.startswith('i'):
                obj = [int(i) for i in line.split()[1:]]
                objects.append(obj)
            elif line.startswith('n'):
                nb_objects = int(line.split()[1])
            elif line.startswith('W'):
                capacity = int(line.split()[1])

    return capacity, nb_objects, np.array(objects)


def readNotDominatedPoints(path):

    with open(path, 'r') as f:
        allLines = f.readlines()

    allPoints = []
    for line in allLines:
        allPoints.append( list(map(int, line.rstrip().split("\t"))) )

    return np.array(allPoints)

def notDominated(path):

	with open(path, 'r') as f:
		allLines = f.readlines()

	allPoints = []
	for line in allLines:
		allPoints.append( list(map(int, line.rstrip().split("\t"))) )

	return np.array(allPoints)


def proportionNotDominated(nd_points, potential_nd_points):
    nd_points_set = set(list(map(tuple, nd_points)))
    potential_nd_points_set = set(list(map(tuple, potential_nd_points)))
    
    return len(nd_points_set & potential_nd_points_set)/len(nd_points)


def averageDistance(nd_points, potential_nd_points):
    nadir_pt = np.array((nd_points[:, 0].min(), nd_points[:, 1].min()))
    print(nadir_pt)
    ideal_pt = np.array((nd_points[:, 0].max(), nd_points[:, 1].max()))
    p1 = 1/(ideal_pt[0]-nadir_pt[0])
    p2 = 1/(ideal_pt[1]-nadir_pt[1])
    
    distances = []
    
    for i, nd_point in enumerate(nd_points):
        euclidian_dist = math.inf
        for potential_nd_point in potential_nd_points:
            euclidian_dist_tmp =  math.sqrt(p1*(potential_nd_point[0]-nd_point[0])**2 + p2*(potential_nd_point[1]-nd_point[1])**2)
            
            if(euclidian_dist_tmp < euclidian_dist):
                euclidian_dist = euclidian_dist_tmp
    
        distances.append(euclidian_dist)
    
    distances = np.array(distances)
    
    return (1/len(nd_points))*distances.sum()


def solutionTotalWeight(solution, objects):
    sum = 0
    for i, sol in enumerate(solution):
        if(sol == 1):
            sum += objects[:,0][i]
    return sum


def generatePop(objects, max_weight, verbose=False):
    solution = np.random.randint(2, size=len(objects))
    sumWeights = 0
    availableObjectsIndexes = []
    
    for i in range(0, len(solution)):
        if(solution[i] == 1):
            sumWeights += objects[:,0][i]
        else:
            availableObjectsIndexes.append(i)

        #make sure that the solution respects max weight
        if(sumWeights > max_weight):
            solution[i] = 0
            sumWeights -= objects[:,0][i]
            availableObjectsIndexes.append(i)
    
    #add random objects to fill the bag
    while(sumWeights < max_weight and len(availableObjectsIndexes) > 0):
        i = rand.randint(0, len(availableObjectsIndexes)-1)
        if(sumWeights + objects[:,0][availableObjectsIndexes[i]] < max_weight):
            solution[availableObjectsIndexes[i]] = 1
            sumWeights += objects[:,0][availableObjectsIndexes[i]]
            #print("add ", objects[:,0][availableObjectsIndexes[i]], sumWeights)
        del availableObjectsIndexes[i]
    
    if(verbose):
        print("current weight : ", sumWeights, " max weight : ", max_weight)
    
    
    return solution


def evaluate_solution(solution, objects, capacity, with_capacity=False):
    evaluation = np.matmul(solution.T, objects)

    # retourne solution + sa validité
    if with_capacity:
        return evaluation[0] <= capacity, evaluation
    else:
        return evaluation[0] <= capacity, evaluation[1:]


def normarlizedRandomWeights(p):
    """Retourne une liste de p poids aléatoires et normalisés à 1"""
    
    weights = [rand.random() for i in range(p)]
    weights = [w_i/np.sum(weights) for w_i in weights]
    
    return weights

def evaluate_WeightedSum(x, weights):
    """Retourne l'evaluation d'un objet en fonction des poids donnés par le décideur"""
    return np.dot(x, weights)


def getBestAlternative(X, weights):
    evaluations = []
    for x in X.values():
        evaluations.append(evaluate_WeightedSum(x, weights))
        
    evaluations = np.array(evaluations)
    return np.argmax(evaluations), np.max(evaluations)
        
def dominate_WeightedSum(x, y, weights):
    """Retourne True si x est préféré à y selon selon la somme pondérée par les poids
    False sinon"""
    
    fx = 0
    fy = 0
    
    for i in range (len(x)): #all lists should be of same length
        fx += weights[i]*x[i]
        fy += weights[i]*y[i]
        
    return fx>fy
