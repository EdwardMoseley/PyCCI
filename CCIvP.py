#!/usr/bin/env python

import csv
import os
from Tkinter import *
import tkFont
import tkFileDialog
from ScrolledText import ScrolledText
import time
import pandas as pd
# Partial implementation of odict library because Python 2.X
# (https://github.com/bluedynamics/odict/blob/master/src/odict/pyodict.py)
# Python Software Foundation License
# (begin oDict library)
import sys


class _Nil(object):
    """Q: it feels like using the class with "is" and "is not" instead of
    "==" and "!=" should be faster.
    A: This would break implementations which use pickle for persisting.
    """

    def __repr__(self):
        return "nil"

    def __eq__(self, other):
        if (isinstance(other, _Nil)):
            return True
        else:
            return NotImplemented

    def __ne__(self, other):
        if (isinstance(other, _Nil)):
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return sys.maxsize


_nil = _Nil()


class _odict(object):
    """Ordered dict data structure, with O(1) complexity for dict operations
    that modify one element.
    Overwriting values doesn't change their original sequential order.
    """

    def _dict_impl(self):
        return None  # pragma NO COVERAGE

    def __init__(self, data=(), **kwds):
        """This doesn't accept keyword initialization as normal dicts to avoid
        a trap - inside a function or method the keyword args are accessible
        only as a dict, without a defined order, so their original order is
        lost.
        """
        if kwds:
            raise TypeError("__init__() of ordered dict takes no keyword "
                            "arguments to avoid an ordering trap.")
        self._dict_impl().__init__(self)
        # If you give a normal dict, then the order of elements is undefined
        if hasattr(data, "iteritems"):
            for key, val in data.iteritems():
                self[key] = val
        else:
            for key, val in data:
                self[key] = val

    # Double-linked list header
    def _get_lh(self):
        dict_impl = self._dict_impl()
        if not hasattr(self, '_lh'):
            dict_impl.__setattr__(self, '_lh', _nil)
        return dict_impl.__getattribute__(self, '_lh')

    def _set_lh(self, val):
        self._dict_impl().__setattr__(self, '_lh', val)

    lh = property(_get_lh, _set_lh)

    # Double-linked list tail
    def _get_lt(self):
        dict_impl = self._dict_impl()
        if not hasattr(self, '_lt'):
            dict_impl.__setattr__(self, '_lt', _nil)
        return dict_impl.__getattribute__(self, '_lt')

    def _set_lt(self, val):
        self._dict_impl().__setattr__(self, '_lt', val)

    lt = property(_get_lt, _set_lt)

    def __getitem__(self, key):
        return self._dict_impl().__getitem__(self, key)[1]

    def get(self, k, x=None):
        if k in self:
            return self._dict_impl().__getitem__(self, k)[1]
        else:
            return x

    def __iter__(self):
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lh')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict_impl.__getitem__(self, curr_key)[2]

    iterkeys = __iter__

    def itervalues(self):
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lh')
        while curr_key != _nil:
            _, val, curr_key = dict_impl.__getitem__(self, curr_key)
            yield val

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lh')
        while curr_key != _nil:
            _, val, next_key = dict_impl.__getitem__(self, curr_key)
            yield curr_key, val
            curr_key = next_key

    def riterkeys(self):
        """To iterate on keys in reversed order.
        """
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lt')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict_impl.__getitem__(self, curr_key)[0]

    __reversed__ = riterkeys

    def ritervalues(self):
        """To iterate on values in reversed order.
        """
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lt')
        while curr_key != _nil:
            curr_key, val, _ = dict_impl.__getitem__(self, curr_key)
            yield val

    def rvalues(self):
        """List of the values in reversed order.
        """
        return list(self.ritervalues())

    def riteritems(self):
        """To iterate on (key, value) in reversed order.
        """
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lt')
        while curr_key != _nil:
            pred_key, val, _ = dict_impl.__getitem__(self, curr_key)
            yield curr_key, val
            curr_key = pred_key

    def _repr(self):
        """_repr(): low level repr of the whole data contained in the odict.
        Useful for debugging.
        """
        dict_impl = self._dict_impl()
        form = "odict low level repr lh,lt,data: %r, %r, %s"
        return form % (dict_impl.__getattribute__(self, 'lh'),
                       dict_impl.__getattribute__(self, 'lt'),
                       dict_impl.__repr__(self))


class odict(_odict, dict):
    def _dict_impl(self):
        return dict


## End odict library


class App:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()
        self.master = master
        master.title("Palliative Care PyCCI")
        self.indicatorvalues = dict(odict([("Care Preferences", 0),
                                           ("Family Meetings", 0),
                                           ("Code Status Limitations", 0),
                                           ("Palliative Care Involvement", 0),
                                           ("Ambiguous", 0),
                                           ("None", 0)]).items())
        # add or take away indicators here and also in writer()
        self.path = 1
        self.total = 0
        self.rowtotal = 0

        self.count = 0  # Initialize count to zero and refer to it later in crane()

        self.header = []  # Hold the header of the csv to grab indices of input variables

        self.TEXT = []
        self.SUBJECT_ID = []
        self.HADM_ID = []
        self.CHARTDATE = []
        self.CATEGORY = []
        self.DESCRIPTION = []
        self.CGID = []
        self.ISERROR = []
        self.TEXT = []
        # Storage is used to provide a list of subject ids
        self.storage = []
        # mem will accept the length of storage
        self.mem = 0
        # SID will accept the zeroth element
        self.SID = []
        self.ROW_ID = []

        self.body()
        self.library()

    def retrieve_line(self, row):
        # If the header is empty then the row contains header data
        if len(self.header) == 0:
            self.header = row

        try:
            self.TEXT.append(row[self.header.index("TEXT")])
        except Exception:
            self.TEXT.append("N/A")
            sys.exc_clear()

        try:
            self.SUBJECT_ID.append(row[self.header.index("SUBJECT_ID")])
        except Exception:
            self.SUBJECT_ID.append("N/A")
            sys.exc_clear()

        try:
            self.HADM_ID.append(row[self.header.index("HADM_ID")])
        except Exception:
            self.HADM_ID.append("N/A")
            sys.exc_clear()

        try:
            self.CHARTDATE.append(row[self.header.index("CHARTDATE")])
        except Exception:
            self.CHARTDATE.append("N/A")
            sys.exc_clear()

        try:
            self.CATEGORY.append(row[self.header.index("CATEGORY")])
        except Exception:
            self.CHARTDATE.append("N/A")
            sys.exc_clear()

        try:
            self.DESCRIPTION.append(row[self.header.index("DESCRIPTION")])
        except Exception:
            self.DESCRIPTION.append("N/A")
            sys.exc_clear()

        try:
            self.CGID.append(row[self.header.index("CGID")])
        except Exception:
            self.CGID.append("N/A")
            sys.exc_clear()

        try:
            self.ISERROR.append(row[self.header.index("ISERROR")])
        except Exception:
            self.ISERROR.append("N/A")
            sys.exc_clear()

        try:
            self.ROW_ID.append(row[self.header.index("ROW_ID")])
        except Exception:
            self.ROW_ID.append("N/A")
            sys.exc_clear()

    def openfile(self):
        if buttonArg == "Annotate":
            self.path += -1
            if self.path == 0:
                self.file = tkFileDialog.askopenfilename()
                self.newfile = self.file[:-4] + "Results.csv"
                with open(self.file, 'r+') as f:
                    self.mycsv = csv.reader(f)
                    # Grab the data and hold it in memory
                    for row in self.mycsv:  ## For loop giving cell all over its values
                        self.retrieve_line(row)


                
                # self.total increments what the text

                self.rowtotal = len(self.SUBJECT_ID)
                self.ptnumber.config(text=str(self.total))
                self.pttotal.config(text=str(self.rowtotal))
                # Hide subject ID from annotator
                # self.ptsubID.config(text = str(self.SUBJECT_ID[self.total]))

                self.pthAdm.config(text=str(self.HADM_ID[self.total]))
                self.ptnotetype.config(text=str(self.CATEGORY[self.total]))

                # Box that displays patient text
                self.pttext.config(state=NORMAL)
                self.pttext.delete(1.0, END)
                self.pttext.insert(END, self.TEXT[self.total])
                self.pttext.config(state=DISABLED)

                # If the file already exists, open it and continue at the spot you were,
                # makes it easier to continue on annotating results
                # self.newfile is the results file
                if os.path.isfile(self.newfile) == True:
                    with open(self.newfile, 'r+') as self.newf:
                        # Storage is used to provide an integer to mem
                        self.storage = csv.reader(self.newf)
                        for line in self.storage:
                            self.SID.append(line[0])
                        self.mem = len(self.SID)
                        # Initiate to length of results file
                        self.crane(self.mem)
                else:
                    self.crane(0)

    ## ###
    ## crane calls writer() and resetbuttons()
    ## ###
    # called whenever you press back or next
    def crane(self, x):  ## This is the incrementer function
        if self.path == 0:
            self.writer()
            self.total += x
            if self.total < 2:
                self.total = 1
            self.ptnumber.config(text=str(self.total))
            self.pttotal.config(text=str(self.rowtotal))


        # self.ptsubID.config(text = str(self.subjID[self.total]))
        self.pthAdm.config(text=str(self.HADM_ID[self.total]))
        self.ptnotetype.config(text=str(self.CATEGORY[self.total]))

        self.pttext.config(state=NORMAL)
        self.pttext.delete(1.0, END)
        self.pttext.insert(END, self.TEXT[self.total])
        self.pttext.config(state=DISABLED)
        self.resetbuttons()

    ## ###
    ## writer() is called every time "Next" or "Back" are pressed
    ## writer() will create a results file if one does not exist
    ## writer() will pass if no indicators are ticked
    ## writer() will write to results file if any indicator is ticked
    ## ###

    def writer(self):
        # If the file does not exist, create it and add the header
        if os.path.isfile(self.newfile) == False:
            with open(self.newfile, 'w') as csvfile:
                datawriter = csv.writer(csvfile, delimiter=',')
                datawriter.writerow(["ROW_ID"]
                                + ["SUBJECT_ID"]
                                + ["HADM_ID"]
                                + ["CHARTDATE"]
                                + ["CATEGORY"]
                                + ["DESCRIPTION"]
                                + ["CGID"]
                                + ["TEXT"]
                                + ["Care Preferences"]
                                + ["Care Preferences Text"]
                                + ["Family Meetings"]
                                + ["Family Meetings Text"]
                                + ["Code Status Limitations"]
                                + ["Code Status Limitations Text"]
                                + ["Palliative Care Involvement"]
                                + ["Palliative Care Involvement Text"]
                                + ["Ambiguous"]
                                + ["None"]
                                + ["STAMP"])

        else:
            # If no indicator is ticked, pass
            if bool(self.indicatorvalues["Care Preferences"].get()) == False \
                + bool(self.indicatorvalues["Family Meetings"].get()) == False \
                + bool(self.indicatorvalues["Code Status Limitations"].get()) == False \
                + bool(self.indicatorvalues["Palliative Care Involvement"].get()) == False \
                + bool(self.indicatorvalues["Ambiguous"].get()) == False \
                + bool(self.indicatorvalues["None"].get()) == False:
                    pass
                # If an indicator is ticked
            else:
                with open(self.newfile, 'a') as csvfile:
                    datawriter = csv.writer(csvfile, delimiter=',')
                    datawriter.writerow([str(self.ROW_ID[self.total])]
                                            + [str(self.SUBJECT_ID[self.total])]
                                            + [str(self.HADM_ID[self.total])]
                                            + [str(self.CHARTDATE[self.total])]
                                            + [str(self.CATEGORY[self.total])]
                                            + [str(self.DESCRIPTION[self.total])]
                                            + [str(self.CGID[self.total])]
                                            + [str(self.TEXT[self.total])]
                                            + [str(self.indicatorvalues["Care Preferences"].get())]
                                            + [str(self.carePrefText.get())] # use this to retrieve character positions
                                            + [str(self.indicatorvalues["Family Meetings"].get())]
                                            + [str(self.famMeetingText.get())]
                                            + [str(self.indicatorvalues["Code Status Limitations"].get())]
                                            + [str(self.codeStatusText.get())]
                                            + [str(self.indicatorvalues["Palliative Care Involvement"].get())]
                                            + [str(self.palCareInvolveText.get())]
                                            + [str(self.indicatorvalues["Ambiguous"].get())]
                                            + [str(self.indicatorvalues["None"].get())]
                                            #+ [str(self.unsureReason.get())])
                                            + [str(time.asctime(time.localtime(time.time())))])


        ## ###
        ## library() will create the checkbuttons and text entry box
        ## ###
    # part of the gui that covers annotations
    def library(self):
        myvar = IntVar()  # self?
        myvar.set(self.indicatorvalues["Care Preferences"])
        self.indicatorvalues["Care Preferences"] = myvar
        l = Checkbutton(self.checkframe,
                        text="Care Preferences",
                        variable=myvar,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=LEFT)
        l.pack(anchor=W)

        self.carePrefText = StringVar()
        self.carePrefBox = Entry(self.checkframe,
                                 #foreground="grey",
                                 width=30,
                                 textvariable=self.carePrefText)
        self.carePrefText.set("Care Preferences Text")
        self.carePrefBox.pack(anchor=W, pady=5)



        myvar = IntVar()  # self?
        myvar.set(self.indicatorvalues["Family Meetings"])
        self.indicatorvalues["Family Meetings"] = myvar
        l = Checkbutton(self.checkframe,
                        text="Family Meetings",
                        variable=myvar,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=LEFT)
        l.pack(anchor=W)

        self.famMeetingText = StringVar()
        self.famMeetingBox = Entry(self.checkframe, width=30, textvariable=self.famMeetingText)
        self.famMeetingText.set("Family Meetings Text")
        self.famMeetingBox.pack(anchor=W, pady=5)



        myvar = IntVar()  # self?
        myvar.set(self.indicatorvalues["Code Status Limitations"])
        self.indicatorvalues["Code Status Limitations"] = myvar
        l = Checkbutton(self.checkframe,
                        text="Code Status Limitations",
                        variable=myvar,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=LEFT)
        l.pack(anchor=W)

        self.codeStatusText = StringVar()
        self.codeStatusBox = Entry(self.checkframe, width=30, textvariable=self.codeStatusText)
        self.codeStatusText.set("Code Status Limitations Text")
        self.codeStatusBox.pack(anchor=W, pady=5)



        myvar = IntVar()  # self?
        myvar.set(self.indicatorvalues["Palliative Care Involvement"])
        self.indicatorvalues["Palliative Care Involvement"] = myvar
        l = Checkbutton(self.checkframe,
                        text="Palliative Care Involvement",
                        variable=myvar,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=LEFT)
        l.pack(anchor=W)

        self.palCareInvolveText = StringVar()
        self.palCareInvolveBox = Entry(self.checkframe, width=30, textvariable=self.palCareInvolveText)
        self.palCareInvolveText.set("Palliative Care Involvement Text")
        self.palCareInvolveBox.pack(anchor=W, pady=5)

        myvar = IntVar()  # self?
        myvar.set(self.indicatorvalues["Ambiguous"])
        self.indicatorvalues["Ambiguous"] = myvar
        l = Checkbutton(self.checkframe,
                        text="Ambiguous",
                        variable=myvar,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=LEFT)
        l.pack(anchor=W)

        myvar = IntVar()  # self?
        myvar.set(self.indicatorvalues["None"])
        self.indicatorvalues["None"] = myvar
        l = Checkbutton(self.checkframe,
                        text="None",
                        variable=myvar,
                        onvalue=1,
                        offvalue=0,
                        height=1,
                        pady=5,
                        justify=LEFT)
        l.pack(anchor=W)

    ## ###
    ## resetbuttons()
    ## ###
    def resetbuttons(self):
        self.carePrefText.set("Care Preferences Text")
        self.famMeetingText.set("Family Meetings Text")
        self.codeStatusText.set("Code Status Limitations Text")
        self.palCareInvolveText.set("Code Status Limitations Text")
        #self.unsureReason.set("Reason for Unsure here.")
        for machine in self.indicatorvalues:
            self.indicatorvalues[machine].set(0)


    ##Body

    def body(self):
        self.k1 = PanedWindow(self.master,
                              height=700,
                              width=900,
                              orient=VERTICAL)
        self.k1.pack(fill=BOTH, expand=1)
        self.titlefont = tkFont.Font(size=12,
                                     weight='bold')
        self.boldfont = tkFont.Font(size=8,
                                    weight='bold')
        self.textfont = tkFont.Font(family='Arial',
                                    size=15)
        self.h3font = tkFont.Font(size=11)

        # Title
        self.title = PanedWindow(self.k1)
        self.k1.add(self.title, padx=10, pady=10)

        self.openbutton = Button(self.title,
                                 text="Open CSV",
                                 command=lambda: self.openfile(),
                                 padx=15)
        self.openbutton.place(anchor=W, x=20, rely=0.25)

        self.photo = """
        R0lGODlhRgAwAPf/AOb58//ylf/JN//PPv/cZjt+oWfiuD6IsHipw//jasba5f/gUjuApP/mWJvs0FbLqj6GrP/eUFjOrKfF1v/zyFPGqFTIqS5
        6qtr07YrdxWTftmjkuTt+oDyCpv/75jyEqv/lc1ORtGDZs1LFp5TpzDp8oP/kVrnR1j+KsdLi617WsbPN0WrnupC1zVfMq+Lt8mXgt//URFrQrka
        Gp//WRv/QMP/SQbLJzDyDqJvnzzyCqIWyypG2ytX16mrnu1zUr//QP77x4Oz69pnrz//iVFzSr6vp1YGux2zpvP/YSf/OPWHasz+KsrHi2f/KOZ
        Dgyf/cTv/bav/MOv778//1h57ezmLdsljMq93p8GHbs3nsw1/Ysj2GrMPW3f/aS8ru5ery9pS61P/hZ5u+0TuBpDGBs26mwozoyWnmuvf6/Iy1z
        f/zt47fx//NPNro7//mpGbhtv/cTD6HrbTP3f/oiWzOtP/gjnHaurrs3oPjw1jMrFvRrv/OPCp9tf/bTP/ZSv/KOv/sgv/kgGTgtJW7zj6FqlzW
        rrLl2f/eTpTnzLXo3JG30F3VsKLr0//tjmnluf/XYv/VXv/tiGvou87g6f/qjP/miLnS3/H3+sbx42nZtv/51//RQPj9/OL48dnl6JLkysTv4pzw
        0rTn22DbsbDN3FXLqEqRtj2Fq//fiZbjyzB/sXCjvjyBpZCzylrSrFnRrbDg15TlyzB9riFzrWPdtT6Irz6IrmLctFrQrf/JODuAo2TetT+Irz+J
        sD6JsD6Fqz2FqmPetWPctWfkuVXJqf/XR1nPrT+IrlXKqjt/o1/XsWbit2PctGbhtzp9oP/TQz2HrTyCpWLctT6Irf/VRVjPq1vUrY/wzWfjuFTK
        p1bJqnDjvP/deevw7liXvmOfwmTUskuMrlOOq5/d0a3t2D2EqV7MrfX39oy62vf599fk58Ln4K/JzGnWtf/WRabn0zh8oePo4a/k19H56mPetsDp
        36DB0o64zjh7ov/qs//xsP/MRY3iyKC+w////yH/C1hNUCBEYXRhWE1QPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6
        TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS4wLWMwNjAgNjEu
        MTM0Nzc3LCAyMDEwLzAyLzEyLTE3OjMyOjAwICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIv
        MjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94
        YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtbG5zOnhtcD0i
        aHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDoyOEQzRURGQjIxQkIxMUU1OERCQTkyNzVBMDI
        3MDYyNCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDoyOEQzRURGQTIxQkIxMUU1OERCQTkyNzVBMDI3MDYyNCIgeG1wOkNyZWF0b3JUb29sPS
        JBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmRpZDoxQUYwODQ2QU
        I2MjFFNTExOEE5NUE3QUZDNUUxMTNBRiIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDoxQUYwODQ2QUI2MjFFNTExOEE5NUE3QUZDNUUxMTNBRi
        IvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PgH//v38+/r5+Pf29fTz8vHw7+
        7t7Ovq6ejn5uXk4+Lh4N/e3dzb2tnY19bV1NPS0dDPzs3My8rJyMfGxcTDwsHAv769vLu6ubi3trW0s7KxsK+urayrqqmop6alpKOioaCfnp2cm5
        qZmJeWlZSTkpGQj46NjIuKiYiHhoWEg4KBgH9+fXx7enl4d3Z1dHNycXBvbm1sa2ppaGdmZWRjYmFgX15dXFtaWVhXVlVUU1JRUE9OTUxLSklIR0
        ZFRENCQUA/Pj08Ozo5ODc2NTQzMjEwLy4tLCsqKSgnJiUkIyIhIB8eHRwbGhkYFxYVFBMSERAPDg0MCwoJCAcGBQQDAgEAACH5BAEAAP8ALAAAAA
        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

        """
        self.photos = PhotoImage(data=self.photo)
        self.panel = Label(self.title, image=self.photos)
        self.panel.pack(side=RIGHT, padx=10)

        Label(self.title, text="\t\tPalliative Care Indications GUI",
              font=self.titlefont,
              fg="dodgerblue4").pack()

        # Top row open csv window & button
        # self.k2 = PanedWindow(self.k1)
        # self.k1.add(self.k2)

        # Panes below buttons
        self.k3 = PanedWindow(self.k1)
        self.k1.add(self.k3)
        self.leftpane = PanedWindow(self.k3)
        self.k3.add(self.leftpane,
                    width=400,
                    padx=30,
                    pady=25,
                    stretch="first")
        self.separator = PanedWindow(self.k3,
                                     relief=SUNKEN)
        self.k3.add(self.separator,
                    width=2,
                    padx=1,
                    pady=20)
        self.rightpane = PanedWindow(self.k3)
        self.k3.add(self.rightpane,
                    width=250,
                    padx=10,
                    pady=25,
                    stretch="never")

        # Left pane patient note text frame doo-diddly
        self.ptframe = LabelFrame(self.leftpane,
                                  text="Medical Record",
                                  font=self.boldfont,
                                  padx=0,
                                  pady=0,
                                  borderwidth=0)
        self.ptframe.pack()

        self.ptnumberframe = Frame(self.ptframe,
                                   padx=0,
                                   pady=0,
                                   borderwidth=0)
        self.ptnumberframe.pack()

        # Label(self.ptnumberframe, text = " ").grid(row = 0)

        self.ptnumber_A = Label(self.ptnumberframe, text="Patient", fg="dodgerblue4")
        self.ptnumber_A.grid(row=1, column=0)
        self.ptnumber = Label(self.ptnumberframe, text=" ")
        self.ptnumber.grid(row=1, column=1)
        self.ptnumber_B = Label(self.ptnumberframe, text="of", fg="dodgerblue4")
        self.ptnumber_B.grid(row=1, column=2)
        self.pttotal = Label(self.ptnumberframe, text=" ")
        self.pttotal.grid(row=1, column=3)

        self.ptframeinfo = Frame(self.ptframe,
                                 padx=0,
                                 pady=3,
                                 borderwidth=0)
        self.ptframeinfo.pack()
        self.ptframeinfo.columnconfigure(1, minsize=300)

        self.phAdm_ = Label(self.ptframeinfo, text="Hospital Admission ID:", fg="dodgerblue4")
        self.phAdm_.grid(row=2, column=0, sticky=E)
        self.pthAdm = Label(self.ptframeinfo, text=" ", font=self.h3font)
        self.pthAdm.grid(row=2, column=1, sticky=W)

        self.ptnotetype_ = Label(self.ptframeinfo, text="Note Type:", fg="dodgerblue4")
        self.ptnotetype_.grid(row=3, column=0, sticky=E)
        self.ptnotetype = Label(self.ptframeinfo, text=" ", font=self.h3font)
        self.ptnotetype.grid(row=3, column=1, sticky=W)



        # Incrementer buttons
        self.buttonframe = Frame(self.ptframe)
        self.buttonframe.pack()
        self.buttonframe.place(relx=0.97, anchor=NE)
        # Back Button
        self.button1 = Button(self.buttonframe,
                              text='Back',
                              width=6,
                              command=lambda: self.crane(-1))  # Argument is -1, decrement
        self.button1.grid(row=0, column=0, padx=2, pady=2)
        # Next Button
        self.button2 = Button(self.buttonframe,
                              text='Next',
                              width=6,
                              command=lambda: self.crane(1))  # Argument is 1, increment
        self.button2.grid(row=0, column=2, padx=2, pady=2)

        # Scrollbar!
        self.ptscroll = Scrollbar(self.ptframe)
        self.ptscroll.pack(side=RIGHT, fill=Y)

        # https://stackoverflow.com/questions/21873195/readonly-tkinter-text-widget
        self.pttext = ScrolledText(self.ptframe,
                                   height=300,
                                   width=400,
                                   wrap=WORD,
                                   font=self.textfont,
                                   spacing1=2,
                                   spacing2=2,
                                   spacing3=3,
                                   padx=15,
                                   pady=15)
        self.pttext.pack(side=BOTTOM)
        self.ptscroll.config(command=self.pttext.yview)
        self.pttext.config(yscrollcommand=self.ptscroll.set)
        self.pttext.config(state=NORMAL)
        self.pttext.delete(1.0, END)
        self.pttext.insert(END, "Please use the ''Open CSV'' button to open the .csv file provided to you, "
                           + "for example:\n'dischargeSummaries29JUN16.csv'\n"
                           + "This will create a 'results' file within the same directory.")

        self.pttext.config(state=DISABLED)
        self.pttext.bind("<1>", lambda event: self.pttext.focus_set())

        ##Note: Changed to ScrolledText (instead of text), and bound event: focus_set() to it.


        # Checkbuttons
        self.checkframe = LabelFrame(self.rightpane, text="Indicators",
                                     font=self.boldfont,
                                     padx=10,
                                     pady=0,
                                     borderwidth=0)
        self.checkframe.pack()


root = Tk()
app = App(root)  ## apply the class "App" to Tk()


def about():
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


def info():
    infopop = Toplevel()
    infopop.title("Guidelines")
    infopop.geometry('400x300')
    infofr = Frame(infopop)
    infofr.pack()

### Menu does not need to be part of the class
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about)
helpmenu.add_command(label="Guidelines", command=info)
menubar.add_cascade(label="Help", menu=helpmenu)
root.config(menu=menubar)
root.mainloop()
