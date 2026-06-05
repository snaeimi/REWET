Inputs
#######

.. Warning:: REWET is under continuous development, which means that:
    1. The names of the input parameters may change.
    2. New methods of inputting data may be provided in the future.
    3. Some input data may be added or removed.

Therefore, please refer to the documentation for the specific version you are using.

There are many inputs in REWET that you need to provide for it to run properly. In this section, we will go through them. However, an example project is set as the default values. As a result, you can browse the input values and learn what each variable does after reading this document.

Overview
========

To run REWET, you need to define:

1. **Scenario Data**: Scenario data mostly consist of damage data. In other words, users usually have different damage data for each scenario than other data such as hydraulic solver parameters. These data are defined in the scenario table. Each row in the scenario table defines:
    1. Scenario name,
    2. Pipe damage data name,
    3. Node-level damage data name,
    4. Pump damage data name,
    5. Tank damage data name,
    6. Probability (Optional. Required if you want to post-process a set of probabilistic scenarios using REWET).

    Each row can also have other scenario parameter data through parameter override. For more information on scenario table, :ref:`Click Here<Scenario Table>`.

2. **Water Distribution Network**: REWET needs to know the specifications of the water distribution network. Thus, an INP file must be provided.

3. **Restoration Plan**: The restoration plan defines the crews, jobs, priorities, and set of effects on the network after the effect.

4. **Pipe and Node-level Damage Modeling**.

5. **Pipe, Node-level, Pump, Tank, General-node, and Reservoir Damage Discovery Model**.

The data required to run REWET's simulation enables the user to control all parts of the hydraulic, damage, and restoration simulation. While the amount of data required for running REWET may seem excessive, the simplicity and intuitiveness of the data help the user to learn how to use it proficiently. If you are not sure about parameters that require technical skills, in most cases, you can simply leave the data to their default values provided in REWET.

Input Settings
==============

Input settings are the main data input point in REWET. All input data are either defined in the input settings data or in files whose locations are given in the input settings. There are two kinds of inputs:

1. **Process Settings**: These are parameters that apply to all simulation scenarios. For instance, the time of the whole simulation for all scenarios is deemed to be the same. So, it is a process setting.

2. **Scenario Settings**: These are parameters that are specific to each scenario. You can define them for all scenarios as well. However, if you want to change the scenario-setting values, you can override those values in the scenarios table. In this way, you can easily change scenario-setting inputs.

The list of process and scenario settings parameters are as follows:

.. csv-table:: REWET Process Setting Inputs
   :file: /docs/tables/REWET_Process_Settings.csv
   :header-rows: 1
   :widths: auto
   :align: center

.. csv-table:: REWET Scenario Setting Inputs
   :file: /docs/tables/REWET_Scenario_Settings.csv
   :header-rows: 1
   :widths: auto
   :align: center

.. tip:: Please make sure to check the :ref:`Units and Tips<Units and Tips>` about input.

How to provide input
--------------------

You can create a REWET input settings using a JSON formatted file. For example, if you want to change the runtime of the simulation, all you need to do is set `RUN_TIME` to your desired time.

.. code-block:: JSON

    {
        "RUN_TIME": 36000
    }

After saving the file in a proper location, you can pass the path to the file's location to REWET by running:

.. code-block:: python

    from rewet.initial import Starter
    
    json_file_location = "./input.json"
    starter = Starter()
    starter.run(json_file_location)

REWET reads and overrides the values that are provided in the JSON file. In this way, when you are not sure about parameters (let's say hydraulic damage model), you can safely ignore those parameters.

Scenario Table
--------------

The scenario table is an Excel file (or Pandas DataFrame pickled into a binary file). The table is as follows:

.. csv-table:: An Example of Scenario Table
   :file: /docs/tables/example_scenario_table.csv
   :header-rows: 1
   :widths: auto
   :align: center

Scenario name is the scenario name. Pipe, node-level, pump, and tank damage data are the respective file names for the element type damages.

.. important:: All damage files must be in one directory! However, there is no necessity to keep the scenario table location in the same place as the damage files. For example, let's say we have input data in the following structure:

    - input_data
        - scenario_table.xlsx
        - damage_files
            - Net3-pipe-damage.xlsx
            - Net3-node-damage.xlsx
            - Net3-Pump-Damage.xlsx
            - Net3-tank-damage.xlsx

    Then by setting ``pipe_damage_file_list`` to ``./input_data/scenario_table.xlsx`` and 
    ``pipe_damage_file_directory`` to ``./input_data/damage_files``, REWET will look at the right places for the scenario table and damage files, whose names have been defined in the scenario table.

Pipe Damage Data
----------------

Pipe damage data is a table in which each row defines a single damage location. There can be mutiple damage in mutiple locations. The tables are saved in excel or Pandas DataFrame pickled into a binary file. An example of such table is as follows:

.. csv-table:: Pipe Damage Data
   :file: /docs/tables/pipe_damage_data.csv
   :header-rows: 1
   :widths: auto
   :align: center

In the table above, `time` defines the time when the pipe damage occurs, `pipe_id` is the damaged pipe ID in the **.inp** file which you provide in the input settings. `Damage_loc` is a number between 0 and 1 (not 0 or 1), showing the relative location of the damage to the beginning of the pipe. The beginning of the pipe is the first node with which the pipe is defined in the **.inp** file. The type of damage can be either **leak** or **break**. `Material` shows the pipe material. The material defines which pipe damage model is used.

Node-level Damage Data
----------------------

Node-level damage data is a table in which each row definss a damage location (a damaged demand node). An example of such table is as follows:

.. csv-table:: Node-level Damage Data
   :file: /docs/tables/node_damage_data.csv
   :header-rows: 1
   :widths: auto
   :align: center

In the table above, `time` defines the time when the node-level damage occurs, `node_id` is thw damaged demand ndoes ID in the **.inp** file which you provide in the input settings. `Number_of_damages` shows how many damages happened in the node-level damage location and
`node_Pipe_Length` defiens what is teh total length of pipes in the damage location.

Pump Damage Data
----------------

Pipe damage data is a table in which a each row defiens a damaged pump. The tables are saved in excel or Pandas DataFrame pickled into a binary file. An example of such table is as follows:

.. csv-table:: Pump Damage Data
   :file: /docs/tables/Net3-pump-damage.csv
   :header-rows: 1
   :widths: auto
   :align: center

In the table above, `time` defines the time when the pump damage occurs, `pump_id` is teh dmaged pump ID in the **.inp** file which you provide in the input settings, and `Restore_time` is the time when the pump is restored.

tank Damage Data
----------------

Tank damage data is a table in which a each row defiens a damaged tank. The tables are saved in excel or Pandas DataFrame pickled into a binary file. An example of such table is as follows:

.. csv-table:: Pump Damage Data
   :file: /docs/tables/Net3_tank_damage.csv
   :header-rows: 1
   :widths: auto
   :align: center

In the table above, `time` defines the time when the tank damage occurs, `tank_id` is teh dmaged pump ID in the **.inp** file which you provide in the input settings, and `Restore_time` is the time when the pump is restored.

Units and Tips
==============

Units
-----

Units used in REWET are SI units. Even units such as time are in seconds. This may lead to big and unintuitive numbers, especially when you are working with the results, but for a Python programmer, converting units should not be a difficult task, so we left that to the users.

Paths
-----

It's best practice to provide paths as absolute values. Absolute paths are such as ``"C:Users/[username]/Desktop/bluh_bluh.ext"`` in Windows and ``/user/bluh_bluh.ext`` in Linux/MacOS systems. You are absolutely free to use relative paths as well. Relative paths are such as ``"./my_project/bluh_bluh.ext"``. If you are using a relative path, please make sure that the path is relative to the current Python working directory.

Power Users
===========

The Settings module is the interface between the Input and Registry modules. One of the data that the Input module creates is an object of Settings, and then it is passed to the Registry module. Users who feel comfortable coding in Python may find it easier to modify the `setting.py` file directly instead of providing the input through REWET's input mechanism.
