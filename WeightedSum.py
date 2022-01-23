from gurobipy import *
import numpy as np
import utils as utils
from ast import literal_eval


def PMR_WeightedSum(x, y, prefs):
    p = len(x) #nb critères
    
    m = Model("PMR Weighted Sum")     
    
    # Declaration variables de decision
    lp_vars = []
    
    for i in range(len(x)):
        lp_vars.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name='omega%d' % (i+1)))
    
    #x = np.array(x_temp)

    # maj du modele pour integrer les nouvelles variables
    m.update()
    
    obj = LinExpr();
    
    for i in range(p):
        obj += (y[i]-x[i])*lp_vars[i]
            
    # Definition de l'objectif
    m.setObjective(obj, GRB.MAXIMIZE)
    
    # Definition des contraintes  
    m.addConstr(quicksum(lp_var for _ in lp_vars) == 1, "Contrainte%d" % 1)
    
    for i,(pref_x, pref_y) in enumerate(prefs): #add constraints with preferences found earlier
        pref_x=np.array(pref_x)
        pref_y=np.array(pref_y)
        m.addConstr(quicksum(lp_vars[j]*(pref_x-pref_y)[j] for j in range(p)) >= 0, "Contrainte%d" % (i)) #x > y
    
    # Resolution
    m.optimize()
    
    if(m.status == 3):
        print ("Infeasible LP")
        return None
    
    return (m, m.objVal) #getLPResult(m, x, pb_dict["n"], verbose)


def MR(x, X, prefs, PMR_function=PMR_WeightedSum):
    """
    X : Ensemble des solutions obtenus après PLS
    prefs : preférences des poids du décideur
    PMR_Function : fonction (PL) à utiliser pour calculer les PMR
    """
    pmr_list = {}
    for y in X.values():
        #if x != y: #verifier si cette condition fait l'effet désiré
        tmp_pmr = PMR_function(x, y, prefs)
        
        if(tmp_pmr != None):
            lp_model, lp_objVal = tmp_pmr
            pmr_list[repr(x)] = (lp_model, lp_objVal)
    
    return (np.max(pmr_list), np.argmax(pmr_list))

    

def MMR(X, prefs, PMR_function=PMR_WeightedSum):
    """
    Retourne le minimax regret et les deux indices des alternatives qui permettent de l'obtenir
    """
    mmr_value = np.inf 
    optX = -1
    optY= -1
    
    print((X.values()))
    
    for ind_x in range(np.shape(X.values())[0]):
        MAXX = -1*np.inf
        tmp_optY = -1
        for ind_y in range((np.shape(X)[0])):
            pmr_xy = PMR_function(X[ind_x], X[ind_y], prefs)
            
            if(pmr_xy > MAXX):
                MAXX = pmr_xy
                #print("MAXX : " + str(MAXX) )
                tmp_optY = ind_y
                if (MAXX > mmr_value):
                    break
                
        if(MAXX < mmr_value):
            mmr_value = MAXX
            optX = ind_x
            optY = tmp_optY
            
    return mmr_value, optX, optY
    

def trueRegret(dm, best_obj, opt_x):
    """
    Retourne le "vrai" regret si l'objet x est choisi selon le vecteur de poids du décideur
    """
    return np.dot(dm, best_obj)-np.dot(dm, opt_x)


def incrementalElicitation_WeightedSum(X, p, delta, PMR_function=PMR_WeightedSum):
    dm = utils.normarlizedRandomWeights(p) #
    
    best_alternative = utils.getBestAlternative(X, dm) #index + value of alternative
    
    prefs = []
    nb_questions = 1
    mmr_value, ind_x, ind_y = MMR(X, prefs, PMR_function)
    
    while(mmr_value >= delta):
        #ask a question
        if(utils.dominate_WeightedSum(X[ind_x], X[ind_y], dm)):
            prefs.append((X[ind_x], X[ind_y]))
        else:
            prefs.append((X[ind_y], X[ind_x]))
            
        mmr_value, ind_x, ind_y = MMR(X, prefs, PMR_function)
        nb_questions += 1
        
    return X[ind_x], utils.evaluate_WeightedSum(X[ind_x], dm), nb_questions



def LP_WeightedSum(pb_dict, liste_poids, verbose=False):
    
    m = Model("PL Somme Ponderee")     
    
    # Declaration variables de decision
    x = []
    for i in range(pb_dict["n"]):
        x.append(m.addVar(vtype=GRB.BINARY, lb=0, ub=1, name="x"+str(i+1)))
    
    #x = np.array(x_temp)

    # maj du modele pour integrer les nouvelles variables
    m.update()
    
    obj = LinExpr();
    obj = quicksum(pb_dict["item_weights"][i]*x[i] for i in range(pb_dict["n"]))
            
    # Definition de l'objectif
    m.setObjective(obj, GRB.MAXIMIZE)
    
    # Definition des contraintes  
    m.addConstr(quicksum(pb_dict["item_weights"][i]*x[i] for i in range(pb_dict["n"])) <= pb_dict["max_weight"], "Contrainte%d" % (1))
    
    # Resolution
    m.optimize()
    
    return getPLResult(m, x, pb_dict["n"], verbose)
    
    
    
def getLPResult(m, x, n, verbose=False):
    if(verbose):
        print('\Optimal affectation:\n')
    
    selected_items = [] #list of indexes
    for i in range(n):
        if(x[i].x == 1):
            selected_items.append(i)
            if(verbose):
                print("x_"+str(i), end=', ')
    
    if(verbose):
        print('\nObjective function value :', m.objVal)
    
    return selected_items




if __name__ == '__main__':

    file_path = "2KP200-TA-0.dat"
    (capacity, nb_objects, objects) = utils.read_from_file(file_path)
    
    #faire PLS
    
    #simuation de solutions potentiellement pareto-opt () 
    nb_sols = 100
    X = {} 
    for i in range(nb_sols):
        generated_sol = utils.generatePop(objects, capacity)
        X[repr(generated_sol)] = utils.solutionTotalWeight(generated_sol, objects)
    
    p = len(objects-1) #nb criteres
    delta = 0.07 #param pour la condition d'arrêt de l'élicitation
    """X = {repr(generated_sol) : [4,2,0,10,5,1]}
    
    solution_potentialy_opt = [[1,0,1,0,1,0,1,1,1,1,0,1,0,1,0]\
                               [1,0,1,0,1,0,1,1,1,1,0,1,0,1,0]\
                                ]
    Y = {0 : [4,2,0,10,5,1], 1 : [3,1,0,0,5,1]}
    Y = {0 : [4,2,0,10,5,1], 1 : [3,1,0,0,5,1]}"""
    
    incrementalElicitation_WeightedSum(X, p, delta, PMR_WeightedSum)
        









