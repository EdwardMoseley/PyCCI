from main_application import *
from menu_bar import *
import tkFont
import tkFileDialog
import Tkinter as tk


def main(): 
	title = "Palliative Care"
	textbox_labels = ["Patient and Family Care Preferences","Communication with Family", "Code Status Limitations", "Palliative Care Team Involvement", "Ambiguous"]
	checkbox_labels = ["None"]
	root = tk.Tk()
	MainApplication(root, title, textbox_labels, checkbox_labels).pack(side="top", fill="both", expand=True)
	menubar = MenuBar(root)
	root.config(menu=menubar)
	root.mainloop()

if __name__ == '__main__':
    main()