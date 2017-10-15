import csv
from main_application import *
from menu_bar import *
import numpy as np
import os
import pandas as pd
from ScrolledText import ScrolledText
import sys
import time
import tkFont
import tkFileDialog
from Tkinter import *


def main(): 
	title = "Palliative Care"
	textbox_labels = ["Care Preferences","Family Meetings", "Code Status Limitations", "Palliative Care Involvement"]
	checkbox_labels = ["Ambiguous", "None"]
	root = Tk()
	MainApplication(root, title, textbox_labels, checkbox_labels).pack(side="top", fill="both", expand=True)
	menubar = MenuBar(root)
	root.config(menu=menubar)
	root.mainloop()

if __name__ == '__main__':
    main()