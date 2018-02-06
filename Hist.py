#!/usr/bin/env python
# @file   Hist.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

from __future__ import division
import ROOT
from Tree import readTree
from array import *
from root_numpy import root2array, tree2array, fill_hist, fill_profile
import numpy as np

import sys
sys.path.append('home/marinang/packages/anaconda2/lib/python2.7/site-packages')
from rootpy.plotting import Hist, Graph, Hist2D, Profile

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
            print "Can not include uniforms bins between "+str(xmin)+" and "+str(xmax)+" because another bin boundary is present in that range!"
            print self.Bins
            
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
        
        if len(kwargs) == 3 and any("nbins" in k for k in kwargs.keys()):
            nbins, xmin, xmax = kwargs["nbins"], kwargs["xmin"], kwargs["xmax"]
            ROOT.TH1F.__init__(self,name,name,nbins,xmin*scale,xmax*scale)
            self.bin_scheme = None
            self.nbins = nbins
            self.xmin = xmin
            self.xmax = xmax
            
        elif len(kwargs) == 1 and any("bin_scheme" in k for k in kwargs.keys()):
            bin_scheme = kwargs["bin_scheme"]
            ROOT.TH1F.__init__(self,name,name,bin_scheme.nBins(),bin_scheme.ReturnArray(scale))
            self.bin_scheme = bin_scheme
            self.nbins = None
            self.xmin = None
            self.xmax = None
        
        self.var = variable
        self.name = name
        self.scale = scale
        self.Yaxis_name = "Efficiency"
        self.Xaxis_name = ""
        self.hist_passed = None
        self.hist_total = None
        self.selection = ""
        self.input = ""
        
    def addInput(self, input):
        #input tree with the events
        self.input = input
        
    def addHists(self, hist_total, hist_passed):
        
        self.hist_total = hist_total.Clone()
        self.hist_passed = hist_passed.Clone()
        
        self.Divide(self.hist_passed,self.hist_total,1.0,1.0,"B")
        self.Sumw2()

    def addSelection(self, selection):
        
        self.selection = selection
                
        if self.bin_scheme:
            self.hist_total = GetHist(self.input, self.var, self.name+"_Total", scale=self.scale, bin_scheme=self.bin_scheme)
            self.hist_passed = GetHist(self.input, self.var, self.name+"_Passed", selection=self.selection, scale=self.scale, bin_scheme=self.bin_scheme)
        else:
            self.hist_total = GetHist(self.input, self.var, self.name+"_Total", scale=self.scale, nbins=self.nbins, xmin=self.xmin, xmax=self.xmax)
            self.hist_passed = GetHist(self.input, self.var, self.name+"_Passed", selection=self.selection, scale=self.scale, nbins=self.nbins, xmin=self.xmin, xmax=self.xmax)
        
        self.Divide(self.hist_passed,self.hist_total,1.0,1.0,"B")
        self.Sumw2()
        
    def return_TGraphAsymmErrors(self, MPL=False):
        
        gr = ROOT.TGraphAsymmErrors()
        gr.Divide(self.hist_passed,self.hist_total)

        if self.Xaxis_name == "":
            gr.GetXaxis().SetTitle(self.variable)
        else:
            gr.GetXaxis().SetTitle(self.Xaxis_name)
            
        if MPL:
            gr = Graph(gr)
            gr.name = self.GetName()
            gr.title = self.GetTitle()
        else:
            gr.SetName(self.GetName()+" ")
            gr.SetTitle(self.GetTitle()+" ")
            gr.GetYaxis().SetTitle(self.Yaxis_name)
            gr.SetMinimum(self.GetMinimum()-0.1)
            gr.SetMaximum(self.GetMaximum()+0.1)

        return gr
    
def InputFile(file, selection, treename, debug=False):
    
    File = False
    Tree = False

    if isinstance(file,(list,tuple)):
        for f in file:
            if (isinstance(f,str)) and ('.root' in f):
                File = True
            else:
                print "The input number "+str(file.index(f)+1)+" of the List is not valid!"
                print "It is a " + str(type(f))
                File = False
                break
    else:
        if (isinstance(file,str)) and ('.root' in file):
            File = True
        elif (isinstance(file,ROOT.TTree)) and (treename in file.GetName()):
            Tree = True
        else:
            print "The input is not valid!"
            print "It is a " + str(type(file))
        
    if File:
        return readTree(file,selection,treename)
    elif Tree:
        return file.CopyTree(selection)
    else:
        print " Error, no valid TFile nor Ttree provided! Check the name, treename etc ... "
        
def GetHist(input, variable, name="", selection="", treename='DecayTree', weights=None, scale=1, **kwargs):
    
    #1 nbins, xmin, xmax
    #2 BinningScheme
    
    if name == "":
        name = variable
        
    scale = float(1 / scale)
    
    if len(kwargs) == 3 and any("nbins" in k for k in kwargs.keys()):
        nbins, xmin, xmax = kwargs["nbins"], kwargs["xmin"]*scale, kwargs["xmax"]*scale
        hist = Hist(nbins,xmin,xmax,name=name,title=name,type='F')
    elif len(kwargs) == 1 and any("bin_scheme" in k for k in kwargs.keys()):
        bin_scheme = kwargs["bin_scheme"]
        hist = Hist(bin_scheme.ReturnBins(scale),name=name,title=name,type='F')
    
    if weights:
        branches = [variable,weights]
    else:
        branches = variable
    
    if isinstance(input,str) and (".root" in input):
        array = root2array(input,treename,branches,selection)
    elif isinstance(input,np.ndarray):
        if isinstance(input.dtype.names,tuple):
            array = input[branches]
        else:
            array = input
    elif isinstance(input,ROOT.TTree):
        array = tree2array(input,branches,selection)
    
    
    if weights:
        fill_hist(hist,array[variable]*scale,array[weights])
    else:
        fill_hist(hist,array*scale)
    
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
    
def Get2DHist(input, variable_x, variable_y, name="", selection="", treename='DecayTree', weights=None, **kwargs):
    
    #1 nbins, xmin, xmax
    #2 BinningScheme

    scale1 = float(1 / kwargs.get("scale1",1))
    scale2 = float(1 / kwargs.get("scale2",1))
    
    if len(kwargs) == 8:
        if any("nbins1" in k for k in kwargs.keys()) and any("nbins2" in k for k in kwargs.keys()):
            nbins1, xmin1, xmax1 = kwargs["nbins1"], kwargs["xmin1"]*scale1, kwargs["xmax1"]*scale1
            nbins2, xmin2, xmax2 = kwargs["nbins2"], kwargs["xmin2"]*scale2, kwargs["xmax2"]*scale2
            params = [nbins1, xmin1, xmax1, nbins2, xmin2, xmax2]
        else: raise ValueError()
    else: raise ValueError()

    hist = Hist2D(*params,name=name,title=name,type='F')
    
    branches = [variable_x,variable_y]
    
    if isinstance(input,str) and (".root" in input):
        array = root2array(input,treename,branches,selection)
    elif isinstance(input,np.ndarray):
        array = input[branches]
    elif isinstance(input,ROOT.TTree):
        array = tree2array(input,branches,selection)

    variable_x = array[variable_x]*scale1
    variable_y = array[variable_y]*scale2
        
    array = np.zeros((len(array),2))
    array[:,0] = variable_x
    array[:,1] = variable_y
            
    fill_hist(hist,array)
        
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

