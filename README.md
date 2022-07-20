<h1 align = "center">AutoCOSHH</h1>

<h3>DESCRIPTION</h3>
As a Chemistry undergraduate at Oxford, time is at a premium. AutoCOSHH is a Python application that attempts to eliminate the menial work involved in manually generating COSHH forms. Given a list of chemicals and their respective hazard codes stored in `reference.csv`, AutoCOSHH performs the logic that bridges the gap between a given hazard code and its associated hazards, exposure routes and control measures. These relationships are defined in a local SQL database. The latexmk package is then used to compile a clean-looking COSHH form in the required format (see images below).

</br></br>
<h3>FEATURES</h3>

* Generate hundred-page long COSHH forms in seconds
* Specify mass, concentration, volume and other details in brackets
* Automatates 'Specific Safety or Risk Implication' section
* Large number of commonly used solvents and chemicals already specified
* Easily add missing chemicals and their respective hazard codes to `reference.csv`
* Randomise display order of chemicals

</br>
<h3>MACOS INSTALLATION</h3>

1. Install Python 3 (preferably an Anaconda distribution)
2. Clone repository to local directory `git clone https://github.com/aymannel/autocoshh.git`
3. Create conda environment with required libraries `conda create --name autocoshh --file requirements.txt`
4. Install [MacTeX](https://tug.org/mactex/)
5. Install the `latexmkrc` package using TeX Live Utility
6. Activate conda environment `conda activate autocoshh`
7. Run application `python interface.py`

</br>
<h3>IMAGES</h3>

![projectimage](https://github.com/aymannel/autocoshh/blob/master/img/autocoshh.png?raw=true)
![projectimage](https://github.com/aymannel/autocoshh/blob/master/img/form.png?raw=true)

<hr>
