from tkinter import messagebox
from shutil import copyfile
import os

import pandas as pd
import itertools
import fileinput
import logging
import sqlite3
import pudb

#colours
white = '\033[1m'
green = '\033[92m'
red = '\033[1;31m'
end = '\033[0m'


class COSHHForm:
    def __init__(self):        
        self.reference = pd.read_csv('reference.csv')
        self.reference_chemicals = [val.lower() for val in self.reference.columns]
        self.coshh_df = pd.DataFrame(columns=['chemical', 'amount', 'hazard code', 'hazard', 'exposure', 'control'])
        logging.info('COSHHForm object instantiated')

    def parse_input(self, input):
        unknown_chemicals = list()

        def extract_false(item):
            try:
                chemical = item[0:item.index('\\\\')].strip()
                amount = item[item.index('\\\\') + 2:]
            except ValueError:
                chemical = item.strip()
                amount = str()
            
            if chemical.lower() in self.reference_chemicals:
                return [self.reference.columns[self.reference_chemicals.index(chemical.lower())], amount]
            else:
                unknown_chemicals.append(chemical)

        parsed_input = map(extract_false, input) #extract false
        parsed_input = list(filter(None, parsed_input)) #filter out None objects
        parsed_input = list(map(list, zip(*parsed_input))) #transpose parsed_input
        self.chemicals = parsed_input[0] #seperate chemicals and amounts
        self.amounts = parsed_input[1]

        #unknown chemicals messagebox
        if len(unknown_chemicals) > 0:
            text = 'Unrecognised Substance(s):\n' + "\n".join(unknown_chemicals)
            messagebox.showinfo('Error: Unrecognised Substance(s)', text)

        #create new row in coshh_df for each valid chemical
        for chemical, amount in zip(self.chemicals, self.amounts):
            new_row = {'chemical': chemical, 'amount': amount}
            self.coshh_df = pd.concat([pd.DataFrame(new_row, index=[0]), self.coshh_df.loc[:]]).reset_index(drop=True)
        
        self.coshh_df.set_index('chemical', inplace=True)

    def get_coshh_data(self):
        self.conn = sqlite3.connect('autocoshh.db')
        self.cursor = self.conn.cursor()

        #fetch all hazard codes
        self.cursor.execute('SELECT hazard_code FROM main')
        all_hazard_codes = [val[0] for val in self.cursor.fetchall()]

        #fetch all exposure statements
        self.cursor.execute('SELECT exposure FROM exposure;')
        exposure_statements = [exposure[0] for exposure in self.cursor.fetchall()]

        #fetch all control statements
        self.cursor.execute('SELECT control FROM control;')
        control_statements = [control[0] for control in self.cursor.fetchall()]

        for chemical in self.chemicals:
            #get hazard codes
            hazard_codes = [val.strip() for val in self.reference[chemical].dropna() if val.strip() in all_hazard_codes]
            self.coshh_df.loc[chemical]['hazard code'] = hazard_codes

            #get hazards and exposures
            if len(hazard_codes) == 0:
                self.coshh_df.loc[chemical]['hazard'] = 'Not a hazardous substance or mixture according to Regulation (EC) No. 1272/2008'
                self.coshh_df.loc[chemical]['exposure'] = dict(zip(exposure_statements, [False]*4))
                self.coshh_df.loc[chemical]['control'] = dict(zip(control_statements, [False]*11))
            else:
                hazards = list()
                exposure_ref = list()
                control_ref = list()

                for hazard_code in hazard_codes:
                    #get hazards
                    self.cursor.execute(f'SELECT hazard FROM main WHERE hazard_code=\'{hazard_code}\';')
                    hazards.append(self.cursor.fetchone()[0])
                    
                    #get exposures
                    self.cursor.execute(f'SELECT exposure_reference FROM main WHERE hazard_code=\'{hazard_code}\';')
                    exposure_ref.extend(list(self.cursor.fetchone()[0]))

                    #get controls
                    self.cursor.execute(f'SELECT control_reference FROM main WHERE hazard_code=\'{hazard_code}\';')
                    control_ref.extend(list(self.cursor.fetchone()[0]))
                
                exposure_ref = list(dict.fromkeys(exposure_ref)); #remove duplicates
                exposure_ref.sort() #alphabetise

                control_ref = list(dict.fromkeys(control_ref)); #remove duplicates
                control_ref.sort() #alphabetise

                exposure_bool = [True if key in exposure_ref else False for key in 'abcd'] #determine Boolean list
                exposures = dict(zip(exposure_statements, exposure_bool)) #create Boolean dict of exposures
                
                control_bool = [True if key in control_ref else False for key in 'abcdefghijk'] #determine Boolean list
                controls = dict(zip(control_statements, control_bool)) #create Boolean dict of controls

                self.coshh_df.loc[chemical]['hazard'] = hazards
                self.coshh_df.loc[chemical]['exposure'] = exposures
                self.coshh_df.loc[chemical]['control'] = controls

        self.conn.close()

        """
            unkn = [hcode.strip() for hcode in self.reference_chemicals[chem].dropna() if hcode.strip() not in hazcodes_all]
            hcode_unkns.append([chem, unkn])
        hcode_unkns = [val for val in hcode_unkns if len(val[1]) > 0]

        if len(hcode_unkns) > 0:
            text_hcodes = ''
            for val in hcode_unkns:
                text_hcodes += val[0] + ' (' + ', '.join(val[1]) + '), '
            text = 'Unrecognised Hazard Codes:\n' + text_hcodes[:-2] + \
                   '\n\nMay be improperly listed as \'not hazardous\' if no other hazard codes are recorded.'
            messagebox.showinfo('Error: Unknown Hazard Code(s)', text)"""

    def get_specific_risk(self):
        self.conn = sqlite3.connect('autocoshh.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('SELECT * FROM specific_risk')
        specific_risk_data = self.cursor.fetchall()
        self.conn.close()

        self.specific_risk = [0] * 4

        hazard_codes = list()
        hazard_codes = self.coshh_df['hazard code'].to_list() #get list of hazard codes
        hazard_codes = [val for sublist in hazard_codes for val in sublist] #flatten list
        hazard_codes = list(dict.fromkeys(hazard_codes)) #remove duplicates
        
        fire_risk = [val[0] for val in specific_risk_data]
        therm_risk = [val for val in [val[1] for val in specific_risk_data] if len(val) > 0]
        gas_risk = [val for val in [val[2] for val in specific_risk_data] if len(val) > 0]
        malodor_risk = [val for val in [val[3] for val in specific_risk_data] if len(val) > 0]

        if True in [True for val in hazard_codes if val in fire_risk]:
            self.specific_risk[0] = ('$\\boxtimes$ & Keep appropriate fire extinguisher nearby at all times. \\\\\hline')
        else:
            self.specific_risk[0] = ('$\\square$ & \\\\\hline')

        if True in [True for val in hazard_codes if val in therm_risk]:
            self.specific_risk[1] = ('$\\boxtimes$ & Keep ice-bath nearby at all times. \\\\\hline')
        else:
            self.specific_risk[1] = ('$\\square$ & \\\\\hline')

        if True in [True for val in hazard_codes if val in gas_risk]:
            self.specific_risk[2] = ('$\\boxtimes$ & Handle substance in fumehood at all times. \\\\\hline')
        else:
            self.specific_risk[2] = ('$\\square$ & \\\\\hline')

        if True in [True for val in hazard_codes if val in malodor_risk]:
            self.specific_risk[3] = ('$\\boxtimes$ & Handle substance in fumehood at all times. \\\\\hline')
        else:
            self.specific_risk[3] = ('$\\square$ & \\\\\hline')

        return self.specific_risk

    def format_pdf(self):
        self.coshh_str = ''
        self.formatted_df = self.coshh_df.copy()
        self.formatted_df.drop('hazard code', axis=1, inplace=True)
        
        for chemical in self.chemicals:
            if len(self.coshh_df.loc[chemical]['hazard code']) == 0:
                pass
            elif bool(self.show_hazard_codes.get()) == True:
                zip_hazard = zip(self.coshh_df.loc[chemical]['hazard code'], self.coshh_df.loc[chemical]['hazard'])
                hazards = ['\\textbf{'+ hazard_code +'} '+ hazard for hazard_code, hazard in zip_hazard]
                self.formatted_df.loc[chemical]['hazard'] = ' \\newline '.join(hazards)
            else:
                self.formatted_df.loc[chemical]['hazard'] = ' \\newline '.join(self.coshh_df.loc[chemical]['hazard'])
        
            exposures = self.coshh_df.loc[chemical]['exposure'].items()
            if bool(self.include_empty.get()) == True:
                exposures = ['$\\boxtimes$ ' + exposure if value == True else '$\\square$ ' + exposure for exposure, value in exposures]
                self.formatted_df.loc[chemical]['exposure'] =  ' \\newline '.join(exposures)
            else:
                exposures = ['$\\boxtimes$ ' + exposure for exposure, value in exposures if value == True]
                self.formatted_df.loc[chemical]['exposure'] =  ' \\newline '.join(exposures)

            controls = self.coshh_df.loc[chemical]['control'].items()
            if bool(self.include_empty.get()) == True:
                controls = ['$\\boxtimes$ ' + control if value == True else '$\\square$ ' + control for control, value in controls]
                self.formatted_df.loc[chemical]['control'] =  ' \\newline '.join(controls)
            else:
                controls = ['$\\boxtimes$ ' + control for control, value in controls if value == True]
                self.formatted_df.loc[chemical]['control'] =  ' \\newline '.join(controls)
        
            self.coshh_str += f"{chemical} & {self.formatted_df.loc[chemical]['amount']} & {self.formatted_df.loc[chemical]['hazard']} & {self.formatted_df.loc[chemical]['exposure']} & {self.formatted_df.loc[chemical]['control']} \\\\\hline \n\n"

    def create_pdf(self):
        tex_path = f'{self.filename.get()}.tex'
        pdf_path = f'{self.filename.get()}.pdf'
        copyfile('template.tex', 'forms/' + tex_path)

        with fileinput.FileInput('forms/' + tex_path, inplace=True) as file:
            for line in file:
                line = line.replace('replace_title', self.title.get())
                line = line.replace('replace_name', self.name.get())
                line = line.replace('replace_college', self.college.get())
                line = line.replace('replace_date', self.date.get())
                line = line.replace('replace_year', self.year.get())

                line = line.replace('replace_coshh', self.coshh_str)
                line = line.replace('replace_firerisk', self.specific_risk[0])
                line = line.replace('replace_thermrisk', self.specific_risk[1])
                line = line.replace('replace_gasrisk', self.specific_risk[2])
                line = line.replace('replace_malodorrisk', self.specific_risk[3])
                print (line, end='')
        
        os.system(f'cd forms && latexmk -pdf "{tex_path}" && latexmk -c && open "{pdf_path}"')
