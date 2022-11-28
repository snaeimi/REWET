# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 18:29:50 2022

@author: snaeimi
"""

from PyQt5 import QtWidgets
import pandas as pd

single_scenario_curve_options = ['Quantity', 'Delivery', 'SSI']
multi_scenario_curve_options = ['Quantity Exceedance', 'Delivery Exceedance']

class Result_Designer():
    def __init__(self):
        
        self.main_tab.currentChanged.connect(self.tabChanged)
        self.all_scenarios_checkbox.stateChanged.connect(self.AllScenarioCheckboxChanged)
        self.save_curve_button.clicked.connect(self.saveCurrentCurveByButton)
        self.scenario_combo.currentTextChanged.connect(self.resultScenarioChanged)
        self.curve_type_combo.currentTextChanged.connect(self.curveTypeChanegd)
        
        self.initalize_result()
    
    def initalize_result(self):
        self.setAllScenarios(True)
        self.all_scenarios_checkbox.setChecked(True)
        self.scenario_combo.addItems(self.scenario_list['Scenario Name'])
        self.current_curve_data = None
        
    def AllScenarioCheckboxChanged(self, state):
        if state == 0:
            self.setAllScenarios(False)
        elif state == 2:
            self.setAllScenarios(True)
    
    def clearCurvePlot(self):
        self.mpl_curve.canvas.ax.cla()
        
    def plot_data(self):
        x=range(0, 10)
        y=range(0, 20, 2)
        self.mpl_curve.canvas.ax.plot(x, y)
        self.mpl_curve.canvas.draw()
        
    def setAllScenarios(self, flag):
        if flag == True:
            self.all_scenarios_checkbox.setChecked(True)
            self.scenario_combo.setEnabled(False)
            self.curve_type_combo.clear()
            self.curve_type_combo.addItems(multi_scenario_curve_options)
            self.clearCurvePlot()
        elif flag == False:
            self.all_scenarios_checkbox.setChecked(False)
            self.scenario_combo.setEnabled(True)
            self.curve_type_combo.clear()
            self.curve_type_combo.addItems(single_scenario_curve_options)
            self.clearCurvePlot()
        else:
            raise ValueError("Unknown flag: " + repr(flag))
    
    def resultScenarioChanged(self, text):
        self.result_current_scenario = text #self.scenario_combo.getText()
        self.current_curve_data = None
    
    def curveTypeChanegd(self, text):
        curve_type = text #self.curve_type_combo.getText()
        if curve_type == 'Quantity Exceedance':
            self.current_curve_data = (curve_type, pd.DataFrame())
            self.plot_data()
        elif curve_type == 'Delivery Exceedance':
            self.current_curve_data = (curve_type, pd.DataFrame())
            self.plot_data()
        elif curve_type == 'Quantity':
            self.current_curve_data = (curve_type, pd.DataFrame())
            self.plot_data()
        elif curve_type == 'Delivery':
            self.current_curve_data = (curve_type, pd.DataFrame())
            self.plot_data()
        elif curve_type == 'SSI':
            self.current_curve_data = (curve_type, pd.DataFrame())
            self.plot_data()
        
            
    
    def tabChanged(self, index):
        if index == 1:
            self.initalize_result()
    
    def saveCurrentCurveByButton(self):
        if self.current_curve_data == None:
            self.errorMSG("REWET", 'No curve is ploted')
            return
        
        file_addr = QtWidgets.QFileDialog.getSaveFileName(self.asli_MainWindow, 'Save File', 
                                                     self.project_file_addr,"Excel Workbook (*.xlsx)")
        if file_addr[0] == '':
            return
        
        self.current_curve_data[1].to_excel(file_addr[0])
        