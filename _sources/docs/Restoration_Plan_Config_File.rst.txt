=================
Restoration Plan
=================


The restoration plan may be defined using sectiosn and directives. Sections includes:

* **[Files]** Files that are in tabulaetd data in it are storedin it.
* **[Sequences]** Defiens sequence of `Actions` that must be done for a damage of an element type, so that damage type is cosnidered restored.
* **[Damaege_Group]** Defiens damages groups made from elements and tehir damage types. 
* **[Crews]** Crew data is defiend in this section.
* **[POINTS]** geographical point groups can be created in thsi sections.
* **[PRIORITIES]** restration pririties are defined here.
* **[JOBS]** Jobs definition are made in this section.
* **[DEFINE]** Job Effect definition is defined here.
* **[Group]** Groups are defien in thsi section.

Files
*****

Files are usedin other sections. Each file is defiend by its name and path. The structure of teh files are as follows
.. code-block::

    <File handle> <File path>

in which `<file handle>` is the handle used in other sections and the `<file path>` is the relational or absolute path 
of the file. The relative path is relative to teh restoration plan config file.  

Sequences
*********

Each element is water distribution network (e.g., pipe, node, tanks, and pump) needs to have a series of `Action` so that 
teh damage location is considerd restored. Each `Action` is a arbitary Action which later used in defining the restioration 
`Priority`. 

The format of the Sequence is as follows:::

    <Element Type> <Action 1> ... <Action n>
    
.. note::
    ELement types include:

    * `PIPE`,
    * `TANK`,
    * `PUMP`, and
    * `NODE`.

    Please note that the element types are used in capital form.

An Example of a sequnce list of actions is as follows:::

   PIPE   drain   repair   repressurize

On this exampel you can define drain, repair and repressurize according to your network's and utilities capacity, 
requirements and starndard operation proceddures.

Damage Groups
*************

teh user may create oen or more `damage groups`. A damage group is a group damage location of the same `element type` with 
or without other attribute of the element the damage happens on. For instance, a damage group can be damage locations that 
happen on a pipe (i.e., `element type==PIPE`) in which pipe has a diameter equal or bigger than 0.5 m (i.e., diameter>=0.5).
The user can create such damage groups according to their network's and utilities capacity, requirements and 
starndard operation proceddures. Such damage groups are later used on `Priorities` definition alonside `Actions`.

The structure format of the damage groups are as follows:::
   
   <Damaeg Group Name>   <Element Type>   <Attribute>   <CONDITION 1>
                               .
                               .
                               .
   <Damaeg Group Name>   <Element Type>   <Attribute>   <CONDITION N>

.. note::

    each line of adde condition connotes logical `AND`.

Conditon
---------

In REWET a condition is created with three values each sepearetd with one colon (i.e., "`:`"). The values are follows:::
   
   <Attribute>:<Condition>:<Condition Value>

Attributes are as in the following table:

.. table:: Attributes in Damage Group
   :widths: auto
   :align: center

   +------------+-----------------+-------------------------------------------------+
   |Element Type| Attributes      |   Description                                   |
   +============+=================+=================================================+
   |PIPE        |DIAMETER         | Diameter of teh pipe                            |
   |            |                 |                                                 |
   |            |FILE             | Names of the element specified in ths file.     |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the element not specified in the file. |
   +------------+-----------------+-------------------------------------------------+
   |            |Number_of_damages| Numebr of damages                               |
   |            |                 |                                                 |
   |NODE        |FILE             | Names of the element specified in ths file.     |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the element not specified in the file. |
   +------------+-----------------+-------------------------------------------------+
   |TANK        |FILE             | Names of the element specified in ths file.     |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the element not specified in the file. |
   +------------+-----------------+-------------------------------------------------+
   |PUMP        |FILE             | Names of the element specified in ths file.     |
   |            |                 |                                                 |
   |            |NOT_IN_FILE      | Names of the element not specified in the file. |
   +------------+-----------------+-------------------------------------------------+

Applicable Conditons are:
* EQ: equal,
* BT: bigger than,
* LT: less than,
* BE: bigger than or equal to,
* LE: less than or equal to,

.. note::

    When File and NOT_IN_FILE are teh attributes, teh conditions can only be EQ, NE amnd teh values can be a file handle.

For the excamples above the Conditon will be:::
   
   a_name   PIPE   DIAMETER:BE:0.5


