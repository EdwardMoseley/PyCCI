import csv
from numpy import NaN, isnan
import os
import pandas as pd
import time
import tkFont
import tkFileDialog
import tkMessageBox
import Tkinter as tk


class AnnotationPanel(tk.Frame):
    def __init__(self, master, checkframe, textbox_labels, checkbox_labels):
        self.master = master
        self.checkframe = checkframe
        tk.Frame.__init__(self, self.master)
        self.textboxes = {}
        self.textbox_labels = textbox_labels
        self.checkbox_labels = checkbox_labels
        self.indicator_values = {label: 0 for label in self.textbox_labels + self.checkbox_labels}
        self.create_annotation_items()

    ### Initialization of annotation panel widgets
    def create_annotation_items(self):
        '''
        Creates the checkbuttons and text entry box
        The part of the gui that covers annotations
        '''
        for item in self.textbox_labels:
            checkbox = self.create_checkbox(item)
            self.create_textbox(item, checkbox)

        for item in self.checkbox_labels:
            cehckbox = self.create_checkbox(item)

    def create_checkbox(self, label):
        checkbox_val = tk.IntVar()
        checkbox_val.set(self.indicator_values[label])
        self.indicator_values[label] = checkbox_val
        l = tk.Checkbutton(self.checkframe,
                        text=label,
                        variable=checkbox_val,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=tk.LEFT)
        l.pack(anchor=tk.W)
        return l

    def create_textbox(self, label, checkbox):
        entry_text = tk.StringVar()
        original_text = label + " Text"
        entry_text.set(original_text)
        entry = tk.Entry(self.checkframe, width=30, textvariable=entry_text)
        entry.pack(anchor=tk.W, pady=5)
        entry.bind("<BackSpace>", lambda event: self.handle_backspace(event, entry_text, checkbox, original_text))
        entry.bind("<Key>", lambda event: self.handle_key(event, entry_text, checkbox))
        entry.bind("<Button-1>", lambda event: self.clear_entry(event, entry, entry_text, checkbox, original_text))
        self.textboxes[label] = entry_text

    def handle_backspace(self, event, entry_text, checkbox, original_text):
        if len(entry_text.get()) < 2:
            checkbox.deselect()
            entry_text.set(original_text)

    def handle_key(self, event, entry_text, checkbox):
        if len(event.char) > 0:
            checkbox.select()

    def clear_entry(self, event, entry, entry_text, checkbox, original_text):
        if entry_text.get() == original_text:
            entry.delete(0,tk.END)
    
    ### Results file generation
    def save_annotations(self, data_df, row_index, results_filename):
        '''
        save_annotations() is called every time "Next" or "Back" are pressed
        save_annotations() will create a results file if one does not exist
        save_annotations() will pass if no indicators are ticked
        save_annotations() will write to results file if any indicator is ticked
        '''
        # If the file does not exist, create it and add the header
        data_labels = list(data_df.columns.values)
        if not os.path.isfile(results_filename):
            with open(results_filename, 'w') as csvfile:
                datawriter = csv.writer(csvfile, delimiter=',')
                datawriter.writerow(self.generate_header(data_labels))

        else:
            indicator_ints = [val.get() for val in self.indicator_values.values()]
            if sum(indicator_ints) != 0:
                results_df = pd.read_csv(results_filename, header=0, index_col=0)
                results_dict = self.generate_results_dict(data_df, row_index)
                if results_dict == None:
                    return False
                results_df = results_df.append(results_dict, ignore_index=True)
                results_df.to_csv(results_filename)
        self.reset_buttons()
        return True

    def generate_results_dict(self, data_df, row_index):
        results = {}
        for item in list(data_df.columns.values):
            results[item] = data_df[item].iloc[row_index]

        for i, item in enumerate(self.textbox_labels):
            results[item] = self.indicator_values[item].get()
            if results[item] == 1:
                # Clean up the annotated text phrase; remove all white space characters and replace
                # with a single space. If whitespace is on either side, removes that.
                # Character start:end reflects this matched against a cleaned
                # version of the original text. However, the saved annotation text phrase is the
                # uncleaned version.
                cleaned_annotation = " ".join(self.textboxes[item].get().split())
                results[item + " Text"] = self.textboxes[item].get()
                # Find annotated portion in cleaned clinical text.
                start_index = " ".join(data_df['TEXT'].iloc[row_index].split()).find(cleaned_annotation)
                if start_index == -1:
                    tkMessageBox.showerror("Error", "Text in " + item + " textbox is not found in original note.")
                    return None
                if len(results[item + " Text"]) < 1:
                    tkMessageBox.showerror("Error", "No text in textbox")
                    return None
                end_index = start_index + len(cleaned_annotation)
            else:
                results[item + " Text"] = NaN
                start_index = NaN
                end_index = NaN

            results[item + ':start'] = start_index
            results[item + ':end'] = end_index

        for item in self.checkbox_labels:
            results[item] = self.indicator_values[item].get()
        
        if 'ISERROR' in results:
            if isnan(results['ISERROR']):
                results['ISERROR'] = 0
        results['STAMP'] = str(time.asctime(time.localtime(time.time())))
        return results

    def generate_header(self, data_labels):
        header = ['Index'] 
        for item in data_labels:
            header.append(item)
        for item in self.textbox_labels:
            header.append(item)
            header.append(item + " Text")
            header.append(item + ':start')
            header.append(item + ":end")

        for item in self.checkbox_labels:
            header.append(item)
        header.append('STAMP')
        return header

    def reset_buttons(self):
        for key, val in self.textboxes.iteritems():
            val.set(key + " Text")
        for machine in self.textbox_labels + self.checkbox_labels:
            self.indicator_values[machine].set(0)
