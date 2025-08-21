"""filebar.py: Display for Folder Content and Convenient File Switch"""

# System Imports
from os import listdir
from os.path import isfile, join

# Third-Party Imports
from tkinter import Frame, Label, Button, Listbox, Scrollbar, Variable, LEFT, RIGHT, BOTH, TOP, END, SINGLE, filedialog

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class Filebar:
    """Right-Hand Side Menu for Viewing Folder Content and Convenient File Switch"""

    def __init__(self, parent):
        """Creates the File Bar"""

        # Define Control Members
        self.parent = parent
        self.visibility = False
        self.folder_name = ""
        self.file_names = Variable(value=[])

        # Create UI Elements
        self.file_bar = Frame(self.parent.root, width=100)
        self.file_bar.pack(side=RIGHT, fill="y")  # TODO Bar Superclass

        self.frame_switch = Frame(self.file_bar)
        self.frame_switch.pack(fill="x", padx=5, pady=5, side=TOP)
        self.button_prev = Button(self.frame_switch, text="<< PREV", borderwidth=10)
        self.button_prev.pack(side=LEFT)
        self.button_next = Button(self.frame_switch, text="NEXT >>", borderwidth=10)
        self.button_next.pack(side=LEFT)

        self.label_folder = Label(self.file_bar, text="Folder Content")
        self.label_folder.pack()
        self.frame_files = Frame(self.file_bar)
        self.frame_files.pack(side=TOP, fill=BOTH, expand=True)
        self.listbox_files = Listbox(self.frame_files, listvariable=self.file_names, height=30,
                                     selectmode=SINGLE, exportselection=False, activestyle='none')
        self.listbox_files.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar_files = Scrollbar(self.frame_files)
        self.scrollbar_files.pack(side=LEFT, fill="y")
        self.listbox_files.config(yscrollcommand=self.scrollbar_files.set)
        self.scrollbar_files.config(command=self.listbox_files.yview)

        self.button_open_folder = Button(self.file_bar, text="Open Folder...")
        self.button_open_folder.pack(side=TOP)

        # Bind Events
        self.button_open_folder.bind('<Button-1>', lambda e: self.open_folder())
        self.button_next.bind('<Button-1>', lambda e: self.select_file())
        self.button_prev.bind('<Button-1>', lambda e: self.select_file(index_shift=-1))
        self.listbox_files.bind('<<ListboxSelect>>', self.file_selected)


    def toggle(self):
        """Toggles the Sidebar's Visibility"""

        self.visibility = not self.visibility

        if self.visibility:
            self.file_bar.pack(after=self.parent.side_bar.side_bar, side=RIGHT, fill="y")  # TODO use grid

        else:
            self.file_bar.pack_forget()


    def open_folder(self):
        """Open Folder Handler"""

        folder_name = filedialog.askdirectory()

        if folder_name:
            self.folder_name = folder_name
            self.file_names.set(sorted([file_name for file_name in listdir(self.folder_name)
                                        if isfile(join(self.folder_name, file_name))]))

            if len(self.file_names.get()):
                self.listbox_files.select_clear(0, END)
                self.listbox_files.select_set(0)
                self.file_selected(None)


    def file_selected(self, event):
        """Handler for File List Box Selection"""

        if len(self.file_names.get()):
            file_name = join(self.folder_name,
                             self.listbox_files.get(self.listbox_files.curselection()))
            self.parent.controller.open_file(file_name)
            self.listbox_files.see(self.listbox_files.curselection())

        else:
            self.open_folder()


    def select_file(self, index_shift=1):
        """Next/Prev File Button Handler"""

        old_selection = self.listbox_files.curselection()
        file_count = len(self.file_names.get())

        if len(old_selection) and 0 <= old_selection[-1] + index_shift < file_count:
            self.listbox_files.select_clear(0, END)
            self.listbox_files.select_set(old_selection[-1] + index_shift)
            self.file_selected(None)
