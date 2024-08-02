Install
#######

Virtual Environment
*******************

It's a good practice to install REWTe and its depencies in a cirtal enviroment. Because it is not necessary, this not explained here. The user can user 
can create a `virtual enviroment<https://docs.python.org/3/library/venv.html>`.

1. Using PyPi
***************
For installing REWET, the easiest way is to install using PyPi.

.. code-block:: bash

    pypi install rewet

2. Local Install 
****************
If you inted to install rewet locally, specificially for devlopment purposes, you can do so with cloning REWET's git repository and tehn installing the package.
To clone the repo, please type teh following in a git-enabled console/terminal.

.. code-block:: bash

    git clone https://github.com/snaeimi/REWET.git

Alternativey you can download the repo's `zip file<https://github.com/snaeimi/REWET/archive/refs/heads/main.zip>` and extract it.

Either way, you will need to navigate to the REWTE's root directory and install the package.

For installing from a local repo **(NOT in devloper mode)**, type the following in your desired python enviroment:

.. tabs::

   .. tab:: Windows
      .. code-block:: bash
	  
         python -m pip install .
   
   .. tab:: Linux
   
      .. code-block:: bash
	  
         python3 -m pip install .

   .. tab:: MacOS
   
      .. code-block:: bash
	  
         python3 -m pip install .

if you want to to install REWET in the **devloper mode**, type the following in your desired python enviroment:\

.. tabs::

   .. tab:: Windows
   
      .. code-block:: bash
	  
         python -m pip install -e .
   
   .. tab:: Linux
   
      .. code-block:: bash
	  
         python3 -m pip install -e .

   .. tab:: MacOS
   
      .. code-block:: bash
	  
         python3 -m pip install -e .

.. note::
    In devloper mode, the package source file are not copied into python site packages directory; 
    thus, any cxhanges in the python codes is applied when running REWET.

3. Test Installation
********************


.. tabs::

   .. tab:: Windows
      .. code-block:: bash
	  
         python -m rewet.test.DefaultSettings
   
   .. tab:: Linux
   
      .. code-block:: bash
	  
         python3 -m pip install -e .

   .. tab:: MacOS
      .. code-block:: bash
	  
         python3 -m rewet.test.DefaultSettings
