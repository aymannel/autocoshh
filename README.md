<h1 align = "center">AutoCOSHH</h1>

<h3>DESCRIPTION</h3>
As a Chemistry undergraduate at Oxford, time is at a premium. AutoCOSHH is a Python application that attempts to eliminate the menial work involved in manually generating COSHH forms. Given a list of chemicals and their respective hazard codes stored in `reference.csv`, AutoCOSHH performs the logic that bridges the gap between a given hazard code and its associated hazards, exposure routes and control measures. These relationships are defined in a local SQL database. The latexmk package is then used to compile a clean-looking COSHH form in the required format (see images below).

</br></br>
<h3>FEATURES</h3>
<ul> 
    <li>Generate hundred-page long COSHH forms in seconds</li>
    <li>Specify mass, concentration, volume and other details in brackets</li>
    <li>Automatates 'Specific Safety or Risk Implication' section</li>
    <li>Large number of commonly used solvents and chemicals already specified in `reference.csv` </li>
    <li>Easily add missing chemicals and their respective hazard codes to `reference.csv`</li>
    <li>Randomise display order of chemicals</li>
</ul>

</br>
<h3>MACOS INSTALLATION</h3>
<ol> 
    <li>Install Python 3 (preferably an Anaconda distribution)</li>
    <li>Clone repository to local directory</li>
    <li>Create and activate a conda virtual environment with the required libraries</li>
    <li>Install [MacTeX](https://tug.org/mactex/)</li>
    <li>Install the `latexmkrc` package using TeX Live Utility</li>
</ol>

```
git clone https://github.com/aymannel/autocoshh.git
conda create --name autocoshh --file requirements.txt
conda activate autocoshh
python interface.py
```

</br>
<h3>IMAGES</h3>

![projectimage](https://github.com/aymannel/autocoshh/blob/master/img/autocoshh.png?raw=true)
![projectimage](https://github.com/aymannel/autocoshh/blob/master/img/form.png?raw=true)

<hr>
