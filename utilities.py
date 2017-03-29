#!/usr/bin/env python
# @file   Utilities.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2015-09-30

from __future__ import division
import ROOT
from PyLHCb.Root.RootUtils import LHCbStyle
from PyLHCb.Root.RootUtils import destruct_object
from PyLHCb.Utilities.Debug import memory_usage
import glob
import os
import math
from Tree import readTree


def destruct_objects(*args):
    for o in args:
        destruct_object(o)

def to_precision(x,p):
    """
        returns a string representation of x formatted with a precision of p
        
        Based on the webkit javascript implementation taken from here:
        https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
        """
    x = float(x)
    if x == 0.:
        return "0." + "0"*(p-1)
    out = []
    if x < 0:
        out.append("-")
        x = -x
    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)
    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)
    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1
    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1
    m = "%.*g" % (p, n)
    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)
    return "".join(out)



def Get2DHist(variable1,variable2,file,name,selection='',weight_var = '',treename="DecayTree",scale=1):
    
    
    hist  = ROOT.TH2F(name,name,variable1['nBins'],variable1['xMin'],variable1['xMax'],variable2['nBins'],variable2['xMin'],variable2['xMax'])
    
    tree = readTree(file,selection,treename)
    nEvts= tree.GetEntries()
    
    
    scale = float(1 / scale)
    for i in xrange(nEvts):
        tree.GetEntry(i)
        value1 = tree.GetLeaf(variable1['Name']).GetValue()
        value2 = tree.GetLeaf(variable2['Name']).GetValue()
        if 'DIRA' in variable1:
            value1 = math.acos(value1)
        if 'DIRA' in variable2:
            value2 = math.acos(value2)
        if weight_var == '':
            hist.Fill(value1,value2)
        else:
            w = tree.GetLeaf(weight_var).GetValue()
            hist.Fill(value1,value2,w)

    hist.GetXaxis().SetTitle(variable1['Name'] + ' ' + scaleUnits(variable1['Units'],scale))
    hist.GetYaxis().SetTitle(variable2['Name'] + ' ' + scaleUnits(variable2['Units'],scale))

    hist.SetBins (variable1['nBins'],variable1['xMin']*scale,variable1['xMax']*scale,variable2['nBins'],variable2['xMin']*scale,variable2['xMax']*scale)
    
    return hist


def scaleUnits(unit,scale=1):
    
    if scale == 1:
        new_unit = unit
    
    #works with *eV:
    elif 'eV' in unit:
        if 'M' in unit:
            if scale == 1E-3:
                new_unit = unit.replace('M','G')

    return new_unit


def plot2Graphs(stack1,stack2,folder,file_name,filled=0,legend=0,normalized=0,logy=0):
    
    cdata = ROOT.TCanvas("cdata","cdata",1100,512)
    cdata.Divide(2)
    maxY  = []
    
    
    cdata.cd(1)
    
    if not isinstance(stack1,(list,tuple)):
        stack1 = [stack1]
    
    if legend == 1:
        leg = ROOT.TLegend(0.57,0.77,0.89,0.94);
    
    i = 2
    for hist in stack1:
        if i == 5:
            i = i + 1
        hist.SetLineWidth(1)
        hist.SetLineColor(i)
        i = i + 1
        
        
        if normalized == 1:
            hist.Sumw2()
            hist.Scale(1./hist.Integral())
            hist.GetYaxis().SetTitle('')
            ROOT.gStyle.SetPadLeftMargin(-0.05)
            ROOT.gROOT.ForceStyle()



        maxY.append(hist.GetMaximum())
    
    #first variable
    if filled == 1:
        stack1[0].SetFillColor(38)
        stack1[0].SetLineColor(4)
        stack1[1].SetLineColor(2)
        if legend == 1:
            leg.AddEntry(stack1[0],stack1[0].GetName(),"f")
            for hist in stack1:
                if hist != stack1[0]:
                    leg.AddEntry(hist,hist.GetName(),"l")
                else:
                    continue
    else:
        if legend == 1:
            for hist in stack1:
                leg.AddEntry(hist,hist.GetName(),"l")




    for i in range(len(stack1)):
        if i == 0:
            stack1[i].Draw('hist')
            stack1[i].SetMaximum(1.14*max(maxY))
            #stack[0].SetMaximum(2.14*max(maxY))
            stack1[i].SetMinimum(0)
        else:
            stack1[i].Draw('histsame')

    if legend == 1:
        leg.Draw()

    maxY  = []

    cdata.cd(2)
    
    if not isinstance(stack2,(list,tuple)):
        stack2 = [stack2]
    
    if legend == 1:
        leg = ROOT.TLegend(0.72,0.77,0.92,0.94);
    
    i = 2
    for hist in stack2:
        if i == 5:
            i = i + 1
        hist.SetLineWidth(1)
        hist.SetLineColor(i)
        i = i + 1
        
        
        if normalized == 1:
            hist.Sumw2()
            hist.Scale(1./hist.Integral())
            hist.GetYaxis().SetTitle('')
        
        
        
        maxY.append(hist.GetMaximum())
    
    #first variable
    if filled == 1:
        stack2[0].SetFillColor(38)
        stack2[0].SetLineColor(4)
        stack2[1].SetLineColor(2)
        if legend == 1:
            leg.AddEntry(stack2[0],stack2[0].GetName(),"f")
            for hist in stack2:
                if hist != stack2[0]:
                    leg.AddEntry(hist,hist.GetName(),"l")
                else:
                    continue
    else:
        if legend == 1:
            for hist in stack2:
                leg.AddEntry(hist,hist.GetName(),"l")




    for i in range(len(stack2)):
        if i == 0:
            stack2[i].Draw('hist')
            stack2[i].SetMaximum(1.14*max(maxY))
            #stack2[0].SetMaximum(2.14*max(maxY))
            stack2[i].SetMinimum(0)
        else:
            stack2[i].Draw('histsame')

    if legend == 1:
        leg.Draw()


    if logy == 1:
        cdata.SetLogy(logy)
    


    if not os.path.isdir(os.path.join('images',folder)):
        os.mkdir( os.path.join('images',folder))
    cdata.SaveAs(os.path.join('images',folder,file_name) )
    cdata.Close()




#def plot2D(var1,var2,file,folder,treename,selection = ''):
def plot2D(hist,folder,file_name):

    """hist = ROOT.TH2D('hist','hist',var1['nBins'],var1['xMin'],var1['xMax'],var2['nBins'],var2['xMin'],var2['xMax'])


    tree = readTree(file,treename,selection)
    nEvts = tree.GetEntries()
    for i in xrange(nEvts):
        tree.GetEntry(i)
        value1 = tree.GetLeaf(var1['Name']).GetValue()
        value2 = tree.GetLeaf(var2['Name']).GetValue()
        hist.Fill(value1,value2)"""

    canvas = ROOT.TCanvas()
    hist.Draw('')
    #hist.GetXaxis().SetTitle(var1['Name'] + "  " + var1['Units'])
    #hist.GetYaxis().SetTitle(var2['Name'] + "  " + var2['Units'])
    hist.GetXaxis().SetTitleOffset(1.05)
    hist.GetYaxis().SetTitleOffset(1.0)
    hist.SetMarkerSize(2)
    hist.SetMarkerColor(4)
    hist.SetMarkerStyle(1)


    #ROOT.gStyle.SetPadLeftMargin(0.16)
    #ROOT.gStyle.SetPadRightMargin(0.15)
    #ROOT.gROOT.ForceStyle()
    
    #file_name = 'fig_'+var1['Name']+'_'+var2['Name']+'.pdf'
    if not os.path.isdir(os.path.join('images',folder)):
        os.mkdir( os.path.join('images',folder) )
    canvas.SaveAs(os.path.join('images',folder,file_name) )
    canvas.Close()
    
    #destruct_object(hist)

def TwoScales(stack1,stack2,folder,file_name,filled=0,legend=0,normalized=0,logy=0,err=0):

    cdata = ROOT.TCanvas()
    maxY1  = []
    maxY2  = []
    
    pad1 = ROOT.TPad("pad1","",0,0,1,1)
    pad2 = ROOT.TPad("pad2","",0,0,1,1)
    pad2.SetFillStyle(4000) #will be transparent
    pad2.SetFrameFillStyle(0)
    pad1.Draw()
    pad1.cd()
    
    if not isinstance(stack1,(list,tuple)):
        stack1 = [stack1]
    
    if not isinstance(stack2,(list,tuple)):
        stack2 = [stack2]


    if legend == 1:
        leg = ROOT.TLegend(0.68,0.77,0.86,0.93);
    
    i = 2
    for hist in stack1:
        hist.SetLineWidth(1)
        if hist == stack1[0]:
            hist.SetLineColor(4)
            
            #first variable
            if filled == 1:
                hist.SetFillColor(38)
                if legend == 1:
                    leg.AddEntry(hist,hist.GetName(),"f")
            elif err == 1:
                hist.SetMarkerColor(4)
                hist.SetMarkerStyle(8)
                hist.SetMarkerSize(0.4)
                if legend == 1:
                    leg.AddEntry(hist,hist.GetName(),"lep")
            else:
                if legend == 1:
                    leg.AddEntry(hist,hist.GetName(),"l")
    
        else:
            if i == 4:
                i = i + 2
            hist.SetLineColor(i)
            
            if err == 1:
                hist.SetMarkerColor(i)
                hist.SetMarkerStyle(8)
                hist.SetMarkerSize(0.4)
                if legend == 1:
                    leg.AddEntry(hist,hist.GetName(),"lep")
            else:
                if legend == 1:
                    leg.AddEntry(hist,hist.GetName(),"l")
            i = i + 1

        if normalized == 1:
            hist.Sumw2()
            hist.Scale(1./hist.Integral())
            hist.GetYaxis().SetTitle('')
        
        maxY1.append(hist.GetMaximum())
            
    for hist in stack1:
        if hist == stack1[0]:
            if err == 0:
                hist.Draw('hist')
            else:
                hist.Draw('E1')
            hist.SetMaximum(1.14*max(maxY1))
            #stack[0].SetMaximum(2.14*max(maxY))
            hist.SetMinimum(0)
            if logy == 1:
                hist.SetMinimum(0.11)
                cdata.SetLogy(logy)
                    
        else:
            if err == 0:
                hist.Draw('histsame')
            else:
                hist.Draw('E1same')

    pad1.Update()
    cdata.cd()
    #cdata.Update()
            
            
    for hist in stack2:
        hist.SetLineWidth(1)
        if i == 4:
            i = i + 2
        hist.SetLineColor(i)
            
        if err == 1:
            hist.SetMarkerColor(i)
            hist.SetMarkerStyle(8)
            hist.SetMarkerSize(0.4)
            if legend == 1:
                leg.AddEntry(hist,hist.GetName(),"lep")
        else:
            if legend == 1:
                leg.AddEntry(hist,hist.GetName(),"l")
        i = i + 1
        
        if normalized == 1:
            hist.Sumw2()
            hist.Scale(1./hist.Integral())
            hist.GetYaxis().SetTitle('')

        maxY2.append(hist.GetMaximum())


    rightmax = 1.14*max(maxY2)
    scale = ROOT.gPad.GetUymax()/rightmax

    pad2.Draw()
    pad2.cd()

    for hist in stack2:
        
        hist.Scale(scale)

        if err == 0:
            hist.Draw('histsameY+')
        else:
            hist.Draw('E1sameY+')

        hist.SetMaximum(1.14*max(maxY2))
        hist.SetMinimum(0)
        if logy == 1:
            hist.SetMinimum(0.11)
            cdata.SetLogy(logy)
                
    pad2.Update()

    #axis = ROOT.TGaxis(ROOT.gPad.GetUxmax(),ROOT.gPad.GetUymin(),ROOT.gPad.GetUxmax(),ROOT.gPad.GetUymax(),0,rightmax,510,"+LB")
    #axis.SetLabelOffset(0.015)

    #axis.Draw()
    
    
    if legend == 1:
        cdata.cd()
        leg.Draw()


    if not os.path.isdir(os.path.join('images',folder)):
        os.mkdir( os.path.join('images',folder))
    cdata.SaveAs(os.path.join('images',folder,file_name) )
    cdata.Close()


