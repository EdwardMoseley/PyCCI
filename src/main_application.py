from annotation_panel import *
import csv
import numpy as np
import os
import pandas as pd
from ScrolledText import ScrolledText
import sys
import re
import time
import tkFont
import tkFileDialog
import Tkinter as tk
from PIL import ImageTk, Image


class MainApplication(tk.Frame):
    def __init__(self, master, title, textbox_labels, comment_boxes, checkbox_labels):
        self.master = master
        self.title = title
        tk.Frame.__init__(self, self.master)
       
        # Define variables
        self.title_text = "\t\t" + self.title + " Indications GUI"
        self.file = None
        self.directory = None
        self.is_comparison_version = False
        self.current_row_index = 0
        self.data_df = pd.DataFrame()
        
        # Create GUI
        self._define_fonts()
        self._create_body()

        self.annotation_panel = AnnotationPanel(master, self.checkframe, textbox_labels, comment_boxes, checkbox_labels)
        self.annotation_panel.pack()

    def crane(self, delta, results_filename):
        '''
        Called whenever you press back or next
        '''
        is_saved = self.save_annotations(results_filename)
        if not is_saved:
            return
        self._change_note(delta)

    def openfile(self):
        if self.file is not None:
            # TODO: Popup
            return

        self.file = tkFileDialog.askopenfilename()
        if not self.file:
            return
        self.data_df = pd.read_csv(self.file)
        # Clean all the text fields
        self.data_df['TEXT'] = self.data_df['TEXT'].map(lambda text: self._clean_text(text))

        # If the file already exists, open it and continue at the spot you were,
        # makes it easier to continue on annotating results
        self.results_filename = self.file[:-4] + "Results.csv"
        if os.path.isfile(self.results_filename):
            results_df = pd.read_csv(self.results_filename)
            # Get ROW_ID of last row
            # Find iloc of ROW_ID in data_df. Crane to this position.
            if 'ROW_ID' in results_df:
                last_row_id = results_df.iloc[-1]['ROW_ID']
                crane_to = self.data_df[self.data_df['ROW_ID'] == last_row_id].index.tolist()[0]
                self._change_note(crane_to + 1)
            else:
                self._change_note(0)
        else:
            self._change_note(0)

    # Open a results file where annotations can be viewed and edited
    def open_results_file(self):
        if self.directory is not None:
            # TODO: popup
            return
        self.directory = tkFileDialog.askdirectory()
        if not self.directory:
            return

        self.is_comparison_version = True
        # Read in first file, using annotations + original text
        print os.listdir(self.directory)

    def _change_comparison_note(self, delta):
        self._create_display_values(10, 100, 'Clinician', 'derp derp derp')
        # Add highlighting

    def save_annotations(self, results_filename):
        return self.annotation_panel.save_annotations(self.data_df, self.current_row_index, results_filename)

    def _define_fonts(self):
        self.titlefont = tkFont.Font(size=16, weight='bold')
        self.boldfont = tkFont.Font(size=14, weight='bold')
        self.textfont = tkFont.Font(family='Helvetica', size=15)
        self.h3font = tkFont.Font(size=11)

    def _resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def _change_note(self, delta):
        num_notes = self.data_df.shape[0]
        self.current_row_index += delta
        if self.current_row_index < 1:
            self.current_row_index = 0

        if self.current_row_index > num_notes-1:
            self.current_row_index = num_notes-1

        admission_id = self.data_df['HADM_ID'].iloc[self.current_row_index]
        note_category = self.data_df['CATEGORY'].iloc[self.current_row_index]
        clin_text = self.data_df['TEXT'].iloc[self.current_row_index]
        self._create_display_values(num_notes, admission_id, note_category, clin_text)

    def _clean_text(self, text):
        cleaned = str(text.replace('\r\r', '\n').replace('\r', ''))
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r' +', ' ', cleaned)
        cleaned = re.sub(r'\t', ' ', cleaned)
        return str(cleaned.strip())

    def _create_display_values(self, total, admission_id, note_category, clin_text):
        # Fill display values
        self.ptnumber.config(text=str(self.current_row_index + 1))
        self.pttotal.config(text=str(total))

        self.pthAdm.config(text=admission_id)
        self.ptnotetype.config(text=note_category)

        # Box that displays patient text
        self.pttext.config(state=tk.NORMAL)
        self.pttext.delete(1.0, tk.END)
        self.pttext.insert(tk.END, clin_text)
        self.pttext.config(state=tk.DISABLED)

    def _create_body(self):
        width, height = 1200, self.master.winfo_screenheight()/1.1
        self.main_window = tk.PanedWindow(self.master, height=height, width=width, orient=tk.VERTICAL)
        self.main_window.pack(fill=tk.BOTH, expand=True)

        # Title
        self.master.title(self.title + " PyCCI")
        self.upper_section = tk.PanedWindow(self.main_window)
        self.main_window.add(self.upper_section, padx=10, pady=10)

        self.openbutton = tk.Button(self.upper_section,
                                 text="Open CSV",
                                 command=self.openfile,
                                 padx=15)
        self.openbutton.place(anchor=tk.W, x=20, rely=0.25)

        # self.otherb = tk.Button(self.upper_section,
        #                          text="Open Results",
        #                          command=self.open_results_file,
        #                          padx=15)
        # self.otherb.place(anchor=tk.W, x=130, rely=0.25)

        image = Image.open(self._resource_path('CCI.png'))
        photo = ImageTk.PhotoImage(image)
      
        self.panel = tk.Label(self.upper_section, image=photo)
        self.panel.image = photo
        self.panel.pack(side=tk.RIGHT, padx=10)

        tk.Label(self.upper_section, text=self.title_text,
              font=self.titlefont,
              fg="dodgerblue4").pack()

        # Panes below buttons
        self.bottom_section = tk.PanedWindow(self.main_window)
        self.bottom_section.pack(fill=tk.BOTH, expand=True)
        self.main_window.add(self.bottom_section)
        self.leftpane = tk.PanedWindow(self.bottom_section)
        self.leftpane.pack(fill=tk.BOTH, expand=True)
        self.bottom_section.add(self.leftpane,
                    width=700,
                    padx=30)
        self.separator = tk.PanedWindow(self.bottom_section,
                                     relief=tk.SUNKEN)
        self.bottom_section.add(self.separator,
                    width=2,
                    padx=5,
                    pady=30)
        self.rightpane = tk.PanedWindow(self.bottom_section)
        self.rightpane.pack(fill=tk.BOTH, expand=True)
        self.bottom_section.add(self.rightpane, width=400)

        # Left pane patient note text frame doo-diddly
        self.ptframe = tk.LabelFrame(self.leftpane,
                                  text="Medical Record",
                                  font=self.boldfont,
                                  padx=0,
                                  pady=10,
                                  borderwidth=0)
        self.ptframe.pack(fill=tk.BOTH, expand=True)

        self.ptnumberframe = tk.Frame(self.ptframe,
                                   padx=6,
                                   pady=3,
                                   borderwidth=0)
        self.ptnumberframe.pack()

        self.ptnumber_A = tk.Label(self.ptnumberframe, text="Patient", fg="dodgerblue4")
        self.ptnumber_A.grid(row=1, column=0, sticky=tk.E)
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

        text_frame = tk.Frame(self.ptframe, borderwidth=1, relief="sunken")
        self.pttext = tk.Text(wrap="word", background="white", 
                            borderwidth=0, highlightthickness=0)
        self.vsb = tk.Scrollbar(orient="vertical", borderwidth=1,
                                command=self.pttext.yview)
        self.pttext.configure(yscrollcommand=self.vsb.set, font=self.textfont, padx=20, pady=20)
        self.vsb.pack(in_=text_frame,side="right", fill="y", expand=False)
        self.pttext.pack(in_=text_frame, side="left", fill="both", expand=True)
        self.pttext.bind("<1>", lambda event: self.pttext.focus_set())
        text_frame.pack(fill="both", expand=True)


        # Below buttons
        self.submit_frame = tk.Frame(self.ptframe)
        self.submit_frame.pack(side=tk.RIGHT)
        self.submit_button = tk.Button(self.submit_frame,
                                       text='Save Annotation',
                                       width=14,
                                       command=lambda: self.save_annotations(self.results_filename))
        self.submit_button.grid(row=0, column=0, padx=2, pady=10)

        self.checkframe = tk.LabelFrame(self.rightpane, text="Indicators",
                                     font=self.boldfont,
                                     padx=10,
                                     pady=20,
                                     borderwidth=0)
        self.checkframe.pack(fill=tk.BOTH, expand=True)
        self._create_display_values(1, "NA", "NA", "Please use the ''Open CSV'' button to open the .csv file provided to you, "
                           + "for example:\n'dischargeSummaries29JUN16.csv'\n"
                           + "This will create a 'results' file within the same directory.")
