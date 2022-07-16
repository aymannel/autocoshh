from tkinter import messagebox
from shutil import copyfile
import os

import pandas as pd
import fileinput
import sqlite3

#colours
white = '\033[1m'
green = '\033[92m'
red = '\033[1;31m'
end = '\033[0m'

chemcsv = pd.read_csv('reference.csv')

class FormData:
    """process COSHH form corresponding to list of chemicals in inout"""

    def __init__(self, input):
        self.conn = sqlite3.connect('autocoshh.db')

        self.coshh_data = list()
        self.chemicals = [val.lower() for val in list(chemcsv.columns)]

        self.cred = {'filename':'', 'title':'', 'name':'', 'college':'', 'year':'', 'date':''}

        self.parse_input(input)
        self.check_chem()

        self.get_hazcodes()
        self.get_hazards()
        self.get_exposures()
        self.get_controls()
        self.get_specrisk()

        self.form_data = {'cred':self.cred, 'main':self.coshh_data, 'specific_risk':self.specific_risk}
        #return(self.form_data)

        self.conn.close()

    def print_form(self):
        for chemical in self.coshh_data:
            print(chemical[0], '(' + chemical[1] + ')')
            print(', '.join([a +' - '+  b for a, b in zip(chemical[2], chemical[3])]))
            print(', '.join([green + exposure + end if chemical[4][exposure] == True else exposure for exposure in chemical[4]]))
            print(', '.join([green + control + end if chemical[5][control] == True else control for control in chemical[5]]), '\n')

    def parse_input(self, input):
        for idx, val in enumerate(input.splitlines()):
            self.coshh_data.append(['', '', '', '', '', ''])
            try:
                amount = val[val.index('(') + 1:val.index(')')]
                chemical = val[0:val.find('(')].lower().strip()
                self.coshh_data[idx][0] = chemical
                self.coshh_data[idx][1] = amount
            except ValueError:
                self.coshh_data[idx][0] = val.lower().strip()
                self.coshh_data[idx][1] = ''

    def check_chem(self):
        chem_unkns = list()

        for idx, val in enumerate([val[0] for val in self.coshh_data]): #identify unknown substances
            try:
                chemcsv.columns[self.chemicals.index(val)]
            except ValueError:
                chem_unkns.append(val)

        self.coshh_data = [val for val in self.coshh_data if val[0] not in chem_unkns] #remove unknown substances

        for val in self.coshh_data: #retrieve properly formatted substance names
            val[0] = chemcsv.columns[self.chemicals.index(val[0])]

        if len(chem_unkns) > 0:
            text = 'Unrecognised Substances:\n' + "'" + "', '".join(chem_unkns) + "'"
            messagebox.showinfo('Error: Unrecognised Substance(s)', text)

    def get_hazcodes(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute('SELECT hazard_code FROM main')
        hazcodes_all = [hcode[0] for hcode in self.cursor.fetchall()]
        hcode_unkns = list()

        for idx, chem in enumerate([val[0] for val in self.coshh_data]):
            self.coshh_data[idx][2] = [hcode.strip() for hcode in chemcsv[chem].dropna() if hcode.strip() in hazcodes_all]

            unkn = [hcode.strip() for hcode in chemcsv[chem].dropna() if hcode.strip() not in hazcodes_all]
            hcode_unkns.append([chem, unkn])
        hcode_unkns = [val for val in hcode_unkns if len(val[1]) > 0]

        if len(hcode_unkns) > 0:
            text_hcodes = ''
            for val in hcode_unkns:
                text_hcodes += val[0] + ' (' + ', '.join(val[1]) + '), '
            text = 'Unrecognised Hazard Codes:\n' + text_hcodes[:-2] + \
                   '\n\nMay be improperly listed as \'not hazardous\' if no other hazard codes are recorded.'
            messagebox.showinfo('Error: Unknown Hazard Code(s)', text)

    def get_hazards(self):

        for idx, hazcodes in enumerate([val[2] for val in self.coshh_data]):
            hazards = list()

            if len(hazcodes) == 0:
                self.coshh_data[idx][3] = 'Not a hazardous substance or mixture according to Regulation (EC) No. 1272/2008'

            else:
                for hazcode in hazcodes:
                    self.cursor.execute(f'SELECT hazard FROM main WHERE hazard_code=\'{hazcode}\';')
                    hazards.append(self.cursor.fetchone()[0])

                self.coshh_data[idx][3] = hazards

    def get_exposures(self):

        for idx, hazcodes in enumerate([val[2] for val in self.coshh_data]):
            exposure_ref = list()

            for hazcode in hazcodes: #retrieve all exposure references
                self.cursor.execute(f'SELECT exposure_reference FROM main WHERE hazard_code=\'{hazcode}\';')
                exposure_ref.extend(list(self.cursor.fetchone()[0]))
            exposure_ref = list(dict.fromkeys(exposure_ref)); #remove duplicates
            exposure_ref.sort() #alphabetise exposure references

            self.cursor.execute('SELECT exposure FROM exposure;')
            exposure_statements = [exposure[0] for exposure in self.cursor.fetchall()] #retrieve all exposure statements
            exposure_bool = [True if key in exposure_ref else False for key in 'abcd'] #determine Boolean list
            exposures = dict(zip(exposure_statements, exposure_bool)) #create Boolean dict of exposures

            self.coshh_data[idx][4] = exposures

    def get_controls(self):

        for idx, hazcodes in enumerate([val[2] for val in self.coshh_data]):
            control_ref = list()

            for hazcode in hazcodes: #retrieve all control references
                self.cursor.execute(f'SELECT control_reference FROM main WHERE hazard_code=\'{hazcode}\';')
                control_ref.extend(list(self.cursor.fetchone()[0]))
            control_ref = list(dict.fromkeys(control_ref)); #remove duplicates
            control_ref.sort() #alphabetise control references

            self.cursor.execute('SELECT control FROM control;')
            control_statements = [control[0] for control in self.cursor.fetchall()] #retrieve all control statements
            control_bool = [True if key in control_ref else False for key in 'abcdefghijk'] #determine Boolean list
            controls = dict(zip(control_statements, control_bool)) #create Boolean dict of controls

            self.coshh_data[idx][5] = controls

    def get_specrisk(self):
        self.specific_risk = [0] * 4
        hazcodes = list()

        [hazcodes.extend(val[2]) for val in self.coshh_data] #retrieve all hazard codes
        hazcodes = list(dict.fromkeys(hazcodes)); #remove duplicates

        self.cursor.execute('SELECT * FROM specific_risk')
        specific_risk_data = self.cursor.fetchall()

        fire_risk = [val[0] for val in specific_risk_data]
        therm_risk = [val for val in [val[1] for val in specific_risk_data] if len(val) > 0]
        gas_risk = [val for val in [val[2] for val in specific_risk_data] if len(val) > 0]
        malodor_risk = [val for val in [val[3] for val in specific_risk_data] if len(val) > 0]

        if True in [True for hazcode in hazcodes if hazcode in fire_risk]:
            self.specific_risk[0] = ('$\\boxtimes$ & Keep appropriate fire extinguisher nearby at all times. \\\\\hline')
        else:
            self.specific_risk[0] = ('$\\square$ & \\\\\hline')

        if True in [True for hazcode in hazcodes if hazcode in therm_risk]:
            self.specific_risk[1] = ('$\\boxtimes$ & Keep ice-bath nearby at all times. \\\\\hline')
        else:
            self.specific_risk[1] = ('$\\square$ & \\\\\hline')

        if True in [True for hazcode in hazcodes if hazcode in gas_risk]:
            self.specific_risk[2] = ('$\\boxtimes$ & Handle substance in fumehood at all times. \\\\\hline')
        else:
            self.specific_risk[2] = ('$\\square$ & \\\\\hline')

        if True in [True for hazcode in hazcodes if hazcode in malodor_risk]:
            self.specific_risk[3] = ('$\\boxtimes$ & Handle substance in fumehood at all times. \\\\\hline')
        else:
            self.specific_risk[3] = ('$\\square$ & \\\\\hline')

class PDFForm:
    """parse COSHH form data, assemble tex file and process COSHH Form as PDF file"""

    def __init__(self, FormData, config):
        self.pdfform = [entry[0:5] for entry in FormData.coshh_data]
        self.form_data = FormData.coshh_data
        self.config = config
        self.cred = FormData.cred

        self.format_hazards()
        self.format_exposures()
        self.format_controls()
        self.format_data()
        self.create_PDF(FormData)

    def format_hazards(self):
        for idx, entry in enumerate(self.form_data):
            if len(entry[2]) == 0:
                self.pdfform[idx][2] = entry[3]
            elif self.config['hazcode'] == True:
                hazards = ['\\textbf{'+ hazcode +'} '+ hazard for hazcode, hazard in zip(entry[2], entry[3])]
                self.pdfform[idx][2] = ' \\newline '.join(hazards)
            else:
                self.pdfform[idx][2] = ' \\newline '.join(entry[3])

    def format_exposures(self):
        for idx, entry in enumerate(self.form_data):
            if self.config['checkboxes'] == True:
                exposures = ['$\\boxtimes$ ' + exposure if entry[4][exposure] == True else '$\\square$ ' + exposure for exposure in entry[4]]
                self.pdfform[idx][3] = ' \\newline '.join(exposures)
            else:
                exposures = ['$\\boxtimes$ ' + exposure for exposure in entry[4] if entry[4][exposure] == True]
                self.pdfform[idx][3] = ' \\newline '.join(exposures)

    def format_controls(self):
        for idx, entry in enumerate(self.form_data):
            if self.config['checkboxes'] == True:
                controls = ['$\\boxtimes$ ' + control if entry[5][control] == True else '$\\square$ ' + control for control in entry[5]]
                self.pdfform[idx][4] = ' \\newline '.join(controls)
            else:
                controls = ['$\\boxtimes$ ' + control for control in entry[5] if entry[5][control] == True]
                self.pdfform[idx][4] = ' \\newline '.join(controls)

    def format_data(self):
        self.coshh_str = ''

        for entry in self.pdfform:
            self.coshh_str += f'{entry[0]} & {entry[1]} & \n{entry[2]} & \n{entry[3]} & \n{entry[4]} \\\\\hline \n\n'

    def create_PDF(self, FormData):
        tex_path = f'{self.cred["filename"]}.tex'
        pdf_path = f'{self.cred["filename"]}.pdf'
        copyfile('template.tex', 'forms/' + tex_path)

        with fileinput.FileInput('forms/' + tex_path, inplace=True) as file:
            for line in file:
                line = line.replace('replace_title', self.cred['title'])
                line = line.replace('replace_name', self.cred['name'])
                line = line.replace('replace_college', self.cred['college'])
                line = line.replace('replace_date', self.cred['date'])
                line = line.replace('replace_year', self.cred['year'])

                line = line.replace('replace_coshh', self.coshh_str)
                line = line.replace('replace_firerisk', FormData.specific_risk[0])
                line = line.replace('replace_thermrisk', FormData.specific_risk[1])
                line = line.replace('replace_gasrisk', FormData.specific_risk[2])
                line = line.replace('replace_malodorrisk', FormData.specific_risk[3])
                print (line, end='')

        #temporarily pause pdf generation until you can figure out why its creating a PDF on start up
#        os.system(f"cd forms && latexmk -pdf '{tex_path}' && latexmk -c && open '{pdf_path}'")


class CSVForm:
    def __init__(self):
        print('CSV Form')

input1 = """1,3-Dibromopropane
1,4-Dichlorobenzene
1-Octanol
2,6-Dimethyl-2,4,6-Octatriene
2-Benzylpyridine
2-Hydroxycinnamicpyridine
2-Hydroxypyridine
2-Methyltetrahydrofuran
2-Nitrobenzaldehyde
2-Propanol
2-Pyridone
2E,4E-Hexa-2,4-dien-1-ol
3-Hydroxycinnamic
3-Methyl-2-butanone
3-Methyl-2-buten-1-ol
3-Methyl-3-buten-1-ol
3-Nitroacetophenone
3-Nitrobenzaldehyde
4-Bromophenylhydrazine Hydrochloride
4-Cyanophenylhydrazine Hydrochloride
4-Hydroxycinnamic
4-Methoxybenzaldehyde
4-Methoxyphenylhydrazine Hydrochloride
4-Nitroaniline
4-Nitrobenzaldehyde
5-Nitro-2-furaldehyde
Acetone
Acetonitrile
Aminoguanidine Hydrochloride
Ammonia
Ammonia Borane
Ammonium Chloride
Ammonium Sulphate
Bacteriological Agar
Bacto Tryptone
Bacto Yeast Extract
Barium Nitrate
Barium Sulphate
Benzaldehyde
Benzil
Benzoin
Benzyl Alcohol
Bromobenzene
Caesium Chloride
Caesium Tetraphenylborate
Calcium Chloride
Calcium Fluoride
Chlorine
Chloroform
Chloroplatinic Acid
Cinnamic
Cobalt
Cobalt Chloride Hexahydrate
Copper Nitrate
Cyclohexane
Cyclohexane.1
DCM
DMSO
Deuterated Chloroform
Deuterium Oxide
Diethyl Adipate
Diethyl Ether
Diphenylmethane
E. Coli K12
EDTA
Ethane-1,2-diol
Ethanoic Acid
Ethanol
Ethyl Acetate
Ethyl Acetoacetate
Ethylene Glycol
Fluorenone
Glacial Acetic Acid
HCl
Hex-1-ene
Hydrogen
Hydrogen Peroxide
Iodine
Iodine Monochloride
Iodine Trichloride
Iron III Nitrate
Lead Acetate
Lithium Iodide
Lithium Perchlorate
Lycopene
Magnesium
Magnesium Sulphate
Mercury Chloride
Methanol
Nitric Acid
Petroleum Ether
Petroleum ether
Platinum
Potassium Chloride
Potassium Manganate
Ruthenium Chloride
Silica Gel
Silver
Silver Chloride
Silver Nitrate
Sodium
Sodium Bicarbonate
Sodium Borohydride
Sodium Chloride
Sodium Hydroxide
Sodium Iodide
Sodium Salicylate
Sodium Sulphate
Sodium Sulphite
Sodium Tetraphenylborate
Sodium Thiosulphate
Styrene
Sulphuric Acid
THF
Tartaric Acid
Tetrahydropyran
Tetramethylsilane
Tin
Toluene
p-Toluenesulfonic Acid Monohydrate"""

config = {'hazcode':True, 'checkboxes':True}

AymanData = FormData(input1)
AymanData.cred.update({'name':'Ayman', 'title':'C118', 'year':'Second', 'college':'St. John\'s', 'filename':'some'})
AymanPDF = PDFForm(AymanData, config)
