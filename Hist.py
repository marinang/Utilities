#!/usr/bin/env python
# @file   Hist.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

from __future__ import division
import ROOT
from .Tree import readTree
from array import *
import numpy as np
from skhep import units
from Utilities.utilities import destruct_objects

import sys
from rootpy.plotting import Hist, Graph, Hist2D, Profile, Hist3D
import uproot
import histbook

class BinningScheme:
    
    def __init__(self, xmin, xmax):
        self.Bins = [xmin,xmax]
        self.Xmin = xmin
        self.Xmax = xmax
        
    def addUniformBins(self, nBins, xmin, xmax):

        overlap = False
        common_min = False
        common_max = False
        
        for j in self.Bins:
            if (j > xmin) and (j<xmax):
                overlap = True
                break
            elif j == xmin:
                common_min = True
            elif j == xmax:
                common_max = True
                
            
        if not overlap:
            unif_bins = []
            bin_width = (xmax - xmin) / nBins
        
            for i in xrange(nBins+1):
                
                if common_min and i == 0:
                    continue
                elif common_max and i == nBins:
                    continue
                    
                unif_bins.append(xmin+(i)*bin_width)
            
            self.Bins = sorted(self.Bins + unif_bins)
        else:
            print("Can not include uniforms bins between "+str(xmin)+" and "+str(xmax)+" because another bin boundary is present in that range!")
            print(self.Bins)
            
    def addBin(self, UpperLimit):
        
        if UpperLimit in self.Bins:
            "Bin limit already set!"
        else:
            self.Bins = sorted(self.Bins+[UpperLimit])
        
    def ReturnArray(self,scale=1):
        
        bins = [i*scale for i in self.Bins]
        return array('d', bins)
        
    def ReturnBins(self,scale=1):
        
        bins = [i*scale for i in self.Bins]
        return bins
        
    def nBins(self):
        
        return len(self.Bins) - 1
        
class EffHist(ROOT.TH1F):
    
    def __init__(self, name, variable, scale=1, **kwargs):
        
        self._kwargs = kwargs
       
        if set(['nbins', 'xmin', 'xmax']).issubset(kwargs.keys()):
            nbins, xmin, xmax = kwargs["nbins"], kwargs["xmin"], kwargs["xmax"]
            ROOT.TH1F.__init__(self,name,name,nbins,xmin*scale,xmax*scale)

        elif set(['bin_scheme']).issubset(kwargs.keys()):
            bin_scheme = kwargs["bin_scheme"]
            ROOT.TH1F.__init__(self,name,name,bin_scheme.nBins(),bin_scheme.ReturnArray(scale))

        elif set(['bins']).issubset(kwargs.keys()):
            bins = array('d', kwargs["bins"])
            ROOT.TH1F.__init__(self,name,name,len(bins)-1, bins)           
        
        self.var = variable
        self.name = name
        self.scale = scale
        self.Yaxis_name = "Efficiency"
        self.Xaxis_name = ""
        self.hist_passed = None
        self.hist_total = None
        self.selection = None
        self.input = None
        
    def addInput(self, input):
        #input tree with the events
        self.input = input
        
    def addHists(self, hist_total, hist_passed):
        
        self.hist_total = hist_total.Clone()
        self.hist_passed = hist_passed.Clone()
        
        self.Divide(self.hist_passed,self.hist_total,1.0,1.0,"B")
        self.Sumw2()
        
    def addSelection(self, selection):
        
        if self.input is not None:
            self.selection = selection
            
            self.hist_total = GetHist(self.input, self.var, self.name+"_Total", **self._kwargs)
            self.hist_passed = GetHist(self.input, self.var, self.name+"_Passed", selection=self.selection, **self._kwargs)

            self.Divide(self.hist_passed,self.hist_total,1.0,1.0,"B")
            self.Sumw2()
            
        else:
            raise NotImplementedError("Add and input first!")
        
    def return_TGraphAsymmErrors(self, MPL=False):
        
        self.gr = ROOT.TGraphAsymmErrors()
        self.gr.Divide(self.hist_passed,self.hist_total)

        if self.Xaxis_name == "":
            self.gr.GetXaxis().SetTitle(self.var)
        else:
            self.gr.GetXaxis().SetTitle(self.Xaxis_name)
            
        self.gr.SetFillStyle(1001)
            
        if MPL:
            self.gr = Graph(self.gr)
            self.gr.name = self.GetName()+"_graph"
            self.gr.title = self.GetTitle()
            yaxis = self.gr.yaxis
            yaxis.title = self.Yaxis_name
        else:
            self.gr.SetName(self.GetName()+"_graph")
            self.gr.SetTitle(self.GetTitle()+" ")
            self.gr.GetYaxis().SetTitle(self.Yaxis_name)
            self.gr.SetMinimum(self.GetMinimum()-0.1)
            self.gr.SetMaximum(self.GetMaximum()+0.1)

        return self.gr
        
    def delete(self):
        destruct_objects(self.hist_passed, self.hist_total, self.gr, self)
    
def InputFile(file, selection, treename, debug=False):
    
    File = False
    Tree = False

    if isinstance(file,(list,tuple)):
        for f in file:
            if (isinstance(f,str)) and ('.root' in f):
                File = True
            else:
                print("The input number "+str(file.index(f)+1)+" of the List is not valid!")
                print("It is a " + str(type(f)))
                File = False
                break
    else:
        if (isinstance(file,str)) and ('.root' in file):
            File = True
        elif (isinstance(file,ROOT.TTree)) and (treename in file.GetName()):
            Tree = True
        else:
            print("The input is not valid!")
            print("It is a " + str(type(file)))
        
    if File:
        return readTree(file,selection,treename)
    elif Tree:
        return file.CopyTree(selection)
    else:
        print(" Error, no valid TFile nor Ttree provided! Check the name, treename etc ... ")
        
        
#def Hist( name, title="", **kwargs):
#
#    if set(['nbins', 'xmin', 'xmax']).issubset(kwargs.keys()):
#        nbins, xmin, xmax = kwargs["nbins"], kwargs["xmin"], kwargs["xmax"]
#        hist = Hist(nbins,xmin,xmax,name=name,title=name,type='F')
#        
#    elif set(['bin_scheme']).issubset(kwargs.keys()):
#        bin_scheme = kwargs["bin_scheme"]
#        hist = Hist(bin_scheme.ReturnBins(),name=name,title=name,type='F')
#        
#    elif set(['bins']).issubset(kwargs.keys()):
#        bins = kwargs["bins"]
#        hist = Hist(bins,name=name,title=name,type='F')
#        
#    return hist
                
def GetHist(input, variable, name="", selection="", treename='DecayTree', weights=None,  **kwargs):

    if name == "":
        name = variable
        
    if weights:
        branches = [variable,weights]
    else:
        branches = variable
                
    if isinstance(input,str) and (".root" in input):
        array = root2array(input,treename,branches,selection)
    elif isinstance(input,np.ndarray):
        if isinstance(input.dtype.names,tuple):
            if isinstance(selection, np.ndarray):
                array = input[selection]
                array = array[branches]
            else:
                array = input[branches]
        else:
            array = input
    elif isinstance(input,ROOT.TTree):
        array = tree2array(input,branches,selection)
        
    if set(['nbins', 'xmin', 'xmax']).issubset(kwargs.keys()):
        nbins, xmin, xmax = kwargs["nbins"], kwargs["xmin"], kwargs["xmax"]
        hist = Hist(nbins,xmin,xmax,name=name,title=name,type='F')
        
    elif set(['bin_scheme']).issubset(kwargs.keys()):
        bin_scheme = kwargs["bin_scheme"]
        hist = Hist(bin_scheme.ReturnBins(),name=name,title=name,type='F')
        
    elif set(['bins']).issubset(kwargs.keys()):
        bins = kwargs["bins"]
        hist = Hist(bins,name=name,title=name,type='F')
    
    if weights:
        hist.Sumw2()
        fill_hist(hist,array[variable],array[weights])
    else:
        fill_hist(hist,array)
    
    return hist
    
def GetProfile(input, variable_x, variable_y, name="", selection="", treename='DecayTree', weights=None, **kwargs):
    
    #1 nbins, xmin, xmax
    #2 BinningScheme

    scale_x = float(1 / kwargs.get("scale_x",1))
    scale_y = float(1 / kwargs.get("scale_y",1))
    
    if len(kwargs) == 5:
        if any("nbins" in k for k in kwargs.keys()):
            nbins, xmin, xmax = kwargs["nbins"], kwargs["xmin"]*scale_x, kwargs["xmax"]*scale_x
            params = [nbins, xmin, xmax]
        else: raise ValueError()
    else: raise ValueError()
    
    hist = Profile(*params,name=name,title=name)
        
    if weights:
        branches = [variable_x,variable_y,weights]
    else:
        branches = [variable_x,variable_y]
    
    if isinstance(input,str) and (".root" in input):
        array = root2array(input,treename,branches,selection)
    elif isinstance(input,np.ndarray):
        if isinstance(selection, np.ndarray):
            array = input[selection]
            array = array[branches]
        else:
            array = input[branches]
    elif isinstance(input,ROOT.TTree):
        array = tree2array(input,branches,selection)
        
    variable_x = array[variable_x]*scale_x
    variable_y = array[variable_y]*scale_y
        
    array = np.zeros((len(array),2))
    array[:,0] = variable_x
    array[:,1] = variable_y
        
    fill_profile(hist,array)
    
    return hist
    
def Get2DHist(input, variables, name, selection="", treename='DecayTree', weights=None, scale = 1.,  **kwargs):
        
    if not isinstance(variables, list) and len(variables) == 2:
        raise NotImplementedError("Remember that you are filling a 2D histogram!")
        
    if not set(['binsx', 'binsy']).issubset(kwargs.keys()):
        raise NotImplementedError("Please provide some binnings for each variable!")
        
    varx, vary= variables[0], variables[1]
    bins = [kwargs["binsx"], kwargs["binsy"]]
        
    if weights:
        branches = variables + [weights]
    else:
        branches = variables
                
    if isinstance(input,str) and (".root" in input):
        array = root2array(input,treename,branches,selection)
    elif isinstance(input,np.ndarray):
        if isinstance(input.dtype.names,tuple):
            if isinstance(selection, np.ndarray):
                array = input[selection]
                array = array[branches]
            else:
                array = input[branches]
        else:
            array = input
    elif isinstance(input,ROOT.TTree):
        array = tree2array(input,branches,selection)
        
    BINS = []
        
    for b in bins:
        if set(['nbins', 'xmin', 'xmax']).issubset(b.keys()):
            nbins, xmin, xmax = b["nbins"], b["xmin"], b["xmax"]
            BINS += [nbins, xmin, xmax]
        
        elif set(['bin_scheme']).issubset(b.keys()):
            bin_scheme = b["bin_scheme"]
            BINS.append(bin_scheme.ReturnBins())
            
        elif set(['bins']).issubset(b.keys()):
            bins = b["bins"]
            BINS.append(bins)
        
    hist = Hist2D(*BINS,name=name,title=name,type='F')
    
    array_to_fill = np.empty((len(array),2))
    
    array_to_fill[:,0] = array[varx]
    array_to_fill[:,1] = array[vary]
    
    if weights:
        hist.Sumw2()
        fill_hist(hist,array_to_fill,array[weights])
    else:
        fill_hist(hist,array_to_fill)
            
    return hist
        
def Get3DHist(input, variables, name, selection="", treename='DecayTree', weights=None, scale = 1.,  **kwargs):
        
    if not isinstance(variables, list) and len(variables) == 3:
        raise NotImplementedError("Remember that you are filling a 3D histogram!")
        
    if not set(['binsx', 'binsy', 'binsz']).issubset(kwargs.keys()):
        raise NotImplementedError("Please provide some binnings for each variable!")
        
    varx, vary, varz = variables[0], variables[1], variables[2]
    bins = [kwargs["binsx"], kwargs["binsy"], kwargs["binsz"]]
        
    if weights:
        branches = variables + [weights]
    else:
        branches = variables
                
    if isinstance(input,str) and (".root" in input):
        array = root2array(input,treename,branches,selection)
    elif isinstance(input,np.ndarray):
        if isinstance(input.dtype.names,tuple):
            if isinstance(selection, np.ndarray):
                array = input[selection]
                array = array[branches]
            else:
                array = input[branches]
        else:
            array = input
    elif isinstance(input,ROOT.TTree):
        array = tree2array(input,branches,selection)
        
    BINS = []
        
    for b in bins:
        if set(['nbins', 'xmin', 'xmax']).issubset(b.keys()):
            nbins, xmin, xmax = b["nbins"], b["xmin"], b["xmax"]
            BINS += [nbins, xmin, xmax]
        
        elif set(['bin_scheme']).issubset(b.keys()):
            bin_scheme = b["bin_scheme"]
            BINS.append(bin_scheme.ReturnBins())
            
        elif set(['bins']).issubset(b.keys()):
            bins = b["bins"]
            BINS.append(bins)
        
    hist = Hist3D(*BINS,name=name,title=name,type='F')
    
    array_to_fill = np.empty((len(array),3))
    
    array_to_fill[:,0] = array[varx]
    array_to_fill[:,1] = array[vary]
    array_to_fill[:,2] = array[varz]
    
    if weights:
        hist.Sumw2()
        fill_hist(hist,array_to_fill,array[weights])
    else:
        fill_hist(hist,array_to_fill)
    
    return hist
    

def AddHists(hists, name):
    
    for hist in hists:
        if hist == hists[0]:
            hist.Sumw2()
            continue
        else:
            hists[0].Add(hist)
            destruct_object(hist)
    
    histogram = hists[0]
    histogram.SetNameTitle(name,name)
    return histogram

