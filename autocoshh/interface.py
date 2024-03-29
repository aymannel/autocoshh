import os
import pudb
import random
import logging
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
from core import COSHHForm

#logging options
logging.basicConfig(level=logging.INFO, format='(%(levelname)-s) %(asctime)s %(message)s', datefmt='%d-%m %H:%M:%S')


class Font():
    title = ('Verdana', 25, 'bold')
    subtitle = ('Calibri', 16, 'bold')
    textbox = ('Calibri', 14)
    entry = ('Calibri', 14, 'bold')
    color_entry = '#464646'


class Variables():
    padx = 5
    pady = 2


class AutoCoshh(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'AutoCOSHH v4')
        logging.info('AutoCOSHH object instantiated')
        
        self.reference = pd.read_csv('reference.csv')

        #instantiate COSHHForm and PDFForm objects
        self.coshhform = COSHHForm()

        #instantiate ttk parent container
        parent_container = ttk.Frame(self, padding='6 3 6 6')
        parent_container.grid(column=0, row=0, sticky=NSEW)
        parent_container.rowconfigure(0, weight=1)
        parent_container.columnconfigure(0, weight=1)

        #instantiate Tk Var objects as attributes of pdfform
        self.coshhform.filename = tk.StringVar(value='New Document')
        self.coshhform.name = tk.StringVar()
        self.coshhform.college = tk.StringVar()
        self.coshhform.title = tk.StringVar()
        self.coshhform.year = tk.StringVar()        
        self.coshhform.date = tk.StringVar()

        self.coshhform.show_hazard_codes = tk.IntVar(value=True)
        self.coshhform.include_empty = tk.IntVar(value=True)
        self.coshhform.radiovar_form = tk.IntVar()
        self.coshhform.radiovar_scheme = tk.IntVar()

        #instantiate and configure ttk.Frame objects
        self.mainpage = MainPage(parent_container, self)
        self.mainpage.grid(row=0, column=0, sticky=NSEW)
        
        self.formdetails = FormDetailsPage(parent_container, self)
        self.formdetails.grid(row=0, column=0, sticky=NSEW)

        self.frames = { MainPage: self.mainpage, FormDetailsPage: self.formdetails }
        self.show_frame(MainPage)


    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()
        logging.info(f'{controller.__name__} object raised')

    def get_input(self):
        return self.mainpage.box_entry.get('1.0', 'end-1c').splitlines()

    def rand_order(self):
        chemicals = self.get_input()
        random.shuffle(chemicals)
        self.mainpage.box_entry.delete('1.0', 'end')
        self.mainpage.box_entry.insert('end', '\n'.join(chemicals))
        logging.info('Order of selected chemicals randomised')
        #pudb.set_trace()

    def add_selection(self):
        cursor_selection = list()

        for chemical in self.mainpage.box_selection.curselection():
            cursor_selection.append(self.mainpage.box_selection.get(chemical))
        self.mainpage.box_entry.insert('end', '\n'.join(cursor_selection) + '\n')
        
        self.mainpage.label_chemicals.config(text='Chemicals (' + str(len(self.get_input())) + ')')
        logging.info(f'{len(self.get_input())} chemicals added')

    def compile_form(self):
        self.coshhform.parse_input(self.get_input())
        self.coshhform.get_coshh_data()
        self.coshhform.format_pdf()
        self.coshhform.get_specific_risk()
        self.coshhform.create_pdf()
        
        self.mainpage.label_chemicals.config(text='Chemicals (' + str(len(self.get_input())) + ')')


class MainPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        #instantiate header title and frame
        self.frame_header = ttk.Frame(self) #frame contains title allowing title to span top of window
        self.frame_header.grid(column=1, row=1, columnspan=4, padx=10, pady=10, sticky=EW)

        self.label_title = ttk.Label(self.frame_header, text='AutoCOSHH', font=Font.title) #title label nested in header frame
        self.label_title.pack(side = LEFT)

        #instantiate options frame
        self.label_options = ttk.Label(self, text='Options', font = Font.subtitle) #options label nested in main frame
        self.label_options.grid(column=1, columnspan=2, row=2, padx=Variables.padx, sticky=W)

        self.frame_options = ttk.Frame(self) #frame contains options checkboxes, radiobuttons, etc
        self.frame_options.grid(column=1, row=3, columnspan=4, pady=10, sticky=EW)

        self.checkbox_show_hazard_codes = ttk.Checkbutton(self.frame_options, text='Include Hazard Codes', variable=controller.coshhform.show_hazard_codes)
        self.checkbox_show_hazard_codes.pack(side = LEFT, padx=10)

        self.checkbox_include_empty = ttk.Checkbutton(self.frame_options, text='Include Empty Checkboxes', variable=controller.coshhform.include_empty)
        self.checkbox_include_empty.pack(side = LEFT, padx=10)

        self.radiobutton_pdf = ttk.Radiobutton(self.frame_options, text='PDF', variable=controller.coshhform.radiovar_form, value=0)
        self.radiobutton_pdf.pack(side = LEFT, padx=10)

        self.radiobutton_csv = ttk.Radiobutton(self.frame_options, text='CSV', variable=controller.coshhform.radiovar_form, value=1)
        self.radiobutton_csv.pack(side = LEFT, padx=10)

        self.frame_filename = ttk.Frame(self.frame_options) #frame contains filename input box
        self.frame_filename.pack(side=LEFT, padx=15)

        self.label_filename = ttk.Label(self.frame_filename, text='Document Name: ', font=Font.entry, foreground=Font.color_entry)
        self.label_filename.pack(side=LEFT, anchor=E, pady=2)

        self.entry_filename = ttk.Entry(self.frame_filename, width=14, textvariable=controller.coshhform.filename)
        self.entry_filename.pack(side=RIGHT)

        self.button_details = ttk.Button(self.frame_options, text='Edit Form Details', command=lambda: controller.show_frame(FormDetailsPage))
        self.button_details.pack(side=RIGHT, padx=10)

        #entry box section
        self.label_chemicals = ttk.Label(self, text='Chemicals (0)', font = Font.subtitle)
        self.label_chemicals.grid(column=1, row=5, padx=Variables.padx, pady=Variables.pady, sticky=W)

        self.box_entry = tk.Text(self, height=1, width=40, font = Font.textbox)
        self.box_entry.grid(column=1, row=6, columnspan=2, padx=Variables.padx, pady=Variables.pady, stick=(E, W, N, S))
        self.box_entry.focus()

        #selection box section
        selection_box_title = 'Recognised Chemicals (' + str(len(controller.reference.columns)) +')'
        self.label_selection_title = ttk.Label(self, text=selection_box_title, font = Font.subtitle)
        self.label_selection_title.grid(column=3, row=5, columnspan=2, padx=Variables.padx, pady=Variables.pady, sticky=EW)

        list_chemicals = list(controller.reference.columns.sort_values())
        self.box_selection = Listbox(self, selectmode = MULTIPLE, height = 18, width = 80, font = Font.textbox)
        [self.box_selection.insert(list_chemicals.index(chem), chem) for chem in list_chemicals]
        self.box_selection.grid(column=3, row=6, columnspan=2, padx=Variables.padx, pady=Variables.pady)

        #footer section
        self.frame_footer = ttk.Frame(self)
        self.frame_footer.grid(column=1, row=7, columnspan=4, padx=Variables.padx, pady=Variables.pady, sticky=EW)

        self.button_open_database = ttk.Button(self.frame_footer, text='Open Database', command=lambda: os.system('open reference.csv'))
        self.button_open_database.pack(side = LEFT)

        self.button_randomise_order = ttk.Button(self.frame_footer, text='Randomise Order', command=lambda: controller.rand_order())
        self.button_randomise_order.pack(side = LEFT)

        self.button_submit = ttk.Button(self.frame_footer, text='Compile', command=lambda: controller.compile_form())
        self.button_submit.pack(side = RIGHT)

        self.button_clear = ttk.Button(self.frame_footer, text='Clear Selection', command=lambda: self.box_entry.delete('1.0', 'end'))
        self.button_clear.pack(side = RIGHT)

        self.button_add_selection = ttk.Button(self.frame_footer, text='Add Selection', command=lambda: controller.add_selection())
        self.button_add_selection.pack(side = RIGHT)


class FormDetailsPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        #instantiate header title and frame
        frame_header = ttk.Frame(self)
        frame_header.grid(column=1, row=1, columnspan=4, padx=10, pady=10, sticky=EW)

        label_title = ttk.Label(frame_header, text='AutoCOSHH', font=Font.title)
        label_title.pack(side = LEFT)


        #instantiate form details title and frame
        label_form_details = ttk.Label(self, text='Form Details', font = Font.subtitle)
        label_form_details.grid(column=1, row=2, padx=Variables.padx, sticky=W)

        frame_form_details = ttk.Frame(self)
        frame_form_details.grid(column=1, row=3, columnspan=2, rowspan=3, padx=10, sticky=E)


        #instantiate entry labels frame
        frame_entry_labels = ttk.Frame(frame_form_details)
        frame_entry_labels.pack(side=LEFT, pady=10)

        #instantiate name label
        label_name = ttk.Label(frame_entry_labels, text='Name: ', font=Font.entry, foreground=Font.color_entry)
        label_name.pack(side=TOP, anchor=E, pady=2)
       
        #instantiate title label
        label_form_title = ttk.Label(frame_entry_labels, text='Title: ', font=Font.entry, foreground=Font.color_entry)
        label_form_title.pack(side=TOP, anchor=E, pady=2)
        
        #instantiate date label
        label_date = ttk.Label(frame_entry_labels, text='Date: ', font=Font.entry, foreground=Font.color_entry)
        label_date.pack(side=TOP, anchor=E, pady=2)

        #instantiate college label
        label_college = ttk.Label(frame_entry_labels, text='College: ', font=Font.entry, foreground=Font.color_entry)
        label_college.pack(side=TOP, anchor=E, pady=2)

        #instantiate year label
        label_year = ttk.Label(frame_entry_labels, text='Year: ', font=Font.entry, foreground=Font.color_entry)
        label_year.pack(side=TOP, anchor=E, pady=2)


        #instantiate entries frame
        frame_entries = ttk.Frame(frame_form_details)
        frame_entries.pack(side=LEFT)
        
        #instantiate name entry
        self.entry_name = ttk.Entry(frame_entries, width=16, textvariable=controller.coshhform.name)
        self.entry_name.pack(side=TOP)
        
        #instantiate title entry
        self.entry_title = ttk.Entry(frame_entries, width=16, textvariable=controller.coshhform.title)
        self.entry_title.pack(side=TOP)

        #instantiate date entry
        self.entry_date = ttk.Entry(frame_entries, width=16, textvariable=controller.coshhform.date)
        self.entry_date.pack(side=TOP)
        
        #instantiate college entry
        self.entry_college = ttk.Entry(frame_entries, width=16, textvariable=controller.coshhform.college)
        self.entry_college.pack(side=TOP)
        
        #instantiate year entry
        self.entry_year = ttk.Entry(frame_entries, width=16, textvariable=controller.coshhform.year)
        self.entry_year.pack(side=TOP)


        label_scheme = ttk.Label(self, text='Reaction Scheme Size', font=Font.subtitle)
        label_scheme.grid(column=3, row=2, padx=10, sticky=W)

        frame_scheme = ttk.Frame(self)
        frame_scheme.grid(column=3, row=3, columnspan=3, padx=10, sticky=W)

        schemesize = tk.IntVar()
        smallscheme_radiobutton = ttk.Radiobutton(frame_scheme, text='Small', variable=controller.coshhform.radiovar_scheme, value = 0)
        smallscheme_radiobutton.pack(side = LEFT, padx=10)

        medcheme_radiobutton = ttk.Radiobutton(frame_scheme, text='Medium', variable=controller.coshhform.radiovar_scheme, value = 1)
        medcheme_radiobutton.pack(side = LEFT, padx=10)

        largescheme_radiobutton = ttk.Radiobutton(frame_scheme, text='Large', variable=controller.coshhform.radiovar_scheme, value = 2)
        largescheme_radiobutton.pack(side = LEFT, padx=10)

        #instantiate footer frame
        frame_footer = ttk.Frame(self)
        frame_footer.grid(column=1, row=7, columnspan=4, padx=Variables.padx, pady=Variables.pady, sticky=EW)

        return_button = ttk.Button(frame_footer, text='Return', command=lambda: controller.show_frame(MainPage))
        return_button.pack(side = RIGHT)


app = AutoCoshh()
app.mainloop()
