from main_application import *
from menu_bar import *
import tkFont
import tkFileDialog
import Tkinter as tk

def main(): 
	title = "Palliative Care"
	textbox_labels = ["Patient and Family Care Preferences","Communication with Family", "Full Code Status", "Code Status Limitations", "Palliative Care Team Involvement", "Ambiguous"]
	comment_boxes = ["Ambiguous"]
	checkbox_labels = ["None"]
	reviewer_labels = ["COD", "FAM", "LIM", "PAL", "CAR"]
	root = tk.Tk()
	MainApplication(root, title, textbox_labels, comment_boxes, checkbox_labels, reviewer_labels).pack(side="top", fill="both", expand=True)
	menubar = MenuBar(root)
	root.config(menu=menubar)
	root.mainloop()

if __name__ == '__main__':
    main()