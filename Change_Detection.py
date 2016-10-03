#!/usr/bin/env python
import os
import sys
import math
import numpy as np
import pandas as pd
from numpy import maximum
from pandas import DataFrame
from pprint import pprint

"""
This script will do:
1) detect any land-use change between 2001_2006_2011:

1 stands for NA values
2 stands for road or no dev zone
200 stands for no change in developed area
300 stands for no change in non-urbanized areas
#### stands for change; the first 2 letters stand for 2001 LU; the latter 2 stands for 2006 LU
"""

# input data names
in_p = "./2001_2006_2011_NLCD/2001asc_road.csv"
in_f = "./2001_2006_2011_NLCD/2006asc_road.csv"

# deal with projection information
def first_6rows(fname):
    matrix = pd.read_csv(fname, skiprows=6, header=None, sep=r"\s+")  # 6 header lines
    with open(fname) as myfile:
        head = [next(myfile) for x in xrange(6)]
    return {'matrix': matrix, 'head': head}

# output data names
outmap = "./Output/2001_2006asc.csv"
class Compare_LU():
    def __init__(self, pname = in_p, fname = in_f, output = outmap):
        #initialize variables
        self.pmat = first_6rows(in_p)
        self.pmat = self.pmat["matrix"]
        self.fmat = first_6rows(in_f)
        self.fmat = self.fmat["matrix"]
        self.head = self.pmat["head"]
        nrow = self.pmat.shape[0]
        ncol = self.pmat.shape[1]
        self.cmat = np.zeros(shape=(nrow, ncol))
        self.cmat = pd.DataFrame(self.cmat)
        self.tmat = np.zeros(shape=(nrow, ncol))
        self.tmat = pd.DataFrame(self.tmat)

    def diff_lu(self, fmat, pmat, cmat, tmat):
        self.omat = cmat
        self.omat[pmat == 1] = 1
        self.omat[pmat == 2] = 2
        self.omat[pmat >= 90] = 2




def main():
    Compare_LU()

if __name__ == "__main__":
    main()