from main_application import *
from menu_bar import *
import tkFont
import tkFileDialog
import Tkinter as tk


def main(): 
	title = "Palliative Care"
	textbox_labels = ["Care Preferences","Family Meetings", "Code Status Limitations", "Palliative Care Involvement"]
	checkbox_labels = ["Ambiguous", "None"]
	root = tk.Tk()
	MainApplication(root, title, textbox_labels, checkbox_labels).pack(side="top", fill="both", expand=True)
	menubar = MenuBar(root)
	root.config(menu=menubar)
	root.mainloop()

if __name__ == '__main__':
    main()