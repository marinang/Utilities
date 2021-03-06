#!/usr/bin/env python
# @file   Plots.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2016-11-09

from Utilities.dependencies import softimport

ROOT = softimport("ROOT")
import glob
import os
import numpy as np
probfit = softimport("probfit")
iminuit = softimport("iminuit")
from scipy.stats import chisquare

import logging 
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 

Hist = softimport(".Hist")
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
rootpy = softimport("rootpy.plotting.root2matplotlib")
from future.utils import iteritems

zfit = softimport("zfit")
tf = softimport("tensorflow")
physt = softimport("physt")
from uncertainties import unumpy, ufloat

import mplhep

def addticks(ax):
    ax.get_yaxis().set_tick_params(direction='in', left=True, right=True)
    ax.get_xaxis().set_tick_params(direction='in', bottom=True, top=True)
    ax.get_yaxis().set_tick_params(direction='in', which='minor', left=True, right=True)
    ax.get_xaxis().set_tick_params(direction='in', which='minor', bottom=True, top=True)
    ax.minorticks_on()

def LHCbStyle():
    
    STYLE = {}

    STYLE['figure.figsize'] = 8.75, 5.92
    STYLE['figure.dpi'] = 100

    STYLE['font.family'] = 'sans-serif'
    STYLE['font.serif'] =  'Times New Roman'
    STYLE['font.size'] =   14
    STYLE['font.style'] = 'normal'

    STYLE['legend.frameon'] = False
    STYLE['legend.handletextpad'] = 0.3
    STYLE['legend.numpoints'] =     1
    STYLE['legend.labelspacing'] =  0.3
    STYLE['legend.fontsize'] =      12

    STYLE['lines.linewidth'] =       1.4
    STYLE['lines.markeredgewidth'] = 1.4
    STYLE['lines.markersize'] =      8
    
    STYLE['errorbar.capsize'] =      1.3

    STYLE['savefig.bbox'] = 'tight'
    STYLE['savefig.pad_inches'] = 0.1
    STYLE['savefig.dpi'] = 250
    
    STYLE['axes.labelsize'] = 16
    STYLE['axes.linewidth'] = 1.4
    STYLE['axes.labelweight'] = 500

    STYLE['xtick.major.size'] =  6
    STYLE['xtick.minor.size'] =  3
    STYLE['xtick.major.width'] = 1.6
    STYLE['xtick.minor.width'] = 1.6
    STYLE['xtick.major.pad'] =   10
    STYLE['xtick.minor.pad'] =   10
    STYLE['xtick.labelsize'] =   17

    STYLE['ytick.major.size'] =  6
    STYLE['ytick.minor.size'] =  3
    STYLE['ytick.major.width'] = 1.4
    STYLE['ytick.minor.width'] = 1.4
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
        if isinstance(h, Hist.EffHist):
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
            
        obj.SetFillStyle(0)
        
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
        
def DrawMPL(Dicts, axes, Logy=False, Err=False, Legend=True, Xlabel=None, Ylabel=None, xlimit = (-999999,999999), ylimit = (-999999,999999)):
    
    rplt = rootpy.plotting.root2matplotlib

    Objs = Dicts
    
    minY, maxY = ylimit[0], ylimit[1]
    minX, maxX = xlimit[0], xlimit[1]

    if minY == -999999:
        minY = min([h["hist"].GetMinimum() for h in Objs])
    if maxY == 999999:
        maxY = 1.48*max([h["hist"].GetMaximum() for h in Objs])
    if Logy:
        if minY <= 0:
            minY = 0.0005
        maxY = 2.2*maxY
        axes.set_yscale("log")
        
    if not Xlabel:
        Xlabel = Objs[0]["hist"].GetXaxis().GetTitle()
 
    patch, name = [],[]
    for objs in Objs:
        
        obj = objs["hist"]
        
        
        if objs.get("err",False) or isinstance(obj, ROOT.TGraphAsymmErrors):
            axes.set_xlabel(Xlabel, ha='right', x=1)
            axes.set_ylabel(Ylabel, ha='right', y=1)
            if not Ylabel:
                Ylabel = Objs[0].GetYaxis().GetTitle()  
            axes.set_ylabel(Ylabel, ha='right', y=1)
            rplt.errorbar(obj,axes=axes,emptybins=False, )
            h, l = axes.get_legend_handles_labels()
            patch.append(h[-1])
            name.append(obj.GetTitle())
            continue
        elif isinstance(obj, ROOT.TH1):
            alpha = getattr(obj, 'alpha', None)
            axes.set_xlabel(Xlabel, ha='right', x=1)
            if not Ylabel:
                Ylabel = "Events"
            axes.set_ylabel(Ylabel, ha='right', y=1)
            rplt.hist(obj,Objsed=False,axes=axes,logy=Logy,linewidth=1.5)
            h, l = axes.get_legend_handles_labels()
            if any(obj.GetFillStyle() == style for style in [0, 1001]):
                patch.append(mpatches.Patch(edgecolor=obj.GetLineColor('mpl'), facecolor=obj.GetFillColor('mpl'), linewidth=obj.GetLineWidth(), alpha=alpha, linestyle = obj.GetLineStyle('mpl')))
            else:
                patch.append(mpatches.Patch(edgecolor=obj.GetLineColor('mpl'), facecolor=obj.GetFillColor('mpl'), linewidth=obj.GetLineWidth(), alpha=alpha, linestyle = obj.GetLineStyle('mpl'), 
                                            hatch = obj.GetFillStyle('mpl')))
            name.append(obj.GetTitle())
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
        
        
def plotFitResult( cost_function, fitresult, y_label, x_label, description={}, nbins=100, plot_residuals=True, logy=False, 
                   chi2_pos=(0.7, 0.5), show_params=False, params_loc=(0.05, 0.95), legend_pos="best", 
                   xlimit=(-999999,999999), ylimit=(-999999,999999), **kwargs ):
                    
    values = fitresult.values
    errors = fitresult.errors
    
    if isinstance(cost_function, probfit.costfunc.BinnedLH):
        draw = lambda parts: cost_function.draw(minuit=fitresult, parts=parts, nfbins=500, no_plot=True, args=values, errors=errors) 
    else:
        draw = lambda parts: cost_function.draw(minuit=fitresult, parts=parts, bins=nbins, nfbins=500, bound=xlimit, no_plot=True, args=values, errors=errors)
                    
    #plotting
    try:
        ((data_edges, datay), (errorp, errorm), (total_pdf_x, total_pdf_y), parts) = draw(True)
        #cost_function.draw(parts=True, bins=nbins, nfbins=500, bound=xlimit, no_plot=True, args=values, errors=errors);
    except TypeError:
        ((data_edges, datay), (errorp, errorm), (total_pdf_x, total_pdf_y), parts) = draw(False)
        #cost_function.draw(parts=False, bins=nbins, nfbins=500, bound=xlimit, no_plot=True, args=values, errors=errors);
    if logy:
        ymin = ylimit[0] if ylimit[0] != -999999 else 0.01
        ymax = ylimit[1] if ylimit[1] !=  999999 else max(datay)*10
    else:
        ymin = ylimit[0] if ylimit[0] != -999999 else min(datay)
        ymax = ylimit[1] if ylimit[1] !=  999999 else max(datay)*1.2
        
    xmin = xlimit[0] if xlimit[0] != -999999 else min(data_edges)
    xmax = xlimit[1] if xlimit[1] !=  999999 else max(data_edges)
                
    LHCbStyle()

    if plot_residuals:
        if kwargs.get("ax1", None) is not None:
            ax1 = kwargs["ax1"]
            f = None
        else:
            f = plt.figure()
            gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1], hspace = 0.125)
            ax1 = plt.subplot(gs[0])
    else:
        f, ax1 = plt.subplots()
        
    
    ax1.axes.set_ylabel(y_label, ha = "right", y=1)
    ax1.axes.set_xlim((xmin,xmax))
    ax1.axes.set_ylim((ymin,ymax))
    if not plot_residuals:
        ax1.axes.set_xlabel(x_label, ha='right', x=1)
    else:
        ax1.set_xticklabels([])

    # plot data
    xerr = np.diff(data_edges)/2
    
    if not "data" in description.keys():
        description["data"] = {"color": "black", "label": "Data"}
    datacolor = description["data"].get("color","black")
    datalabel = description["data"].get("label","Data")
    _ = ax1.errorbar(probfit.mid(data_edges), datay, yerr = errorp, xerr = xerr, fmt='.', capsize=0, color=datacolor, label=datalabel, markersize = 6)
    # plot model
    if not "fullmodel" in description.keys():
        description["fullmodel"] = {"color": "blue", "label": "Full model"}
    fmodelcolor = description["fullmodel"].get("color","blue")
    fmodellabel = description["fullmodel"].get("label","Full model")
    _ = ax1.plot(total_pdf_x, total_pdf_y, color=fmodelcolor, lw=2, label=fmodellabel)
    
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
        
    for i,part in enumerate(parts):
        if not f"model_{i}" in description.keys():
            description[f"model_{i}"] = {"color": colors[i], "label": f"model_{i}"}
        _color = description[f"model_{i}"].get("color",colors[i])
        _label = description[f"model_{i}"].get("label",f"model_{i}")
        x, y = part
        _ = ax1.plot(x, y, ls='--', color=_color, label=_label)
    
    ax1.get_yaxis().set_tick_params(direction='in', left=True, right=True)
    ax1.get_xaxis().set_tick_params(direction='in', bottom=True, top=True)
    ax1.get_yaxis().set_tick_params(direction='in', which='minor', left=True, right=True)
    ax1.get_xaxis().set_tick_params(direction='in', which='minor', bottom=True, top=True)
    ax1.minorticks_on()
    ax1.legend(loc=legend_pos, fontsize=kwargs.get("fontsize", 12))
    
    if logy:
        ax1.set_yscale("log", nonposy='clip')
        
    if show_params:
        to_print = []
        
        for k in values.keys():
            to_print.append(rf"{k} = {values[k]:.3f} $\pm$ {errors[k]:.3f}")
            
        to_print = '\n'.join(to_print)
        
        props = dict(boxstyle='square', facecolor='None')
        
        ax1.text(params_loc[0], params_loc[1], to_print, transform=ax1.transAxes, verticalalignment='top', bbox = props)
            
    
    if plot_residuals:

        if kwargs.get("ax2", None) is not None:
            ax2 = kwargs["ax2"]
        else:
            ax2 = plt.subplot(gs[1])
        
        ax2.axes.set_ylim((-5,5))
        ax2.axes.set_xlim((xmin, xmax))
        ax2.axes.set_ylabel("Pulls")
        ax2.axes.set_xlabel(x_label, ha ='right', x=1)
        ax2.get_yaxis().set_tick_params(direction='in', left=True, right=True)
        ax2.get_xaxis().set_tick_params(direction='in', bottom=True, top=True)
        ax2.get_yaxis().set_tick_params(direction='in', which='minor', left=True, right=True)
        ax2.get_xaxis().set_tick_params(direction='in', which='minor', bottom=True, top=True)
        ax2.plot([xmin, xmax], [2, 2], color = "indianred", lw=1.5, linestyle = '-.')
        ax2.plot([xmin, xmax], [0, 0], color = "grey", lw=1.5, linestyle = '-.')
        ax2.plot([xmin, xmax], [-2, -2], color = "indianred", lw=1.5, linestyle = '-.')
        ax2.minorticks_on()
        
        if isinstance(cost_function, probfit.costfunc.BinnedLH):
            cost_function.draw_residual(minuit=fitresult, show_errbars=True, errbar_algo='sumw2', norm=True, ax=ax2, mec='Black', mfc='Black', 
                                        ecolor='Black', markersize=6, zero_line=False, bound=xlimit)
        else:
            cost_function.draw_residual(show_errbars=True, errbar_algo='sumw2', norm=True, ax=ax2, mec='Black', mfc='Black', 
                                        ecolor='Black', markersize=6, bins=nbins, zero_line=False, bound=xlimit, args=values, errors=errors)
                    
    f.align_ylabels()
    
def plotZfitResult(pdf, data, x_label, y_label=None, description={}, nbins=100, plot_residuals=True, logy=False, 
                   chi2_pos=(0.7, 0.5), legend_pos="best", xlim=None, ylim=None, chi2=True,
                   units="GeV/c$^{2}$", **kwargs ):
                
    bounds = xlim if xlim else pdf.space.limit1d 
    
    datay, bin_edges = np.histogram(data, bins=nbins, range=bounds)
    errory = np.sqrt(datay)
    bin_centers = (bin_edges[:-1] + bin_edges[1:])/2
#    data_hist = physt.h1(data, nbins, range=bounds)
#    datay = data_hist.frequencies
#    errory = data_hist.errors
#    bin_centers = data_hist.bin_centers
    binwidth = (bounds[1] - bounds[0]) / nbins
    
    IB = pdf.integrate(bounds)

    if pdf.is_extended:
        N = zfit.run(IB)
        IB = IB/pdf.get_yield() 
    else:
        N = np.sum(datay)
            
    scale = N * binwidth
    
    if not ylim:
        if logy:
            ylim = (min(datay), max(datay)*10.)
        else:
            ylim = (0.01, max(datay)*1.2)
       
    yscale = "log" if logy else ""             
        
    x = np.linspace(*bounds, num=1000)
    
    LHCbStyle()

    if plot_residuals:
        if kwargs.get("ax1", None) is not None:
            ax1 = kwargs["ax1"]
            f = None
        else:
            f = plt.figure()
            gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1], hspace = 0.125)
            ax1 = plt.subplot(gs[0])
    else:
        f, ax1 = plt.subplots()
        
    # plot data
    if not "data" in description.keys():
        description["data"] = {"color": "black", "label": "Data"}
    datacolor = description["data"].get("color","black")
    datalabel = description["data"].get("label","Data")
    #data_hist.plot(ax=ax1, kind="scatter", color=datacolor, errors=True, yscale=yscale,
    #               label=datalabel, s=6, xlabel=None)
    mplhep.histplot(datay, bins=bin_edges, label=datalabel, ax=ax1, histtype="errorbar", 
                    color="black", markersize=4, yerr=True, elinewidth=1.5)
    
    # plot model
    if not "fullmodel" in description.keys():
        description["fullmodel"] = {"color": "blue", "label": "Full model"}
    fmodelcolor = description["fullmodel"].get("color","blue")
    fmodellabel = description["fullmodel"].get("label","Full model")
        
    try:
        toplot = []
        toresiduals = []
        for i, (m, frac) in enumerate(zip(pdf.get_models(), pdf.fracs)):
            if m.is_extended:
                _frac = (frac / IB) * (m.integrate(bounds) / m.get_yield())
            else:
                _frac = (frac / IB) * m.integrate(bounds)
            y = zfit.run(m.pdf(x, norm_range=bounds) * _frac * scale)
            yb = zfit.run(m.pdf(bin_centers, norm_range=bounds) * _frac * scale)
            toplot.append(y)
            toresiduals.append(yb)
            
        _ = ax1.plot(x, np.sum(toplot, axis=0), color=fmodelcolor, lw=2, label=fmodellabel)
        
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
            
        for i, (m, y) in enumerate(zip(pdf.get_models(), toplot)):
            if not f"model_{i}" in description.keys():
                description[f"model_{i}"] = {"color": colors[i], "label": f"model_{i}"}
            _color = description[f"model_{i}"].get("color",colors[i])
            _label = description[f"model_{i}"].get("label",f"model_{i}")
            _ = ax1.plot(x, y, ls="--", color=_color, label=_label)

        pdfy = np.sum(toresiduals, axis=0)
        
    except AttributeError:        
        pdfy = zfit.run(pdf.pdf(bin_centers, norm_range=bounds)) * scale
        _ = ax1.plot(x, zfit.run(pdf.pdf(x, norm_range=bounds)) * scale, color=fmodelcolor, lw=2, label=fmodellabel)


    if y_label is None:
        y_label=f"Candidates/({binwidth:.2f} {units})"
        
    ax1.axes.set_ylabel(y_label, ha = "right", y=1)
    ax1.axes.set_xlim(bounds)
    ax1.axes.set_ylim(ylim)
    if not plot_residuals:
        ax1.axes.set_xlabel(x_label, ha='right', x=1)
    else:
        ax1.set_xticklabels([])
        
    addticks(ax1)
    ax1.minorticks_on()
    ax1.legend(loc=legend_pos, fontsize=kwargs.get("fontsize", 12))
    
    if chi2:
        nfree_params = kwargs.get("nfree_params", len(pdf.get_dependents()))
        chi2 = chisquare(datay, pdfy, nfree_params)[0]
        ndof = nbins - 1 + nfree_params
        chi2ndof = chi2  / ndof 
        ax1.text(chi2_pos[0], chi2_pos[1], r'$\chi^{2}$/ndof = ' + f"{chi2ndof:.2f}", transform = ax1.transAxes )
    
        
    if plot_residuals:
        
        if kwargs.get("ax2", None) is not None:
            ax2 = kwargs["ax2"]
        else:
            ax2 = plt.subplot(gs[1])
            
        ax2.axes.set_ylim((-5,5))
        ax2.axes.set_xlim(bounds)
        ax2.axes.set_ylabel("Pulls")
        ax2.axes.set_xlabel(x_label, ha ='right', x=1)
        addticks(ax2)
        ax2.plot(list(bounds), [2, 2], color = "indianred", lw=1.5, linestyle = '-.')
        ax2.plot(list(bounds), [0, 0], color = "grey", lw=1.5, linestyle = '-.')
        ax2.plot(list(bounds), [-2, -2], color = "indianred", lw=1.5, linestyle = '-.')
        ax2.minorticks_on()
        datay = unumpy.uarray(datay, errory)
        errory = np.where(datay == 0., np.ones(errory.shape), errory)
        pully = (datay - pdfy) / errory
        ax2.errorbar(bin_centers, unumpy.nominal_values(pully), yerr=unumpy.std_devs(pully), fmt='.', ecolor='Black',
                     markersize=4, color='Black', elinewidth=1.5)
    else:
        ax2 = None
    
    try:
        f.align_ylabels()
    except (UnboundLocalError, AttributeError):
        pass
        
    if logy:
        ax1.set_yscale("log", nonposy='clip')
        
    return f, ax1, ax2
    
    
def PullImpact(fitresult, constraints, paramdict=None):
    
    uf = lambda p: ufloat(fitresult.params[p]["value"], fitresult.params[p]["minuit_hesse"]["error"])
    
    pdict = {}
    params = []
    
    for c in constraints:
        _params = list(c.params.values())
        pre_values = zfit.run(c._mu)
        pre_errors = np.diag(zfit.run(c._covariance))**0.5
        for i, p in enumerate(_params):
            pdict[p.name] = dict(pre_value=pre_values[i], value=uf(p),
                                 pre_error=pre_errors[i])
            params.append(p.name)
                                
    if paramdict is not None:
        params = list(paramdict.keys())
        x = list(paramdict.values())
    else:
        x = params
        
    
    values = np.array([pdict[p]["value"] for p in params])
    pre_values = np.array([pdict[p]["pre_value"] for p in params])
    pre_errors = np.array([pdict[p]["pre_error"] for p in params])
    pulls = (values - pre_values)/pre_errors
    
    print(x)
    print(pulls)
    
    f, ax = plt.subplots()
    ax.errorbar(x, unumpy.nominal_values(pulls), yerr=unumpy.std_devs(pulls), fmt='o')
    return f, ax
                                
    
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
    
    
def plotlimit(poivalues, pvalues, alpha=0.05, CLs=True, ax=None):
    """
    plot pvalue scan for different values of a parameter of interest (observed, expected and +/- sigma bands)

    Args:
        poivalues (List, `np.array`): values of a parameter of interest used to compute p-values
        pvalues (Dict): CLsb, CLs, expected (+/- sigma bands) p-values
        alpha (float, default=0.05): significance level
        CLs (bool, optional): if `True` uses pvalues as $$p_{cls}=p_{null}/p_{alt}=p_{clsb}/p_{clb}$$
            else as $$p_{clsb} = p_{null}$
        ax (matplotlib axis, optionnal)


    """
    if ax is None:
        _, ax = plt.subplots()

    if CLs:
        cls_clr = "r"
        clsb_clr = "b"
    else:
        cls_clr = "b"
        clsb_clr = "r"

    ax.plot(poivalues, pvalues["cls"], label="Observed CL$_{s}$", marker=".", color='k',
            markerfacecolor=cls_clr, markeredgecolor=cls_clr, linewidth=2.0, ms=11)

    ax.plot(poivalues, pvalues["clsb"], label="Observed CL$_{s+b}$", marker=".", color='k',
            markerfacecolor=clsb_clr, markeredgecolor=clsb_clr, linewidth=2.0, ms=11, linestyle=":")

    ax.plot(poivalues, pvalues["clb"], label="Observed CL$_{b}$", marker=".", color='k', markerfacecolor="k",
            markeredgecolor="k", linewidth=2.0, ms=11)

    ax.plot(poivalues, pvalues["expected"], label="Expected CL$_{s}-$Median", color='k', linestyle="--",
            linewidth=1.5, ms=10)

    ax.plot([poivalues[0], poivalues[-1]], [alpha, alpha], color='r', linestyle='-', linewidth=1.5)

    ax.fill_between(poivalues, pvalues["expected"], pvalues["expected_p1"], facecolor="lime",
                    label="Expected CL$_{s} \\pm 1 \\sigma$")

    ax.fill_between(poivalues, pvalues["expected"], pvalues["expected_m1"], facecolor="lime")

    ax.fill_between(poivalues, pvalues["expected_p1"], pvalues["expected_p2"], facecolor="yellow",
                    label="Expected CL$_{s} \\pm 2 \\sigma$")

    ax.fill_between(poivalues, pvalues["expected_m1"], pvalues["expected_m2"], facecolor="yellow")

    ax.set_ylim(-0.01, 1.1)
    ax.set_ylabel("p-value", fontsize=14, ha = "right", y=1)
    ax.set_xlabel("parameter of interest", fontsize=14, ha = "right", x=1)
    ax.legend(loc="best", fontsize=14)

    return ax
    

