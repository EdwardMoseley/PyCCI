from annotation_panel import *
import csv
import numpy as np
import os
import pandas as pd
from ScrolledText import ScrolledText
import sys
import time
import tkFont
import tkFileDialog
from Tkinter import *
from PIL import ImageTk, Image


class MainApplication(Frame):
    def __init__(self, master, title, textbox_labels, checkbox_labels):
        self.master = master
        self.title = title
        self.master.title(self.title + " PyCCI")
        Frame.__init__(self, self.master)
       
        # Define variables
        self.title_text = "\t\t" + self.title + " Indications GUI"
        self.current_row_index = 0
        self.data_df = pd.DataFrame()
        
        # Create GUI
        self.define_fonts()
        self.create_body()

        self.annotation_panel = AnnotationPanel(master, self.checkframe, textbox_labels, checkbox_labels)
        self.annotation_panel.pack()

    def define_fonts(self):
        self.titlefont = tkFont.Font(size=12, weight='bold')
        self.boldfont = tkFont.Font(size=8, weight='bold')
        self.textfont = tkFont.Font(family='Arial', size=15)
        self.h3font = tkFont.Font(size=11)

    def openfile(self):
        file = tkFileDialog.askopenfilename()
        if not file:
            return
        self.data_df = pd.read_csv(file)

        # If the file already exists, open it and continue at the spot you were,
        # makes it easier to continue on annotating results
        self.results_filename = file[:-4] + "Results.csv"
        if os.path.isfile(self.results_filename):
            results_df = pd.read_csv(self.results_filename)
            self.crane(results_df.shape[0], self.results_filename)
        else:
            self.crane(0, self.results_filename)

    def crane(self, delta, results_filename):
        '''
        Called whenever you press back or next
        '''
        num_notes = self.data_df.shape[0]
        is_saved = self.annotation_panel.save_annotations(self.data_df, self.current_row_index, results_filename)
        if not is_saved:
            return

        self.current_row_index += delta
        if self.current_row_index < 1:
            self.current_row_index = 0

        if self.current_row_index > num_notes-1:
            self.current_row_index = num_notes-1

        admission_id = self.data_df['HADM_ID'].iloc[self.current_row_index]
        note_category = self.data_df['CATEGORY'].iloc[self.current_row_index]
        clin_text = self.data_df['TEXT'].iloc[self.current_row_index]
        self.create_display_values(num_notes, admission_id, note_category, clin_text)

    def create_display_values(self, total, admission_id, note_category, clin_text):
        # Fill display values
        self.ptnumber.config(text=str(self.current_row_index + 1))
        self.pttotal.config(text=str(total))

        self.pthAdm.config(text=admission_id)
        self.ptnotetype.config(text=note_category)

        # Box that displays patient text
        self.pttext.config(state=NORMAL)
        self.pttext.delete(1.0, END)
        self.pttext.insert(END, clin_text.replace("\r\n", "\n"))
        self.pttext.config(state=DISABLED)

    def create_body(self):
        self.k1 = PanedWindow(self.master, height=700, width=900, orient=VERTICAL)
        self.k1.pack(fill=BOTH, expand=1)

        # Title
        self.title = PanedWindow(self.k1)
        self.k1.add(self.title, padx=10, pady=10)

        self.openbutton = Button(self.title,
                                 text="Open CSV",
                                 command=self.openfile,
                                 padx=15)
        self.openbutton.place(anchor=W, x=20, rely=0.25)
        image = Image.open('CCI.png')
        photo = ImageTk.PhotoImage(image)
      
        self.panel = Label(self.title, image=photo)
        self.panel.image = photo
        self.panel.pack(side=RIGHT, padx=10)

        Label(self.title, text=self.title_text,
              font=self.titlefont,
              fg="dodgerblue4").pack()

        # Panes below buttons
        self.k3 = PanedWindow(self.k1)
        self.k1.add(self.k3)
        self.leftpane = PanedWindow(self.k3)
        self.k3.add(self.leftpane,
                    width=400,
                    padx=30,
                    pady=25,
                    stretch="first")
        self.separator = PanedWindow(self.k3,
                                     relief=SUNKEN)
        self.k3.add(self.separator,
                    width=2,
                    padx=1,
                    pady=20)
        self.rightpane = PanedWindow(self.k3)
        self.k3.add(self.rightpane,
                    width=250,
                    padx=10,
                    pady=25,
                    stretch="never")

        # Left pane patient note text frame doo-diddly
        self.ptframe = LabelFrame(self.leftpane,
                                  text="Medical Record",
                                  font=self.boldfont,
                                  padx=0,
                                  pady=0,
                                  borderwidth=0)
        self.ptframe.pack()

        self.ptnumberframe = Frame(self.ptframe,
                                   padx=0,
                                   pady=0,
                                   borderwidth=0)
        self.ptnumberframe.pack()

        self.ptnumber_A = Label(self.ptnumberframe, text="Patient", fg="dodgerblue4")
        self.ptnumber_A.grid(row=1, column=0)
        self.ptnumber = Label(self.ptnumberframe, text=" ")
        self.ptnumber.grid(row=1, column=1)
        self.ptnumber_B = Label(self.ptnumberframe, text="of", fg="dodgerblue4")
        self.ptnumber_B.grid(row=1, column=2)
        self.pttotal = Label(self.ptnumberframe, text=" ")
        self.pttotal.grid(row=1, column=3)

        self.ptframeinfo = Frame(self.ptframe,
                                 padx=0,
                                 pady=3,
                                 borderwidth=0)
        self.ptframeinfo.pack()
        self.ptframeinfo.columnconfigure(1, minsize=300)

        self.phAdm_ = Label(self.ptframeinfo, text="Hospital Admission ID:", fg="dodgerblue4")
        self.phAdm_.grid(row=2, column=0, sticky=E)
        self.pthAdm = Label(self.ptframeinfo, text=" ", font=self.h3font)
        self.pthAdm.grid(row=2, column=1, sticky=W)

        self.ptnotetype_ = Label(self.ptframeinfo, text="Note Type:", fg="dodgerblue4")
        self.ptnotetype_.grid(row=3, column=0, sticky=E)
        self.ptnotetype = Label(self.ptframeinfo, text=" ", font=self.h3font)
        self.ptnotetype.grid(row=3, column=1, sticky=W)

        # Incrementer buttons
        self.buttonframe = Frame(self.ptframe)
        self.buttonframe.pack()
        self.buttonframe.place(relx=0.97, anchor=NE)
        # Back Button
        self.button1 = Button(self.buttonframe,
                              text='Back',
                              width=6,
                              command=lambda: self.crane(-1, self.results_filename))  # Argument is -1, decrement
        self.button1.grid(row=0, column=0, padx=2, pady=2)
        # Next Button
        self.button2 = Button(self.buttonframe,
                              text='Next',
                              width=6,
                              command=lambda: self.crane(1, self.results_filename))  # Argument is 1, increment
        self.button2.grid(row=0, column=2, padx=2, pady=2)

        # https://stackoverflow.com/questions/21873195/readonly-tkinter-text-widget
        self.pttext = ScrolledText(self.ptframe, font=self.textfont)
        self.pttext.pack(side=BOTTOM)
        self.pttext.delete(1.0, END)
        self.pttext.config(state=DISABLED)
        self.pttext.bind("<1>", lambda event: self.pttext.focus_set())

        self.checkframe = LabelFrame(self.rightpane, text="Indicators",
                                     font=self.boldfont,
                                     padx=10,
                                     pady=0,
                                     borderwidth=0)
        self.checkframe.pack()
        self.create_display_values(1, "NA", "NA", "Please use the ''Open CSV'' button to open the .csv file provided to you, "
                           + "for example:\n'dischargeSummaries29JUN16.csv'\n"
                           + "This will create a 'results' file within the same directory.")
