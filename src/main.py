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
    root = Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    menubar = MenuBar(root)
    root.config(menu=menubar)
    root.mainloop()

if __name__ == '__main__':
    main()