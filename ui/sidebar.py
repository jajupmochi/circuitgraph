"""sidebar.py: Display and Editor of Node, Edge and Graph Attributes"""

# System Imports
import json
from pathlib import Path
from threading import Lock
from tkinter import Frame, OptionMenu, Label, Spinbox, Scale, Button, Entry, Canvas, StringVar, DoubleVar, SOLID, NW, \
    TOP, LEFT, RIGHT, HORIZONTAL, INSERT

# Third-Party Imports
from PIL import ImageTk, ImageDraw, ImageChops, Image

# Project Imports
from ui.itemlisteditor import ItemListEditor
from ui.utils import bbox_to_pos, pos_to_bbox

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022-2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"

CUR_ABS_DIR = Path(__file__).parent.resolve()

SIZE_SNIPPET = 100


class Sidebar:
    """Left-Hand Side Menu for Viewing and Editing Graph, Node and Edge Attributes"""

    def __init__(self, parent):
        """Creates the Side Bar"""

        # Define Control Members
        self.parent = parent
        self.visibility = True
        self.update_lock = Lock()
        self.snippet = None
        self.pos_left = StringVar()
        self.pos_right = StringVar()
        self.pos_top = StringVar()
        self.pos_bottom = StringVar()
        self.pos_rotation = DoubleVar()
        self.CLASSES = self.load_classes()
        self.cls = StringVar()
        self.cls.set(self.CLASSES[0])
        self.text = StringVar()

        # Create UI Elements
        self.side_bar = Frame(parent.root, width=100)
        self.side_bar.pack(side=LEFT, fill="y")

        self.label_snippet = Label(self.side_bar, text="Snippet")
        self.label_snippet.pack(pady=10)
        self.canvas_snippet = Canvas(self.side_bar, width=SIZE_SNIPPET, height=SIZE_SNIPPET, bg="white", bd=1,
                                     relief=SOLID)
        self.canvas_snippet.pack()

        self.label_position = Label(self.side_bar, text="Position")
        self.label_position.pack(pady=10)

        self.frame_left = Frame(self.side_bar)
        self.frame_left.pack(fill="x")
        self.label_left = Label(self.frame_left, text="Left")
        self.label_left.pack(side=LEFT)
        self.spinbox_left = Spinbox(self.frame_left, from_=0, to=10000, textvariable=self.pos_left,
                                    state="readonly", readonlybackground="ghostwhite")
        self.spinbox_left.pack(side=RIGHT)

        self.frame_right = Frame(self.side_bar)
        self.frame_right.pack(fill="x")
        self.label_right = Label(self.frame_right, text="Right")
        self.label_right.pack(side=LEFT)
        self.spinbox_right = Spinbox(self.frame_right, from_=0, to=10000, textvariable=self.pos_right,
                                     state="readonly", readonlybackground="ghostwhite")
        self.spinbox_right.pack(side=RIGHT)

        self.frame_top = Frame(self.side_bar)
        self.frame_top.pack(fill="x")
        self.label_top = Label(self.frame_top, text="Top")
        self.label_top.pack(side=LEFT)
        self.spinbox_top = Spinbox(self.frame_top, from_=0, to=10000, textvariable=self.pos_top,
                                   state="readonly", readonlybackground="ghostwhite")
        self.spinbox_top.pack(side=RIGHT)

        self.frame_bottom = Frame(self.side_bar)
        self.frame_bottom.pack(fill="x")
        self.label_bottom = Label(self.frame_bottom, text="Bottom")
        self.label_bottom.pack(side=LEFT)
        self.spinbox_bottom = Spinbox(self.frame_bottom, from_=0, to=10000, textvariable=self.pos_bottom,
                                      state="readonly", readonlybackground="ghostwhite")
        self.spinbox_bottom.pack(side=RIGHT)

        self.frame_rotation = Frame(self.side_bar)
        self.frame_rotation.pack(fill="x")
        self.label_rotation = Label(self.frame_rotation, text="Rotation")
        self.label_rotation.pack(side=TOP, pady=(10, 0))
        self.scale_rotation = Scale(self.frame_rotation, from_=0, to=360, orient=HORIZONTAL, variable=self.pos_rotation)
        self.scale_rotation.pack(side=TOP, fill="x", expand=True)

        self.label_class = Label(self.side_bar, text="Class")
        self.label_class.pack(pady=10)

        self.optionmenu_class = OptionMenu(self.side_bar, self.cls, *self.CLASSES)
        self.optionmenu_class.pack(fill="x")

        self.frame_text = Frame(self.side_bar)
        self.frame_text.pack(fill="x")
        self.label_text = Label(self.frame_text, text="Text")
        self.label_text.pack(pady=10)
        self.entry_text = Entry(self.frame_text, text="Text", textvariable=self.text)
        self.entry_text.pack(side=LEFT, padx=(5, 1))
        self.button_my = Button(self.frame_text, text="µ")
        self.button_my.pack(side=LEFT)
        self.button_omega = Button(self.frame_text, text="Ω")
        self.button_omega.pack(side=LEFT)
        self.port_editor = ItemListEditor(self, title="Connectors",
                                          attributes={"Name": lambda port: port.name,
                                                      "X": lambda port: port.position.x,
                                                      "Y": lambda port: port.position.y},
                                          prototype={'name': 'A', 'position': {'x': 650, 'y': 1485}})
        self.property_editor = ItemListEditor(self, title="Properties",
                                              attributes={"Name": lambda prop: prop.name,
                                                          "Value": lambda prop: str(prop.value),
                                                          "X": lambda prop: prop.position.x,
                                                          "Y": lambda prop: prop.position.y},
                                              prototype={'name': 'A', 'value': 'B', 'position': {'x': 1, 'y': 1}})

        # Bind Events
        self.pos_left.trace("w", lambda name, index, mode, sv=self.pos_left: self.set(sv))
        self.pos_right.trace("w", lambda name, index, mode, sv=self.pos_left: self.set(sv))
        self.pos_top.trace("w", lambda name, index, mode, sv=self.pos_left: self.set(sv))
        self.pos_bottom.trace("w", lambda name, index, mode, sv=self.pos_left: self.set(sv))
        self.pos_rotation.trace("w", lambda name, index, mode, sv=self.pos_left: self.set(sv))
        self.cls.trace("w", lambda name, index, mode, sv=self.cls: self.set(sv))
        self.text.trace("w", lambda name, index, mode, sv=self.pos_left: self.set(sv))
        self.button_my.bind('<Button-1>', lambda e: self.entry_text.insert(INSERT, "µ"))
        self.button_omega.bind('<Button-1>', lambda e: self.entry_text.insert(INSERT, "Ω"))

    def load_classes(self) -> list:

        with open(CUR_ABS_DIR / "../converter/symbols/classes_ports.json") as cls_file:
            return list(json.load(cls_file).keys())

    def toggle(self):
        """Toggles the Sidebar's Visibility"""

        self.visibility = not self.visibility

        if self.visibility:
            self.side_bar.pack(before=self.parent.editor.canvas, side=LEFT, fill="y")  # TODO use grid

        else:
            self.side_bar.pack_forget()

    def update(self):
        """Updates the Values Displayed in the Sidebar"""

        if self.update_lock.locked():  # TODO Rework this hotfix
            return None

        self.update_lock.acquire()

        # Fallback if no Node is Selected
        self.canvas_snippet.delete("all")
        left, right, top, bottom, rotation = "", "", "", "", 0
        cls = ""
        text = ""
        ports = []
        props = []

        if self.parent.editor.graph and self.parent.editor.selected_node is not None:
            node_data = self.parent.editor.graph.nodes[self.parent.editor.selected_node]
            left, right, top, bottom, rotation = pos_to_bbox(node_data["position"])
            cls = node_data["type"]
            text = node_data["text"]
            ports = node_data["ports"]
            props = node_data["properties"]

            if self.parent.editor.img_raw:
                snippet_raw = self.parent.editor.img_raw.crop((left, top, right, bottom)). \
                    resize((SIZE_SNIPPET + 1, SIZE_SNIPPET + 1))

                if node_data['shape'] and self.parent.editor.renderer_settings['shapes']:
                    mask = Image.new('RGB', (SIZE_SNIPPET + 1, SIZE_SNIPPET + 1), (255, 255, 255))
                    ImageDraw.Draw(mask).polygon([((SIZE_SNIPPET + 1) * (x - left) / (right - left),
                                                   (SIZE_SNIPPET + 1) * (y - top) / (bottom - top))
                                                  for x, y in node_data['shape']],
                                                 outline=1, fill=1)
                    snippet_raw = ImageChops.lighter(snippet_raw, mask)

                self.snippet = ImageTk.PhotoImage(snippet_raw)
                self.canvas_snippet.create_image(1, 1,
                                                 image=self.snippet,
                                                 anchor=NW)

        self.pos_left.set(left)
        self.pos_right.set(right)
        self.pos_top.set(top)
        self.pos_bottom.set(bottom)
        self.pos_rotation.set(rotation)
        self.cls.set(cls)
        self.text.set(text)
        self.port_editor.set(ports)
        self.property_editor.set(props)

        self.update_lock.release()

    def set(self, event):
        """Collects the Inputs and Triggers the Parent Window Update"""

        if not self.update_lock.locked():

            if self.parent.editor.graph and self.parent.editor.selected_node is not None:
                node_data = self.parent.editor.graph.nodes[self.parent.editor.selected_node]
                node_data['position'] = bbox_to_pos(float(self.pos_left.get()),
                                                    float(self.pos_right.get()),
                                                    float(self.pos_top.get()),
                                                    float(self.pos_bottom.get()),
                                                    round(float(self.pos_rotation.get())))
                node_data['type'] = self.cls.get()
                node_data['text'] = self.text.get()

            self.parent.update()
