# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 21:04:18 2021

@author: snaeimi
"""

import sys
import copy
import os
import pickle
import time
import pandas as pd
import logging
#import numpy as np
import Input.Input_IO as io
#from starter.io import *
from Input.Settings import Settings
from Result_Project import Project_Result
logging.basicConfig(level=50)

from restoration.registry import Registry
from restoration.model import Restoration
import StochasticModel
import Damage
import time
import logging


class Project():
    def __init__(self, project_settings, scenario_list):
        self.scenario_list    = scenario_list
        self.project_settings = project_settings


log=[]
W_N = 2


result_directory = 'damage_input/list_akhar_with_prob.xlsx'

class Starter():

    def read_damage_list(self, list_file_addr, file_directory, iCheck=False):
        """
        Reads damage sceanrio list.

        Parameters
        ----------
        list_file_addr : Address to the target list file
            DESCRIPTION.
        file_directory : TYPE
            DESCRIPTION.
        iCheck : TYPE, optional
            DESCRIPTION. The default is False. Checks if all damage files are found.

        Raises
        ------
        RuntimeError
            if file not found.

        Returns
        -------
        damage_list : Pandas Dataframe
            DESCRIPTION.

        """
        damage_list=None
        error_file_name=[]
        with open(list_file_addr, 'rb') as f:
            #damage_list = pd.read_pickle(f)
            damage_list = pd.read_excel(f)
        iError=False
        temp = damage_list['Pipe Damage'].tolist()
        
        if iCheck==False:
            return damage_list
        
        for file_name in temp:
            if not os.path.exists(file_name):
                iError=True
                error_file_name.append(file_name)
        
        if iError:
            raise RuntimeError('The Follwoing files could not be found: '+repr(error_file_name))
        return damage_list
    
    def run(self):
        """
        Runs the ptogram. It initiates the Settings class and based on the
        settings, run the program in either single scenario, multiple serial or
        multiple parallel mode.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        settings = Settings()
        self.run_mpi(settings)
    
    def run_mpi(self, settings):
        from mpi4py import MPI
        import mpi4py
        comm = MPI.COMM_WORLD
        mpi4py.rc.recv_mprobe = False

        
        pipe_damage_list=self.read_damage_list('damage_input/list_akhar_with_prob.xlsx', [])
        addr = os.path.join(settings.process['result_directory'], 'project.prj')
        pr = Project_Result(addr, ignore_not_found=True)
        pr.readPopulation()
        pipe_damage_list = pr.project.scenario_list
        pipe_damage_list = pipe_damage_list.reset_index(drop=False)
        
        if comm.rank == 0:
                
            scn_name_list    = pipe_damage_list['Scenario Name'].to_list()
            file_name_list   = pipe_damage_list['Pipe Damage'].to_list()
            
        
        if comm.rank == 0:
            pr = Project_Result(addr, ignore_not_found=True)
            time_jobs_saved = time.time()
            jobs = pd.DataFrame(columns=['scenario_name', 'file_name', 'worker', 'Done', 'time_assigned', 'time_confirmed'])
            jobs['scenario_name'] = scn_name_list
            jobs['file_name']     = file_name_list
            jobs['worker']        = None
            jobs['Done']          = "False"
            jobs['time_assigned'] = None
            jobs['time_confirmed']= None
            
            workers = pd.Series(data=-1, index=[1+i for i in range(W_N-1)])
            res  = {}
            sett = {}
            iContinue = True
            while iContinue:
                
                    
                if comm.iprobe():
                    status=MPI.Status()
                    recieved_msg = comm.recv(status=status)
                    worker_rank  = status.Get_source()
                    #print(type(recieved_msg), flush=True)
                    #print(recieved_msg)
                    #if recieved_msg==1 or recieved_msg==2: #check if the job is done
                        #msg_interpretation = None
                        #if recieved_msg==1:
                            #msg_interpretation = 'done'
                            
                        #print('messaged recieved= '+repr(msg_interpretation)+' rank recivied= '+repr(worker_rank))
                    # In both cases it means the jobs is done, only in different ways
                    #else:
                        #raise ValueError('Recieved message from worker is not recognized: ' + str(recieved_msg) + ', ' + str(worker_rank))
                    jobs_index = workers.loc[worker_rank]
                    scn_name = jobs.loc[jobs_index, 'scenario_name']
                    res[scn_name] = recieved_msg
                        #sett[scn_name] = recieved_msg[1]
                    jobs.loc[jobs_index, 'Done']='True'
                        
                    jobs.loc[jobs_index,'time_confirmed']=time.time()
                    workers.loc[worker_rank]=-1
                    
                    time_began  = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobs.loc[jobs_index, 'time_assigned']))
                    time_end    = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobs.loc[jobs_index, 'time_confirmed']))
                    time_lapsed = jobs.loc[jobs_index,'time_confirmed']-jobs.loc[jobs_index,'time_assigned']
                    
                binary_vector =(jobs['worker'].isna())
                not_assigned_data = jobs[binary_vector]
                free_workers = workers[workers==-1]
                time_constraint=False
                    
                if len(not_assigned_data)>0 and len(free_workers)>0 and time_constraint==False:
                    jobs_index     = not_assigned_data.index[0]
                    worker_rank    = free_workers.index[0]
                    print('trying to send '+repr(jobs_index)+' to '+repr(worker_rank), flush=True)
                    comm.isend(jobs_index, worker_rank, tag=0)
                    
                    workers.loc[worker_rank]=jobs_index
                    jobs.loc[jobs_index, 'worker']=worker_rank
                    jobs.loc[jobs_index, 'time_assigned']=time.time()
                    
                    time_began  = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobs.loc[jobs_index, 'time_assigned']))
                    
                binary_vector = (jobs['Done']=='False')
                iContinue = (binary_vector.any() and (not time_constraint) )
            
            #Finish workers with sending them a dummy data with tag=100 (death tag)
            with open("read_res.pkl", 'wb') as f:
                pickle.dump(res, f)
            for i in range(1, W_N):
                print('Death msg (tag=100) is sent to all workers. RIP!', flush=True)
                comm.send('None',dest=i ,tag=100)
            jobs['time_lapsed']=jobs['time_confirmed']-jobs['time_assigned']
            jobs['time_assigned']=jobs.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x.loc['time_assigned'])), axis=1)
            jobs['time_confirmed']=jobs.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x.loc['time_confirmed'])), axis=1)
            #jobs.to_excel('jobs.xlsx')
                
            print('MAIN NODE FINISHED. Going under!', flush=True)

        
        else:
            worker_exit_flag=None
            while True:
                if comm.iprobe(source=0):
                    status = MPI.Status()
                    print('trying to recieve msg. -> rank= '+repr(comm.rank),flush=True)
                    scenario_index = comm.recv(source=0, status=status)
                  
                    if status.Get_tag()!=100:            
                        scenario_name  = pipe_damage_list.loc[scenario_index,'Scenario Name']
                        print('Rank= '+repr(comm.rank)+'  is assigned to '+str(scenario_index)+' : '+str(scenario_name), flush=True)
                        addr = os.path.join(settings.process['result_directory'], 'project.prj')
                        #pr = Project_Result(addr, ignore_not_found=True)
                        s = pr.getOutageTimeGeoPandas_4(scenario_name, LOS='QN', leak_ratio=0, consistency_time_window=7200)
                        #data = self.readData(scenario_name)
                        comm.isend(s, dest=0)
                        last_time_message_recv=time.time()
                    else:
                        worker_exit_flag='Death message recieved!'
                        break
                    
                    if (time.time()-last_time_message_recv) > settings.process['maximun_worker_idle_time']:
                        worker_exit_flag='Maximum time reached.'
                        break
            print(repr(worker_exit_flag)+" I'm OUT -> Rank= "+repr(comm.rank), flush=True)
    
        
    def readData(self, scn_name):
            
        scenario_registry_file_name = scn_name+"_registry.pkl"
        registry_file_data_addr = os.path.join(result_directory, scenario_registry_file_name)
        
        with open(registry_file_data_addr, 'rb') as f:
            if not os.path.exists(registry_file_data_addr):
                print("Registry File Not Found: "+ str(registry_file_data_addr))
                return False
            #current_scenario_registry =  pickle.load(f)
        
        #self.pipe_damages[scn_name] = current_scenario_registry.damage.pipe_all_damages
        #self.node_damages[scn_name] = current_scenario_registry.node_damage
        #self.pump_damages[scn_name] = current_scenario_registry.damaged_pumps
        #self.tank_damages[scn_name] = current_scenario_registry.tank_damage 
                    
        res_addr = os.path.join(result_directory, scn_name+'.res')
        
        with open(res_addr, 'rb') as f:
            #print(output_addr)
            res_file_data = pickle.load(f)
        
        settings_file_name = scn_name+'.xlsx'                
        settings_file_addr = os.path.join(result_directory, settings_file_name) 
        scenario_set       = 1#= pd.read_excel(settings_file_addr)
        res = {}
        res['scn_name']     = scn_name
        res['scenario_set'] = scenario_set
        
        res_file_data.node['head']    = None
        res_file_data.node['quality'] = None
        self.remove_maximum_trials(res_file_data)
        print(sys.getsizeof(res_file_data.node['demand'].to_numpy()) )
        res['data']                   = res_file_data
       
        
        print(str(scn_name) +" loaded")
        return 1
        

        
        
    def remove_maximum_trials(self, data):

        all_time_list = data.maximum_trial_time
        result_time_list = data.node['demand'].index.to_list()
        result_time_max_trailed_list = [ time for time in result_time_list if time in all_time_list]
        
        demand_data = data.node['demand']
        demand_data.drop(result_time_max_trailed_list, inplace=True)
        

        
        pressure_data = data.node['pressure']
        pressure_data.drop(result_time_max_trailed_list, inplace=True)
        
        setting_data = data.link['setting']
        setting_data.drop(result_time_max_trailed_list, inplace=True)
        
        status_data = data.link['status']
        status_data.drop(result_time_max_trailed_list, inplace=True)
        
        result_time_list = data.node['leak'].index.to_list()
        result_time_max_trailed_list = [ time for time in result_time_list if time in all_time_list]
        leak_data = data.node['leak']
        leak_data.drop(result_time_max_trailed_list, inplace=True)
        
        result_time_list = data.link['flowrate'].index.to_list()
        result_time_max_trailed_list = [ time for time in result_time_list if time in all_time_list]
        flow_data = data.link['flowrate']
        flow_data.drop(result_time_max_trailed_list, inplace=True)
        
start = Starter()
tt = start.run()  
