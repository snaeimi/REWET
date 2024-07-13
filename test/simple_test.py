# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 12:45:10 2024

@author: naeim
"""
import unittest
import pickle
import rewet
from rewet.initial import Starter
from pathlib import Path
import pandas as pd


class TestHydaulic(unittest.TestCase):

    def open_default_settings(self):
        start = Starter()
        start.run()

    def test_10day_net3_normal(self):
        start = Starter()
        start.run("./test_data/10_day_Net3_No_restoration/input.json")

        baseline_res_path = Path(
            "./test_data/10_day_Net3_No_restoration/test_baseline.res")

        with open(baseline_res_path, "rb") as f:
            baseline_result = pickle.load(f)

        result_dierctory = start.registry.settings["result_directory"]
        result_dierctory = Path(result_dierctory)
        scneario_res_fl =  start.registry.scenario_name + ".res"
        result_dierctory = ".." / result_dierctory / scneario_res_fl

        with open(result_dierctory, "rb") as f:
            tbt_result = pickle.load(f)

        self.check_two_result_value(baseline_result, tbt_result)

    def check_two_result_value(self, res1, res2):

        print("link")
        link_1 = res1.link
        link_2 = res2.link
        self.check_two_subresult_value(link_1, link_2)

        print("node")
        node_1 = res1.link
        node_2 = res2.link
        self.check_two_subresult_value(node_1, node_2)


    def check_two_subresult_value(self, subres1, subres2):

        atts_1 = set(subres1.keys())
        atts_2 = set(subres2.keys())

        common_atts = atts_1.intersection(atts_2)


        for att in common_atts:
            self.check_two_times(subres1[att], subres2[att])

            if (isinstance(subres1[att], pd.core.frame.DataFrame) and
                isinstance(subres2[att], pd.core.frame.DataFrame)):
                #if both are Pandas DataFrame

                element_name_list_1 = subres1[att].columns.to_list()
                element_name_list_2 = subres2[att].columns.to_list()

                self.assertEqual(element_name_list_1, element_name_list_2)

                time_list = subres1[att].index.to_list()
                for time in time_list:
                    print(att)
                    values_1 = subres1[att].loc[time]
                    values_2 = subres2[att].loc[time]

                    self.check_Two_series_value(values_1, values_2)
            else:
                print(type(subres1[att]), type(subres2[att]))

    #@classmethod
    def check_two_times(self, dataframe_1, dataframe_2):
        time_1 = dataframe_1.index
        time_2 = dataframe_2.index
        self.check_Two_series_value(time_1, time_2)
            #if time_1 != time_2:
                #raise ValueError("two ")


    def check_Two_series_value(self, serie_1, serie_2):
        if not isinstance(serie_1, pd.core.series.Series):
            serie_1 = serie_1.to_series()

        if not isinstance(serie_2, pd.core.series.Series):
            serie_2 = serie_2.to_series()

        self.assertTrue((serie_1 == serie_2).all())

if __name__ == '__main__':
    unittest.main()
