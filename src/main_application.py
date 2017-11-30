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
import tkMessageBox


class MainApplication(tk.Frame):
    def __init__(self, master, title, textbox_labels, comment_boxes, checkbox_labels, reviewer_labels):
        self.master = master
        self.title = title
        self.reviewer_labels = reviewer_labels
        tk.Frame.__init__(self, self.master)
       
        # Define variables
        self.title_text = "\t\t" + self.title + " Indications GUI"
        self.file = None
        self.comparison_files = None
        self.is_comparison_mode = False
        self.current_row_index = 0
        self.current_results_note = 0
        self.data_df = pd.DataFrame()
        self.results_filename = None
        
        self.ann_file_prefix = None
        self.total_notes_df = None
        self.total_ann_df = None
        self.total_ann_df_edits = None
        self.current_ann_filename = None
        self.tag_label_dict = {}
        # Create GUI
        self._define_fonts()
        self._create_body()

        self.annotation_panel = AnnotationPanel(master, self.checkframe, textbox_labels, comment_boxes, checkbox_labels)
        self.annotation_panel.pack()

    def crane(self, delta, results_filename):
        '''
        Called whenever you press back or next
        '''
        # Save labels changed
        if self.is_comparison_mode:
            self._change_comparison_note(delta)
        else:
            is_saved = self.save_annotations()
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

        self.is_comparison_mode = False
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
        self.comparison_files = tkFileDialog.askopenfilenames(parent=self.master,title='Select two files')
        self.comparison_files = self.master.tk.splitlist(self.comparison_files)
        
        if not self.comparison_files:
            tkMessageBox.showerror("Please select two files.")
            return
        if len(self.comparison_files) < 2:
            tkMessageBox.showerror("Please select two files.")
            return   

        file1 = self.comparison_files[0]
        file2 = self.comparison_files[1]

        total_ann_file = None
        total_notes_file = None
        if 'all_notes' in file1:
            total_notes_file = file1
            total_ann_file = file2
        elif 'all_notes' in file2:
            total_notes_file = file2
            total_ann_file = file1

        if total_ann_file is None or total_notes_file is None:
            tkMessageBox.showerror("Please select a file with 'train, 'valid,' or 'test' annotations and a file with all notes.")
            return
        # Get file prefix
        if 'train' in total_ann_file:
            self.ann_file_prefix = 'train_text_'
        elif 'valid' in total_ann_file:
            self.ann_file_prefix = 'valid_text_'
        elif 'test' in total_ann_file:
            self.ann_file_prefix = 'test_text_'
        else:
            # Show error
            tkMessageBox.showerror("Please select a file with 'train, 'valid,' or 'test' annotations.")
            return

        self.is_comparison_mode = True

        self.total_notes_df = pd.read_csv(total_notes_file, index_col=0, header=0)
        self.total_ann_df = pd.read_csv(total_ann_file, index_col=0, header=0)
        row_ids = [int(f[-5:]) for f in self.total_ann_df['filename'].unique()]
        self.total_notes_df = self.total_notes_df[self.total_notes_df.index.isin(row_ids)]

        # If review edits file exists
        self.reviewer_edits_filename = total_ann_file[:-4] + "_reviewed.csv"
        if os.path.isfile(self.reviewer_edits_filename):
            self.total_ann_df_edits = pd.read_csv(self.reviewer_edits_filename, index_col=0, header=0, dtype=str)
        else:
            self.total_ann_df_edits = pd.read_csv(total_ann_file, index_col=0, header=0, dtype=str)
            self.total_ann_df_edits['reviewer_ann'] = ""
        self._change_comparison_note(0)

    def _change_comparison_note(self, delta):
        num_notes = self.total_notes_df.shape[0]
        self.current_results_note += delta
        if self.current_results_note < 1:
            self.current_results_note = 0
        if self.current_results_note > num_notes-1:
            self.current_results_note = num_notes-1

        current_row = self.total_notes_df.iloc[self.current_results_note]
        note_num = int(current_row.name)
        note_num = format(note_num, '05d')
        self.current_ann_filename = self.ann_file_prefix + note_num

        ann_df = self.total_ann_df[self.total_ann_df['filename'] == self.current_ann_filename]
        admission_id = current_row['HADM_ID']
        note_category = current_row['CATEGORY']
        clin_text = current_row['TEXT']

        self._create_display_values(self.current_results_note, num_notes, admission_id, note_category, clin_text, ann_df)

    def save_annotations(self):
        if self.is_comparison_mode:
            self.total_ann_df_edits.to_csv(self.reviewer_edits_filename)
            return True
        else:
            return self.annotation_panel.save_annotations(self.data_df, self.current_row_index, self.results_filename)

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
        self._create_display_values(self.current_row_index, num_notes, admission_id, note_category, clin_text)

    def _clean_text(self, text):
        cleaned = str(text.replace('\r\r', '\n').replace('\r', ''))
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r' +', ' ', cleaned)
        cleaned = re.sub(r'\t', ' ', cleaned)
        return str(cleaned.strip())

    def delete_tag(self, tag_name, start, end, char_start, key):
        # Change the tag label dict to reflect these changes
        # Delete the tag
        self.pttext.tag_remove(tag_name, start, end)
        self.tag_label_dict.pop(key, None)
        # Add information to annotation file
        char_start = char_start
        match = self.total_ann_df_edits.index[(self.total_ann_df_edits.filename == self.current_ann_filename) & (self.total_ann_df_edits.start == char_start)].tolist()
        index = match[0]
        self.total_ann_df_edits.at[index, 'reviewer_ann'] = 'O'
        
    def change_tag(self, tag_add, tag_name, start, end, char_start, label, key):
        # Change the tag label dict to reflect these changes
        # Change tag to be machine color
        self.pttext.tag_remove(tag_name, start, end)
        self.pttext.tag_add(tag_add, start, end)
        self.tag_label_dict[key] = ['reviewer: ' + label]
        # Add information to annotation file
        match = self.total_ann_df_edits.index[(self.total_ann_df_edits.filename == self.current_ann_filename) & (self.total_ann_df_edits.start == char_start)].tolist()
        index = match[0]
        self.total_ann_df_edits.at[index, 'reviewer_ann'] = 'B-' + label
        
    # https://stackoverflow.com/questions/3296893/how-to-pass-an-argument-to-event-handler-in-tkinter
    def _on_tag_click(self, event, tag_name):
        # get the index of the mouse click
        index = event.widget.index("@%s,%s" % (event.x, event.y))
        tag_indices = list(event.widget.tag_ranges(tag_name))

        # iterate them pairwise (start and end index)
        for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
            # check if the tag matches the mouse click index
            if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
                add_human = False
                add_machine = False
                human_label = None
                machine_label = None
                tag_text = event.widget.get(start, end)
                popup_menu = tk.Menu(self.master, tearoff=0)
                char_start = str(self.master.call(event.widget, "count", "1.0", start))
                key = '1.0+' + char_start + 'c'
                for item in self.tag_label_dict[key]:
                    popup_menu.add_command(label=item, command='')
                    if 'human' in item:
                        add_human = True
                        human_label = item.split(" ")[1]
                    if 'machine' in item:
                        add_machine = True
                        machine_label = item.split(" ")[1]

                # Add separator
                popup_menu.add_separator()
                popup_menu.add_command(label="Delete", command=lambda: self.delete_tag(tag_name, start, end, char_start, key))
                if add_human:
                    popup_menu.add_command(label="Accept Human", command=lambda: self.change_tag("human", tag_name, start, end, char_start, human_label, key))
                if add_machine:
                    popup_menu.add_command(label="Accept Machine", command=lambda: self.change_tag("machine", tag_name, start, end, char_start, machine_label, key))
                label_menu = tk.Menu(popup_menu, tearoff=0)
                for label in self.reviewer_labels:
                    label_menu.add_command(label=label, command=lambda: self.change_tag("reviewer", tag_name, start, end, char_start, label, key))
                popup_menu.add_cascade(label="Change Label", menu=label_menu)
                popup_menu.tk_popup(event.x_root, event.y_root, 0)

    # Creates items displayed in the notes panel. Adds highlights if in comparison mode.
    def _create_display_values(self, current_note_num, total, admission_id, note_category, clin_text, ann_df=None):
        # Fill display values
        self.ptnumber.config(text=str(current_note_num + 1))
        self.pttotal.config(text=str(total))

        self.pthAdm.config(text=admission_id)
        self.ptnotetype.config(text=note_category)

        # Box that displays patient text
        self.pttext.config(state=tk.NORMAL)
        self.pttext.delete(1.0, tk.END)
        self.pttext.insert(tk.END, clin_text)
        self.pttext.config(state=tk.DISABLED)
        if self.is_comparison_mode and ann_df is not None:
            # Tags
            self.pttext.tag_config('human', background='gold')
            self.pttext.tag_config('machine', background='light sky blue')
            self.pttext.tag_config('overlap_agree', background='green yellow')
            self.pttext.tag_config('overlap_disagree', background='indian red')
            self.pttext.tag_config('reviewer', background='orange2')
            # Map start -> label
            self.tag_label_dict = {}
            start = '1.0'
            keyword = 'a'
            # Iterates through all tokens in note
            # TODO: handle if note has been reviewed
            for index, row in ann_df.iterrows():
                manual_ann = row['manual_ann']
                machine_ann = row['machine_ann'] 
                
                # TODO: Right click to see what the tag is
                pos_start = '{}+{}c'.format(start, row['start'])
                pos_end = '{}+{}c'.format(start, row['end'])
                # Neither tagged
                if manual_ann == 'O' and machine_ann == 'O':
                    continue
                # Tagged same (overlap_agree)
                elif manual_ann == machine_ann:
                    self.pttext.tag_add('overlap_agree', pos_start, pos_end)
                    self.tag_label_dict[pos_start] = ['both: ' + manual_ann.split('-')[1]]
                # Tagged different (overlap_disagree)
                elif manual_ann != 'O' and machine_ann != 'O':
                    self.pttext.tag_add('overlap_disagree', pos_start, pos_end)
                    self.tag_label_dict[pos_start] = ['human: ' + manual_ann.split('-')[1],
                        'machine: ' + machine_ann.split('-')[1]]
                # Human tagged
                elif machine_ann == 'O' and manual_ann != 'O':
                    self.pttext.tag_add('human', pos_start, pos_end)
                    self.tag_label_dict[pos_start] = ['human: ' + manual_ann.split('-')[1], 'machine: 0']
                # Machine tagged
                elif machine_ann != 'O' and manual_ann == 'O':
                    self.pttext.tag_add('machine', pos_start, pos_end)
                    self.tag_label_dict[pos_start] = ['human: 0', 'machine: ' + machine_ann.split('-')[1]]
                else:
                    continue
            self.pttext.tag_bind("human", "<Button-1>", lambda event: self._on_tag_click(event, 'human'))
            self.pttext.tag_bind("machine", "<Button-1>", lambda event: self._on_tag_click(event, 'machine'))
            self.pttext.tag_bind("overlap_agree", "<Button-1>", lambda event: self._on_tag_click(event, 'overlap_agree'))
            self.pttext.tag_bind("overlap_disagree", "<Button-1>", lambda event: self._on_tag_click(event, 'overlap_disagree'))
            self.pttext.tag_bind("reviewer", "<Button-1>", lambda event: self._on_tag_click(event, 'reviewer'))

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

        self.otherb = tk.Button(self.upper_section,
                                 text="Open Results",
                                 command=self.open_results_file,
                                 padx=15)
        self.otherb.place(anchor=tk.W, x=130, rely=0.25)

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
        self.bottom_section.add(self.leftpane,
                    width=600,
                    padx=20)
        self.separator = tk.PanedWindow(self.bottom_section,
                                     relief=tk.SUNKEN)
        self.bottom_section.add(self.separator,
                    width=2,
                    padx=5,
                    pady=30)
        self.rightpane = tk.PanedWindow(self.bottom_section)
        self.bottom_section.add(self.rightpane, width=400)

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
                                       command=self.save_annotations)
        self.submit_button.grid(row=0, column=0, padx=2, pady=10)

        # Create canvas with scrollbar
        canvas = tk.Canvas(self.rightpane)
        scrollbar = tk.Scrollbar(self.rightpane, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        canvas.pack(side=tk.LEFT, fill='both', expand=True)
        
        # put frame in canvas

        self.checkframe = tk.LabelFrame(canvas, text="Indicators",
                                     font=self.boldfont,
                                     padx=10,
                                     pady=20,
                                     borderwidth=0)
        canvas.create_window((0,0), window=self.checkframe, anchor='nw', tags='self.checkframe')
        self.checkframe.bind('<Configure>', lambda event: self.on_configure(event,canvas))


        #self.checkframe.pack(fill=tk.BOTH, expand=True)
        self._create_display_values(0, 1, "NA", "NA", "Please use the ''Open CSV'' button to open the .csv file provided to you, "
                           + "for example:\n'dischargeSummaries29JUN16.csv'\n"
                           + "This will create a 'results' file within the same directory.")
    def on_configure(self, event, canvas):
        canvas.configure(scrollregion=canvas.bbox('all'))
