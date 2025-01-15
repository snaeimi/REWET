# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 21:04:18 2021

@author: snaeimi
"""

import os
import pickle
import time
import logging
import warnings
import pandas as pd

from rewet                            import Timeline
from rewet import Damage
from rewet.Input.Settings             import Settings
from rewet.EnhancedWNTR.network.model import WaterNetworkModel
from rewet.restoration.registry       import Registry
from rewet.restoration.model          import Restoration
from rewet.Project                    import Project
from rewet.Input.Input_IO             import resolve_path
import rewet.Input.Input_IO           as io

logging.basicConfig(level=50)

class Starter():

    def RunLocally(self, damage_list, settings, i):
        logging.info(f"scenario index = {i}")
        t1 = time.time()
        settings.initializeScenarioSettings(i) #initialize scenario-specific settings for each list/usefule for sensitivity analysis
        scenario_name     = damage_list.loc[i, 'Scenario Name']
        pipe_damage_name  = damage_list.loc[i, 'Pipe Damage']
        tank_damage_name  = damage_list.loc[i, 'Tank Damage']
        nodal_damage_name = damage_list.loc[i, 'Nodal Damage']
        pump_damage_name  = damage_list.loc[i, 'Pump Damage']

        self.run_local_single(pipe_damage_name, scenario_name, settings, nodal_damage_file_name = nodal_damage_name, pump_damage_file_name = pump_damage_name, tank_damage_file_name = tank_damage_name)

        t2 = time.time()
        logging.info(f"Time of Single run is: {repr((t2-t1)/3600)} (hr)")

    def read_input_file(self, settings, input_file_path):
        """
        Reads a REWET input file and set the settings object accordingly.
        teh function does nothingh when None is passed as input_file_path.

        Parameters
        ----------
        settings : REWET.Settings
            Seeting object to be setup after reading the input file.
        input_file_path : string
            input file path.

        Raises
        ------
        ValueError
            Unknown File is provided.

        Returns
        -------
        None.

        """
        # Checks if the path is valid and is not None
        # TODO: change this to Path annd chaneg this function
        if (type(input_file_path) != type(None) and
            type(input_file_path) != type(str)):
            # if the path is not string type, then make it string
            input_file_path = str(input_file_path)

        # Check if gile type is project (.prj) oor JSON (.json)
        # TODO: better check is requred. A File with wrong extention but right format might be given
        if type(input_file_path) != type(None):
            if input_file_path.split(".")[-1].lower() == "prj":
                settings.importProject(input_file_path)
            elif input_file_path.split(".")[-1].lower() == "json":
                settings.importJsonSettings(input_file_path)
                input_file_path = None
            else:
                raise ValueError("The input file has an unrgnizable extension: {}".format(input_file_path.split(".")[-1].lower()) )

    def run(self, project_file=None, api=False):
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

        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            settings = Settings()
            self.read_input_file(settings, project_file)

            damage_list = io.read_damage_list(settings.process['pipe_damage_file_list'], settings.process['pipe_damage_file_directory'])
            settings.process.settings['list'] = damage_list
            #if type(project_file) == type(None):
            Project.createProjectFile(settings, damage_list, "project.prj")
            #raise
            if settings.process['number_of_proccessor']==1: #Single mode
                #get damage list as Pandas Dataframe
                if settings.process['number_of_damages'] == 'multiple':
                    damage_list_size = len(damage_list)
                    for i in range(0, damage_list_size):
                        if api == False:
                            self.RunLocally(damage_list, settings, i)
                        #print(i, flush=True)
                        #settings.initializeScenarioSettings(i) #initialize scenario-specific settings for each list/usefule for sensitivity analysis
                        #scenario_name    = damage_list.loc[i, 'Scenario Name']
                        #pipe_damage_name = damage_list.loc[i, 'Pipe Damage']
                        #tank_damage_name = damage_list.loc[i, 'Tank Damage']
                        #self.run_local_single(pipe_damage_name, scenario_name, settings, nodal_damage_file_name = damage_list.loc[i,'Nodal Damage'], pump_damage_file_name = damage_list.loc[i,'Pump Damage'], tank_damage_file_name = tank_damage_name)

                elif settings.process['number_of_damages'] == 'single':
                    if api == False:
                        self.RunLocally(damage_list, settings, 0)
                    #t1 = time.time()
                    #settings.initializeScenarioSettings(0) #initialize scenario-specific settings for the first line of damage list
                    #scenario_name = damage_list.loc[0, 'Scenario Name']
                    #pipe_damage_name = damage_list.loc[0, 'Pipe Damage']
                    #tank_damage_name = damage_list.loc[0, 'Tank Damage']
                    #self.run_local_single(pipe_damage_name, scenario_name, settings, nodal_damage_file_name = damage_list.loc[0,'Nodal Damage'], pump_damage_file_name = damage_list.loc[0,'Pump Damage'], tank_damage_file_name = tank_damage_name)
                    #t2 = time.time()
                    #print('Time of Single run is: ' + repr((t2-t1)/3600) + '(hr)')
                else:
                    raise ValueError(f"Unknown value for settings['number_of_damages']: {settings['number_of_damages']}")

            elif settings.process['number_of_proccessor']>1:
                if api == True:
                    raise ValueError("API cannot be laoded while using MPI for multiprocessing.")
                self.run_mpi(settings)
            else:
                raise ValueError('Number of proccessor must be equal to or more than 1')


    def run_local_single(self, file_name, scenario_name, settings, worker_rank=None, nodal_damage_file_name=None, pump_damage_file_name=None, tank_damage_file_name=None):
        """
        Runs a single scenario on the local machine.

        Parameters
        ----------
        file_name : str
            File damage file name.
        scenario_name : str
            scneario name.
        settings : Settings
            Settings object.
        worker_rank : int, optional
            Specifies the rank of the currnet woker. If the scneario is being run as single or multiple-serial mode, the can be anything. It  is used for naming temp files. The default is None.
        nodal_damage_file_name : str, optional
            nodal damages file name. The default is None.
        pump_damage_file_name : TYPE, optional
            pump damages file name. The default is None.
        tank_damage_file_name : TYPE, optional
            Tank damages file name. The default is None.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        print(scenario_name + ' - ' + file_name + ' - ' + nodal_damage_file_name + ' - ' + str(pump_damage_file_name), flush=True)
        if settings.process['number_of_proccessor'] > 1 and worker_rank == None:
            raise ValueError('for multiple proccessor analysis, worker_rank_must be provided')

        if type(file_name) != str:
            file_name = str(file_name) #for number-only names to convert from int/float to str

        if type(tank_damage_file_name) != str:
            tank_damage_file_name = str(tank_damage_file_name) #for number-only names to convert from int/float to str

        if type(nodal_damage_file_name)!=str:
            nodal_damage_file_name = str(nodal_damage_file_name) #for number-only names to convert from int/float to str

        if type(pump_damage_file_name) != str:
            pump_damage_file_name = str(pump_damage_file_name) #for number-only names to convert from int/float to str


# =============================================================================
#         if settings.scenario['Pipe_damage_input_method'  ] == 'pickle':
#             pipe_damages = io.read_pipe_damage_seperate_pickle_file(settings.process['pipe_damage_file_directory'], file_name)
#             node_damages = io.read_node_damage_seperate_pickle_file(settings.process['pipe_damage_file_directory'], nodal_damage_file_name)
#             tank_damages = io.read_tank_damage_seperate_pickle_file(settings.process['pipe_damage_file_directory'], tank_damage_file_name)
#             pump_damages = io.read_pump_damage_seperate_pickle_file(settings.process['pipe_damage_file_directory'], pump_damage_file_name)
#         elif settings.scenario['Pipe_damage_input_method'] == 'excel':
#             pipe_damages = io.read_pipe_damage_seperate_EXCEL_file(settings.process['pipe_damage_file_directory'], file_name)
#             node_damages = io.read_node_damage_seperate_EXCEL_file(settings.process['pipe_damage_file_directory'], nodal_damage_file_name)
#             tank_damages = io.read_tank_damage_seperate_EXCEL_file(settings.process['pipe_damage_file_directory'], tank_damage_file_name)
#             pump_damages = io.read_pump_damage_seperate_EXCEL_file(settings.process['pipe_damage_file_directory'], pump_damage_file_name)
#         else:
#             raise ValueError("Unknown value for settings['Pipe_damage_input_method']")
# =============================================================================

# =============================================================================
#         pipe_damage_file_inputs = {
#             "damage_file_directory": settings.process['pipe_damage_file_directory'],
#             "pipe_damage_file_name": file_name,
#             "node_damage_file_name": nodal_damage_file_name,
#             "pump_damage_file_name": pump_damage_file_name,
#             "tank_damage_file_name": tank_damage_file_name,
#             }
# =============================================================================

        pipe_damages, node_damages, pump_damages, tank_damages = \
        io.read_damage_files(settings.process['pipe_damage_file_directory'],
                             file_name,
                             nodal_damage_file_name,
                             pump_damage_file_name,
                             tank_damage_file_name,
                             settings.scenario['Pipe_damage_input_method'])

        if (pipe_damages.empty == True
                and node_damages.empty == True
                and tank_damages.empty == True
                and pump_damages.empty == True
                and settings.process['ignore_empty_damage']):
            #means it didn't  run due to lack of any damage in pipe lines
            return 2

        """
            reads WDN definition and checks set the settinsg defined from settings
        """
        wn = WaterNetworkModel(settings.process['WN_INP'])

        delta_t_h = settings['hydraulic_time_step']
        wn.options.time.hydraulic_timestep = int(delta_t_h)
        #wn.options.time.pattern_timestep   = int(delta_t_h)
        #wn.options.time.pattern_timestep   = int(delta_t_h)
        # FIXME What about rule time step. Also one may want to change pattern time step

        demand_ratio = settings.process['demand_ratio']
        for junction_name, junction in wn.junctions():
            if junction.demand_timeseries_list[0].base_value > 0:
                base_value = junction.demand_timeseries_list[0].base_value
                junction.demand_timeseries_list[0].base_value = base_value * demand_ratio

        self.damage = Damage(None, settings.scenario)
        self.registry = Registry(wn,
                                 settings,
                                 scenario_name,
                                 pipe_damages,
                                 node_damages,
                                 pump_damages,
                                 tank_damages,
                                 self.damage)

        # TODO: All these data can immigrate to registry
        #self.registry.damage           = self.damage
        #self.damage.pipe_all_damages   = pipe_damages
        #self.damage.node_damage        = node_damages
        #if tank_damages.empty == False:
            #self.damage.tank_damage = tank_damages['Tank_ID']
        #if pump_damages.empty == False:
            #self.damage.damaged_pumps = pump_damages['Pump_ID']

        restoration = Restoration(settings.scenario['Restortion_config_file'],
                                  self.registry,
                                  self.damage)

        #restoration.pump_restoration = pump_damages
        #restoration.tank_restoration = tank_damages

        self.timeline  = Timeline(wn,
                                  self.damage,
                                  self.registry,
                                  simulation_end_time=settings.process['RUN_TIME'],
                                  restoration = restoration,
                                  mode='PDD',
                                  i_restoration=settings.process['Restoration_on'])

        result   = self.timeline.runLinearScenario(self.damage, settings, worker_rank)
        self.res = result
        io.save_single(settings, result, scenario_name, self.registry)
        return 1

    def run_mpi(self, settings):
        from mpi4py import MPI
        import mpi4py
        comm = MPI.COMM_WORLD
        mpi4py.rc.recv_mprobe = False

        pipe_damage_list= io.read_damage_list(settings.process['pipe_damage_file_list'   ], settings.process['pipe_damage_file_directory'])

        if settings.process['mpi_resume'] == True:
            pipe_damage_list = pipe_damage_list.set_index('Scenario Name')
            #_done_file = pd.read_csv('done.csv')
            #_done_file = _done_file.transpose().reset_index().transpose().set_index(0)
            file_lists = os.listdir(settings.process['result_directory'])
            done_scenario_list=[]
            for name in file_lists:

                if name.split('.')[-1] != 'res':
                    continue
                split_k = name.split('.res')[:-1]
                #print(split_k)
                kk = ""
                for portiong in split_k:
                    kk += portiong
                if kk not in done_scenario_list and kk in pipe_damage_list.index:
                    done_scenario_list.append(kk)

            pipe_damage_list = pipe_damage_list.drop(done_scenario_list)
            pipe_damage_list = pipe_damage_list.reset_index()

        if comm.rank == 0:
            scn_name_list    = pipe_damage_list['Scenario Name'].to_list()
            file_name_list   = pipe_damage_list['Pipe Damage'].to_list()
        else:
            file_name_list=[]

        if comm.rank == 0:
            time_jobs_saved = time.time()
            jobs = pd.DataFrame(columns=['scenario_name', 'file_name', 'worker', 'Done', 'time_assigned', 'time_confirmed'])
            jobs['scenario_name'] = scn_name_list
            jobs['file_name']     = file_name_list
            jobs['worker']        = None
            jobs['Done']          = "False"
            jobs['time_assigned'] = None
            jobs['time_confirmed']= None

            workers = pd.Series(data=-1, index=[1+i for i in range(settings.process['number_of_proccessor']-1)])

            iContinue = True
            while iContinue:

                if (time.time()-time_jobs_saved)>120:
                    jobs.to_excel('temp-jobs.xlsx') #only for more informaton about the latest job status for the user in teh real time
                    time_jobs_saved = time.time()

                if comm.iprobe():
                    status=MPI.Status()
                    recieved_msg = comm.recv(status=status)
                    worker_rank  = status.Get_source()
                    if recieved_msg==1 or recieved_msg==2 or recieved_msg==3: #check if the job is done
                        msg_interpretation = None
                        if recieved_msg==1:
                            msg_interpretation = 'done'
                        elif recieved_msg==2:
                            msg_interpretation = 'done w/o simulation'
                        elif recieved_msg==3:
                            msg_interpretation = 'exception happened'

                        print('messaged recieved= '+repr(msg_interpretation)+' rank recivied= '+repr(worker_rank))
                    # In both cases it means the jobs is done, only in different ways
                    else:
                        raise ValueError('Recieved message from worker is not recognized: ' + str(recieved_msg) + ', ' + str(worker_rank))

                    jobs_index = workers.loc[worker_rank]
                    if recieved_msg==1:
                        jobs.loc[jobs_index, 'Done']='True'
                    elif recieved_msg==2:
                        jobs.loc[jobs_index, 'Done']='No need'
                    elif recieved_msg==3:
                        jobs.loc[jobs_index, 'Done']='exception'

                    jobs.loc[jobs_index,'time_confirmed']=time.time()
                    workers.loc[worker_rank]=-1

                    time_began  = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobs.loc[jobs_index, 'time_assigned']))
                    time_end    = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobs.loc[jobs_index, 'time_confirmed']))
                    time_lapsed = jobs.loc[jobs_index,'time_confirmed']-jobs.loc[jobs_index,'time_assigned']
                    with open('done.csv', 'a', encoding='utf-8', buffering=1000000) as f: #shows teh order of done jobs
                        f.write( jobs.loc[jobs_index, 'scenario_name'] + ',' + jobs.loc[jobs_index, 'file_name']+','+str(jobs.loc[jobs_index, 'worker'])+','+str(time_lapsed)+','+str(time_began)+','+str(time_end)+'\n')

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
                    with open('runing.csv', 'a', encoding='utf-8', buffering=1000000) as f:
                        f.write( jobs.loc[jobs_index, 'scenario_name'] + ',' + jobs.loc[jobs_index, 'file_name']+','+str(jobs.loc[jobs_index, 'worker'])+','+str(time_began)+'\n')

                binary_vector = (jobs['Done']=='False')
                iContinue = (binary_vector.any() and (not time_constraint) )

            #Finish workers with sending them a dummy data with tag=100 (death tag)
            for i in range(1, settings.process['number_of_proccessor']):
                print('Death msg (tag=100) is sent to all workers. RIP!', flush=True)
                comm.send('None',dest=i ,tag=100)
            jobs['time_lapsed']=jobs['time_confirmed']-jobs['time_assigned']
            jobs['time_assigned']=jobs.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x.loc['time_assigned'])), axis=1)
            jobs['time_confirmed']=jobs.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x.loc['time_confirmed'])), axis=1)
            jobs.to_excel('jobs.xlsx')
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
                        settings.initializeScenarioSettings(scenario_index)
                        print('Rank= '+repr(comm.rank)+'  is assigned to '+str(scenario_index)+' : '+str(scenario_name), flush=True)
                        #row        = pipe_damage_list[pipe_damage_list['scenario_name']==scenario_name]
                        row              = pipe_damage_list.loc[scenario_index]
                        file_name        = row['Pipe Damage']
                        nodal_name       = row['Nodal Damage']
                        pump_damage      = row['Pump Damage']
                        tank_damage_name = row['Tank Damage']
                        try:
                            run_flag   = self.run_local_single(file_name, scenario_name, settings,  worker_rank=repr(scenario_name)+'_'+repr(comm.rank), nodal_damage_file_name=nodal_name, pump_damage_file_name = pump_damage, tank_damage_file_name = tank_damage_name)
                            print('run_flag for worker: '+ repr(comm.rank)+' --> '+repr(run_flag))
                            comm.isend(run_flag, dest=0)
                        except Exception as e:

                            error_dump_file = None
                            if type(scenario_name) == str:
                                error_dump_file = "dump_"+scenario_name+".pkl"
                            else:
                                error_dump_file = "dump_"+repr(scenario_name)+".pkl"

                            with open(error_dump_file, "wb") as f:
                                pickle.dump(self, f)

                            comm.isend(3, dest=0)
                        last_time_message_recv=time.time()

                    else:
                        worker_exit_flag='Death message recieved!'
                        break

                    if (time.time()-last_time_message_recv) > settings.process['maximun_worker_idle_time']:
                        worker_exit_flag='Maximum time reached.'
                        break
            print(repr(worker_exit_flag)+" I'm OUT -> Rank= "+repr(comm.rank), flush=True)

    def checkArgument(self, argv):
        if len(argv) > 2:
            print("REWET USAGE is as [./REWET Project.prj: optional]")
        if len(argv) == 1:
            return False
        else:
            return True

if __name__ == "__main__":
    import sys
    start = Starter()
    if_project = start.checkArgument(sys.argv)
    if if_project:
        if os.path.exists(sys.argv[1]):
            tt = start.run(sys.argv[1])
        else:
            print("Project file address is not valid: " + repr(sys.argv[1]) )
    else:
        tt = start.run()
