from __future__ import division
import pyplatypus.dataset.reflectdataset as reflectdataset
import numpy as np
import pyplatypus.analysis.reflect as reflect
import matplotlib.artist as artist
import os.path, os
import string
    
class Model(object):
    def __init__(self, parameters, **kwds):
        __members = {'file':None, 'parameters': None, 'fitted_parameters':None, 'uncertainties':None, 'covariancematrix':None,
        'limits':None, 'usedq':True, 'useerrors': True, 'costfunction':reflect.costfunction_logR_noweight}
        
        if 'file' in kwds:
            self.load(kwds['file'])        
        else:
            for key in __members:
                if key in kwds:
                   setattr(self, key, kwds[key])
                else:
                    setattr(self, key, __members[key])
            
            self.parameters = parameters
            if self.fitted_parameters is None:
                self.fitted_parameters = np.array([], dtype = 'int')
            
            if self.uncertainties is None:
                self.uncertainties = np.array([np.nan] * parameters.size, dtype = 'float64')
                
            if self.covariancematrix is None:
                self.covariancematrix = np.zeros((parameters.size, parameters.size))
            
            if self.limits is None:
                self.defaultlimits()
                       
        self.useerrors = True
        self.usedq = True
        self.costfunction = reflect.costfunction_logR_noweight
       
        
    def save(self, f):
        f.write(f.name + '\n')
        f.write(str(self.parameters.size) + '\n')
        f.write('parameter\thold\tlowlin\thilim\tuncertainty\n')
        holdvector = np.ones_like(self.parameters, dtype = 'int')
        holdvector[self.fitted_parameters] = 0
        
        if self.limits is None or self.limits.ndim != 2 or np.size(self.limits, 1) != np.size(self.parameters):
            self.defaultlimits()
                
        #go through and write parameters to file        
        np.savetxt(f, np.column_stack((self.parameters, holdvector, self.limits.T, self.uncertainties)))

        
        f.write('covariance matrix\n')
        np.savetxt(f, self.covariancematrix)
        
    
    def load(self, f):
        h1 = f.readline()
        h2 = f.readline()
        h3 = f.readline()
        numparams = int(h2)
            
        array = np.fromfile(f, dtype = 'float64', sep = '\t', count = numparams * 5)
        array =  array.reshape(numparams, 5)
                 
        self.parameters, a2, lowlim, hilim , self.uncertainties = np.hsplit(array, 5)
        
        self.parameters = self.parameters.flatten()
        self.uncertainties = self.uncertainties.flatten()
        self.limits = np.column_stack((lowlim, hilim)).T
        
        a2 = a2.flatten()
        self.fitted_parameters = np.where(a2==0)[0]
        
        #now read covariance matrix
        h4 = f.readline()
        self.covariancematrix = np.fromfile(f, dtype = 'float64', sep = ' \t', count = numparams * numparams)
        self.covariancematrix = self.covariancematrix.reshape((numparams, numparams))
        
    def defaultlimits(self):
        self.limits = np.zeros((2, np.size(self.parameters)))
            
        for idx, val in enumerate(self.parameters):
            if val < 0:
                self.limits[0, idx] = 2 * val
            else:
                self.limits[1, idx] = 2 * val 
                    