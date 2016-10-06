"""
This script will do:
1. (optional)-overlap the miniumum of 100 travelcost maps to have a complete travelcost map. ./Data/travelcost-pop.txt
2. read the interpolated attrmap and the travelcost map into an array seperately, and create a dictionary to map them. Sort.
3. use the two arrays and matplotlib libarary and ggplot2 to generate:
   (1) travelcost vs. attractiveness graph
   (2) travelcost vs. low&high residential frequency (type 21, 22)
   (3) travelcost vs. low&high commercial frequency (type 23, 24)
   (4) attractiveness vs. low&high residentail frequency 
   (5) attractivenss vs. low&high commercial frequency

"""

#from ggplot import * #ggplot is best to be used with pandas DataFrames
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from optparse import OptionParser
from Utils import createdirectorynotexist, extractheader, outfilename
import time 

#if (len(sys.argv) < 3):
#    print "Error: You need to specify at least two arguments: #attrmap baskets and #costmap baskets."
#    exit(1)

#option parsers -c centertype, -l landuse type, -t cost/attractiveness -s change or static map
def opt_parser():
    parse = OptionParser()
    parse.add_option('-c', '--centers', metavar='CENTERTYPE', default=False,
                    help='the center type can either be "emp" or "pop" ')

    isemp = 0
    opts, args = parse.parse_args()
    opts_c = opts.centers
    if not opts.centers:
        opts_c = "pop"
        isemp = 0
        print "No centertype given. Default to be pop"
    elif opts.centers == 'emp':
        isemp = 1
    elif opts.centers == 'pop':
        isemp = 0
    else:
        parse.error("-c option needs to be either 'emp' or 'pop'")

    attrbasketnum = int(sys.argv[1]) #number of tick bins

    return{'bnum':attrbasketnum,'ctype': isemp, 'c_opts':opts_c}


#Data loader
def data_loader(isemp):
    isemp = opt_parser()['ctype']

    #load different center map data based on different options
    if isemp == 1:
        #centerlist = "./Data/empcenterlist.txt" # load center list
        attrmap = "./Data/emp_att.txt" # load attraction/travel-cost map
        #freqmap = "./Data/analysis/emp/attrfreq-commericial" #frequency map creation

    else:
        #centerlist = "./Data/popcenterlist.txt"
        attrmap = "./Data/pop_att.txt"
        #freqmap = "./Data/analysis/pop/attrfreq-commericial.png"

    # load and flatten array for land-use class  for each cell
    landroadclassmap_file = "./Data/2006asc.txt"  # load land-use map
    landroadclassmap = pd.read_csv(landroadclassmap_file, sep=r"\s+", skiprows=6, header=None)
    landroad_arr = landroadclassmap.values.flatten()

    # load and flatten array for attribute values for each cell
    attrmap = pd.read_csv(attrmap, sep=r"\s+", skiprows=6, header=None)
    attrmap = attrmap.round().astype(np.int)
    attr_arr_org = attrmap.values.flatten()


    # create mask for all cells and residential cells
    all_cells = np.array([21, 22, 31, 41, 42, 43, 52, 71, 81, 82, 85])
    res_cells = np.array([21, 22])

    #find the location of those cells in the mask
    mask_all = np.in1d(landroad_arr, all_cells)
    mask_res = np.in1d(landroad_arr, res_cells)

    #create shortened arrays
    attr_arr = attr_arr_org[mask_all]
    attr_res_arr = attr_arr_org[mask_res]

    #sort the arrays (ascending)
    attr_arr = np.sort(attr_arr)
    attr_res_arr = np.sort(attr_res_arr)

    #ASCII MAP HEADER
    header = "./Input/arcGISheader.txt"

    return{'res_arr': attr_res_arr, 'all_array': attr_arr,'header': header}

#naming graphs
def graph_names(ltype, ctype, bnum, ischg):
    outmapename = "./DataOut/analysis/" + ltype + ctype + str(bnum) + ischg + ".png"
    outdataname = "./DataOut/analysis/" + ltype + ctype + str(bnum) + ischg + ".csv"
    createdirectorynotexist(outmapename)

    return{'outmapename': outmapename, 'outdataname': outdataname}

# change y label to percent
def to_percent(y, position):
    """[reference:http://matplotlib.org/examples/pylab_examples/histogram_percent_demo.html]
    """
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'

# plot graph
def plotgraph(x, y, xsize, outfile, name, mapname):
    plt.close("all")
    fig, ax = plt.subplots()
    # set the grids of the x axis
    # When data are highly skewed, the ticks value needs to be
    # set differently for different number of baskets.
    major_ticks = xrange(0, x[-1]+x[-1]-x[-2], int((x[-1]+x[-1]-x[-2])/10))
    minor_ticks = xrange(0, x[-1]+x[-1]-x[-2], max(1, int((x[-1]+x[-1]-x[-2])/100)))

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # set the range of the y axis
    plt.ylim(0, 1)
    # set the title and labels
    plt.title(name +' ' + mapname + ' Frequency Distribution')
    plt.xlabel(mapname + ' Score')
    plt.ylabel('Fraction ' + name + ' Over All Landuse Type ' + mapname +' Frequency')
    # set the y axis values to be 100% times.
    formatter = FuncFormatter(to_percent)
    plt.gca().yaxis.set_major_formatter(formatter)

    #plot the graph and pinpoint the max y value point
    x = np.insert(x, 0, 0) #if not this, x will be shorter than y
    plt.plot(x, y, 'ro--')
    ymax_index = np.argmax(y)
    ymax       = y[ymax_index]
    ymax_xval  = x[ymax_index]
    plt.scatter(ymax_xval, ymax*100)
    plt.grid(True)

    # save the figure to file
    plt.savefig(outfile)  # cut 10 percentile tail and head values

# csv output
def write_data(x , y , outfile, name, mapname):
    x = np.insert(x, 0, 0)  # if not this, x will be shorter than y
    outdata_arr = np.asarray([x,y])
    outdata_arr = np.transpose(outdata_arr)
    np.savetxt(outfile, outdata_arr, fmt='%5.5f', delimiter=',',
               header="x,y", comments='')

#cut 5 percentile tail and head values, and mask the residential array
def cut_values(attr_res_arr, attr_arr, bnum):

    # create unique arrays from the attribute array
    attr_uni = np.unique(attr_arr)

    #find the high and low cutoff at 5 and 95 percentile
    a_len = len(attr_uni)
    low_ind = round(a_len * 0.1)
    high_ind = round(a_len * 0.9)
    low_cut = attr_uni[(low_ind-1)]
    print low_cut
    high_cut = attr_uni[(high_ind - 1)]
    print high_cut

    #make the cut
    attr_arr = attr_arr[attr_arr >= low_cut]
    attr_arr = attr_arr[attr_arr <= high_cut]
    attr_res_arr = attr_res_arr[attr_res_arr >= low_cut]
    attr_res_arr = attr_res_arr[attr_res_arr <= high_cut]

    #create x axis values
    attr_arr_len = len(attr_arr)
    attrbasketsize = attr_arr_len / bnum
    attr_arr_sort = np.sort(attr_arr)
    attr_arr_x = attr_arr_sort[0:attr_arr_len - 1:attrbasketsize]  # the x axis tick values
    attr_arr_x = attr_arr_x[0:bnum + 1]  # merge the last basket to the previous one
    attr_arr_x = np.unique(attr_arr_x)

    return {'attr_arr': attr_arr, 'attr_res_arr': attr_res_arr, 'attr_arr_x': attr_arr_x}


#analyze frequency at each quantile cutoff
def frequencyanalysis_attr(attr_res_arr, attr_arr, attr_arr_x):

    xlen = len(attr_arr_x)
    #attr_res_arr_nb         = attr_res_arr[attr_res_arr > ATTRBASE]
    print " CELLS CONSIDERED: ", len(attr_res_arr)
    #attr_arr_sort     = np.sort(attr_res_arr)
    #attr_res_basketsize_1st = len(attr_res_arr[attr_res_arr == ATTRBASE])
    #attr_basketsize_1st      = len(attr_arr    [attr_arr     == ATTRBASE])
    attr_res_freq = [] # frequency array for residential cells
    attr_arr_freq = [] # frequency array for all cells
    cur1 = attr_arr_x[0] # initialize lower bound of the cutoff

    #calculate the first basket
    mask = (attr_res_arr >= 0) & (attr_res_arr <= cur1)  # residential cells with values within the cutoff
    attr_res_freq.append(len(attr_res_arr[mask])) # add new residential frequency to the frequency array
    mask = (attr_arr >= 0) & (attr_arr <= cur1) # all cells with values within the cutoff
    attr_arr_freq.append(len(attr_arr[mask])) # add all cells frequency to the frequency array

    for i in xrange(1, xlen): #i is for cur2. in total ATTRBASKETNUM baskets.
        cur2 = attr_arr_x[i] # upper boundary of the cutoff
        mask = (attr_res_arr > cur1) & (attr_res_arr <= cur2) # residential cells with values within the cutoff
        attr_res_freq.append(len(attr_res_arr[mask])) # add new residential frequency to the frequency array
        mask = (attr_arr > cur1) & (attr_arr <= cur2) # all cells with values within the cutoff
        attr_arr_freq.append(len(attr_arr[mask])) # add all cells frequency to the frequency array
        cur1 = cur2 #update lower bound of the cutoff

    attr_res_freq.append(len(attr_res_arr[attr_res_arr > cur1])) #add final cuoff values
    attr_arr_freq.append(len(attr_arr[attr_arr > cur1]))# add final cutoff values
    
    print "---------------------attr_res_freq----------------\n",[int(i) for i in attr_res_freq] #print res frequency
    print "---------------------attr_arr_freq----------------\n",[int(i) for i in attr_arr_freq] #print total frequency
    attr_res_y = np.divide(attr_res_freq, attr_arr_freq, dtype=np.float) # calculate y values on the axis
    attr_res_y = np.nan_to_num(attr_res_y) # eliminate nan values
    print "---------------------attr_y----------------\n",attr_res_y #print y values
    return{'attr_res_y': attr_res_y, 'xlen':  xlen}


def main():
    dict = opt_parser()
    [m_bnum, m_isemp, m_mapname] = [dict.get(k) for k in ('bnum','ctype','c_opts')]

    dict = data_loader(m_isemp)
    [m_res_raw,m_all_raw] = [dict.get(k) for k in ('res_arr','all_array')]

    dict = cut_values(m_res_raw, m_all_raw, m_bnum)
    [m_x, m_res, m_all] = [dict.get(k) for k in ('attr_arr_x', 'attr_res_arr', 'attr_arr')]

    dict = frequencyanalysis_attr(m_res, m_all, m_x)
    [m_y, m_len] = [dict.get(k) for k in ('attr_res_y', 'xlen')]
    m_name = 'res'

    dict = graph_names(m_name, m_mapname, m_bnum, 'nochange')
    [m_outgraph, m_outdata] = [dict.get(k) for k in ('outmapename', 'outdataname')]

    plotgraph(m_x, m_y, m_len, str(m_outgraph), m_name, m_mapname)
    write_data(m_x, m_y, str(m_outdata), m_name, m_mapname)



if __name__ == "__main__":
    if (len(sys.argv) < 1):
        print "Required: Arg1 ATTRBASKETNUM, Arg2 COSTBASKETNUM"
        exit(1)
    main()
    
