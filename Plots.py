#!/usr/bin/env python
# @file   Plots.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

import ROOT
import glob
import os
from Hist import EffHist

def DecorateHists(stack,filled=0,legend=0,normalized=0,err=0,candle=0):
    
    if not isinstance(stack,(list,tuple)):
        stack = [stack]
    
    new_stack = []
    
    for h in stack:
        if isinstance(h, EffHist):
            gr = h.return_TGraphAsymmErrors()
            new_stack.append(gr)
        else:
            new_stack.append(h)
    stack = new_stack  
          
    if legend != 0:
        leg = ROOT.TLegend(legend)
    else:
        leg = False
    # ROOT.TLegend(0.57,0.77,0.89,0.94)
    
    i = 2
    for hist in stack:
        
        name_leg = "#bf{"+hist.GetTitle()+"}"
        
        hist.SetLineWidth(1)
        if hist == stack[0]:
            hist.SetLineColor(4)
            
            #first variable
            if filled == 1:
                hist.SetFillColor(38)
                if legend != 0:
                    leg.AddEntry(hist,name_leg,"f")
            elif (candle == 1) or isinstance(hist, ROOT.TGraphAsymmErrors) or (err == 1):
                hist.SetLineWidth(2)
                hist.SetMarkerColor(4)
                hist.SetMarkerStyle(8)
                hist.SetMarkerSize(0.8)
                if legend != 0:
                    leg.AddEntry(hist,name_leg,"lep")
            else:
                if legend != 0:
                    leg.AddEntry(hist,name_leg,"l")

        else:
            if i == 4:
                i = i + 2
            hist.SetLineColor(i)
            if (candle == 1) or isinstance(hist, ROOT.TGraphAsymmErrors) or (err == 1):
                hist.SetLineWidth(2)
                hist.SetMarkerColor(i)
                hist.SetMarkerStyle(8)
                hist.SetMarkerSize(0.8)
                if legend != 0:
                    leg.AddEntry(hist,name_leg,"lep")
            else:
                if legend != 0:
                    leg.AddEntry(hist,name_leg,"l")
            i = i + 1
        
        if normalized == 1:
            
            hist.Scale(1./hist.Integral())
            hist.GetYaxis().SetTitle('Normalized Distribution')
                
    dict = {'hists':stack, 'leg':leg}

    return dict


def DrawHists(dict,logy=0,err=0,candle=0,minY=-999999,maxY=999999):

    stack,leg = dict.get('hists'),dict.get('leg')
    
    if minY == -999999:
        minY = min([h.GetMinimum() for h in stack])
    if maxY == 999999:
        maxY = 1.12*max([h.GetMaximum() for h in stack])
        
    for hist in stack:
    
        if hist == stack[0]:
            if candle == 1:
                hist.Draw('CANDLE')
            elif isinstance(hist, ROOT.TGraphAsymmErrors):
                hist.Draw('AP')
            elif err == 0:
                hist.Draw('hist')
            else:
                hist.Draw('E1')
            if not isinstance(hist, ROOT.TGraphAsymmErrors):
                if logy == 1:
                    minY = 0.0005
                    maxY = 1.3*maxY
            hist.SetMaximum(maxY)
            hist.SetMinimum(minY)
                    
        else:
            if candle == 1: 
                hist.Draw('SAME')
            elif isinstance(hist, ROOT.TGraphAsymmErrors):
                hist.Draw('P')
            elif err == 0:
                hist.Draw('histsame')
            else:
                hist.Draw('E1same')

    if leg != False:
        leg.Draw()


def plotVariables(stack,folder,file_name,filled=0,legend=0,normalized=0,logy=0,err=0,candle=0,minY=-999999,maxY=999999):
    
    cdata = ROOT.TCanvas()
    
    hl = DecorateHists(stack,filled,legend,normalized,err,candle)

    DrawHists(hl,logy,err,candle,minY,maxY)

    if logy == 1:
         cdata.SetLogy(logy)
    
    if not os.path.isdir(os.path.join('images',folder)):
        os.mkdir( os.path.join('images',folder))
    cdata.SaveAs(os.path.join('images',folder,file_name) )
    cdata.Close()

