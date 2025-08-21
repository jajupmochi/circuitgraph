"""statusbar.py: Bottom Info Panel"""

# Third-Party Imports
from tkinter import Label, SUNKEN, W, X, BOTTOM

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022-2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class Statusbar:
    """Bottom Info Panel"""

    def __init__(self, parent):

        # Define Control Members
        self.parent = parent
        self.visibility = True

        # Create UI Elements
        self.status_bar = Label(self.parent.root, text="Welcome to Circuitgraph", bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)


    def toggle(self) -> None:
        """Toggles the Sidebar's Visibility"""

        self.visibility = not self.visibility

        if self.visibility:
            self.status_bar.pack(after=self.parent.editor.canvas, side=BOTTOM, fill=X)

        else:
            self.status_bar.pack_forget()


    def set(self, status_text: str) -> None:
        """Sets the Text of the Statusbar"""

        self.status_bar.config(text=status_text)
