<h1 align = "center">AutoCOSHH</h1>

<h3>DESCRIPTION</h3>
As a Chemistry undergraduate at Oxford, time is at a premium. AutoCOSHH attempts to eliminate the menial work involved in manually generating COSHH forms for labs.

Given a list of chemicals and their respective hazard codes, AutoCOSHH performs all of the menial work involved in generating a COSHH form. The built-in reference sheet specifies many of the most commonly used solvents and chemicals. The `latexmkrc` module is used to generate the COSHH form in the required format.

</br>
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
    <li>Clone repository to local directory: `git clone url /path/to/directory`</li>
    <li>Navigate to local directory: `cd /path/to/directory`</li>
    <li>Create and activate conda virtual environment: `conda create --name autocoshh && conda activate autocoshh`</li>
    <li>Install required packages: `conda install requirements.txt`</li>
    <li>Install LaTeX: [url]</li>
    <li>Install `latexmkrc` using TeXLive Utility</li>
    <li>Run AutoCOSHH: `python interface.py`</li>
</ol>

</br>
<h3>IMAGES</h3>

![projectimage](https://github.com/aymannel/autocoshh/blob/master/img/autocoshh.png?raw=true)
![projectimage](https://github.com/aymannel/autocoshh/blob/master/img/form.png?raw=true)

<hr>
