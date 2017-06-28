#!/usr/bin/env python
# @file   Plots.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

import ROOT
import glob
import os
from Hist import EffHist

def DecorateHists(stack, filled=False, legend=None, normalized=False, err=False, candle=False):
    
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
    
    if legend:
        leg = ROOT.TLegend(legend)
    else:
        leg = legend
              
    i = 2
    for hist in stack:
        
        name_leg = "#bf{"+hist.GetTitle()+"}"
        
        hist.SetLineWidth(1)
        if hist == stack[0]:
            hist.SetLineColor(4)
            
            #first variable
            if filled == True:
                hist.SetFillColor(38)
                if legend:
                    leg.AddEntry(hist,name_leg,"f")
            elif (candle == True) or isinstance(hist, ROOT.TGraphAsymmErrors) or (err == True):
                hist.SetLineWidth(2)
                hist.SetMarkerColor(4)
                hist.SetMarkerStyle(8)
                hist.SetMarkerSize(0.8)
                if legend:
                    leg.AddEntry(hist,name_leg,"lep")
            else:
                if legend:
                    leg.AddEntry(hist,name_leg,"l")

        else:
            if i == 4:
                i = i + 2
            hist.SetLineColor(i)
            if (candle == True) or isinstance(hist, ROOT.TGraphAsymmErrors) or (err == True):
                hist.SetLineWidth(2)
                hist.SetMarkerColor(i)
                hist.SetMarkerStyle(8)
                hist.SetMarkerSize(0.8)
                if legend:
                    leg.AddEntry(hist,name_leg,"lep")
            else:
                if legend:
                    leg.AddEntry(hist,name_leg,"l")
            i = i + 1
        
        if normalized == True:
            
            hist.Scale(1./hist.Integral())
            hist.GetYaxis().SetTitle('Normalized Distribution')
                
    dict = {'hists':stack, 'leg':leg}

    return dict


def DrawHists(dict, logy=False, err=False, candle=False, minY=-999999, maxY=999999):

    stack,leg = dict.get('hists'),dict.get('leg')
    
    if minY == -999999:
        minY = min([h.GetMinimum() for h in stack])
    if maxY == 999999:
        maxY = 1.12*max([h.GetMaximum() for h in stack])
        
    for hist in stack:
    
        if hist == stack[0]:
            if candle == True:
                hist.Draw('CANDLE')
            elif isinstance(hist, ROOT.TGraphAsymmErrors):
                hist.Draw('AP')
            elif err == False:
                hist.Draw('hist')
            else:
                hist.Draw('E1')
            if not isinstance(hist, ROOT.TGraphAsymmErrors):
                if logy == True:
                    minY = 0.0005
                    maxY = 1.3*maxY
            hist.SetMaximum(maxY)
            hist.SetMinimum(minY)
                    
        else:
            if candle == True: 
                hist.Draw('SAME')
            elif isinstance(hist, ROOT.TGraphAsymmErrors):
                hist.Draw('P')
            elif err == False:
                hist.Draw('histsame')
            else:
                hist.Draw('E1same')

    if leg:
        leg.Draw()


def plotVariables(stack, folder, file_name, filled=False, legend=None, normalized=False, logy=False, err=False, candle=False, minY=-999999, maxY=999999):
    
    cdata = ROOT.TCanvas()
    
    hl = DecorateHists(stack,filled,legend,normalized,err,candle)

    DrawHists(hl,logy,err,candle,minY,maxY)

    if logy == True:
         cdata.SetLogy(logy)
    
    if not os.path.isdir(os.path.join('images',folder)):
        os.mkdir( os.path.join('images',folder))
    cdata.SaveAs(os.path.join('images',folder,file_name) )
    cdata.Close()
    
    
def TwoScales(stack1, stack2, folder, file_name, legend=None, err=False):

    if not isinstance(stack1,(list,tuple)):
        stack1 = [stack1]
        
    if not isinstance(stack2,(list,tuple)):
        stack2 = [stack2]


    cdata = ROOT.TCanvas()
    maxY1  = []
    maxY2  = []
    
    pad1 = ROOT.TPad("pad1","",0,0,1,1)
    pad2 = ROOT.TPad("pad2","",0,0,1,1)
    pad2.SetFillStyle(4000) #will be transparent
    pad2.SetFrameFillStyle(0)

    hl = DecorateHists(stack1+stack2,legend=legend,err=err)
    hl1 = {'hists':hl['hists'][0:len(stack1)], 'leg':None}
    hl2 = {'hists':hl['hists'][len(stack1):], 'leg':None}
      
    pad1.Draw()
    pad1.cd()
      
    DrawHists(hl2,err=err)
   
    pad1.Update()
    cdata.cd()
    
    maxY2 = [hist.GetMaximum() for hist in hl1['hists']]
    rightmax = 1.12*max(maxY2)
    scale = ROOT.gPad.GetUymax()/rightmax
    
    pad2.Draw()
    pad2.cd()
    
    for hist in hl1['hists']:
        
#        hist = hist.GetHistogram()
#        print(hist)
        
        hist.Scale(scale)
        
#        if isinstance(hist, ROOT.TGraphAsymmErrors):
#            h = hist.GetHistogram()
#            h.Scale(scale)
#            h.SetAxisRange(-130,300,"X")
#            h.Draw('E1sameY+') 
##            .Draw('PY-')
        if err == False:
            hist.Draw('histsameY+')
        else:
            hist.Draw('E1sameY+') 

        hist.SetMaximum(1.12*max(maxY2))
        hist.SetMinimum(0)

    pad2.Update() 
    cdata.cd()   
    
    if legend:
        legend.Draw()


    if not os.path.isdir(os.path.join('images',folder)):
        os.mkdir( os.path.join('images',folder))
    cdata.SaveAs(os.path.join('images',folder,file_name) )
    cdata.Close()

