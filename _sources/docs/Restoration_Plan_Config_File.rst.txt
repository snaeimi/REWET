Restoration Plan
=================


The restoration plan may be defined using sectiosn and directives. Sections includes:

* **[Files]** Files that are in tabulated data are stored in this section.
* **[Sequences]** Defines a sequence of `Actions` that must be done for a damage of an element type so that the damage type is considered restored.
* **[Damage_Group]** Defines damage groups made from elements and their damage types.
* **[Crews]** Crew data is defined in this section.
* **[Zone]** Zones are defined in this section.
* **[POINTS]** Geographical point groups can be created in this section.
* **[PRIORITIES]** Restoration priorities are defined here.
* **[JOBS]** Job definitions are made in this section.
* **[DEFINE]** Job Effect definitions are defined here.

Files
*****

Files are used in other sections. Each file is defined by its name and path. The structure of the files is as follows:
.. code-block::

    <File handle> <File path>

In which `<file handle>` is the handle used in other sections, and the `<file path>` is the relative or absolute path 
of the file. The relative path is relative to the restoration plan config file.

Sequences
*********

Each element in the water distribution network (e.g., pipe, node, tanks, and pump) needs to have a series of `Actions` so that 
the damage location is considered restored. Each `Action` is an arbitrary action, which is later used in defining the restoration 
`Priority`.

The format of the Sequence is as follows::

    <Element Type> <Action 1> ... <Action n>
    
.. note::
    Element types include:

    * `PIPE`,
    * `TANK`,
    * `PUMP`, and
    * `NODE`.

    Please note that the element types are used in capital form.

An example of a sequence list of actions is as follows::

   PIPE   drain   repair   repressurize

For this example, you can define drain, repair, and repressurize according to your network's and utilities' capacity, 
requirements, and standard operating procedures.

Damage Groups
*************

The user may create one or more `damage groups`. A damage group is a group of damage locations of the same `element type` with 
or without other attributes of the element where the damage occurs. For instance, a damage group can be damage locations that 
occur on a pipe (i.e., `element type==PIPE`) in which the pipe has a diameter equal to or greater than 0.5 m (i.e., diameter>=0.5).
The user can create such damage groups according to their network's and utilities' capacity, requirements, and 
standard operating procedures. Such damage groups are later used in `Priorities` definition alongside `Actions`.

The structure format of the damage groups is as follows::
   
   <Damage Group Name>   <Element Type>   <Attribute>   <CONDITION 1>
                               .
                               .
                               .
   <Damage Group Name>   <Element Type>   <Attribute>   <CONDITION N>

.. note::

    Each line of added condition connotes logical `AND`.

Condition
---------

In REWET, a condition is created with three values each separated by a colon (i.e., "`:`"). The values are as follows::
   
   <Attribute>:<Condition>:<Condition Value>

Attributes are as listed in the following table:

.. table:: Attributes in Damage Group
   :widths: auto
   :align: center

   +------------+-----------------+-------------------------------------------------+
   |Element Type| Attributes      |   Description                                   |
   +============+=================+=================================================+
   |PIPE        |DIAMETER         | Diameter of the pipe                            |
   |            |                 |                                                 |
   |            |FILE             | Names of the elements specified in this file.   |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the elements not specified in the file.|
   +------------+-----------------+-------------------------------------------------+
   |            |Number_of_damages| Number of damages                               |
   |            |                 |                                                 |
   |NODE        |FILE             | Names of the elements specified in this file.   |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the elements not specified in the file.|
   +------------+-----------------+-------------------------------------------------+
   |TANK        |FILE             | Names of the elements specified in this file.   |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the elements not specified in the file.|
   +------------+-----------------+-------------------------------------------------+
   |PUMP        |FILE             | Names of the elements specified in this file.   |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the elements not specified in the file.|
   +------------+-----------------+-------------------------------------------------+

Applicable Conditions are:
* EQ: equal,
* BT: bigger than,
* LT: less than,
* BE: bigger than or equal to,
* LE: less than or equal to,

.. note::

    When File and NOT_IN_FILE are the attributes, the conditions can only be EQ or NE, and the values can be a file handle.

For the examples above, the Condition will be::
   
   a_name   PIPE   DIAMETER:BE:0.5

Crews
*****

Crews are defined as the number of crews for each shift and their base location. Because this data is tabular, you define
such data in files in a tabular format and then just use the file handle after the crew's name. The format of defining crews is::

    <Crew Name>   File   <File Handle>   <Zone Name:Column Identifier>

.. note::

    *Zone Name* is optional. If in the Zone section, we define zones for elements, then we have to define zones for crews
    too. Otherwise, crews will never be assigned to those elements (or some elements), and those elements will never be restored.

The column identifier is the Zone-Name column's identifier in the crew tabular data file.


In the file represented by <File Handle>, the following information must be given:
    
.. table:: Attributes in Damage Group
    :widths: auto
    :align: center

    +------------+-----------------+-------------+-------------+-------------------------------------+
    |Home-X-Coord| Home-Y-Coord    | Number      |     Shift   |      Zone-Name column identifier    |   
    +============+=================+=============+=============+=====================================+
    |   <X>      |      <Y>        |  <N>        |  Shift Name |        <Zone-Name>                  |
    +------------+-----------------+-------------+-------------+-------------------------------------+

.. note::

    The table above is a comma-delimited table. The columns and data are separated by commas.

.. note::

    *Zone Name* is optional. If in the Zone section, we define zones for elements, then we have to define zones for crews
    too. Otherwise, crews will never be assigned to those elements (or some elements), and those elements will never be restored.

There can be multiple crews of the same type in one file (i.e., different numbers and different shifts). If the
crews are grouped into zones, then the user may provide <Zone-Name>.

Zone (Group)
************

When you want to assign the crews to a group of elements (most likely based on their geographical location),
you can do so using the Zone (AKA grouping) feature. In this way, each zone (aka group) is defined in one line as follows::

    <ZONE Name>   <Element Type>   FILE   <File Handle>   <ELEMENT Column Identifier>   <Zone-Name Column Identifier>

When you define a zone, you give a name to the zone, the element type that the zone is related to, and after
FILE, you give the file handle of the file that contains the zone data. The two last arguments are the elements' and 
zone-name column identifiers in the file that is represented by the file handle.

POINTS
******

You can define groups of geographical points in this section. The format of defining points is as follows:::

    <Point-Group Name>   <X Coordinate>:<Y Coordinate>   ...   <X Coordinate>:<Y Coordinate>

In the above format, the X and Y coordinates are separated by a colon (i.e., `:`). Each point's coordinates are separated by a space.

You can use the point group in priorities as a **secondary priority**. Such points can be representative of (but not limited to)
focal points, water sources, important establishments, etc.

PRIORITIES
**********

Priorities are defined in this section. Each priority is defined by a name, a damage group, a sequence, and a crew.
There are two sorts of priorities: `Primary` and `Secondary`. The *Primary* priorities are the main priorities showing a job,
which is a combination of *Actions* that is happening on a damage location belonging to a *Damage Group*. The *Secondary*, however, 
defines which damage location should be worked on within the *Primary* priority. A priority is a list of primary and secondary
priorities.

The format of defining priorities is as follows::

    <Crew>   <ACTION>:<Damage Group>   ...   <ACTION>:<Damage Group>
    <CREW>   <SECONDARY PRIORITY>      ...   <SECONDARY PRIORITY>

.. note::

    The Secondary priorities are either a point group name that is defined before or one of the built-in secondary priorities.
    The built-in secondary priorities are:
	
    * **HYD_SIG**: The hydraulic significance of the element.	
    * **Shortest Distance** [FUTURE],
    * **Minimum Damages** [FUTURE],
    * **Largest Diameter** [FUTURE],
    * **Smallest Diameter** [FUTURE], and
    * **Crew Base** [FUTURE].
	
For instance, if a point group has been defined before as ‘P_Group’, then the following is an example of such a priority definition:

.. code-block::
    
   Crew_A    REPAIR:all_critical_pipes  
   Crew_A    P_Group

    Restoration Crew A  REPAIR:al

JOBS
****

Jobs are defined in this section. Each job is specified by a crew name, the job (defined as a primary priority), the time it takes, and its effect on the system once the job is completed. The format for defining jobs is as follows:::

    <CREW>   <ACTION>:<DAMAGE GROUP> FIX:<TIME>   <EFFECT NAME>

.. note::
    Currently, all time values defined in REWET are a fixed time in seconds. Thus, the text "FIX" must always be used in this manner.

The effect name is defined in the `DEFINE` section, which is essentially a list of *Basic Effects*.

.. note::
    *INSPECT* is a *Basic Effect*. However, you can use *INSPECT* instead of EFFECTS. In this way, you will not have to define an EFFECT solely for *INSPECT*. Nevertheless, you can do that as well. The purpose of this exemption is to make it easier for the user to use *INSPECT* when the result of the job is only *INSPECT*.

DEFINE
******

In this section, you define the effects of the jobs. An EFFECT can consist of one or more effects. The format for defining effects is as follows::

   <Effect Name>	<Method no.>  <Basic Effect 1> ... <Basic Effect n>

Basic Effects are as follows:

.. table:: Attributes in Damage Group
    :widths: auto
    :align: center

    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Basic Effect   | Definition                                                                                                                                                                                                                                                                                                                                                                                                                    |
    +================+===============================================================================================================================================================================================================================================================================================================================================================================================================================+
    | INSPECT        | Keeps the crew busy for the job duration but has no effect on the network. It can be used for any task where this applies. When applied to a demand node, it records the flow to determine if it should be isolated.                                                                                                                                                                                                          |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | STOP_LEAK      | Removes extra pipe and reservoir that were added to represent the leak and closes the downstream pipe. This prevents water from flowing out of the pipe through a leak but does not allow it to continue downstream to its original destination either.                                                                                                                                                                       |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | COMPLETE_BYPASS| Bypasses multiple damage locations by adding a new pipe from one end of a pipe segment to the other. The user may specify the diameter and pipe friction for the new pipe to reflect the nature of the bypass (by default, values associated with the original pipe are used). Alternatively, the user may specify a fraction of the diameter of the original pipe instead of explicitly specifying the bypass pipe.          |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | LOCAL_BYPASS   | Similar to a complete pipe bypass, but for a single damage location.                                                                                                                                                                                                                                                                                                                                                          |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ADD_RESERVOIR  | Represents a connection to a supplemental water source. Adds a reservoir to both sides of a pipe damage location, each with a check valve allowing water to flow only from the reservoirs to the pipe. The user may specify the height of each reservoir relative to the node it is attached to (default is zero), and/or include a pump to reflect the nature of the water source.                                           |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ISOLATE_NODE   | Closes the extra pipe that was added to represent damage to a demand node. Represents the isolation of demand nodes to stop water loss if there is excessive demand node damage at the time of inspection, where “excessive” is based on a user-specified ratio of post-damage to pre-event damage (default is three).                                                                                                        |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | REPAIR         | Returns the element to its original state.                                                                                                                                                                                                                                                                                                                                                                                    |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | SKIP           | No job is assigned, and the action in the sequence of the elements will be skipped. This basic effect is used after the conditional basic effect to instruct REWET that the job is assigned only if certain conditions hold.                                                                                                                                                                                                  |
    +----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Method
------

There can be multiple effects in different methods. REWET checks each method in the order defined in the effect definition, and if the method can be applied, the the method is run. Effect-method number starts from 1.  in the job definition. REWET uses a probability-based method. Let's explain it using an example. For example, if you want to repair pipes based on their material (materials M1 and M2), and for Pipe M1 you only want to inspect because you cannot repair it, while for M2, you want to first inspect and then stop the leak, you can do the following: 

You know the names of all pipes in the input file and their materials, so you create a small CSV file with the element ID (pipe names) and the method applicable to each pipe: 1 for M1 and 2 for M2. Since there is only one method for each material, you define the probability as 1 for each of those methods. The CSV file will look something like this:

    Pipe-Name,Method,Probability
    Pipe-1,1,1
    Pipe-2,2,1
    Pipe-3,2,1
    Pipe-4,1,1
    Pipe-5,2,1

Then, in the [DEFINE] section, you specify that for a specific <effect name>, the method information is provided in the file. The format of the definition is as follows:

    
    <Effect Name>	FILE  <FILE HANDLE>   ELEMENT_NAME:<Element-ID Column Identifier>   METHOD_NAME:<Method Column Identifier> METHOD_PROBABILITY:<Probability Column Identifier>

For our example, assuming the CSV file is defined with a handle called method_file, the definition will be as follows:::

    Pipe_job   FILE   method_file   ELEMENT_NAME:Pipe-Name   METHOD_NAME:Method   METHOD_PROBABILITY:Probability

Then, of course, you have to define the effect in the [DEFINE] section. The definition will be as follows:

    Pipe_job 1 INSPECT
    Pipe_job 2 INSPECT STOP_LEAK

Now, let's make the example a little more complicated. Let's say that for M2, half of the time you cannot stop the leak. In this case, you let REWET know that there is a 50% chance for selecting the method for M2 only. To do this, you add a line for all M2 pipes (i.e., Pipe-2, Pipe-3, and Pipe-5) in the method file. The file will look like this:::
    
    Pipe-Name,Method,Probability
    Pipe-1,1,1
    Pipe-2,2,0.5
    Pipe-2,2,0.5
    Pipe-3,2,0.5
    Pipe-3,2,0.5
    Pipe-4,1,1
    Pipe-5,2,0.5
    Pipe-5,2,0.5

Now, what if each method is going to take a different amount of time? In this case, you can override the time value that you defined for the job, even based on the element ID value (for example, longer pipes may take longer time). To do this, you can define the override command as follows:::

    <Effect Name>	FILE  <FILE HANDLE>   ELEMENT_NAME:<Element-ID Column Identifier>   METHOD_NAME:<Method Column Identifier> METHOD_PROBABILITY:<Probability Column Identifier>   FIXED_TIME_OVERWRITE:<Time-override column identifier>

