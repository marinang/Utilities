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



def readTree(file,selection='',treename='DecayTree'):
    #doesn't work if a TFile is open
    if not file:
        raise ValueError('No file!!!')
    if not isinstance(file,(list,tuple)):
        file = [file]
    chain = ROOT.TChain(treename)
    for file in file:
        if not os.path.isfile(file):
            #doesn't like path with $HOME for example
            continue
        chain.AddFile(file)
    return chain.CopyTree(selection)


def makeTree(files,treename,fileoutput,selection=''):
    
    #tree = readTree(files,selection,treename)
    
    #-->
    file_out = ROOT.TFile(fileoutput,'RECREATE')
    #tree_out = tree.CloneTree()
    tree_out = readTree(files,selection,treename)
    print tree_out.GetEntries()
    tree_out.SetName('DecayTree')
    tree_out.Write()
    file_out.Write()
    file_out.Close()

def Efficiency(tree_total,selection=''):
    
    number_total = tree_total.GetEntries()
    tree_passed = tree_total.CopyTree(selection)
    number_passed = tree_passed.GetEntries()
    
    efficiency = float(number_passed/number_total)
    
    M = number_passed
    N = number_total

    uncertainty = float(math.sqrt((M * (N - M))/math.pow(N,3)))
    
    return {"efficiency":efficiency, "error":uncertainty, "Nbefore":N, "Nafter":M}
