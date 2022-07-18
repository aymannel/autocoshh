from core import FormData, PDFForm, CSVForm

import os
import logging
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import date
from random import shuffle

#logging options
logging.basicConfig(level=logging.INFO, format='(%(levelname)-s) %(asctime)s %(message)s', datefmt='%d-%m %H:%M:%S')

chemcsv = pd.read_csv('reference.csv')
padx = 5
pady = 2

class Font():
    def __init__(self):
        self.title = ('Verdana', 25, 'bold')
        self.subtitle = ('Calibri', 16, 'bold')
        self.textbox = ('Calibri', 14)
        self.entry = ('Calibri', 14, 'bold')
        self.color_entry = '#464646'


class Variables():
    def __init__(self):
        self.date = str(date.today().strftime('%d %B %Y'))
        self.filename = ''
        self.name = ''
        self.year = ''
        self.college = ''
        self.title = ''


font = Font()
variables = Variables()


class AutoCoshh(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'AutoCOSHH v4')

        #container setup
        container = ttk.Frame(self, padding='6 3 6 6')
        container.grid(column=0, row=0, sticky=NSEW)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = dict()

        for page in (MainPage, FormDetails):
            frame = page(container, self, variables)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky=NSEW)

        self.show_frame(MainPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class MainPage(ttk.Frame):
    def __init__(self, parent, controller, variables):
        ttk.Frame.__init__(self, parent)
        
        #initialise tk variables
        self.filename = tk.StringVar(value='New Form')
        self.show_hazard_codes = tk.IntVar(value=True)
        self.include_empty = tk.IntVar(value=True)
        self.radiovariable = tk.IntVar()

        #header section ----------------------------------------
        self.frame_header = ttk.Frame(self) #frame contains title allowing title to span top of window
        self.frame_header.grid(column=1, row=1, columnspan=4, padx=10, pady=10, sticky=EW)

        self.label_title = ttk.Label(self.frame_header, text='AutoCOSHH', font=font.title) #title label nested in header frame
        self.label_title.pack(side = LEFT)

        #options section ----------------------------------------
        self.label_options = ttk.Label(self, text='Options', font = font.subtitle) #options label nested in main frame
        self.label_options.grid(column=1, columnspan=2, row=2, padx=padx, sticky=W)

        self.frame_options = ttk.Frame(self) #frame contains options checkboxes, radiobuttons, etc
        self.frame_options.grid(column=1, row=3, columnspan=4, pady=10, sticky=EW)

        self.checkbox_show_hazard_codes = ttk.Checkbutton(self.frame_options, text='Include Hazard Codes', variable=self.show_hazard_codes)
        self.checkbox_show_hazard_codes.pack(side = LEFT, padx=10)

        self.checkbox_include_empty = ttk.Checkbutton(self.frame_options, text='Include Empty Checkboxes', variable=self.include_empty)
        self.checkbox_include_empty.pack(side = LEFT, padx=10)

        self.radiobutton_pdf = ttk.Radiobutton(self.frame_options, text='PDF', variable=self.radiovariable, value=0)
        self.radiobutton_pdf.pack(side = LEFT, padx=10)

        self.radiobutton_csv = ttk.Radiobutton(self.frame_options, text='CSV', variable=self.radiovariable, value=1) #has this been implemented
        self.radiobutton_csv.pack(side = LEFT, padx=10)

        self.frame_filename = ttk.Frame(self.frame_options) #frame contains filename input box
        self.frame_filename.pack(side=LEFT, padx=15)

        self.label_filename = ttk.Label(self.frame_filename, text='Document Name: ', font=font.entry, foreground=font.color_entry)
        self.label_filename.pack(side=LEFT, anchor=E, pady=2)

        self.entry_filename = ttk.Entry(self.frame_filename, width=14, textvariable=self.filename)
        self.entry_filename.pack(side=RIGHT)

        self.button_details = ttk.Button(self.frame_options, text='Edit Form Details', command=lambda: controller.show_frame(FormDetails))
        self.button_details.pack(side=RIGHT, padx=10)

        #entry box section ----------------------------------------
        self.label_selected_chemicals = ttk.Label(self, text='Chemicals (0)', font = font.subtitle)
        self.label_selected_chemicals.grid(column=1, row=5, padx=padx, pady=pady, sticky=W)

        self.box_entry = tk.Text(self, height=1, width=40, font = font.textbox)
        self.box_entry.grid(column=1, row=6, columnspan=2, padx=padx, pady=pady, stick=(E, W, N, S))
        self.box_entry.focus()

        #selection box section ----------------------------------------
        selection_box_title = 'Recognised Chemicals (' + str(len(chemcsv.columns)) +')'
        self.label_selection_title = ttk.Label(self, text=selection_box_title, font = font.subtitle)
        self.label_selection_title.grid(column=3, row=5, columnspan=2, padx=padx, pady=pady, sticky=EW)

        list_chemicals = list(chemcsv.columns.sort_values())
        self.box_selection = Listbox(self, selectmode = MULTIPLE, height = 18, width = 80, font = font.textbox)
        [self.box_selection.insert(list_chemicals.index(chem), chem) for chem in list_chemicals]
        self.box_selection.grid(column=3, row=6, columnspan=2, padx=padx, pady=pady)

        #footer section -----------------------------------------------
        self.frame_footer = ttk.Frame(self)
        self.frame_footer.grid(column=1, row=7, columnspan=4, padx=padx, pady=pady, sticky=EW)

        self.button_open_database = ttk.Button(self.frame_footer, text='Open Database', command=lambda: os.system('open reference.csv'))
        self.button_open_database.pack(side = LEFT)

        self.button_randomise_order = ttk.Button(self.frame_footer, text='Randomise Order', command=lambda: self.rand_order())
        self.button_randomise_order.pack(side = LEFT)

        self.button_submit = ttk.Button(self.frame_footer, text='Compile', command=lambda: self.compile_form())
        self.button_submit.pack(side = RIGHT)

        self.button_clear = ttk.Button(self.frame_footer, text='Clear Selection', command=lambda: self.box_entry.delete('1.0', 'end'))
        self.button_clear.pack(side = RIGHT)

        self.button_add_selection = ttk.Button(self.frame_footer, text='Add Selection', command=lambda: self.add_selection())
        self.button_add_selection.pack(side = RIGHT)

    def get_input(self):
        variables.selected_chemicals = self.box_entry.get('1.0', 'end-1c').lower().splitlines()

    def rand_order(self):
        self.get_input()
        
        shuffle(variables.selected_chemicals)
        self.box_entry.delete('1.0', 'end')
        self.box_entry.insert('end', '\n'.join(variables.selected_chemicals))

    def add_selection(self):
        cursor_selection = []

        for chemical in self.box_selection.curselection():
            cursor_selection.append(self.box_selection.get(chemical))
        
        self.box_entry.insert('end', '\n'.join(cursor_selection) + '\n')
        
        self.get_input()
        self.label_selected_chemicals.config(text='Chemicals (' + str(len(variables.selected_chemicals)) + ')')

        self.get_input()
        logging.info(f'Following chemicals added: {variables.selected_chemicals}')

    def update_variables(self):
        variables.filename = self.filename.get()
        #the following must be updated in the FormDetails class
#        variables.title
#        variables.name
#        variables.year
#        variables.college      

    def compile_form(self):
        input = self.box_entry.get('1.0','end-1c')
        config = {'hazcode': bool(self.show_hazard_codes.get()), 'checkboxes': bool(self.include_empty.get())}

        #update displayed number of selected chemicals
        self.label_selected_chemicals.config(text = 'Chemicals (' + str(len(input.splitlines())) + ')')

        self.update_variables()
        form_data = FormData(input)
        form_data.cred.update({'name':variables.name,
                                    'title':variables.title,
                                    'date':variables.date,
                                    'year':variables.year,
                                    'college':variables.college,
                                    'filename':variables.filename})

        self.form = PDFForm(form_data, config)

class FormDetails(ttk.Frame):
    def __init__(self, parent, controller, variables):
        ttk.Frame.__init__(self, parent)

        #initialise tk variables
        self.name = tk.StringVar()
        self.college = tk.StringVar()
        self.title = tk.StringVar()
        self.year = tk.StringVar()        

        #TITLE & HEADER
        frame_header = ttk.Frame(self)
        frame_header.grid(column=1, row=1, columnspan=4, padx=10, pady=10, sticky=EW)

        label_title = ttk.Label(frame_header, text='AutoCOSHH', font=font.title)
        label_title.pack(side = LEFT)

        #DETAILS
        label_form_details = ttk.Label(self, text='Form Details', font = font.subtitle)
        label_form_details.grid(column=1, row=2, padx=padx, sticky=W)

        frame_form_details = ttk.Frame(self)
        frame_form_details.grid(column=1, row=3, columnspan=2, rowspan=3, padx=10, sticky=E)

        label_frame = ttk.Frame(frame_form_details)
        label_frame.pack(side=LEFT, pady=10)

        name_label = ttk.Label(label_frame, text='Name: ', font = font.entry, foreground=font.color_entry)
        name_label.pack(side=TOP, anchor=E, pady=2)

        college_label = ttk.Label(label_frame, text='College: ', font = font.entry, foreground=font.color_entry)
        college_label.pack(side=TOP, anchor=E, pady=2)

        label_form_title = ttk.Label(label_frame, text='Title: ', font = font.entry, foreground=font.color_entry)
        label_form_title.pack(side=TOP, anchor=E, pady=2)

        year_label = ttk.Label(label_frame, text='Year: ', font = font.entry, foreground=font.color_entry)
        year_label.pack(side=TOP, anchor=E, pady=2)

        entry_frame = ttk.Frame(frame_form_details)
        entry_frame.pack(side=LEFT)

        name_entry = ttk.Entry(entry_frame, width=16, textvariable=self.name)
        name_entry.pack(side=TOP)

        college_entry = ttk.Entry(entry_frame, width=16, textvariable=self.college)
        college_entry.pack(side=TOP)

        title_entry = ttk.Entry(entry_frame, width=16, textvariable=self.title)
        title_entry.pack(side=TOP)

        year_entry = ttk.Entry(entry_frame, width=16, textvariable=self.year)
        year_entry.pack(side=TOP)

        scheme_label = ttk.Label(self, text='Reaction Scheme Size', font=font.subtitle)
        scheme_label.grid(column=3, row=2, padx=10, sticky=W)

        scheme_frame = ttk.Frame(self)
        scheme_frame.grid(column=3, row=3, columnspan=3, padx=10, sticky=W)

        schemesize = tk.IntVar()
        smallscheme_radiobutton = ttk.Radiobutton(scheme_frame, text='Small', variable=schemesize, value = 0)
        smallscheme_radiobutton.pack(side = LEFT, padx=10)

        medcheme_radiobutton = ttk.Radiobutton(scheme_frame, text='Medium', variable=schemesize, value = 1)
        medcheme_radiobutton.pack(side = LEFT, padx=10)

        largescheme_radiobutton = ttk.Radiobutton(scheme_frame, text='Large', variable=schemesize, value = 2)
        largescheme_radiobutton.pack(side = LEFT, padx=10)

        #BOTTOM BAR
        frame_footer = ttk.Frame(self)
        frame_footer.grid(column=1, row=7, columnspan=4, padx=padx, pady=pady, sticky=EW)

        return_button = ttk.Button(frame_footer, text='Return', command=lambda: controller.show_frame(MainPage))
        return_button.pack(side = RIGHT)

    def update_variables(self):
        variables.name = self.name.get()
        variables.title = self.title.get()
        variables.year = self.year.get()
        variables.college = self.college.get()

app = AutoCoshh()
app.mainloop()
