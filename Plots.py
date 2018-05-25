#!/usr/bin/env python
# @file   Plots.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

import ROOT
import glob
import os

from .Hist import EffHist
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from future.utils import iteritems


def LHCbStyle():
    
    STYLE = {}

    STYLE['figure.figsize'] = 8.75, 5.92
    STYLE['figure.dpi'] = 300

    STYLE['font.family'] = 'sans-serif'
    STYLE['font.serif'] =  'Times New Roman'
    STYLE['font.size'] =   2
    STYLE['font.weight'] = 500
    STYLE['font.style'] = 'normal'

    STYLE['legend.frameon'] = False
    STYLE['legend.handletextpad'] = 0.3
    STYLE['legend.numpoints'] =     1
    STYLE['legend.labelspacing'] =  0.3
    STYLE['legend.fontsize'] =      17

    STYLE['lines.linewidth'] =       1.4
    STYLE['lines.markeredgewidth'] = 1.4
    STYLE['lines.markersize'] =      8
    
    STYLE['errorbar.capsize'] =      1.3

    STYLE['savefig.bbox'] = 'tight'
    STYLE['savefig.pad_inches'] = 0.1
    STYLE['savefig.dpi'] = 800
    
    STYLE['axes.labelsize'] = 20
    STYLE['axes.linewidth'] = 1.8
    STYLE['axes.labelweight'] = 500

    STYLE['xtick.major.size'] =  11
    STYLE['xtick.minor.size'] =  6
    STYLE['xtick.major.width'] = 2
    STYLE['xtick.minor.width'] = 2
    STYLE['xtick.major.pad'] =   10
    STYLE['xtick.minor.pad'] =   10
    STYLE['xtick.labelsize'] =   17

    STYLE['ytick.major.size'] =  11
    STYLE['ytick.minor.size'] =  6
    STYLE['ytick.major.width'] = 1.8
    STYLE['ytick.minor.width'] = 1.8
    STYLE['ytick.major.pad'] =   10
    STYLE['ytick.minor.pad'] =   10
    STYLE['ytick.labelsize'] =   17
    
    for k, v in iteritems(STYLE):
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
    
    if Legend and not MPL:
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
                if Legend and not MPL:
                    leg.AddEntry(obj,name_leg,"f")
            elif (Candle == True) or isinstance(obj, ROOT.TGraphAsymmErrors) or (Err == True):
                obj.SetLineWidth(2)
                obj.SetMarkerColor(4)
                obj.SetMarkerStyle(8)
                obj.SetMarkerSize(0.8)
                if Legend and not MPL:
                    leg.AddEntry(obj,name_leg,"lep")
            else:
                if Legend and not MPL:
                    leg.AddEntry(obj,name_leg,"l")
        else:
            if i == 4:
                i = i + 2
            if i == 10:
                i = 1
            obj.SetLineColor(i)
            if (Candle == True) or isinstance(obj, ROOT.TGraphAsymmErrors) or (Err == True):
                obj.SetLineWidth(2)
                obj.SetMarkerColor(i)
                obj.SetMarkerStyle(8)
                obj.SetMarkerSize(0.8)
                if Legend and not MPL:
                    leg.AddEntry(obj,name_leg,"lep")
            else:
                if Legend and not MPL:
                    leg.AddEntry(obj,name_leg,"l")
            i = i + 1
        
        if Normalized:
            obj.Scale(1./obj.Integral())
            obj.GetYaxis().SetTitle('Normalized Distribution')
                
    Dict = {'objs':Objs, 'leg':leg}

    return Dict


def Draw(Dict, Logy=False, Err=False, minY=-999999, maxY=999999, Candle=False):

    Objs,leg = Dict.get('objs'),Dict.get('leg')
    
    if minY == -999999:
        minY = min([h.GetMinimum() for h in Objs])
    if maxY == 999999:
        maxY = 1.20*max([h.GetMaximum() for h in Objs])

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
                    maxY = 1.32*maxY
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
        
def DrawMPL(Dict, axes, Logy=False, Err=False, Legend=True, Xlabel=None, Ylabel=None, xlimit = (-999999,999999), ylimit = (-999999,999999)):

    Objs = Dict.get('objs')
    
    minY, maxY = ylimit[0], ylimit[1]
    minX, maxX = xlimit[0], xlimit[1]

    if minY == -999999:
        minY = min([h.GetMinimum() for h in Objs])
    if maxY == 999999:
        maxY = 1.48*max([h.GetMaximum() for h in Objs])
    if Logy:
        minY = 0.0005
        maxY = 2.2*maxY
        axes.set_yscale("log", nonposx='clip')
        
    if not Xlabel:
        Xlabel = Objs[0].GetXaxis().GetTitle()
 
    patch, name = [],[]
    for obj in Objs:
        
        if Err or isinstance(obj, ROOT.TGraphAsymmErrors):
            axes.set_xlabel(Xlabel, ha='right', x=1)
            axes.set_ylabel(Ylabel, ha='right', y=1)
            if Logy:
                axes.set_yscale("log", nonposy='clip')
            if not Ylabel:
                Ylabel = Objs[0].GetYaxis().GetTitle()  
            axes.set_ylabel(Ylabel, ha='right', y=1)
            rplt.errorbar(obj,axes=axes,emptybins=False)
            h, l = axes.get_legend_handles_labels()
            patch.append(h[-1])
            name.append(l[-1])
            continue
        elif isinstance(obj, ROOT.TH1):
            alpha = getattr(obj, 'alpha', None)
            axes.set_xlabel(Xlabel, ha='right', x=1)
            if not Ylabel:
                Ylabel = "Events"
            axes.set_ylabel(Ylabel, ha='right', y=1)
            rplt.hist(obj,Objsed=False,axes=axes,logy=Logy,linewidth=1.5)
            h, l = axes.get_legend_handles_labels()
            patch.append(mpatches.Patch(edgecolor=obj.GetLineColor('mpl'), facecolor=obj.GetFillColor('mpl'), linewidth=obj.GetLineWidth(), alpha=alpha, linestyle = obj.GetLineStyle('mpl')))
            name.append(l[-1])
            continue
        elif isinstance(obj, ROOT.TH2):
            axes.set_xlabel(Xlabel, ha='right', x=1)
            axes.set_ylabel(Ylabel, ha='right', x=1)
            rplt.hist2d(obj, axes=axes)
            h, l = axes.get_legend_handles_labels()
            
    axes.get_yaxis().set_tick_params(direction='in', left=True, right=True)
    axes.get_xaxis().set_tick_params(direction='in', bottom=True, top=True)
    axes.get_yaxis().set_tick_params(direction='in', which='minor', left=True, right=True)
    axes.get_xaxis().set_tick_params(direction='in', which='minor', bottom=True, top=True)
    if not( maxX == 999999 and minX == -999999 ):
        axes.set_xlim(minX,maxX)
    axes.set_ylim(minY,maxY)
    
    if Legend:
        plt.legend(patch, name, loc='best')
    
def plotVariables(Objs, Folder, FileName, Filled=False, Legend=None, Normalized=False, Logy=False, Err=False, MPL=False, Xlabel=None, Ylabel=None, xlimit = (-999999,999999), ylimit = (-999999,999999)):
        
    hl = Decorate(Objs,Filled,Legend,Normalized,Err,MPL=MPL)
    if Normalized:
         Ylabel = "Normalized Distribution"
    
    if not os.path.isdir(os.path.join('images',Folder)):
        os.mkdir( os.path.join('images',Folder))
    
    if not MPL:
        
        minY, maxY = ylimit[0], ylimit[1]

        cdata = ROOT.TCanvas()
        Draw(hl,Logy,Err,minY,maxY)

        if Logy == True:
            cdata.SetLogy(Logy)

        cdata.SaveAs(os.path.join('images',Folder,FileName) )
        cdata.Close()
        
    else:
        LHCbStyle()
        fig, axes = plt.subplots()

        DrawMPL(hl,axes,Logy,Err,Legend,Xlabel,Ylabel,xlimit,ylimit)
        plt.minorticks_on()
        
        fig.savefig(os.path.join('images',Folder,FileName))
        print("Figure {0} has been created".format(os.path.join('images',Folder,FileName))) 
        plt.close(fig)
    
    
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
    
    patch = []
    for h in hl1:
        patch.append(mpatches.Patch(edgecolor=h.GetLineColor('mpl'), facecolor="none", linewidth=h.GetLineWidth()))
    
    if Legend:
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.Legend(patch+h2, l1+l2, loc='best')

    #fig.tight_layout()
        
    plt.minorticks_on()
    
    if not os.path.isdir(os.path.join('images',Folder)):
        os.mkdir( os.path.join('images',Folder))
    fig.savefig(os.path.join('images',Folder,FileName))
    print("Figure {0} has been created".format(os.path.join('images',Folder,FileName)))    
    

