#!/usr/bin/env python
# @file   Tree.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

from __future__ import division
import ROOT
from PyLHCb.Root.RootUtils import LHCbStyle
from PyLHCb.Root.RootUtils import destruct_object
from PyLHCb.Utilities.Debug import memory_usage
import glob
import os
import math
import numpy as np
from root_numpy import array2tree, tree2array, root2array, array2root
from rootpy.tree import TreeChain


def readTree(file,selection='',treename='DecayTree',fraction=1):
    #doesn't work if a TFile is open
    if not file:
        raise ValueError('No file!!!')
    if not isinstance(file,(list,tuple)):
        file = [file]
    chain = ROOT.TChain(treename)
#    chain = TreeChain(treename,file)
    for file in file:
        if not os.path.isfile(file):
            #doesn't like path with $HOME for example
            continue
        chain.AddFile(file)
    tree = chain.CopyTree(selection)
        
    if fraction == 1:
        return tree
    else:
        return FracOfTree(tree,fraction)
    
    
def FracOfTree(tree,fraction=1):
    
    nEvts = tree.GetEntries()
    new_nEvts = int(nEvts*fraction)
    
    array = tree2array(tree)
    array = np.random.choice(array,new_nEvts)
    
    new_tree = array2tree(array,name=tree.GetName())
    destruct_object(tree)
    
    return new_tree
    
def makeTree(files,treename,fileoutput,selection='',fraction=1.0,branches=None):
    
    tree_array = root2array(files,treename,branches,selection)

    if not fraction == 1.0:
        nEvts = int(len(tree_array)*fraction)
        tree_array = np.random.choice(tree_array,nEvts)
        
    print len(tree_array)
    
    array2root(tree_array,fileoutput,'DecayTree','recreate')

def Efficiency(tree_total,selection=''):
    
    number_total = tree_total.GetEntries()
    tree_passed = tree_total.CopyTree(selection)
    number_passed = tree_passed.GetEntries()
    
    efficiency = float(number_passed/number_total)
    
    M = number_passed
    N = number_total

    uncertainty = float(math.sqrt((M * (N - M))/math.pow(N,3)))
    
    destruct_object(tree_passed)
    
    return {"efficiency":efficiency, "error":uncertainty, "Nbefore":N, "Nafter":M}

