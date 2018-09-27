#!/usr/bin/env python
# @file   Tree.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

from __future__ import division
from .dependencies import softimport
import ROOT
import glob
import os
import math
import numpy as np
root_numpy = softimport("root_numpy")

class tchain(object):
    
    def __init__(self, name, files = [], nevents = ""):
        
        self.name  = name
        self.chain = ROOT.TChain(name)
        if nevents != "":
            self.__nevents = True
            self._neventspath = nevents
            self._nevents = 0
        else:
            self.__nevents = False
            
        if not isinstance(files, list):
            files = [files]
        
        for f in files:
            self.chain.Add(f)
            
            if self.__nevents:
                self.neventsfile( f )
            
    @property
    def nentries(self):
        return self.chain.GetEntries()
        
    @property
    def nevents(self):
        if self.__nevents:
            return self._nevents
        else:
            return self.chain.GetEntries()
            
    def select(self, selection=""):
        
        new_tree = self.chain.CopyTree(selection)
        
        return ttree(new_tree)
    
    def neventsfile(self, _file):
        _f = ROOT.TFile( _file, "READ" )
        nev = _f.Get(self._neventspath)
        
        nev.GetEntry(0)
        self._nevents += nev.GetLeaf("nevents").GetValue()
        
        _f.Close()
        
    def __len__(self):
        return self.nentries
            
    def addfile(self, _file):
        
        self.chain.Add(_file)
        
        if self.__nevents:
            self.neventsfile( _file )
        
        
    def tofile(self, filename, treename = ""):
        
        f = ROOT.TFile(filename, "recreate")
        
        chain = self.chain.CopyTree("")
                
        if treename != "":
            chain.SetName(treename)
            
        if self.__nevents:
            nevents = ROOT.TTree("nevents", "nevents")
            nevents.SetEntries(1)
            a_nevents  = np.zeros(1,dtype=np.float64)
            br_nevents = nevents.Branch( 'nevents', a_nevents, 'nevents/D')
            nevents.GetEntry(0)
            a_nevents[0] = self._nevents
            br_nevents.Fill()
            
        f.Write()
        f.Close()
        
        print("TChain {0} written into {1}".format( self.name, filename ))
        
        
class ttree(object):
    
    def __init__(self, tree):
        
        self.tree = tree
        
    def tofile(self, filename, treename = ""):
        
        f = ROOT.TFile(filename, "recreate")

        tree = self.tree.CopyTree("")
        
        if treename != "":
            tree.SetName(treename)
        
        f.Write()
        f.Close()
        
        print("TTree written into {0}".format( filename ))
        


def readTree(file,selection='',treename='DecayTree',fraction=1,branches=None):
    
    tree_array = root_numpy.root2array(file,treename,branches,selection)
            
    if not fraction == 1:
        nEvts = int(len(tree_array)*fraction)
        tree_array = np.random.choice(tree_array,nEvts)
        
    return root_numpy.array2tree(tree_array,name=treename)
    
def mergefiles(files,treename,fileoutput,selection='',fraction=1.0,branches=None):
    
    chain = ROOT.TChain(files)
    
    tree_array = root_numpy.root2array(files,treename,branches,selection)

    if not fraction == 1.0:
        nEvts = int(len(tree_array)*fraction)
        tree_array = np.random.choice(tree_array,nEvts)
        
    print(len(tree_array))
    
    root_numpy.array2root(tree_array,fileoutput,'DecayTree','recreate')

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
    
def NEfficiency(array_total,array_selection):
    
    number_total = len(array_total)
    number_passed = len(array_selection)
    
    efficiency = float(number_passed/number_total)
    
    M = number_passed
    N = number_total

    uncertainty = float(math.sqrt((M * (N - M))/math.pow(N,3)))
    
    return {"efficiency":efficiency, "error":uncertainty, "Nbefore":N, "Nafter":M}

