import csv
from numpy import NaN, isnan
import os
import pandas as pd
import re
import time
import tkFont
import tkFileDialog
import tkMessageBox
import Tkinter as tk


class AnnotationPanel(tk.Frame):
    def __init__(self, master, checkframe, textbox_labels, comment_boxes, checkbox_labels):
        self.master = master
        self.checkframe = checkframe
        tk.Frame.__init__(self, self.master)
        self.textfont = tkFont.Font(family='Helvetica', size=15)
        self.smallfont = tkFont.Font(family='Helvetica', size=12)
        self.textbox_labels = textbox_labels
        self.comment_boxes = comment_boxes
        self.checkbox_labels = checkbox_labels
        self.text_columns = [label + " Text" for label in self.textbox_labels] + [label + " Comments" for label in self.comment_boxes]
        self.textboxes = {}
        self.comments = {}
        self.indicator_values = {label: 0 for label in self.textbox_labels + self.checkbox_labels}
        self.create_annotation_items()

    ### Initialization of annotation panel widgets
    def create_annotation_items(self):
        '''
        Creates the checkbuttons and text entry box
        The part of the gui that covers annotations
        '''
        for item in self.textbox_labels:
            checkbox, checkbox_val = self.create_checkbox(item)
            self.create_textbox(item, checkbox, checkbox_val)
        for item in self.comment_boxes:
            self.create_comment_box(item)
        for item in self.checkbox_labels:
            cehckbox = self.create_checkbox(item)

    def create_comment_box(self, label):
        original_text = label + " Comments"
        text_frame = tk.Frame(self.checkframe, borderwidth=1, relief="sunken")
        entry = tk.Text(wrap="word", background="white", 
                            borderwidth=0, highlightthickness=0, height=2)
        entry.insert(tk.END, original_text)
        vsb = tk.Scrollbar(orient="vertical", borderwidth=1,
                                command=entry.yview)
        entry.configure(yscrollcommand=vsb.set, font=self.smallfont, padx=3, pady=3)
        vsb.pack(in_=text_frame,side="right", fill="y", expand=False)
        entry.pack(in_=text_frame, side="left", fill="both", expand=True)
        text_frame.pack(anchor=tk.W, fill=tk.X, pady=5, padx=(0,5))
        entry.bind("<Button-1>", lambda event: self.clear_entry(event, entry, original_text))
        self.comments[label] = entry

    def create_checkbox(self, label):
        checkbox_val = tk.IntVar()
        checkbox_val.set(self.indicator_values[label])
        self.indicator_values[label] = checkbox_val
        checkbox = tk.Checkbutton(self.checkframe,
                        text=label,
                        variable=checkbox_val,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=tk.LEFT)
        checkbox.pack(anchor=tk.W)
        return checkbox, checkbox_val

    def create_textbox(self, label, checkbox, checkbox_val):
        original_text = label + " Text"
        text_frame = tk.Frame(self.checkframe, borderwidth=1, relief="sunken")
        entry = tk.Text(wrap="word", background="white", 
                            borderwidth=0, highlightthickness=0, height=2)
        entry.insert(tk.END, original_text)
        vsb = tk.Scrollbar(orient="vertical", borderwidth=1,
                                command=entry.yview)
        entry.configure(yscrollcommand=vsb.set, font=self.smallfont, padx=3, pady=3)
        vsb.pack(in_=text_frame,side="right", fill="y", expand=False)
        entry.pack(in_=text_frame, side="left", fill="both", expand=True)
        text_frame.pack(anchor=tk.W, fill=tk.X, pady=5, padx=(0,5))

        checkbox.bind("<Button-1>", lambda event: self.clear_entry_from_check(event, entry, checkbox_val, original_text))
        entry.bind("<BackSpace>", lambda event: self.handle_backspace(event, entry, checkbox, original_text))
        entry.bind("<Key>", lambda event: self.handle_key(event, checkbox))
        entry.bind("<Button-1>", lambda event: self.clear_entry(event, entry, original_text))
        self.textboxes[label] = entry

    def handle_backspace(self, event, entry, checkbox, original_text):
        if len(entry.get(1.0, 'end-1c')) < 2:
            checkbox.deselect()

    def handle_key(self, event, checkbox):
        if len(event.char) > 0:
            checkbox.select()

    def clear_entry(self, event, entry, original_text):
        if entry.get(1.0, 'end-1c') == original_text:
            entry.delete(1.0, tk.END)

    def clear_entry_from_check(self, event, entry, checkbox_val, original_text):
        if checkbox_val.get() == 1:
            entry.delete(1.0, tk.END)
    
    ### Results file generation
    def save_annotations(self, data_df, row_index, results_filename):
        '''
        save_annotations() is called every time "Next" or "Back" are pressed
        save_annotations() will create a results file if one does not exist if 
        an annotation is made
        save_annotations() will pass if no indicators are ticked
        save_annotations() will write to results file if any indicator is ticked
        '''
        # If the file does not exist, create it and add the header
        data_labels = self.generate_header(list(data_df.columns.values))
        indicator_ints = [val.get() for val in self.indicator_values.values()]
        if sum(indicator_ints) != 0:
            results_df = self.generate_results_dict(data_df, row_index, data_labels)
            if results_df is None:
                return False
            if os.path.isfile(results_filename):
                original_results_df = pd.read_csv(results_filename, header=0, index_col=0)
                # Clean results_df
                for label in self.text_columns:
                    if label in original_results_df:
                        original_results_df[label] = original_results_df[label].map(lambda text: self._clean_text(text))
                results_df = pd.concat([original_results_df, results_df], ignore_index=True)
            results_df = results_df[data_labels]
            results_df.to_csv(results_filename)
        self.reset_buttons()
        return True

    def _clean_text(self, text):
        if type(text) == float:
            return text
        cleaned = str(text.replace('\r\r', '\n').replace('\r', ''))
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r' +', ' ', cleaned)
        cleaned = re.sub(r'\t', ' ', cleaned)
        return str(cleaned.strip())

    def generate_results_dict(self, data_df, row_index, data_labels):
        results = {}
        for item in list(data_df.columns.values):
            if "Unnamed" not in item: 
                results[item] = data_df[item].iloc[row_index]

        for item in self.textbox_labels:
            results[item] = self.indicator_values[item].get()
            if results[item] == 1:
                # Strip annotation phrase. 
                annotation = self.textboxes[item].get(1.0, 'end-1c').strip()
                results[item + " Text"] = str(annotation)
                # Check that the text is actually in the clinical note (prevent copy errors)
                start_index = data_df['TEXT'].iloc[row_index].find(annotation)
                if start_index == -1:
                    tkMessageBox.showerror("Error", "Text in " + item + " textbox is not found in original note.")
                    return None
                if len(results[item + " Text"]) < 1:
                    tkMessageBox.showerror("Error", "No text in textbox")
                    return None
            else:
                results[item + " Text"] = NaN

        for item in self.comment_boxes:
            comment_text = self.comments[item].get(1.0, 'end-1c')
            if comment_text != item + " Comments":
                results[item + " Comments"] = str(comment_text)
            else:
                results[item + " Comments"] = NaN

        for item in self.checkbox_labels:
            results[item] = self.indicator_values[item].get()
        
        if 'ISERROR' in results:
            if isnan(results['ISERROR']):
                results['ISERROR'] = 0
        results['STAMP'] = str(time.asctime(time.localtime(time.time())))
        results = pd.DataFrame(results, columns=data_labels, index=[0])
        return results

    def generate_header(self, data_labels):
        header = [] 
        for item in data_labels:
            if "Unnamed" not in item:
                header.append(item)
        for item in self.textbox_labels:
            header.append(item)
            header.append(item + " Text")
        for item in self.comment_boxes:
            header.append(item + " Comments")
        for item in self.checkbox_labels:
            header.append(item)
        header.append('STAMP')
        return header

    def reset_buttons(self):
        for key, entry in self.textboxes.iteritems():
            entry.delete(1.0,tk.END)
            entry.insert(tk.END, key + " Text")
        for key, entry in self.comments.iteritems():
            entry.delete(1.0,tk.END)
            entry.insert(tk.END, key + " Comments")
        for machine in self.textbox_labels + self.checkbox_labels:
            self.indicator_values[machine].set(0)
