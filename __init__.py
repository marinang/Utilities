#!/usr/bin/python

# Definition of handy colours for printing
_default    = '\x1b[00m'
_green      = '\x1b[01;32m'
_red        = '\x1b[01;31m'
_blue       = '\x1b[01;34m'
_magenta    = '\x1b[1;35m'
_cyan       = '\x1b[01;36m'
_yellow     = '\x1b[01;33m'

def cdefault( text ):
    return "{0}{1}{2}".format( _default, text, _default)

def green( text ):
    return "{0}{1}{2}".format( _green, text, _default)
    
def red( text ):
    return "{0}{1}{2}".format( _red, text, _default)
    
def blue( text ):
    return "{0}{1}{2}".format( _blue, text, _default)
    
def magenta( text ):
    return "{0}{1}{2}".format( _magenta, text, _default)
    
def cyan( text ):
    return "{0}{1}{2}".format( _cyan, text, _default)
    
def yellow( text ):
    return "{0}{1}{2}".format( _yellow, text, _default)
    
from .dependencies import softimport
    
import sys
if sys.version_info[0] < 3:
    sys.path.append('/share/lphe/home/marinang/SimulationProduction/EvtTypes/MG5_aMC_v2_6_7')
    from madgraph.various import lhe_parser

