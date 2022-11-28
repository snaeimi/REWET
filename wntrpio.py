# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 01:08:58 2020

@author: snaeimi
"""

import io
import pandas as pd
import copy


def read_material(filename):
    
    #pipe_mat = pd.Series()
    lnum = 0
    pipe=[]
    mat=[]
    with io.open(filename, 'r', encoding='utf-8') as f:        
        for line in f:
            lnum += 1
            #edata['lnum'] = lnum
            line = line.strip()
            line = line.split()
            nwords = len(line)
            if len(line) == 0:
                continue
            elif len(line) != 2:
                print('ength is ' + str(len(line)))
                print(line)
                raise IOError("There must be two rows")
            if lnum == 1:     
                if line[0].upper() != 'PIPE':
                    raise IOError("the first word of the first row must be PIPE")
                elif line[1].upper() != 'MATERIAL':
                    raise IOError("the second word of the first row must be MATERIAL")
            else:
                #pipe_mat[line[0]] = line[1]
                pipe.append(line[0])
                mat.append(line[1])
    pipe_mat = pd.Series(index=pipe, data=mat)
    return pipe_mat

def readDemandNodeList():
    demand_node_list=[]
    with io.open('DemandNodeList.csv', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            demand_node_list.append(line)
    return demand_node_list
    
def assigne_material_to_model(wn, pipe_mat):
    pipe_list = copy.copy(wn.pipe_name_list)
    for pipe_name, pipe_material in pipe_mat.iteritems():
        not_in_list = False
        try:
            pipe_list.remove(pipe_name)
        except ValueError:
            not_in_list = True
        
        if not_in_list == False:
            pipe = wn.get_link(pipe_name)
            pipe.material = pipe_material.upper()
        
def material_length(wn, pipe_mat):
    
    diameter = []
    length   = []
    NA_n  = []
    NA_d  = []
    NA_l  = []
    NA_m  = []
    
    name     = []
    mat      = []
    no_mat_n = []
    no_mat_d = []
    no_mat_l = []
    not_in_pipe_list = []
    
    for pname, pmat in pipe_mat.iteritems():
        if pname in wn.pipe_name_list and pmat != 'N/A':
            p = wn.get_link(pname)
            if p.diameter > 20 * 2.54/100:
                length.append(p.length)
                diameter.append(p.diameter*100/2.54)
                name.append(pname)
                mat.append(pmat)
            e
        else:
            if pname not in wn.pipe_name_list:
                not_in_pipe_list.append(pname) 
            else:
                p=wn.get_link(pname)
                NA_n.append(pname)
                NA_d.append(p.diameter*100/2.54)
                NA_l.append(p.length/1000)
                if pname in pipe_mat.index:
                    NA_m.append(pipe_mat[pname])
                else:
                    NA_m.append(None)
    
    for pname in wn.pipe_name_list:
        p = wn.get_link(pname)
        if p.diameter > 20*2.54/100:
            if pname not in pipe_mat.index:
                no_mat_n.append(pname)
                no_mat_d.append(p.diameter*100/2.54)
                no_mat_l.append(p.length/1000)
    print(not_in_pipe_list)
    must_not_be_included = pd.DataFrame()
    must_not_be_included['material']=NA_m
    must_not_be_included['diameter']=NA_d
    must_not_be_included['length']=NA_l
    must_not_be_included['name']=NA_n
    must_not_be_included.to_csv('NA.csv')

    
    #print(no_mat_n)
    no_mat_more_20 = pd.DataFrame()
    no_mat_more_20['name'] = no_mat_n
    no_mat_more_20['diameter'] = no_mat_d
    no_mat_more_20['length'] = no_mat_l
    print(len(pd.Series(index=no_mat_n, data = no_mat_l)))
    
    data_tuple = zip(mat,diameter, length)
    data = pd.DataFrame(index = name, data =  data_tuple, columns =['Material', 'Diameter', 'Length'])
    data.to_csv('mterial_pipe_table.csv')
    
    print(data)
    no_mat_more_20.to_csv('pipe_more_than_20_with_no_material.csv')