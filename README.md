# ProjetMADMC2022
Élicitation incrémentale et recherche locale pour le problème du sac à dos multi-objectifs

Nous avons 2 fichiers principaux :
- Main_Exp_ProjetMADMC.ipynb : fichier utilisé pour travailler sur PLS
- WeightedSum.py : fichier utilisé pour décrire toutes les fonctions sur l'agregateur des sommes pondérés et les fonctions sur le minimaxRegret


Nous avons également 2 fichiers annexes :
- NDTree.py : fichier qui décrit la structure de donnée que nous utilisons
- utils.py : fichier qui sert de caisse à outils pour les autres fichiers


Point sur les structures de données utilisées :
- Pour PLS nous utilisons un ND-tree (détail dans le dit fichier)
- Pour MMR nous utilisons un dictionnaire pour notre ensemble d'alternatives, sous la forme {x : y(x)} 
  avec x une solution et y(x) son évaluation, chacun étant un vecteur