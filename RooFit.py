# -*- coding: utf-8 -*-
#!/usr/bin/env python
# @file   RooFit.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2017-19-05

from __future__ import division
import ROOT
from PyLHCb.Root.RootUtils import destruct_object
import glob
import os
import math
import numpy as np
from root_numpy import array2tree, tree2array, root2array, array2root, hist2array

ROOT.RooWorkspace.rfimport = getattr(ROOT.RooWorkspace,'import')

# Proxies for RooFit classes
RooFit        = ROOT.RooFit
RooDataHist   = ROOT.RooDataHist
RooRealVar    = ROOT.RooRealVar
RooArgList    = ROOT.RooArgList
RooArgSet     = ROOT.RooArgSet
RooAbsReal    = ROOT.RooAbsReal
RooDataSet    = ROOT.RooDataSet
RooCBShape    = ROOT.RooCBShape
RooAddPdf     = ROOT.RooAddPdf
RooExtendPdf  = ROOT.RooExtendPdf
RooPolynomial = ROOT.RooPolynomial
RooLinearVar  = ROOT.RooLinearVar
RooConst      = ROOT.RooFit.RooConst
RooConstVar   = ROOT.RooConstVar
RooChebychev  = ROOT.RooChebychev
RooArgusBG    = ROOT.RooArgusBG
RooExponential= ROOT.RooExponential

def DataSet(Input,RooVar,DataSetName,Variable=None,Treename='DecayTree',Selection='',Wspace=None,Scale=1):
    
    Scale = float(1 / Scale)
    
    if isinstance(Input,str) and (".root" in Input):
        array = root2array(Input,Treename,Variable,Selection) * Scale
    elif isinstance(Input,np.ndarray):
        if isinstance(Input.dtype.names,tuple):
            array = Input[Variable] * Scale
        else:
            array = Input * Scale
    elif isinstance(Input,ROOT.TTree):
        array = tree2array(Input,Variable,Selection) * Scale
        

    dataSet = RooDataSet(DataSetName,DataSetName,RooArgSet(RooVar))
    
    for i in array:
        RooVar.setVal(i)
        dataSet.add(RooArgSet(RooVar))
        
    dataSet.Print('v')
    
    if not Wspace == None:
        if not Wspace.allVars().contains(RooVar):
            "Print the RooRealVar dubbed {0} is added to the working space {1}!".format(RooVar.GetName(),Wspace.GetName())
            Wspace.rfimport(RooVar)  
    
    Wspace.rfimport(dataSet)

    return dataSet
    

    
    


