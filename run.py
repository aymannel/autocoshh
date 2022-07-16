from core import FormData, PDFForm, CSVForm

import subprocess
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import date
from random import shuffle

padx = 5
pady = 2

class Font():
    def __init__(self):
        self.title = ('Verdana', 25, 'bold')
        self.subtitle = ('Calibri', 16, 'bold')
        self.textbox = ('Calibri', 14)
        self.entry = ('Calibri', 14, 'bold')
        self.color_entry = '#464646'

chemcsv = pd.read_csv('reference.csv')
font = Font() #place me somewhere better no?

class Variables():
    def __init__(self):
        #MainPage variables
        self.date = str(date.today().strftime('%d %B %Y'))
        self.show_hazard_codes = tk.IntVar(value=True)
        self.include_empty = tk.IntVar(value=True)
        self.radiovariable = tk.IntVar() #radiovariable shared between multiple radiobuttons thus do not specify value here

        #FormData variables
        self.filename = tk.StringVar()
        self.name = tk.StringVar()
        self.college = tk.StringVar()
        self.title = tk.StringVar()
        self.year = tk.StringVar()

class AutoCoshh(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'AutoCOSHH v4')

        variables = Variables()

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

        #header section ----------------------------------------
        frame_header = ttk.Frame(self) #frame contains title allowing title to span top of window
        frame_header.grid(column=1, row=1, columnspan=4, padx=10, pady=10, sticky=EW)

        label_title = ttk.Label(frame_header, text='AutoCOSHH', font=font.title) #title label nested in header frame
        label_title.pack(side = LEFT)

        #options section ----------------------------------------
        label_options = ttk.Label(self, text='Options', font = font.subtitle) #options label nested in main frame
        label_options.grid(column=1, columnspan=2, row=2, padx=padx, sticky=W)

        frame_options = ttk.Frame(self) #frame contains options checkboxes, radiobuttons, etc
        frame_options.grid(column=1, row=3, columnspan=4, pady=10, sticky=EW)

        checkbox_show_hazard_codes = ttk.Checkbutton(frame_options, text='Include Hazard Codes', variable=variables.show_hazard_codes)
        checkbox_show_hazard_codes.pack(side = LEFT, padx=10)

        checkbox_include_empty = ttk.Checkbutton(frame_options, text='Include Empty Checkboxes', variable=variables.include_empty)
        checkbox_include_empty.pack(side = LEFT, padx=10)

        radiobutton_pdf = ttk.Radiobutton(frame_options, text='PDF', variable=variables.radiovariable, value=0)
        radiobutton_pdf.pack(side = LEFT, padx=10)

        radiobutton_csv = ttk.Radiobutton(frame_options, text='CSV', variable=variables.radiovariable, value=1) #currently does nothing? check me
        radiobutton_csv.pack(side = LEFT, padx=10)

        frame_filename = ttk.Frame(frame_options) #frame contains filename input box
        frame_filename.pack(side=LEFT, padx=15)

        label_filename = ttk.Label(frame_filename, text='Document Name: ', font=font.entry, foreground=font.color_entry)
        label_filename.pack(side=LEFT, anchor=E, pady=2)

        entry_filename = ttk.Entry(frame_filename, width=14, textvariable=variables.filename)
        entry_filename.pack(side=RIGHT)

        button_details = ttk.Button(frame_options, text='Edit Form Details', command=lambda: controller.show_frame(FormDetails))
        button_details.pack(side=RIGHT, padx=10)

        #entry box section ----------------------------------------
        self.label_selected_chemicals = ttk.Label(self, text='Chemicals (0)', font = font.subtitle)
        self.label_selected_chemicals.grid(column=1, row=5, padx=padx, pady=pady, sticky=W)

        self.chembox = Text(self, height=1, width=40, font = font.textbox)
        self.chembox.grid(column=1, row=6, columnspan=2, padx=padx, pady=pady, stick=(E, W, N, S))
        self.chembox.focus()

        #selection box section ----------------------------------------
        selection_box_title = 'Recognised Chemicals (' + str(len(chemcsv.columns)) +')'
        label_selection_title = ttk.Label(self, text = selection_box_title, font = font.subtitle)
        label_selection_title.grid(column=3, row=5, columnspan=2, padx=padx, pady=pady, sticky=EW)

        list_chemicals = list(chemcsv.columns.sort_values())
        self.selbox = Listbox(self, selectmode = MULTIPLE, height = 18, width = 80, font = font.textbox)
        [self.selbox.insert(list_chemicals.index(chem), chem) for chem in list_chemicals]
        self.selbox.grid(column=3, row=6, columnspan=2, padx=padx, pady=pady)

        #BOTTOM BAR
        bottombar_frame = ttk.Frame(self)
        bottombar_frame.grid(column=1, row=7, columnspan=4, padx=padx, pady=pady, sticky=EW)

        opendatabase_button = ttk.Button(bottombar_frame, text='Open Database', command=lambda: self.open_database())
        opendatabase_button.pack(side = LEFT)

        rand_order_button = ttk.Button(bottombar_frame, text='Randomise Order', command=lambda: self.rand_order())
        rand_order_button.pack(side = LEFT)

        submit_button = ttk.Button(bottombar_frame, text='Compile', command=lambda: self.compile_form(variables))
        submit_button.pack(side = RIGHT)

        clear_button = ttk.Button(bottombar_frame, text='Clear Selection', command=lambda: self.clear_selection())
        clear_button.pack(side = RIGHT)

        add_button = ttk.Button(bottombar_frame, text='Add Selection', command=lambda: self.add_selection())
        add_button.pack(side = RIGHT)


    def compile_form(self, variables):
        input = self.chembox.get('1.0','end-1c')
        #[True if var == 1 else False for var in variables.show_hazard_codes]
        #[True if var == 1 else False for var in variables.include_empty]
        config = {'hazcode': True, 'checkboxes': True}

        self.label_selected_chemicals.config(text = 'Chemicals (' + str(len(input.splitlines())) + ')')

        if variables.filename.get() != '':
            filename = variables.filename.get()
        else:
            filename = 'New COSHH Form'

        self.form_data = FormData(input)
        self.form_data.cred.update({'name':variables.name.get(),
                                    'title':variables.title.get(),
                                    'date':variables.date,
                                    'year':variables.year.get(),
                                    'college':variables.college.get(),
                                    'filename':filename})
        self.form = PDFForm(self.form_data, config)

    def rand_order(self):
        contents = list()
        input = self.chembox.get('1.0','end-1c')
        [contents.append(line) for line in input.lower().splitlines()]

        shuffle(contents)
        self.chembox.delete('1.0', 'end')
        self.chembox.insert('end', '\n'.join(contents))

    def add_selection(self):
        chemindex = self.selbox.curselection()
        list_chemicals = list()
        [list_chemicals.append(self.selbox.get(chem)) for chem in chemindex]
        self.chembox.insert('end', '\n'.join(list_chemicals) + '\n')
        self.label_selected_chemicals.config(text = 'Chemicals (' + str(len(self.chembox.get('1.0','end-1c').splitlines())) + ')')
        print('\n'.join(list_chemicals))

    def clear_selection(self):
        self.selbox.selection_clear(0, END)

    def open_database(self):
        bashcommand = 'open -a Microsoft\ Excel reference.csv'
        output = subprocess.check_output(['bash','-c', bashcommand])


class FormDetails(ttk.Frame):
    def __init__(self, parent, controller, variables):
        ttk.Frame.__init__(self, parent)

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

        name_entry = ttk.Entry(entry_frame, width=16, textvariable=variables.name)
        name_entry.pack(side=TOP)

        college_entry = ttk.Entry(entry_frame, width=16, textvariable=variables.college)
        college_entry.pack(side=TOP)

        title_entry = ttk.Entry(entry_frame, width=16, textvariable=variables.title)
        title_entry.pack(side=TOP)

        year_entry = ttk.Entry(entry_frame, width=16, textvariable=variables.year)
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
        bottombar_frame = ttk.Frame(self)
        bottombar_frame.grid(column=1, row=7, columnspan=4, padx=padx, pady=pady, sticky=EW)

        return_button = ttk.Button(bottombar_frame, text='Return', command=lambda: controller.show_frame(MainPage))
        return_button.pack(side = RIGHT)

app = AutoCoshh()
app.mainloop()
