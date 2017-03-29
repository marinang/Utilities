#!/usr/bin/env python
# @file   Hist.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

from __future__ import division
import ROOT
from Tree import readTree
from array import *

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
                print j
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
        
    def nBins(self):
        
        return len(self.Bins) - 1
        
class EffHist(ROOT.TH1F):
    
    def __init__(self, name, variable):
        
        self.var = variable
        bin_scheme  = variable.get('BinningScheme','')
        self.NAME = variable.get('Name','')
        NBINS = variable.get('nBins','')
        XMIN = variable.get('xMin','')
        XMAX = variable.get('xMax','')
        self.SCALE = variable.get('scale',1)
        self.Yaxis_name = "Efficiency"
        self.Xaxis_name = ""
        
        
        if isinstance(bin_scheme, BinningScheme) and (XMIN == '') and (XMAX == '') and (NBINS == ''):
            ROOT.TH1F.__init__(self,name,name,bin_scheme.nBins(),bin_scheme.ReturnArray(self.SCALE))
        else:
            ROOT.TH1F.__init__(self,name,name,NBINS,XMIN*self.SCALE,XMAX*self.SCALE)
        
        self.hist_passed = None
        self.hist_total = None
        self.selection = ""
        self.file = ""
        
        
    def addFile(self,file,selection="",treename="DecayTree"):
        #input file with the events
        self.file = InputFile(file, selection, treename)

    def addSelection(self,selection):
        #Efficiency is computed using this selection
        
        self.selection = selection
        
        self.hist_total = GetHist(self.var,self.file,self.NAME+"_Total",treename='DecayTree',scale=self.SCALE)
        
        self.hist_passed = GetHist(self.var,self.file,self.NAME+"_Total",selection=self.selection,treename='DecayTree',scale=self.SCALE)
        
        self.Divide(self.hist_passed,self.hist_total,1.0,1.0,"B")
        self.Sumw2()
        
    def return_TGraphAsymmErrors(self):
        
        gr = ROOT.TGraphAsymmErrors()
        gr.Divide(self.hist_passed,self.hist_total)
        gr.SetName(self.GetName()+" ")
        gr.GetYaxis().SetTitle(self.Yaxis_name)
        if self.Xaxis_name == "":
            gr.GetXaxis().SetTitle(self.var['Name'] + ' ' + self.var.get('Units',''))
        else:
            gr.GetXaxis().SetTitle(self.Xaxis_name)
        return gr
    
def InputFile(file,selection,treename,debug=False):
    
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

def GetHist(variable,file,name,selection = '',treename='DecayTree',weight_var = '',name_opt=0,scale=1,debug=False):
    
    #variable is a dictionnary of a list of dictionnaries
    #ex: muE = {'Name':'mu_plus_PE', 'xMin':550, 'xMax':1000000,  'nBins':100, 'Units':'MeV'}
    #of course if it's a list, all variables are compatible i.e can be added together
    #name_opt = 1 give the name of the histogram for the X axis
    
    if not isinstance(variable,(list,tuple)):
        variable = [variable]
    
    hists = []

    tree = InputFile(file,selection,treename,debug)

    nEvts= tree.GetEntries()

    scale = float(1 / scale)

    for var in variable:
        
        bin_scheme  = var.get('BinningScheme','')
        NAME = var.get('Name','')
        NBINS = var.get('nBins','')
        XMIN = var.get('xMin','')
        XMAX = var.get('xMax','')
        
        if isinstance(bin_scheme, BinningScheme) and (XMIN == '') and (XMAX == '') and (NBINS == ''):
            hist  = ROOT.TH1F(NAME,NAME,bin_scheme.nBins(),bin_scheme.ReturnArray(scale))
        else:
            hist  = ROOT.TH1F(NAME,NAME,NBINS,XMIN*scale,XMAX*scale)
        
        hist.Sumw2()
        #unit = scaleUnits(var['Units'],scale)
        unit = var.get('Units','')
        
        hist.GetXaxis().SetTitle(var['Name'] + ' ' + unit)
        hist.GetYaxis().SetTitle('Events')
        hist.GetYaxis().SetTitleOffset(1.15)
        
        if name_opt == 0:
            hist.GetXaxis().SetTitle(var['Name'] + ' ' + unit)
        elif name_opt == 1:
            hist.GetXaxis().SetTitle(name + ' ' + unit)
        
        hists.append(hist)
    
    
    for i in xrange(nEvts):
        
        tree.GetEntry(i)
        for hist in hists:
            value = tree.GetLeaf(hist.GetName()).GetValue()
            if 'DIRA' in var:
                value = math.acos(value)
            if weight_var == '':
                hist.Fill(value*scale)
            else:
                w = tree.GetLeaf(weight_var).GetValue()
                hist.Fill(value*scale,w)
                
                
    return AddHists(hists,name)
    
    destruct_object(tree)



def AddHists(hists,name):
    
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

"""
def scaleUnits(unit,scale=1):
    
    new_unit=''
    
    if scale == 1:
        new_unit = unit
    
    #works with *eV:
    elif 'eV' in unit:
        if 'M' in unit:
            if scale == 1E-3:
                new_unit = unit.replace('M','G')

    return new_unit
"""
