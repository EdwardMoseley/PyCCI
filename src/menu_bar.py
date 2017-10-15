import csv
import numpy as np
import os
import pandas as pd
from ScrolledText import ScrolledText
import sys
import time
import tkFont
import tkFileDialog
from Tkinter import *


class MenuBar(Menu):
    def __init__(self, master):
        Menu.__init__(self, master)
        filemenu = Menu(self, tearoff=0)
        helpmenu = Help(self)
        self.add_cascade(label="File", menu=filemenu)
        self.add_cascade(label="Help", menu=helpmenu)

class Help(Menu):
    def __init__(self, master):
        Menu.__init__(self, master, tearoff=0)
        self.add_command(label="About", command=self.about)
        self.add_command(label="Guidelines", command=self.info)
        
    def about(self):
        aboutpop = Toplevel()
        aboutpop.title("About Us")
        aboutpop.geometry('700x450')
        aboutfr = Frame(aboutpop)
        aboutfr.pack()
        Label(aboutfr, text='Important Information: This code was developed for use in Python versions >2.5 and < 3.0\n '
                            'with the use of the base Tkinter library and Tcl/Tk version 8.5.9\n \n'
                            'Development team: \n'
                            'Front-end Developer: Kai-ou Tang \n'
                            'Development Support: William Moseley\n'
                            'Project Manager: Edward Moseley \n'
              , pady=150).pack()

    def info(self):
        infopop = Toplevel()
        infopop.title("Guidelines")
        infopop.geometry('400x300')
        infofr = Frame(infopop)
        infofr.pack()
