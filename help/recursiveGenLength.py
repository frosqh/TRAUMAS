#!/usr/lib/python3.6
# -*-coding:Utf-8 -*

import sys
import time

import igraph as ig
import mpmath as mp
import numpy as np
import numpy.random as npr


# -- Aurélie Jeanmougin-- Génération récursive avec contrainte de longueur


# objet noeud pour enregistrer les arcs et id et le prédécesseur nécessaire
class Noeud(object):

    def __init__(self):
        self._ID = 1
        self._arcs = []

    def _get_ID(self):
        return self._ID

    def _set_ID(self, v):
        self._ID = v

    def _get_arcs(self):
        return self._arcs

    def _set_arcs(self, v):
        self._arcs = v

    ID = property(_get_ID, _set_ID)
    arcs = property(_get_arcs, _set_arcs)


# calcule k parmi n
def combin(n, k):
    """Nombre de combinaisons de n objets pris k a k"""
    if k > n // 2:
        k = n - k
    x = 1
    y = 1
    i = n - k + 1
    while i <= n:
        x = (x * i) // y
        y += 1
        i += 1
    return x


# génération du DAG à partir de la liste de nombre de noeuds par niveau
# DAG où noeuds les plus petits (1er étage construit) n'ont pas d'arcs sortants
def shapeToDag(s):
    i = 0
    IDcount = 1
    DAG = []
    while i < len(s):
        j = 0
        liste = []

        while j < s[i]:
            nd = Noeud()
            nd.ID = IDcount
            IDcount += 1
            if i > 0:
                noeudTmp = npr.choice(DAG[i - 1], 1)
                nd.arcs.append(noeudTmp[0].ID)
                stmp = s[i - 1]
                if stmp > 1:
                    pb = float((stmp * (float(2 ** (stmp - 1)) / float(2 ** stmp - 1)) - 1)) / float((stmp - 1))
                    for n in DAG[i - 1]:
                        if n.ID != noeudTmp[0].ID:
                            test = npr.choice([True, False], 1, p=[pb, 1 - pb])
                            if test:
                                nd.arcs.append(n.ID)

                k = 0
                while k < i - 1:
                    for n in DAG[k]:
                        test = npr.choice([True, False], 1)
                        if test:
                            nd.arcs.append(n.ID)
                    k += 1

            liste.append(nd)
            j += 1

        DAG.append(liste)
        i += 1
    return DAG


# transformation du DAG en matrice pour l'affichage
def dagToMatrix(dag, n=10):
    mat = np.zeros((n, n), int)
    for l in dag:
        for n in l:
            for a in n.arcs:
                mat[a - 1][n.ID - 1] = 1

    return mat


# transformation du DAG en graphe pour l'affichage
def dagToGraph(dag, n=10):
    graph = ig.Graph(directed=True)
    graph.add_vertices(n)
    for l in dag:
        for n in l:
            for a in n.arcs:
                graph.add_edges([(a - 1, n.ID - 1)])
    graph.degree(mode="in")

    return graph


# compte le nombre de DAGs possible à partir du tableau
def countAn(tab, n=10, l=1):
    i = 0
    res = mp.mpf(0.0)
    while i < n:
        res += tab[n - 1][i][l - 1]
        i += 1
    return res


# génère le tableau des A(n,k,l)
def countingMethod(n=10, length=1):
    tab = np.zeros((n, n, length), mp.mpf)
    if length > n:
        return tab

    tab[0][0][0] = mp.mpf(1.0)

    i = 2
    while i <= n:
        k = 1
        while k <= i:
            if i == k:
                tab[i - 1][k - 1][0] = mp.mpf(1.0)
            else:
                l = 2
                while l <= length:
                    s = 1
                    tmp = 0.0
                    while s <= (i - k):
                        tmp += (mp.mpf(2) ** k - 1) ** s * mp.mpf(2) ** (k * (i - k - s)) * tab[i - k - 1][s - 1][l - 2]
                        s += 1

                    tab[i - 1][k - 1][l - 1] = tmp * mp.mpf(combin(i, k))
                    l += 1
            k += 1
        i += 1
    return tab


# liste de nombre de noeuds par niveau
def randomShape(tab, n=10, l=1):
    liste = []
    j = n
    while l > 0:
        i = 0
        nb = []
        pb = []
        An = countAn(tab, j, l)

        if l == 1:
            s[0] = j
        else:
            while i < n:
                nb.append(i + 1)
                pb.append(mp.mpf(tab[j - 1][i][l - 1] / An))
                i += 1

            s = npr.choice(a=nb, p=pb, size=1)

        liste.append(int(s[0]))
        l = l - 1
        j = j - int(s[0])
    return liste


def chrono(n=10, l=4):
    start = time.time()
    taille = n
    longueur = l

    tableau = countingMethod(taille, longueur)
    shape = randomShape(tableau, taille, longueur)
    dag = shapeToDag(shape)

    return time.time() - start


def widthVariation(n=10, l=4):
    taille = n
    longueur = l

    tableau = countingMethod(taille, longueur)
    shape = randomShape(tableau, taille, longueur)

    # dag = rec.shapeToDag(shape)

    return shape


# Exécution principale :

if __name__ == '__main__':
    taille = 10
    longueur = 4
    if len(sys.argv) > 1:
        taille = int(sys.argv[1])
    if len(sys.argv) > 2:
        longueur = int(sys.argv[2])
    tableau = countingMethod(taille, longueur)
    shape = randomShape(tableau, taille, longueur)
    print("liste de nombre de noeuds par niveau : ")
    print(shape)

    dag = shapeToDag(shape)

    # affichage avec graphe
    G = dagToGraph(dag, taille)
    G.write("recGenLength_n" + str(taille) + "_lg" + str(longueur), "gml")


# nx.draw_shell(G, with_labels=True, font_weight='bold')
# plt.savefig("Glong.png")

# affichage avec matrice
# matrix = rec.dagToMatrix(dag, taille)
# print("----------------------------------")
# print("matrice d'adjacence :")
# for l in matrix:

#    for n in l:
#        print n,
#    print(" ")

def initialisationSeed(seed):
    npr.seed(seed)


def executionL(n=10, l=4, filename="output-igraph.gml"):
    taille = n
    longueur = l

    tableau = countingMethod(taille, longueur)
    shape = randomShape(tableau, taille, longueur)
    dag = shapeToDag(shape)
    G = dagToGraph(dag, taille)
    G.write(filename)
    return G
