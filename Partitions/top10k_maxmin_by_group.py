import re
import os
import sys

top10k_file = str(sys.argv[1])

top10k = open(top10k_file, 'r')

top10k_lines = top10k.readlines()

top10k_dict = {}
top10k_list = []
for line in top10k_lines:
    mod_line = re.sub(r'[\[\]]*', r'', line)
    mod_line = mod_line.split(',')
    mod_line[2] = mod_line[2].strip()
    top10k_list.append([mod_line[1], mod_line[0], mod_line[2]])
    if(mod_line[2] not in top10k_dict.keys()):
        top10k_dict[mod_line[2]] = [[mod_line[1], mod_line[0]]]
    else:
        top10k_dict[mod_line[2]].append([mod_line[1], mod_line[0]])
    
top10k_list.sort(key=lambda elem: int(elem[0]))
top10k_list.reverse()
for group in top10k_dict.keys():
    top10k_dict[group].sort(key=lambda elem: int(elem[0]))
    top10k_dict[group].reverse()
    print '############### ' + group + ' ###############'
    print 'Category:\t\tLeast Followed\t\tMost Followed' 
    print 'Top 10k rank:\t\t' + str(top10k_list.index([top10k_dict[group][-1][0],top10k_dict[group][-1][1],group]) + 1) + '\t\t\t' + str(top10k_list.index([top10k_dict[group][0][0],top10k_dict[group][0][1],group]) + 1)
    print 'User ID:\t\t' + top10k_dict[group][-1][1] + '\t\t' + top10k_dict[group][0][1]
    print 'Number of followers:\t' + top10k_dict[group][-1][0] + '\t\t\t' + top10k_dict[group][0][0]




