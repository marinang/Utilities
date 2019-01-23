#!/usr/bin/env python
# @file   Utilities.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2015-09-30

from .dependencies import softimport
import math
import sys


def destruct_objects(*args):
    """Destruct an object inheriting from TObject.

    See http://root.cern.ch/download/doc/ROOTUsersGuideHTML/ch19.html#d5e27551
    for more details

    :param object_: object to delete
    :type object_: TObject

    """
    ROOT = softimport("ROOT")
    
    for object_ in args:
        if issubclass(type(object_), ROOT.TObject):
            object_.IsA().Destructor(object_)


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
    
def dicttoarray( arraydict ):
    
    np     = softimport("numpy")
    uproot = softimport("uproot")
    awkward = softimport("awkward")
    
    """Convert a dictionnary into a structured array."""
    
    def jaggedtoarray( jaggedarray ):
        
        array = np.empty(len(jaggedarray), np.object)
        for index,a in enumerate(jaggedarray):
            array[index] = a
    
    names = sorted(list(arraydict.keys()))
    formats = []
    for n in names:
        _array = arraydict[n]
        try:
            _dtype = _array.dtype
            if len(_array.shape) > 1:
                _shape = _array.shape[1:]
                _dtype = np.dtype(( _dtype, _shape ))
            else:
                _dtype = np.dtype( _dtype )
        except AttributeError:
            _dtype = np.dtype(np.object)
            
        formats.append(_dtype)
        
    if sys.version_info[0] > 2:
        names = [n.decode() for n in names]
    
    dtypes = {'names': names, 'formats': formats}
    shape  = (len(list(arraydict.values())[0]),)

    array  = np.zeros(shape,dtypes)
        
    for k in arraydict.keys():
        
        if sys.version_info[0] > 2:
            k_new_array = k.decode()
        else:
            k_new_array = k

        if isinstance(arraydict[k], awkward.array.jagged.JaggedArray):
            _array = jaggedtoarray(arraydict[k])
        else:
            _array = arraydict[k]
                    
        try:
            array[k_new_array] = _array
        except ValueError:
            print(k)
            print(type(_array))
            print(_array)
                
    return array

