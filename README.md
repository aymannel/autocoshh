# AutoCOSHH

## DESCRIPTION
AutoCOSHH is a Python application that attempts to eliminate the menial work involved in manually generating COSHH forms. Given a list of chemicals and their respective hazard codes, AutoCOSHH performs the logic that relates a given hazard code to its associated hazards, exposure routes and control measures. These relationships are defined in a local SQL database. The latexmk package is then used to compile a clean COSHH form in the required format (see images below).


## FEATURES

* Generate hundred-page long COSHH forms in seconds
* Specify mass, concentration, volume and other details after '\\'
* Automatates 'Specific Safety or Risk Implication' section
* Large number of commonly used solvents and chemicals already specified
* Easily add missing chemicals and their respective hazard codes to `reference.csv`
* Randomise display order of chemicals


## MACOS INSTALLATION

1. Install Python 3 (preferably an Anaconda distribution)
2. Clone repository to local directory `git clone https://github.com/aymannel/autocoshh.git`
3. Create conda environment with required libraries `conda create --name autocoshh --file requirements.txt`
4. Install [MacTeX](https://tug.org/mactex/)
5. Install the `latexmkrc` package using TeX Live Utility
6. Activate conda environment `conda activate autocoshh`
7. Run application `python interface.py`

## MORE ON THIS PROJECT
Writing AutoCOSHH has been a learning experience for me, allowing me to create a program that makes use of Python's Object Oriented Programming capabilities, understand how to connect to and manipulate an SQL database and more. Below are some features that I learned the most from upon implementing.

* `map()` and `filter()` functions allowed more natural flow of code
* Integrated SQL database
* Integrated LaTeX
* Each COSHH form represents COSHHForm() object that is manipulated by main AutoCOSHH() object


## IMAGES

![projectimage](img/autocoshh.png?raw=true)
![projectimage](img/form.png?raw=true)
