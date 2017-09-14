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
from rootpy import asrootpy
from uuid import uuid4
from rootpy.plotting import Hist
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from Utilities.Plots import LHCbStyle

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
    
class Frame(object):
    def __init__(self, Var, nBins, xMin=None, xMax=None):
        self.var = Var
        self.nbins = nBins
        if xMin is None:
            xMin = Var.getMin()
        if xMax is None:
            xMax = Var.getMax()
        self.xmin = xMin
        self.xmax = xMax
        self.Histograms = []
        self.Curves = []
        self.frame = Var.frame(nBins, xMin, xMax)
        self.chisq = None
        
    def PlotIn(self, Object, *args):
        
        Object.plotOn(self.frame, *args)
        
        if isinstance(Object, ROOT.RooAbsData):
            self.Histograms.append(Object)
        elif isinstance(Object, ROOT.RooAbsPdf):
            self.Curves.append(Object)
            
    def ChiSquare(self, FloatPars):
        self.chisq = self.frame.chiSquare(FloatPars)
        return self.chisq
    
#    
#    
#class ResidualPlot(object):
#    def __init__(self, title, frame):
#        self.title = title
#        self._id = str(uuid4())
#        self._frame = frame
#        self.residualHisto = None
#        self.pullHisto = None
#        self.alphaLabel = None
#        self.canvas = None
##        self.pullCanvas = None
##        self.objects = {}
##        self.boxes = []
##        self._boxes = []
#
#    def plot(self, bigLabels=False, removeTitle=True, residualBand=False, yLogScale=False, statusLabel=None, labelPosition="L"):
##        def _setMargins(pad):
##            pad.SetBottomMargin(0.1)
##            pad.SetLeftMargin(0.13)
##            pad.SetTopMargin(0.05)
##            pad.SetRightMargin(0.05)
#            
#            
#        LHCbStyle()
#        
#        fig, axes = plt.subplots()
#        axes.set_xlabel(Xlabel, ha='right', x=1)
#        axes.set_ylabel(Ylabel, ha='right', y=1)
#            
#        for obj in self._frame.data_hists:
#            rplt.errorbar(obj,axes=axes,emptybins=False)
#        for obj in self._frame.curves:
#            rplt.errorbar(obj,axes=axes,emptybins=False)
#            
#        axes.get_yaxis().set_tick_params(direction='in', left=True, right=True)
#        axes.get_xaxis().set_tick_params(direction='in', bottom=True, top=True)
#        axes.get_yaxis().set_tick_params(direction='in', which='minor', left=True, right=True)
#        axes.get_xaxis().set_tick_params(direction='in', which='minor', bottom=True, top=True)
#
#        plt.show()
#
##        self.canvas = ROOT.TCanvas("{0}_{1}".format(self.title, self._id), self.title, 800, 700)
##        padHisto, padResid = self.prepareCanvas(bool(self.residualHisto))
#
#
#
##        if removeTitle:
##            ROOT.gStyle.SetOptTitle(0)
##        if padHisto:
##            if removeTitle:
##                padHisto.SetTitle("")
##            padHisto.cd()
##            _setMargins(padHisto)
##        _setMargins(self.canvas)
##        fXAxis = self._frame.GetXaxis()
##        fYAxis = self._frame.GetYaxis()
##        if bigLabels:
##            fXAxis.SetTitleOffset(1.0)
##            fXAxis.SetTitleSize(0.045)
##            fXAxis.SetLabelSize(0.045)
##            fYAxis.SetTitleSize(0.045)
##            fYAxis.SetLabelSize(0.042)
##            fYAxis.SetTitleOffset(1.45)
##        else:
##            fXAxis.SetTitleOffset(1.0)
##            fXAxis.SetTitleSize(0.04)
##            fXAxis.SetLabelSize(0.04)
##            fYAxis.SetTitleSize(0.04)
##            fYAxis.SetLabelSize(0.04)
##            fYAxis.SetTitleOffset(1.55)
##        self._frame.Draw()
##        for boxMin,boxMax in self.boxes:
##            box = ROOT.TBox(max(fXAxis.GetXmin(),boxMin),
##                                 0,
##                                 min(fXAxis.GetXmax(),boxMax),
##                                 self._frame.GetMaximum())
##            box.SetFillStyle(1001)
##            box.SetFillColor(ROOT.kGray)
##            line = ROOT.TLine(max(fXAxis.GetXmin(),boxMin),self._frame.GetMaximum(),min(fXAxis.GetXmax(),boxMax),self._frame.GetMaximum())
##            self._boxes.append(box)
##            self._boxes.append(line)
##            box.Draw("same")
##            line.Draw("same")
##        self._frame.Draw("same")
##        if padHisto:
##            if yLogScale:
##                padHisto.SetLogy()
##            if statusLabel:
##                from rootpy.plotting.style.lhcb.labels import LHCb_label as lhcb_label
##                statusArgs = {'status': statusLabel}
##                if statusLabel not in ['final', 'preliminary', 'unofficial']:
##                    statusArgs['status'] = 'custom'
##                    if statusLabel == 'simulation':
##                        statusArgs['text'] = "#splitline{LHCb}{#scale[1.0]{Simulation}}"
##                    else:
##                        statusArgs['text'] = statusLabel
##                statusArgs['pad'] = padHisto
##                label, _ = lhcb_label(labelPosition, **statusArgs)
##                label.SetFillStyle(0)
##        for obj in self.objects.values():
##            obj.Draw("same")
##        if self.residualHisto:
##            fXAxis.CenterTitle()
##            fXAxis.SetTitleOffset(0.5)
##            fXAxis.SetLabelSize(0)
##            padResid.cd()
##            padHisto.SetLeftMargin(0.13)
##            padHisto.SetBottomMargin(0.07)
##            padResid.SetRightMargin(0.05)
##            padResid.SetLeftMargin(0.13)
##            # Axes
##            resXaxis = self.residualHisto.GetXaxis()
##            resYaxis = self.residualHisto.GetYaxis()
##            sr = 1.0/0.2
##            #srH = 1.0/0.8
##            resXaxis.SetTickLength ( sr * resXaxis.GetTickLength() )
##            resXaxis.SetLabelOffset( sr * resXaxis.GetLabelOffset() )
##            resXaxis.SetTitleSize    ( 0 )
##            resXaxis.SetLabelOffset(0.05)
##            resYaxis.SetNdivisions ( 504 )
##            if bigLabels:
##                fYAxis.SetTitleSize(0.05)
##                fXAxis.SetTitleSize(0.05)
##                fYAxis.SetLabelSize(0.05)
##                fYAxis.SetTitleOffset(1.35)
##                resXaxis.SetLabelSize    ( sr * 0.04 )
##                resYaxis.SetLabelSize    ( sr * 0.04 )
##            else:
##                fYAxis.SetTitleSize(0.045)
##                fXAxis.SetTitleSize(0.045)
##                fYAxis.SetLabelSize(0.045)
##                fYAxis.SetTitleOffset(1.45)
##                resXaxis.SetLabelSize    ( 0.037*sr )
##                resYaxis.SetLabelSize    ( 0.037*sr )
##            if not residualBand:
##                self.residualHisto.Draw("E1")
##            else:
##                self.residualHisto.SetFillColor(39)
##                self.residualHisto.SetMarkerSize(0.01)
##                self.residualHisto.Draw("E3")
##            self.lines = self.plotLines(self.residualHisto)
##            if self.alphaLabel:
##                self.canvas.cd()
##                self.alphaLabel.Draw()
##                self.canvas.Update()
##            padResid.Update()
#
#    def plotPull(self):
#        #gStyle.SetOptStat(0)
#        #gStyle.SetOptFit(0111)
#        self.pullCanvas = ROOT.TCanvas()
#        self.pullHisto.GetXaxis().SetTitle("residuals")
#        self.pullHisto.Fit('gaus')
#
#    def addResidual(self, histName, curveName, xMin=None, xMax=None, numParams=0):
#        histo = self._frame.getHist(histName)
#        curve = self._frame.getCurve(curveName)
#        xaxis = self._frame.GetXaxis()
#        #xaxis = histo.GetXaxis()
#        if not histo:
#            raise ValueError("Cannot find histo -> %s" % histName)
#        if not curve:
#            raise ValueError("Cannot find curve -> %s" % curveName)
#        # Residual range
#        if xMin is None:
#            xMin = xaxis.GetXmin()
#        if xMax is None:
#            xMax = xaxis.GetXmax()
#        # Create residual histogram
#        self.residualHisto, chisum = self.residualHist(histo, curve, xaxis, (xMin, xMax))
#        if numParams > 0:
#            dof = self._frame.getHist(histName).GetN() - numParams - 1
#            self.alphaLabel = self.calculateAlpha(chisum, dof)
#        return chisum
##
##    def prepareCanvas(self, addResidual):
##        padHisto = self.canvas.GetListOfPrimitives().At(0)
##        padResid = None
##        if addResidual:
##            self.canvas.Divide(1, 2, 0.01, 0.01)
##            padHisto = self.canvas.GetListOfPrimitives().At(0)
##            padResid = self.canvas.GetListOfPrimitives().At(1)
##            small = 0.07
##            r = 0.2
##            # Configure the pad for the histo
##            padHisto.SetPad(0.,r ,1.0, 1.0)
##            # Configure the pad for the residuals
##            padHisto.SetBottomMargin(small-0.01)
##            padResid.SetPad(0.0, 0.0, 1.0, r)
##            padResid.SetBottomMargin(0.25)
##            padResid.SetTopMargin(small)
##        return padHisto, padResid
#
#    def calculateAlpha(self, chisum, dof):
#        alpha = ROOT.TMath.Prob(chisum, dof)
#        alphaStr = "#alpha = %.4f" % alpha
#        label = ROOT.TLatex(0.83, 0.2, alphaStr)
#        label.SetTextSize(0.03)
#        print "I have a chi2 of %s and %s dof, so alpha is %s" % (chisum, dof, alpha)
#        return label
#
#    def residualHist(self, data, curve, xAxis, resRange, chisum=0.0):
#        def getResidual(y_data, y_pdf):
#            chi2 = 0.0
#            if y_pdf > 0:
#                chi2 += 2.0 * (y_pdf-y_data)
#                if y_data > 0:
#                    chi2 += 2.0 * y_data * log(y_data/y_pdf)
#            return sqrt(chi2) if datum > pdf else -sqrt(chi2)
#
#        nBins = data.GetN()
#        xMin = xAxis.GetXmin()
#        xMax = xAxis.GetXmax()
#        residuals = Hist(nBins, xMin, xMax, name="residuals_{0}".format(self._id), title="", type='F')
#        pulls     = Hist(11, -5.5, 5.5, name="pulls_{0}".format(self._id), title="", type='F')
#        
#        yBin, xBin, resValue  = ROOT.Double(0.0), ROOT.Double(0.0), ROOT.Double(0.0)
#        rangeMin, rangeMax = resRange
#        
#        if curve:
#            for bin in range(nBins):
#                data.GetPoint(bin, xBin, yBin)
#                if xBin < rangeMin or xBin > rangeMax:
#                    continue
#                pdf = curve.Eval(xBin)
#                resValue = getResidual(yBin, pdf)
#                chisum += resValue*resValue
#                residuals.SetBinContent(bin+1, resValue)
#                residuals.SetBinError(bin+1, 1.0)
#                pulls.Fill(resValue)
#        
#        residuals.SetMinimum( -5. )
#        residuals.SetMaximum( 5. )
#        residuals.SetStats( False )
#        residuals.SetMarkerStyle( 20 )
#        residuals.SetMarkerSize( .8 )
#        self.pullHisto = pulls
#        
#        return residuals, chisum
#
#    def plotLines(self, residHisto):
#        xMin = residHisto.GetXaxis().GetXmin()
#        xMax = residHisto.GetXaxis().GetXmax()
#        # Create lines
#        uppLine = ROOT.TLine(xMin, 2.0, xMax, 2.0)
#        midLine = ROOT.TLine(xMin, 0.0, xMax, 0.0)
#        lowLine = ROOT.TLine(xMin, -2.0, xMax, -2.0)
#        uppLine.SetLineColor( ROOT.kRed )
#        lowLine.SetLineColor( ROOT.kRed )
#        uppLine.Draw("same")
#        midLine.Draw("same")
#        lowLine.Draw("same")
#        return uppLine, midLine, lowLine
#
#    def getHistoPad(self):
#        return self.canvas.GetListOfPrimitives().At(0) if self.canvas else None
#
#    def getResidualPad(self):
#        return self.canvas.GetListOfPrimitives().At(1) if self.canvas and self.residualHisto else None
#
#    def addObject(self, obj, name):
#        self.objects[name] = obj
#
#    def getObject(self, name):
#        return self.objects.get(name, self.objects.get(name, None))
#
#    def addBox(self, binMin, binMax):
#        if binMax <= binMin:
#            return
#        xMin = self._frame.GetXaxis().GetXmin()
#        xMax = self._frame.GetXaxis().GetXmax()
#        if binMin > xMin or binMax < xMax:
#            self.boxes.append((binMin,binMax))
#
#    def addLeftLabel(self, text):
#        # Add MC label
#        labelMC = ROOT.TLatex(0.17, 0.85, text)
#        labelMC.SetTextSize(labelMC.GetTextSize()*1.8)
#        labelMC.SetNDC(True)
#        self.addObject(labelMC, text)
#
#    def fixYLabel(self, histo_name):
#        histo = self._frame.getHist(histo_name)
#        self._frame.SetYTitle(histo.getYAxisLabel().replace('Events', 'Candidates'))
#    
#
#    
#    
#
#
