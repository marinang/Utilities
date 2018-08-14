# -*- coding: utf-8 -*-
#!/usr/bin/env python
# @file   RooFit.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2017-19-05

from __future__ import division
import ROOT
import glob
import os
import math
import numpy as np
from rootpy import asrootpy
from rootpy.plotting import Hist
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from Utilities.Plots import LHCbStyle
from uuid import uuid4
from math import sqrt, log


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

class RooDataset(object):
    
    def __init__(self, Name, RooVar):
        
        self.var  = RooVar
        self.data = RooDataSet( Name, Name, RooArgSet(self.var))
        
    def fill(self, array):
        
        for ai in array:
            self.var.setVal(ai)
            self.data.add(RooArgSet(self.var))
            
    def Print(self, option):
            
        self.data.Print( option )
        
    def to_wspace(self, wspace ):
        
        if not wspace.allVars().contains(self.var):
            "Print the RooRealVar dubbed {0} is added to the working space {1}!".format( self.var.GetName(), wspace.GetName())
            wspace.rfimport(self.var)  
            
        wspace.rfimport( self.data )
        
def RemoveEmptyBins(frame,hist_name="0"):

    # histname=0 means that the last RooHist is taken from the RooPlot

    hist = frame.findObject(hist_name,ROOT.RooHist.Class())

    x = hist.GetX()
    y = hist.GetY()
    
    import math

    for i in range(hist.GetN()):
        if math.fabs(y[i] < 0.0000001) and (hist.GetErrorYhigh(i) > 0.):
            hist.SetPointEYlow(i,0)
            hist.SetPointEYhigh(i,0)
        

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
    
    
class ResidualPlot(object):
    def __init__(self, title, frame):
        self.title = title
        self._id = str(uuid4())
        self._frame = frame
        self.residualHisto = None
        self.pullHisto = None
        self.alphaLabel = None
        self.canvas = None
        self.pullCanvas = None
        self.objects = {}
        self.boxes = []
        self._boxes = []

    def plot(self, bigLabels=False, removeTitle=True, residualBand=False, yLogScale=False, statusLabel=None, labelPosition="L"):
        def _setMargins(pad):
            pad.SetBottomMargin(0.1)
            pad.SetLeftMargin(0.13)
            pad.SetTopMargin(0.05)
            pad.SetRightMargin(0.05)

        self.canvas = ROOT.TCanvas("{0}_{1}".format(self.title, self._id), self.title, 800, 700)
        padHisto, padResid = self.prepareCanvas(bool(self.residualHisto))
        if removeTitle:
            ROOT.gStyle.SetOptTitle(0)
        if padHisto:
            if removeTitle:
                padHisto.SetTitle("")
            padHisto.cd()
            _setMargins(padHisto)
        _setMargins(self.canvas)
        fXAxis = self._frame.GetXaxis()
        fYAxis = self._frame.GetYaxis()
        if bigLabels:
            fXAxis.SetTitleOffset(1.0)
            fXAxis.SetTitleSize(0.045)
            fXAxis.SetLabelSize(0.045)
            fYAxis.SetTitleSize(0.045)
            fYAxis.SetLabelSize(0.042)
            fYAxis.SetTitleOffset(1.45)
        else:
            fXAxis.SetTitleOffset(1.0)
            fXAxis.SetTitleSize(0.04)
            fXAxis.SetLabelSize(0.04)
            fYAxis.SetTitleSize(0.04)
            fYAxis.SetLabelSize(0.04)
            fYAxis.SetTitleOffset(1.55)
        self._frame.Draw()
        for boxMin,boxMax in self.boxes:
            box = ROOT.TBox(max(fXAxis.GetXmin(),boxMin),
                                 0,
                                 min(fXAxis.GetXmax(),boxMax),
                                 self._frame.GetMaximum())
            box.SetFillStyle(1001)
            box.SetFillColor(ROOT.kGray)
            line = ROOT.TLine(max(fXAxis.GetXmin(),boxMin),self._frame.GetMaximum(),min(fXAxis.GetXmax(),boxMax),self._frame.GetMaximum())
            self._boxes.append(box)
            self._boxes.append(line)
            box.Draw("same")
            line.Draw("same")
        self._frame.Draw("same")
        if padHisto:
            if yLogScale:
                padHisto.SetLogy()
            if statusLabel:
                from rootpy.plotting.style.lhcb.labels import LHCb_label as lhcb_label
                statusArgs = {'status': statusLabel}
                if statusLabel not in ['final', 'preliminary', 'unofficial']:
                    statusArgs['status'] = 'custom'
                    if statusLabel == 'simulation':
                        statusArgs['text'] = "#splitline{LHCb}{#scale[1.0]{Simulation}}"
                    else:
                        statusArgs['text'] = statusLabel
                statusArgs['pad'] = padHisto
                label, _ = lhcb_label(labelPosition, **statusArgs)
                label.SetFillStyle(0)
        for obj in self.objects.values():
            obj.Draw("same")
        if self.residualHisto:
            fXAxis.CenterTitle()
            fXAxis.SetTitleOffset(0.5)
            fXAxis.SetLabelSize(0)
            padResid.cd()
            padHisto.SetLeftMargin(0.13)
            padHisto.SetBottomMargin(0.07)
            padResid.SetRightMargin(0.05)
            padResid.SetLeftMargin(0.13)
            # Axes
            resXaxis = self.residualHisto.GetXaxis()
            resYaxis = self.residualHisto.GetYaxis()
            sr = 1.0/0.2
            #srH = 1.0/0.8
            resXaxis.SetTickLength ( sr * resXaxis.GetTickLength() )
            resXaxis.SetLabelOffset( sr * resXaxis.GetLabelOffset() )
            resXaxis.SetTitleSize    ( 0 )
            resXaxis.SetLabelOffset(0.05)
            resYaxis.SetNdivisions ( 504 )
            if bigLabels:
                fYAxis.SetTitleSize(0.05)
                fXAxis.SetTitleSize(0.05)
                fYAxis.SetLabelSize(0.05)
                fYAxis.SetTitleOffset(1.35)
                resXaxis.SetLabelSize    ( sr * 0.04 )
                resYaxis.SetLabelSize    ( sr * 0.04 )
            else:
                fYAxis.SetTitleSize(0.045)
                fXAxis.SetTitleSize(0.045)
                fYAxis.SetLabelSize(0.045)
                fYAxis.SetTitleOffset(1.45)
                resXaxis.SetLabelSize    ( 0.037*sr )
                resYaxis.SetLabelSize    ( 0.037*sr )
            if not residualBand:
                self.residualHisto.Draw("E1")
            else:
                self.residualHisto.SetFillColor(39)
                self.residualHisto.SetMarkerSize(0.01)
                self.residualHisto.Draw("E3")
            self.lines = self.plotLines(self.residualHisto)
            if self.alphaLabel:
                self.canvas.cd()
                self.alphaLabel.Draw()
                self.canvas.Update()
            padResid.Update()

    def plotPull(self):
        #gStyle.SetOptStat(0)
        #gStyle.SetOptFit(0111)
        self.pullCanvas = ROOT.TCanvas()
        self.pullHisto.GetXaxis().SetTitle("residuals")
        self.pullHisto.Fit('gaus')

    def addResidual(self, histName, curveName, xMin=None, xMax=None, numParams=0):
        histo = self._frame.getHist(histName)
        curve = self._frame.getCurve(curveName)
        xaxis = self._frame.GetXaxis()
        #xaxis = histo.GetXaxis()
        if not histo:
            raise ValueError("Cannot find histo -> %s" % histName)
        if not curve:
            raise ValueError("Cannot find curve -> %s" % curveName)
        # Residual range
        if xMin is None:
            xMin = xaxis.GetXmin()
        if xMax is None:
            xMax = xaxis.GetXmax()
        # Create residual histogram
        self.residualHisto, chisum = self.residualHist(histo, curve, xaxis, (xMin, xMax))
        if numParams > 0:
            dof = self._frame.getHist(histName).GetN() - numParams - 1
            self.alphaLabel = self.calculateAlpha(chisum, dof)
        return chisum

    def prepareCanvas(self, addResidual):
        padHisto = self.canvas.GetListOfPrimitives().At(0)
        padResid = None
        if addResidual:
            self.canvas.Divide(1, 2, 0.01, 0.01)
            padHisto = self.canvas.GetListOfPrimitives().At(0)
            padResid = self.canvas.GetListOfPrimitives().At(1)
            small = 0.07
            r = 0.2
            # Configure the pad for the histo
            padHisto.SetPad(0.,r ,1.0, 1.0)
            # Configure the pad for the residuals
            padHisto.SetBottomMargin(small-0.01)
            padResid.SetPad(0.0, 0.0, 1.0, r)
            padResid.SetBottomMargin(0.25)
            padResid.SetTopMargin(small)
        return padHisto, padResid

    def calculateAlpha(self, chisum, dof):
        #print "chisum",chisum
        #print "dof", dof
        alpha = ROOT.TMath.Prob(chisum, dof)
        alphaStr = "#alpha = %.4f" % alpha
        label = ROOT.TLatex(0.83, 0.2, alphaStr)
        label.SetTextSize(0.03)
        print("I have a chi2 of %s and %s dof, so alpha is %s" % (chisum, dof, alpha))
        return label

    def residualHist(self, data, curve, xAxis, resRange, chisum=0.0):
        def getResidual(datum, pdf):
            chi2 = 0.0
            if pdf > 0:
                chi2 += 2.0 * (pdf-datum)
                if datum > 0:
                    chi2 += 2.0 * datum * log(datum/pdf)
            return sqrt(chi2) if datum > pdf else -sqrt(chi2)

        # Proportion correction
        #r = 0.2
        #sr = 1.0/0.2
        # Histo features
        n = data.GetN()
        #print "N bins: ",n
        xMin = xAxis.GetXmin()
        xMax = xAxis.GetXmax()
        #print xMin, xMax
        # Create residual histo
        residuals = ROOT.TH1F("residuals_{0}".format(self._id), "", n, xMin, xMax)
        pulls     = ROOT.TH1F("pulls_{0}".format(self._id), "", 11, -5.5, 5.5)
        datum = ROOT.Double(0.0)
        pdf     = 0.0
        xBin    = ROOT.Double(0.0)
        resValue = ROOT.Double(0.0)
        # ranges
        rangeMin, rangeMax = resRange
        if curve:
            for bin in range(n):
                data.GetPoint(bin, xBin, datum)
                if xBin < rangeMin or xBin > rangeMax:
                    continue
                pdf = curve.Eval(xBin)
                resValue = getResidual(datum, pdf)
                chisum += resValue*resValue
                #print datum, pdf
                #print "chisum:", chisum
                #print "Setting bin: ", bin+1, resValue
                residuals.SetBinContent(bin+1, resValue)
                residuals.SetBinError(bin+1, 1.0)
                pulls.Fill(resValue)
        # Cosmetics
        residuals.SetMinimum        ( -5.     )
        residuals.SetMaximum        (    5.     )
        residuals.SetStats            ( False )
        residuals.SetMarkerStyle( 20        )
        residuals.SetMarkerSize ( .8        )
        self.pullHisto = pulls
        return residuals, chisum

    def plotLines(self, residHisto):
        xMin = residHisto.GetXaxis().GetXmin()
        xMax = residHisto.GetXaxis().GetXmax()
        # Create lines
        uppLine = ROOT.TLine(xMin, 2.0, xMax, 2.0)
        midLine = ROOT.TLine(xMin, 0.0, xMax, 0.0)
        lowLine = ROOT.TLine(xMin, -2.0, xMax, -2.0)
        uppLine.SetLineColor( ROOT.kRed )
        lowLine.SetLineColor( ROOT.kRed )
        uppLine.Draw("same")
        midLine.Draw("same")
        lowLine.Draw("same")
        return uppLine, midLine, lowLine

    def getHistoPad(self):
        return self.canvas.GetListOfPrimitives().At(0) if self.canvas else None

    def getResidualPad(self):
        return self.canvas.GetListOfPrimitives().At(1) if self.canvas and self.residualHisto else None

    def addObject(self, obj, name):
        self.objects[name] = obj

    def getObject(self, name):
        return self.objects.get(name, self.objects.get(name, None))

    def addBox(self, binMin, binMax):
        if binMax <= binMin:
            return
        xMin = self._frame.GetXaxis().GetXmin()
        xMax = self._frame.GetXaxis().GetXmax()
        if binMin > xMin or binMax < xMax:
            self.boxes.append((binMin,binMax))

    def addLeftLabel(self, text):
        # Add MC label
        labelMC = ROOT.TLatex(0.17, 0.85, text)
        labelMC.SetTextSize(labelMC.GetTextSize()*1.8)
        labelMC.SetNDC(True)
        self.addObject(labelMC, text)

    def fixYLabel(self, histo_name):
        histo = self._frame.getHist(histo_name)
        self._frame.SetYTitle(histo.getYAxisLabel().replace('Events', 'Candidates'))


# EOF

    
