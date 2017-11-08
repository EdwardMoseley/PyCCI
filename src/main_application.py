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
import Tkinter as tk
from PIL import ImageTk, Image


class MainApplication(tk.Frame):
    def __init__(self, master, title, textbox_labels, comment_boxes, checkbox_labels):
        self.master = master
        self.title = title
        self.master.title(self.title + " PyCCI")
        tk.Frame.__init__(self, self.master)
       
        # Define variables
        self.title_text = "\t\t" + self.title + " Indications GUI"
        self.current_row_index = 0
        self.data_df = pd.DataFrame()
        
        # Create GUI
        self.define_fonts()
        self.create_body()

        self.annotation_panel = AnnotationPanel(master, self.checkframe, textbox_labels, comment_boxes, checkbox_labels)
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
            last_row_id = results_df.iloc[-1]['ROW_ID']
            crane_to = self.data_df[self.data_df['ROW_ID'] == last_row_id].index.tolist()[0]
            # Get ROW_ID of last row
            # Find iloc of ROW_ID in data_df. Crane to this position.
            self.crane(crane_to + 1, self.results_filename)
        else:
            self.crane(0, self.results_filename)

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def save_annotations(self, results_filename):
        return self.annotation_panel.save_annotations(self.data_df, self.current_row_index, results_filename)

    def crane(self, delta, results_filename):
        '''
        Called whenever you press back or next
        '''
        is_saved = self.save_annotations(results_filename)
        if not is_saved:
            return

        num_notes = self.data_df.shape[0]
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
        self.pttext.config(state=tk.NORMAL)
        self.pttext.delete(1.0, tk.END)
        self.pttext.insert(tk.END, clin_text.replace("\r\n", "\n"))
        self.pttext.config(state=tk.DISABLED)

    def create_body(self):
        self.k1 = tk.PanedWindow(self.master, height=700, width=900, orient=tk.VERTICAL)
        self.k1.pack(fill=tk.BOTH, expand=1)

        # Title
        self.title = tk.PanedWindow(self.k1)
        self.k1.add(self.title, padx=10, pady=10)

        self.openbutton = tk.Button(self.title,
                                 text="Open CSV",
                                 command=self.openfile,
                                 padx=15)
        self.openbutton.place(anchor=tk.W, x=20, rely=0.25)
        image = Image.open(self.resource_path('CCI.png'))
        photo = ImageTk.PhotoImage(image)
      
        self.panel = tk.Label(self.title, image=photo)
        self.panel.image = photo
        self.panel.pack(side=tk.RIGHT, padx=10)

        tk.Label(self.title, text=self.title_text,
              font=self.titlefont,
              fg="dodgerblue4").pack()

        # Panes below buttons
        self.k3 = tk.PanedWindow(self.k1)
        self.k1.add(self.k3)
        self.leftpane = tk.PanedWindow(self.k3)
        self.k3.add(self.leftpane,
                    width=400,
                    padx=30,
                    pady=25,
                    stretch="first")
        self.separator = tk.PanedWindow(self.k3,
                                     relief=tk.SUNKEN)
        self.k3.add(self.separator,
                    width=2,
                    padx=1,
                    pady=20)
        self.rightpane = tk.PanedWindow(self.k3)
        self.k3.add(self.rightpane,
                    width=250,
                    padx=10,
                    pady=25,
                    stretch="never")

        # Left pane patient note text frame doo-diddly
        self.ptframe = tk.LabelFrame(self.leftpane,
                                  text="Medical Record",
                                  font=self.boldfont,
                                  padx=0,
                                  pady=0,
                                  borderwidth=0)
        self.ptframe.pack()

        self.ptnumberframe = tk.Frame(self.ptframe,
                                   padx=0,
                                   pady=0,
                                   borderwidth=0)
        self.ptnumberframe.pack()

        self.ptnumber_A = tk.Label(self.ptnumberframe, text="Patient", fg="dodgerblue4")
        self.ptnumber_A.grid(row=1, column=0)
        self.ptnumber = tk.Label(self.ptnumberframe, text=" ")
        self.ptnumber.grid(row=1, column=1)
        self.ptnumber_B = tk.Label(self.ptnumberframe, text="of", fg="dodgerblue4")
        self.ptnumber_B.grid(row=1, column=2)
        self.pttotal = tk.Label(self.ptnumberframe, text=" ")
        self.pttotal.grid(row=1, column=3)

        self.ptframeinfo = tk.Frame(self.ptframe,
                                 padx=0,
                                 pady=3,
                                 borderwidth=0)
        self.ptframeinfo.pack()
        self.ptframeinfo.columnconfigure(1, minsize=300)

        self.phAdm_ = tk.Label(self.ptframeinfo, text="Hospital Admission ID:", fg="dodgerblue4")
        self.phAdm_.grid(row=2, column=0, sticky=tk.E)
        self.pthAdm = tk.Label(self.ptframeinfo, text=" ", font=self.h3font)
        self.pthAdm.grid(row=2, column=1, sticky=tk.W)

        self.ptnotetype_ = tk.Label(self.ptframeinfo, text="Note Type:", fg="dodgerblue4")
        self.ptnotetype_.grid(row=3, column=0, sticky=tk.E)
        self.ptnotetype = tk.Label(self.ptframeinfo, text=" ", font=self.h3font)
        self.ptnotetype.grid(row=3, column=1, sticky=tk.W)

        # Incrementer buttons
        self.buttonframe = tk.Frame(self.ptframe)
        self.buttonframe.pack()
        self.buttonframe.place(relx=0.97, anchor=tk.NE)
        # Back Button
        self.back_button = tk.Button(self.buttonframe,
                              text='Back',
                              width=6,
                              command=lambda: self.crane(-1, self.results_filename))  # Argument is -1, decrement
        self.back_button.grid(row=0, column=0, padx=2, pady=0)
        # Next Button
        self.next_button = tk.Button(self.buttonframe,
                              text='Next',
                              width=6,
                              command=lambda: self.crane(1, self.results_filename))  # Argument is 1, increment
        self.next_button.grid(row=0, column=2, padx=2, pady=0)

        # https://stackoverflow.com/questions/21873195/readonly-tkinter-text-widget
        self.pttext = ScrolledText(self.ptframe, font=self.textfont)
        self.pttext.pack()
        self.pttext.delete(1.0, tk.END)
        self.pttext.config(state=tk.DISABLED)
        self.pttext.bind("<1>", lambda event: self.pttext.focus_set())

        # Below buttons
        self.submit_frame = tk.Frame(self.ptframe)
        self.submit_frame.pack(side=tk.RIGHT)
        self.submit_button = tk.Button(self.submit_frame,
                                       text='Save Annotation',
                                       width=10,
                                       command=lambda: self.save_annotations(self.results_filename))
        self.submit_button.grid(row=0, column=0, padx=2, pady=10)

        self.checkframe = tk.LabelFrame(self.rightpane, text="Indicators",
                                     font=self.boldfont,
                                     padx=10,
                                     pady=0,
                                     borderwidth=0)
        self.checkframe.pack()
        self.create_display_values(1, "NA", "NA", "Please use the ''Open CSV'' button to open the .csv file provided to you, "
                           + "for example:\n'dischargeSummaries29JUN16.csv'\n"
                           + "This will create a 'results' file within the same directory.")
