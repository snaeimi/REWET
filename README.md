# REWET

REstoration of Water after Event Tool (REWET) is a tool for the simulation of functionality in water distribution networks after natural hazard events. It is designed to support any network with the state-of-art hydraulic simulation capabilities and damage modeling in mind.

## Installation
The current release of REWET (V0.15.2) only support Windows AMD64 systems right now. Version for running on Linux and MacOS will be available on the next versions. REWET is also integrated into [NHERI SimCenter R2D tool](https://simcenter.designsafe-ci.org/research-tools/r2dtool/) which supports Windows and MacOS.

### 1. Dependecies and Virtual Enviroment
To install the package, first intall the depencies. Usung a vitual enviroment using [Python virtual enviroment](https://docs.python.org/3/library/venv.html) or [Anaconda](https://www.anaconda.com) is prescribed.

[!NOTE]
We leave making a virual enviroment and activating it to teh users. The links provided above are sufficient for leanring knowhow.


### 2. Install

### 2.1 Downlaod teh code
After activating the virtual enviroment, one can use GIT to clone the REWET's repository by typing the following and change the current directory to the cloned repository:

```bash
git clone https://github.com/snaeimi/REWET.git
cd REWET
```
 or alternatiovely download teh code and unzip teh file from the [project](https://github.com/snaeimi/rewet) Github and change the current directory to the decompressed directory.

### 2.2 Install from Local

Being in REWET's directory, type:

```bash
python -m pip install -e .
```

## Usage

After Installing REWET, you can use the REWET in one of teh ways that is possible. To run REWET, one can import and run REWET in any code:

```python
from rewet import Starter
start = Starter()
start.run()
```

With running code above, you will run the example. However, you may want to run your own network and modify other inputs. To see a list of inputs, you can explore `rewet/input/settings.py`. Any variable in process scenario settings classes can be an input to REWET. REWET accepts JSON formated input with variables in `settings.py` file can be given as input in the json file. You need to overwrite the default variable values in `settings.py` with your own values using teh jsn file and pass the json file path and name when you are runing REWET. For example, let's assume that we want to change the simulation run to 1 day. thus, we will make a json file called `input.json` and fill it with following data:

```json
{
    "RUN_TIME": 86400,
}
```

After saving the file, we will pas the file path to run function (the json file extention must be json or REWET would not recognise it as a json file):

```python
from rewet import Starter
start = Starter()
start.run("input.json")
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

For any pottential collaboratiion, please contact the author.

## Citing

For citation, please contact the author.

## License

No Liciense yet

## ACKNOWLEDGMENTS

This project was funded with National Science Foundation Award No. CMMI-1735483. The Developer also extended gratitude to Los Angeles Department of Water and Power (LADWP) for providing the input and water network which was the testbed for the development of REWET. REWET was produced as part of Doctoral Dissertation at University of Delaware, and is supervised by Doctor Rachel Davidson, Department of Civil and Environmental Engineering, University of Delaware.