"""itemlisteditor.py: Editable Menu List for Node Connectors and Properties"""

# System Imports
from typing import Union
from copy import deepcopy

# Third-Party Imports
from tkinter import Frame, Label, Button, Entry, StringVar, LEFT

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"


class ItemListEditor(Frame):
    """Editable Menu List for Node Connectors and Properties"""

    def __init__(self, parent, title, attributes, prototype, **kw):

        super().__init__(parent.side_bar, **kw)
        self.pack(fill="x")

        # Define Control Members
        self.items: Union[list, None] = None
        self.item_vars = []
        self.parent = parent
        self.title = title
        self.attributes = attributes
        self.prototype = prototype

        # Create UI Elements
        self.label_title = Label(self, text=self.title)
        self.label_title.pack(pady=10)

        self.frame_header = Frame(self)
        self.frame_header.pack(fill="x")

        for attribute_name in self.attributes.keys():
            Label(self.frame_header, text=attribute_name).pack(side=LEFT, padx=15)

        self.frame_items = Frame(self)
        self.frame_items.pack(fill="x")

        self.button_add = Button(self, text="Add..")
        self.button_add.pack()

        # Bind Events
        self.button_add.bind('<Button-1>', lambda e: self.add_item())


    def set(self, items):
        """Updates the Item List"""

        if items is not self.items:
            self.items = items

            for widget in self.frame_items.winfo_children():
                widget.destroy()

            if self.items is not None:
                for item in self.items:
                    frame = Frame(self.frame_items)
                    frame.pack(fill="x")

                    for attribute_getter in self.attributes.values():
                        var_attr = StringVar(self.frame_items)
                        var_attr.set(attribute_getter(item))
                        entry_attr = Entry(frame, width=8, text="", textvariable=var_attr)
                        entry_attr.pack(side=LEFT)

                        self.item_vars  # TODO resolve

            self.frame_items.update()
            self.update()


    def add_item(self):
        """Adds one Item to both the Data Structure and the UI"""

        if self.items is not None:
            self.items.append(deepcopy(self.prototype))

        self.parent.update()
