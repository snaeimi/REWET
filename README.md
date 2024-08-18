[![Build Status](https://app.travis-ci.com/snaeimi/REWET.svg?token=91urGyEqZhmpDJMxDzye&branch=main)](https://app.travis-ci.com/snaeimi/REWET)

# REWET

REstoration of Water after Event Tool (REWET) is a tool for simulating the functionality of water distribution networks after natural hazard events. It is designed to support any network with state-of-the-art hydraulic simulation capabilities and damage modeling.

# Documentation

REWET's [documentation](https://snaeimi.github.io/REWET) is being devloped and is accessible. Meanwhile, please refer to the [PhD Dissertation](https://udspace.udel.edu/items/c0977c19-7138-4220-aa30-b4de91af084b).

## Installation

The current release of REWET (V0.2.0-Alpha.1) supports Windows, Linux, and MacOS(Excluding M1, M2 and M3 CPUS). The repository version also supports Linux AMD64.

### 1. Dependencies and Virtual Environment

To install the package, first install the dependencies. Using a virtual environment with [Python virtual environment](https://docs.python.org/3/library/venv.html) or [Anaconda](https://www.anaconda.com) is recommended.

> [!NOTE]
> We leave creating and activating a virtual environment to the users. The links provided above are sufficient for learning how to do so.

### 2. Install REWET

For installing REWET, please make sure you have Python installed on your machine. The latest version of the Pyhton that we tested REWET with is 3.9.13. However, you may be able to run REWET with higher version too. We just did not test it! Also, the oldest version of Python that REWET works with is 3.6. Based n your needs, you can choose one of the following methods.

#### 2.1 PyPi

After activating the virtual environment, you can easily install REWET using PyPi. To so so, open the comman prompt/terminal in your machine and type the following:

```bash
pip3 install rewet
```

#### 2.2 Download the Repository

 You can also use GIT to clone REWET's repository and change the current directory to the cloned repository:

```bash
git clone https://github.com/snaeimi/REWET.git
cd REWET
```
Alternatively, download the code and unzip the file from the project GitHub and change the current directory to the decompressed directory.

##### 2.2.1 Install as Users

Being in REWET's directory, type:

```bash
python -m pip install
```

##### 2.2.2 Install as Developers

Being in REWET's directory, type:

```bash
python -m pip install -e .
```

When you install REWET as developer (i.e., using "-e ."), the package is not coppied to where Python usually keeps its packages. This helps you to modify and use the code as you go.

## Usage

After installing REWET, you can use it in several ways. To run REWET, import and run it in any code:

```python
from rewet.initial import Starter
start = Starter()
start.run()
```

Running the code above will execute the example. However, you may want to run your own network and modify other inputs. To see a list of inputs, you can explore rewet/input/settings.py. Any variable in the process scenario settings classes can be an input to REWET. REWET accepts JSON formatted input with variables from the settings.py file. You need to overwrite the default variable values in settings.py with your own values using a JSON file and pass the JSON file path and name when you run REWET. For example, let's assume we want to change the simulation run to 1 day. We will make a JSON file called input.json and fill it with the following data:

```json
{
    "RUN_TIME": 86400,
}
```

After saving the file, we will pass the file path to the run function (the JSON file extension must be .json or REWET will not recognize it as a JSON file):

```python
from rewet.initial import Starter
start = Starter()
start.run("input.json")
```

## Contributtiom

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

For any potential collaboration, please contact the author.

## Citation

When you use REWET, please cite REWET as follows:

Sina Naeimi, Rachel A. Davidson. Forthcoming. "REWET: A Tool to Model System Function and Restoration of Damaged Water Supply Systems." [Forthcomming] *ASCE Journal of Infrastructure Systems*. 10.1061/JITSE4/ISENG-2427

## License
REWET is released under the MIT license. See [LICENSE](https://github.com/snaeimi/REWET/blob/main/LICENSE) for more details.

* **WNTR License:** is distributed under the MIT License. Please refer to the WNTR [license file](https://github.com/USEPA/WNTR/blob/main/LICENSE.md) for more information.
* **EPANET License:** EPANET is distributed under the Public Domain. Please refer to the EPANET [license file](https://raw.githubusercontent.com/USEPA/EPANET2.2/master/SRC_engines/LICENSE) for more information.

# News

REWET has been adapted in NHERI SimCenter's **R2DTool V4.2 [[1]](#1)**.

## ACKNOWLEDGMENTS

This project was funded by National Science Foundation Award No. CMMI-1735483. The developer also extends gratitude to the Los Angeles Department of Water and Power (LADWP) for providing the input and water network, which served as the testbed for the development of REWET. REWET was produced as part of a Doctoral Dissertation at the University of Delaware, supervised by Dr. Rachel Davidson, Department of Civil and Environmental Engineering, University of Delaware.

This project uses the following tools:
* **Water Network Tool for Resilience (WNTR) [[2]](#2)** developed by the U.S. Environmental Protection Agency. WNTR is a Python package designed for analyzing the resilience of water distribution networks. For more information about WNTR, visit the official WNTR [documentation](https://usepa.github.io/WNTR/).
* **EPANET [[3]](#3)** Developed by the U.S. Environmental Protection Agency, EPANET is a software application used throughout the world to model water distribution piping systems. For more information about EPANET, visit the official EPANET [documentation](https://www.epa.gov/water-research/epanet)

![image](doc/_static/UD_NSF_Logo.jpg)
## References
<a id="1">[1]</a>
Frank McKenna, Stevan Gavrilovic, Jinyan Zhao, Kuanshi Zhong, Adam Zsarnoczay, Barbaros Cetiner, Sang-ri Yi, Aakash Bangalore Satish, Sina Naeimi, & Pedro Arduino. (2024). NHERI-SimCenter/R2DTool: Version 4.2.0 (v4.2.0). Zenodo. https://doi.org/10.5281/zenodo.11175489

<a id="2">[2]</a>
Klise, K.A., Hart, D.B., Bynum, M., Hogge, J., Haxton, T., Murray, R., Burkhardt, J. (2020). Water Network Tool for Resilience (WNTR) User Manual: Version 0.2.3. U.S. EPA Office of Research and Development, Washington, DC, EPA/600/R-20/185, 82p.

<a id="3">[3]</a>
Rossman, L., H. Woo, M. Tryby, F. Shang, R. Janke, AND T. Haxton. EPANET 2.2 User Manual. U.S. Environmental Protection Agency, Washington, DC, EPA/600/R-20/133, 2020.



