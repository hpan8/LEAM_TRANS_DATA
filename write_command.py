l_opts = ["resn", "resc", "comn", "comc"]
c_opts = ['empa', 'popa', 'empc', 'popc', 'mpopa', 'mpopc','empa', 'mempc', 'statec', 'countyc',
          'roadc', 'ramp', 'intsectc', 'transc', 'waterc', 'frstc', 'slopec']

f = open('cmd_line.txt','w')
for i in range(17):
    for j in range(4):
        cmd_line = "python dataanalysis_2.py 10 -c " + str(c_opts[i]) + " -l " + str(l_opts[j]) + "\n"
        f.write(cmd_line)  # python will convert \n to os.linesep


