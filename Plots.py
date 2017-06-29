#!/usr/bin/env python
# @file   Plots.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

import ROOT
import glob
import os

import sys
sys.path.append('home/marinang/packages/anaconda2/lib/python2.7/site-packages')

from Hist import EffHist
import matplotlib as mpl
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt


def LHCbStyle():
    
    STYLE = {}

    STYLE['figure.figsize'] = 8.75, 5.92
    STYLE['figure.dpi'] = 1000

    STYLE['font.family'] = 'sans-serif'
    STYLE['font.serif'] =  'Times New Roman'
    STYLE['font.size'] =   2
    STYLE['font.weight'] = 200

    STYLE['legend.frameon'] = False
    STYLE['legend.handletextpad'] = 0.3
    STYLE['legend.numpoints'] =     1
    STYLE['legend.labelspacing'] =  0.3
    STYLE['legend.fontsize'] =      17

    STYLE['lines.linewidth'] =       1.4
    STYLE['lines.markeredgewidth'] = 1.4
    STYLE['lines.markersize'] =      8

    STYLE['savefig.bbox'] = 'tight'
    STYLE['savefig.pad_inches'] = 0.1
    
    STYLE['axes.labelsize'] = 20
    STYLE['axes.linewidth'] = 1

    STYLE['xtick.major.size'] =  11
    STYLE['xtick.minor.size'] =  6
    STYLE['xtick.major.width'] = 1.2
    STYLE['xtick.minor.width'] = 1.2
    STYLE['xtick.major.pad'] =   10
    STYLE['xtick.minor.pad'] =   10
    STYLE['xtick.labelsize'] =   17

    STYLE['ytick.major.size'] =  11
    STYLE['ytick.minor.size'] =  6
    STYLE['ytick.major.width'] = 1.2
    STYLE['ytick.minor.width'] = 1.2
    STYLE['ytick.major.pad'] =   10
    STYLE['ytick.minor.pad'] =   10
    STYLE['ytick.labelsize'] =   17
    
    for k, v in STYLE.iteritems():
            mpl.rcParams[k] = v
    
def Decorate(Objs, Filled=False, Legend=None, Normalized=False, Err=False, Candle=False, MPL=False):
    
    
    if not isinstance(Objs,(list,tuple)):
        Objs = [Objs]
            
    new_Objs = []
    
    for h in Objs:
        if isinstance(h, EffHist):
            gr = h.return_TGraphAsymmErrors(MPL)
            new_Objs.append(gr)
        else:
            new_Objs.append(h)
    Objs = new_Objs 
    
    if Legend:
        leg = ROOT.TLegend(Legend)
    else:
        leg = Legend
              
    i = 2
    for obj in Objs:
        name_leg = "#bf{"+obj.GetTitle()+"}"
        if MPL:
            obj.SetLineWidth(1)
        else:
            obj.SetLineWidth(1)
        
        if obj == Objs[0]:
            obj.SetLineColor(4)
            
            #first variable
            if Filled == True:
                obj.SetFillColor(38)
                if Legend:
                    leg.AddEntry(obj,name_leg,"f")
            elif (Candle == True) or isinstance(obj, ROOT.TGraphAsymmErrors) or (Err == True):
                obj.SetLineWidth(2)
                obj.SetMarkerColor(4)
                obj.SetMarkerStyle(8)
                obj.SetMarkerSize(0.8)
                if Legend:
                    leg.AddEntry(obj,name_leg,"lep")
            else:
                if Legend:
                    leg.AddEntry(obj,name_leg,"l")
        else:
            if i == 4:
                i = i + 2
            obj.SetLineColor(i)
            if (Candle == True) or isinstance(obj, ROOT.TGraphAsymmErrors) or (Err == True):
                obj.SetLineWidth(2)
                obj.SetMarkerColor(i)
                obj.SetMarkerStyle(8)
                obj.SetMarkerSize(0.8)
                if Legend:
                    leg.AddEntry(obj,name_leg,"lep")
            else:
                if Legend:
                    leg.AddEntry(obj,name_leg,"l")
            i = i + 1
        
        if Normalized:
            obj.Scale(1./obj.Integral())
            obj.GetYaxis().SetTitle('Normalized Distribution')
                
    Dict = {'objs':Objs, 'leg':leg}

    return Dict


def Draw(Dict, Logy=False, Err=False, Candle=False, minY=-999999, maxY=999999):

    Objs,leg = Dict.get('objs'),Dict.get('leg')
    
    if minY == -999999:
        minY = min([h.GetMinimum() for h in Objs])
    if maxY == 999999:
        maxY = 1.12*max([h.GetMaximum() for h in Objs])

    for obj in Objs:
        
        if obj == Objs[0]:
            if Candle == True:
                obj.Draw('Candle')
            elif isinstance(obj, ROOT.TGraphAsymmErrors):
                obj.Draw('AP')
            elif Err == False:
                obj.Draw('hist')
            else:
                obj.Draw('E1')
            if not isinstance(obj, ROOT.TGraphAsymmErrors):
                if Logy == True:
                    minY = 0.0005
                    maxY = 1.3*maxY
            obj.SetMaximum(maxY)
            obj.SetMinimum(minY)
                    
        else:
            if Candle == True: 
                obj.Draw('SAME')
            elif isinstance(obj, ROOT.TGraphAsymmErrors):
                obj.Draw('P')
            elif Err == False:
                obj.Draw('histsame')
            else:
                obj.Draw('E1same')

    if leg:
        leg.Draw()
        
def DrawMPL(Dict, axes, Logy=False, Err=False, Legend=True, Xlabel=None, Ylabel=None,minY=-999999, maxY=999999):

    Objs = Dict.get('objs')
    
    if minY == -999999:
        minY = min([h.GetMinimum() for h in Objs])
    if maxY == 999999:
        maxY = 1.12*max([h.GetMaximum() for h in Objs])
    if Logy:
        minY = 0.0005
        maxY = 1.3*maxY
        
    if not Xlabel:
        Xlabel = Objs[0].GetName()
    if not Ylabel:
        Ylabel = ""

    for obj in Objs:
        
        if Err or isinstance(obj, ROOT.TGraphAsymmErrors):
            axes.set_xlabel(Xlabel, ha='right', x=1)
            axes.set_ylabel(Ylabel, ha='right', y=1)
            if Logy:
                axes.set_yscale("log", nonposy='clip')
            rplt.errorbar(obj,axes=axes,emptybins=False)
        
        if isinstance(obj, ROOT.TH1F):
            axes.set_xlabel(Xlabel, ha='right', x=1)
            axes.set_ylabel("Events", ha='right', y=1)
            rplt.hist(obj,Objsed=False,axes=axes,logy=Logy)
            
    axes.set_ylim(minY,maxY)
    
    if Legend:
        leg = plt.Legend(loc='best')
            
    
def plotVariables(Objs, Folder, FileName, Filled=False, Legend=None, Normalized=False, Logy=False, Err=False, MPL=False, Xlabel=None, Ylabel=None, minY=-999999, maxY=999999):
    
    hl = Decorate(Objs,Filled,Legend,Normalized,Err,MPL=MPL)
    
    if not os.path.isdir(os.path.join('images',Folder)):
        os.mkdir( os.path.join('images',Folder))
    
    if not MPL:
    
        cdata = ROOT.TCanvas()
        Draw(hl,Logy,Err,Candle,minY,maxY)

        if Logy == True:
            cdata.SetLogy(Logy)
        
        cdata.SaveAs(os.path.join('images',Folder,FileName) )
        cdata.Close()
        
    else:
        
        LHCbStyle()
        fig = plt.figure()
        axes = plt.axes()
        
        DrawMPL(hl,axes,Logy,Err,Legend,Xlabel,Ylabel,minY,maxY)
        plt.minorticks_on()
        
        fig.savefig(os.path.join('images',Folder,FileName))
        print("Figure {0} has been created".format(os.path.join('images',Folder,FileName)))  
    
    
def TwoScales(Hists, Effs, Folder, FileName, Xlabel="", Legend=False, **kwargs):
    
    LHCbStyle()
    
    if not isinstance(Hists,(list,tuple)):
        Hists = [Hists]
        
    if not isinstance(Effs,(list,tuple)):
        Effs = [Effs]
        
    hl = Decorate(Hists+Effs,MPL=True)
    hl1 = hl['objs'][0:len(Hists)]
    hl2 = hl['objs'][len(Hists):]

    fig, ax1 = plt.subplots()
            
    rplt.hist(hl1, Objsed=False, axes=ax1)
    ax1.set_xlabel(Xlabel, ha='right', x=1)
    ax1.set_ylabel("Events", ha='right', y=1)
    
    ax2 = ax1.twinx()
        
    rplt.errorbar(hl2, axes=ax2, emptybins=False)
    ax2.set_ylabel("Efficiency", ha='right', y=1)
    
    if "y2_min" in kwargs.keys() and "y2_max" in kwargs.keys():
        ax2.set_ylim(kwargs["y2_min"],kwargs["y2_maxs"])
    elif "y2_min" in kwargs.keys() and not "y2_max" in kwargs.keys():
        ax2.set_ylim(kwargs["y2_min"],1)
    elif not "y2_min" in kwargs.keys() and "y2_max" in kwargs.keys():
        ax2.set_ylim(0.0,kwargs["y2_max"])

    plt.minorticks_on()
    
    import matplotlib.patches as mpatches
    
    patch = []
    for h in hl1:
        patch.append(mpatches.Patch(edgecolor=h.GetLineColor('mpl'), facecolor="none", linewidth=h.GetLineWidth()))
    
    if Legend:
        h1, l1 = ax1.get_Legend_handles_labels()
        h2, l2 = ax2.get_Legend_handles_labels()
        ax1.Legend(patch+h2, l1+l2, loc='best')
    
        
    #fig.tight_layout()
        
    plt.minorticks_on()
    
    if not os.path.isdir(os.path.join('images',Folder)):
        os.mkdir( os.path.join('images',Folder))
    fig.savefig(os.path.join('images',Folder,FileName))
    print("Figure {0} has been created".format(os.path.join('images',Folder,FileName)))    
    

