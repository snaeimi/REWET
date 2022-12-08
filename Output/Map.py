# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 09:43:00 2022
This file includes all Map Related Results.

Class:
    Map: inherieted by Project_Result{

    functions:
        loadShapeFile
        joinTwoShapeFiles
        createGeopandasPointDataFrameForNodes
        getDLQNExceedenceProbabilityMap
        getOutageTimeGeoPandas_4
}

@author: snaeimi
"""

import geopandas as gpd
import pandas    as pd
import numpy     as np
import shapely
import Output.Helper as Helper

class Map():
    def __init__(self):
        pass
    def loadShapeFile(shapeFileAddr='Northridge\GIS\Demand\demand_polygons.shp'):
        shape_file = gpd.read_file(shapeFileAddr)
        return shape_file
        
    def joinTwoShapeFiles(first, second):

        second = second.set_crs(epsg=first.crs.to_epsg())
        joined_map = gpd.sjoin(first, second)
            
        return joined_map
    
    def createGeopandasPointDataFrameForNodes(self, node_list):
        s = gpd.GeoDataFrame(index=self.demand_node_name_list)
        point_list      = []
        point_name_list = []
        
        for name in node_list:
            coord = self.wn.get_node(name).coordinates
            point_list.append(shapely.geometry.Point(coord[0],coord[1]))
            point_name_list.append(name)
        s.geometry = point_list
        return s
    
    def getDLQNExceedenceProbabilityMap(self, data_frame, ihour , param):
        data = data_frame.transpose()
        scn_prob_list =  self.scenario_prob
        #DLQN_dmg = pd.DataFrame(data=0, index=data.index, columns=data.columns)
        
        scn_prob = [scn_prob_list[scn_name] for scn_name in data.index]
        data['prob'] = scn_prob
            
        res_dict_list = []
        
        if ihour:
            for node_name in data_frame.index:
                loop_dmg = data[[node_name,'prob']]
                loop_dmg = loop_dmg.sort_values(node_name, ascending=False)
                loop_ep  = Helper.EPHelper(loop_dmg['prob'].to_numpy())
                loop_dmg['ep'] = loop_ep
                inter_ind = param
                if inter_ind >= loop_dmg['ep'].max():
                    max_ind = loop_dmg[loop_dmg['ep'] == loop_dmg['ep'].max()].index[0]
                    inter_value = loop_dmg.loc[max_ind, node_name]
                elif inter_ind <= loop_dmg['ep'].min():
                    min_ind = loop_dmg[loop_dmg['ep'] == loop_dmg['ep'].min()].index[0]
                    inter_value = loop_dmg.loc[min_ind, node_name]
                else:
                    loop_dmg.loc['inter', 'ep'] = inter_ind
                    
                    loop_dmg = loop_dmg.sort_values('ep')
                    ep_list = loop_dmg['ep'].to_list()
        
                    inter_series = pd.Series(index=ep_list, data=loop_dmg[node_name].to_list())
                    inter_series = inter_series.interpolate(method='linear')
                    inter_value  = inter_series.loc[inter_ind]
                    if type(inter_value) != np.float64:
                        inter_value = inter_value.mean()
                res_dict_list.append({'node_name':node_name, 'res':inter_value})

        else:
            for node_name in data_frame.index:
                loop_dmg = data[[node_name,'prob']]
    
                loop_dmg = loop_dmg.sort_values(node_name, ascending=False)
                loop_ep  = Helper.EPHelper(loop_dmg['prob'].to_numpy())
                loop_dmg['ep'] = loop_ep
                inter_ind = param
                if inter_ind >= loop_dmg[node_name].max():
                    max_ind = loop_dmg[loop_dmg[node_name] == loop_dmg[node_name].max()].index[0]
                    inter_value = loop_dmg.loc[max_ind, 'ep']
                elif inter_ind <= loop_dmg[node_name].min():
                    min_ind = loop_dmg[loop_dmg[node_name] == loop_dmg[node_name].min()].index[0]
                    inter_value = loop_dmg.loc[min_ind, 'ep']
                else:
                    loop_dmg.loc['inter', node_name] = inter_ind
                    
                    loop_dmg = loop_dmg.sort_values(node_name)
                    hour_list = loop_dmg[node_name].to_list()
        
                    inter_series = pd.Series(index=hour_list, data=loop_dmg['ep'].to_list())
                    inter_series = inter_series.interpolate(method='linear')
                    inter_value  = inter_series.loc[inter_ind]
                    if type(inter_value) != np.float64:
                        inter_value = inter_value.mean()
 
                res_dict_list.append({'node_name':node_name, 'res':inter_value})
        
        res = pd.DataFrame.from_dict(res_dict_list)
        res = res.set_index('node_name')['res']
        
        s = gpd.GeoDataFrame(index=self.demand_node_name_list)
        point_list=[]
        point_name_list=[]
            
        for name in self.demand_node_name_list:
            coord=self.wn.get_node(name).coordinates
            point_list.append(shapely.geometry.Point(coord[0],coord[1]))
            point_name_list.append(name)
        
        s.geometry=point_list
        s['res']=res
    
        polygon = gpd.read_file('Northridge\GIS\Demand\demand_polygons.shp')
        s = s.set_crs(epsg=polygon.crs.to_epsg())
        joined_map = gpd.sjoin(polygon, s)
        #joined_map.plot(column='res', legend=True, categorical=True, cmap='Accent', ax=ax)
        #ax.get_legend().set_title('Hours without service')
        #ax.get_legend()._loc=3
        #props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            
        return joined_map
    
    def getOutageTimeGeoPandas_4(self, scn_name, LOS='DL' , leak_ratio=0, consistency_time_window=7200):
        self.loadScneariodata(scn_name)
        res         = self.data[scn_name]
        map_res     = pd.Series(data=0 , index=self.demand_node_name_list, dtype=np.int64)
        
        demands     = self.getRequiredDemandForAllNodesandtime(scn_name)
        refined_res = res.node['demand'][self.demand_node_name_list]
        union_      = set(res.node['leak'].columns).union(set(self.demand_node_name_list) - (set(res.node['leak'].columns) ) - set(self.demand_node_name_list)) - (set(self.demand_node_name_list) - set(res.node['leak'].columns))
        leak_res    = res.node['leak'][union_]
        
        leak_data = []
        for name in leak_res:
            demand_name = demands[name]
            current_leak_res = leak_res[name].dropna()
            time_list = set(leak_res[name].dropna().index)
            time_list_drop = set(demands.index) - time_list
            demand_name = demand_name.drop(time_list_drop)
            leak_more_than_criteria = current_leak_res >=  leak_ratio * demand_name
            if leak_more_than_criteria.any(0):
                leak_data.append(leak_more_than_criteria)
        leak_data = pd.DataFrame(leak_data).transpose()

        demands = demands[self.demand_node_name_list]
        
        if LOS=="DL":
            DL_res_not_met_bool = refined_res <= demands * 0.01
        elif LOS =="QN":
            DL_res_not_met_bool = refined_res < demands * 0.98
        
        time_window = consistency_time_window
        time_list = DL_res_not_met_bool.index.to_list()
        time_list.reverse()
        
        for time in time_list:
            past_time_beg = time - time_window
            window_data = DL_res_not_met_bool.loc[past_time_beg:time]
            window_data = window_data.all()
            window_data_false = window_data[window_data == False]
            DL_res_not_met_bool.loc[time, window_data_false.index] = False
        
        for name in DL_res_not_met_bool:
            if name in leak_data.columns:
                leak_data_name = leak_data[name]
                for time in leak_data_name.index:
                    if leak_data_name.loc[time] == True:
                        DL_res_not_met_bool.loc[time, name] = True
                   
        all_node_name_list = refined_res.columns
        only_not_met_bool  = DL_res_not_met_bool.any(0)
        only_not_met_any   = all_node_name_list[only_not_met_bool]
        DL_res_not_met = DL_res_not_met_bool.filter(only_not_met_any)
        DL_res_MET = ~DL_res_not_met
        time_window = 4

        for name in only_not_met_any:

            rolled_DL_res_MET = DL_res_MET[name].rolling(time_window, center=True).sum()
            rolled_DL_res_MET = rolled_DL_res_MET.sort_index(ascending=False)
            rolled_DL_res_MET.dropna(inplace=True)
            
            false_found, found_index = Helper.helper_outageMap(rolled_DL_res_MET.ge(time_window-1))
            
            if false_found == False:
                latest_time = 0
            else:
                latest_time = rolled_DL_res_MET.index[found_index]
            
            map_res.loc[name] = latest_time

        #map_res = map_res/(3600*24)
        geopandas_df = self.createGeopandasPointDataFrameForNodes(self.demand_node_name_list, )
        geopandas_df.loc[map_res.index.to_list(), 'restoration_time'] = map_res.to_list()
        
        return geopandas_df