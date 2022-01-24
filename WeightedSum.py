from gurobipy import *
import numpy as np
import utils as utils
import time
import matplotlib.pyplot as plt

    
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


def PMR_WeightedSum(x, y, prefs):
    p = len(x) #nb critères
    
    env = Env(empty=True)
    env.setParam('OutputFlag', 0)
    env.start()
    m = Model("PMR Weighted Sum", env=env)     
    
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
    m.addConstr(quicksum(lp_var for lp_var in lp_vars) == 1, "Contrainte%d" % 1)
    
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
    Retourne le minimax regret et les deux alternatives qui permettent de l'obtenir
    """
    mmr_value = np.inf 
    optX = -1
    optY= -1
    
    #nb_sols = np.shape(list(X.values()))[0] 
    
    for x in X.values():
        MAXX = -1*np.inf
        tmp_optY = -1
        for y in X.values():
            pmr_xy = PMR_function(x, y, prefs)[1] #pmr value
            
            if(pmr_xy > MAXX):
                MAXX = pmr_xy
                #print("MAXX : " + str(MAXX) )
                tmp_optY = y
                if (MAXX > mmr_value):
                    break
                
        if(MAXX < mmr_value):
            mmr_value = MAXX
            optX = x
            optY = tmp_optY
            
    return mmr_value, optX, optY
    

def trueRegret(dm, best_obj, opt_x):
    """
    Retourne le "vrai" regret si l'objet x est choisi selon le vecteur de poids du décideur
    """
    return np.dot(dm, best_obj)-np.dot(dm, opt_x)
   

def incrementalElicitation_WeightedSum(X, p, delta, PMR_function=PMR_WeightedSum, nb_max_questions = 40):
    """
    Retourne une solution s'approchant de l'optimal selon le decision maker (dm) grâce à une elicitation incrémentale
    """
    start_time = time.time()
    dm = utils.normarlizedRandomWeights(p) #
    
    best_alternative = utils.getBestAlternative(X, dm) #index + value of alternative
    
    prefs = []
    nb_questions = 0
    
    MMRs_evolution = []
    nb_questions_evolution = []
    
    #do-while
    while(True):
        mmr_value, x, y = MMR(X, prefs, PMR_function)
        nb_questions_evolution.append(nb_questions)
        MMRs_evolution.append(mmr_value)
        nb_questions += 1
        
        #ask a question
        if(utils.dominate_WeightedSum(x, y, dm)):
            prefs.append((x, y))
        else:
            prefs.append((y, x))
        
        print("\n Question asked : MMR="+str(mmr_value), x, y)
        #print("prefs : ", prefs, "\n")
        
        if(mmr_value < delta or nb_questions > nb_max_questions): #condition d'arret
            break
        
        #print("regret between real opt alternative and current x : ", trueRegret(dm, best_alternative, x))
    
    duration_time = time.time()-start_time
    
    return x, best_alternative, utils.evaluate_WeightedSum(x, dm), nb_questions, duration_time, nb_questions_evolution, MMRs_evolution


def simulateIncrElicitation(n_min, n_step, n_max, p):
    """
    Génère des problèmes avec de plus en plus d'objets et retourne le nombre de questions
    posés pour chaque problème
    """
    utils.generateInstance(n, p)
    current_n = n_min
    nb_questions = []
    nb_questions.append(incrementalElicitation_WeightedSum(X, p, delta, PMR_WeightedSum)[3])

if __name__ == '__main__':

    file_path = "2KP200-TA-0.dat"
    (capacity, nb_objects, objects) = utils.read_from_file(file_path)
    
    nb_ite = 5
    
    for i in range(nb_ite):
        #simuation de solutions potentiellement pareto-opt avec des solutions admissibles générées aléatoirement
        nb_sols = 20
        X = {} 
        for i in range(nb_sols):
            generated_sol = utils.generatePop(objects, capacity)
            X[repr(generated_sol)] = utils.evaluate_solution(generated_sol, objects, capacity, with_capacity=False)[1] #[0] = si solution est admissible ou non
        
        p = len(objects[0])-1 #nb criteres
        delta = 0.1 #param pour la condition d'arrêt de l'élicitation
        
        #print(utils.evaluate_solution(generated_sol, objects, capacity, with_capacity=False))
        
        incrElicitation = incrementalElicitation_WeightedSum(X, p, delta, PMR_WeightedSum)
        
        
        plt.plot(incrElicitation[-2], incrElicitation[-1])
    
    plt.title("Evolution du minimaxRegret en fonction du nombre de questions posées")
    plt.xlabel('Nombre de questions')
    plt.ylabel('Valeur de MMR')
    plt.legend()
    plt.show() 
        









