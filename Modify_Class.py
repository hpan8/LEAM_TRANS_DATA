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
1) change NLCD class to LEAM class
2) make road unique layers
"""
lu_name = "./2001_2006_2011_NLCD/2001asc.txt"
o_lu_name = "./2001_2006_2011_NLCD/lu_raster.txt"
rd_name = "./2001_2006_2011_NLCD/road.txt"
output_name_1 = "./2001_2006_2011_NLCD/2001asc_class.csv"
output_name_2 = "./2001_2006_2011_NLCD/2001asc_road.csv"

road_flag = 0

#header rows
def first_6rows(fname):
    matrix = pd.read_csv(fname, skiprows=6, header=None, sep=r"\s+") # 6 header lines
    with open(fname) as myfile:
        head = [next(myfile) for x in xrange(6)]
    return{'matrix':matrix, 'head':head}

# change LU classes
# change na value in lu_raster to 1 in the nlcd lu map

def class_change(lu, olu):
    from_lu = np.array([11, 21, 22, 23, 24, 95])
    to_lu = np.array([11, 85, 21, 22, 23, 92])

    for i in range (len(from_lu)):
        lu[lu == from_lu[i]] = to_lu[i]
        print i

    #fill nodata by 1
    siz = olu.shape
    nrow = siz[0]
    ncol = siz[1]
    matrix = lu
    matrix = matrix.loc[0:(nrow-1), 0:(ncol-1)] #fit nlcd into leam frame
    matrix[olu == 0] = 1

    return matrix


# change road and neighborhooding cells in road raster to 2 in the nlcd lu_map
def mask_lu(lu, road):
    #ind = np.argwhere(lu == 0)
    #print ind.transpose()
    siz = road.shape
    nrow = siz[0]
    ncol = siz[1]



    matrix = lu
    #fill road and its adjacency by 2
    matrix[road > 1] = 2
    road_0 = np.zeros(shape=(nrow, ncol))
    road_1 = pd.DataFrame(road_0)
    road_1.loc[0:(nrow-2), :] = road.loc[1:(nrow-1), :]
    matrix[road_1 > 1] = 2

    road_1 = pd.DataFrame(road_0)
    road_1.loc[1:(nrow - 1), :] = road.loc[0:(nrow - 2), :]
    matrix[road_1 > 1] = 2

    road_1 = pd.DataFrame(road_0)
    road_1.loc[:, 0:(ncol - 2)] = road.loc[:, 1:(ncol - 1)]
    matrix[road_1 > 1] = 2

    road_1 = pd.DataFrame(road_0)
    road_1.loc[:, 1:(ncol - 1)] = road.loc[:, 0:(ncol - 2)]
    matrix[road_1 > 1] = 2

    #matrix.loc[np.array(ind)] = 1
    #print matrix.loc[ind]
    print matrix.shape

    return matrix

def outmap(outname, head, tail):
    with open(outname, 'w') as w:
        w.writelines(head)
    tail.to_csv(path_or_buf=outname, sep=' ', index=False, header=False, mode='a')  # append



def main():
    o_lu = first_6rows(o_lu_name)
    new_lu = first_6rows(lu_name)
    ro_lu = first_6rows(rd_name)
    o_lu_m = o_lu['matrix']
    o_lu_h = o_lu['head']
    new_lu = new_lu['matrix']
    ro_lu = ro_lu['matrix']

    c_lu = class_change(new_lu, o_lu_m)
    outmap(output_name_1, o_lu_h, c_lu)

    m_lu = mask_lu(c_lu, ro_lu)
    outmap(output_name_2, o_lu_h, m_lu)

if __name__ == "__main__":
    main()