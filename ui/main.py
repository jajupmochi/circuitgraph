"""main.py: Starting Point and Container for the Application"""

from pathlib import Path
# Third-Party Imports
from tkinter import Tk, Menu, PhotoImage, messagebox, colorchooser

from ui.controller import Controller
from ui.editor import GraphEditor
from ui.filebar import Filebar
# Project Imports
from ui.sidebar import Sidebar
from ui.statusbar import Statusbar

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022-2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"

CUR_ABS_DIR = Path(__file__).parent.resolve()


class MainWindow:
    """Starting Point and Container for the Application"""

    def __init__(self):
        """Creates the Main Window"""

        self.root = Tk(className='Circuitgraph')
        self.root.title('Circuitgraph')
        self.root.iconphoto(False, PhotoImage(file=CUR_ABS_DIR / "logo.png"))
        self.side_bar = Sidebar(self)
        self.file_bar = Filebar(self)
        self.editor = GraphEditor(self)
        self.status_bar = Statusbar(self)
        self.controller = Controller(self)
        self.create_menu()

        self.fullscreen = False

    def run(self):
        """Runs the Main Window"""

        self.root.mainloop()

    def create_menu(self) -> None:
        """Creates the Main Menu"""

        self.root.option_add('*tearOff', False)
        self.menu_main = Menu(self.root)
        self.root.config(menu=self.menu_main)

        # Create UI Elements
        self.menu_file = Menu(self.menu_main)
        self.menu_main.add_cascade(label="File", menu=self.menu_file)
        self.menu_file.add_command(label="New", command=self.controller.new_file)
        self.menu_file.add_command(label="Open File...", command=self.controller.open_file, accelerator="Ctrl+R")
        self.menu_file.add_command(label="Open Cam", command=self.controller.read_cam)
        self.menu_file.add_command(label="Save Annotation...", command=self.controller.save_annotation,
                                   accelerator="Ctrl+S")
        self.menu_file.add_command(label="Save Annotation As...", command=self.controller.save_annotation_as)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.root.quit)

        self.menu_view = Menu(self.menu_main)
        self.menu_main.add_cascade(label="View", menu=self.menu_view)
        self.menu_view.add_command(label="Show Raw Image", command=lambda: self.editor.set_rendering("rawImage"))
        self.menu_view.add_command(label="Show Bounding Boxes", accelerator="F1",
                                   command=lambda: self.editor.set_rendering("rectangles"))
        self.menu_view.add_command(label="Set Bounding Box Color", accelerator="CTRL+F1",
                                   command=lambda: self.set_editor_color("rectangleColor"))
        self.menu_view.add_command(label="Show Masks", accelerator="F2",
                                   command=lambda: self.editor.set_rendering("shapes"))
        self.menu_view.add_command(label="Set Mask Color", accelerator="CTRL+F2",
                                   command=lambda: self.set_editor_color("shapeColor"))
        self.menu_view.add_command(label="Show Symbols", accelerator="F3",
                                   command=lambda: self.editor.set_rendering("symbol"))
        self.menu_view.add_command(label="Set Symbol Color", accelerator="CTRL+F3",
                                   command=lambda: self.set_editor_color("symbolColor"))
        self.menu_view.add_command(label="Show Node Texts", accelerator="F4",
                                   command=lambda: self.editor.set_rendering("text"))
        self.menu_view.add_command(label="Set Text Color", accelerator="CTRL+F4",
                                   command=lambda: self.set_editor_color("textColor"))
        self.menu_view.add_command(label="Show Node IDs",
                                   command=lambda: self.editor.set_rendering("drawNodeId"))
        self.menu_view.add_command(label="Show Node Classes", accelerator="F5",
                                   command=lambda: self.editor.set_rendering("drawNodeType"))
        self.menu_view.add_command(label="Show Node Rotations", accelerator="F6",
                                   command=lambda: self.editor.set_rendering("drawRotation"))
        self.menu_view.add_command(label="Show Connector Position",
                                   command=lambda: self.editor.set_rendering("portPosition"))
        self.menu_view.add_command(label="Show Connector Owners", accelerator="F7",
                                   command=lambda: self.editor.set_rendering("portOwner"))
        self.menu_view.add_command(label="Show Connector Types", accelerator="F8",
                                   command=lambda: self.editor.set_rendering("portType"))
        # self.menu_view.add_command(label="Show Edge Lines", accelerator="F9",
        #                           command=lambda: self.editor.toggle_rendering("shapes")) <- todo independent impl.
        self.menu_view.add_command(label="Show Property Owners",
                                   command=lambda: self.editor.set_rendering("propOwner"))
        self.menu_view.add_separator()
        self.menu_view.add_command(label="Zoom in", accelerator="+", command=lambda: self.editor.zoom("+"))
        self.menu_view.add_command(label="Zoom out", accelerator="-", command=lambda: self.editor.zoom("-"))
        self.menu_view.add_command(label="Fit View", accelerator="0", command=lambda: self.editor.fit_view())
        self.menu_view.add_separator()
        self.menu_view.add_command(label="Show File Bar", command=self.file_bar.toggle, accelerator="F9")
        self.menu_view.add_command(label="Show Side Bar", command=self.side_bar.toggle, accelerator="F10")
        self.menu_view.add_command(label="Fullscreen", command=self.toggleFullscreen, accelerator="F11")
        self.menu_view.add_command(label="Show Status Bar", command=self.status_bar.toggle, accelerator="F12")

        self.menu_edit = Menu(self.menu_main)
        self.menu_main.add_cascade(label="Edit", menu=self.menu_edit)
        self.menu_edit.add_command(label="Add Node", accelerator="Q", command=self.editor.new_annotation)
        self.menu_edit.add_command(label="Duplicate Node", accelerator="CTRL+D", command=self.editor.duplicate_node)
        self.menu_edit.add_command(label="Remove Node", accelerator="Del", command=self.editor.remove_node)
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Add Edge", accelerator="M", command=self.editor.new_edge)
        self.menu_edit.add_command(label="Remove Edge", accelerator="Del", command=self.remove_edge)
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Enable BB Dragging", accelerator="CTRL+E",
                                   command=self.editor.toggle_dragging)

        self.menu_process = Menu(self.menu_main)
        self.menu_main.add_cascade(label="Process", menu=self.menu_process)
        self.menu_process.add_command(label="Detect Objects", command=self.controller.object_detection)
        self.menu_process.add_command(label="Rotation Recognition", command=self.controller.rotation_recognition)
        self.menu_process.add_command(label="Text Recognition", command=self.controller.text_recognition)
        self.menu_process.add_command(label="Connection Recognition", command=self.controller.connection_recognition)
        self.menu_process.add_separator()
        self.menu_process.add_command(label="Resolve Text Nodes", command=self.editor.resolve_text_nodes)
        self.menu_process.add_command(label="Resolve Wire Hops", command=self.editor.resolve_wire_hops)
        self.menu_process.add_command(label="Encapsulate Text Nodes", command=self.editor.encapsulate_text_nodes)
        self.menu_process.add_command(label="Encapsulate Wire Hops", command=self.editor.encapsulate_wire_hops)
        self.menu_process.add_separator()
        self.menu_process.add_command(label="Shake", command=self.editor.shake)
        self.menu_process.add_command(label="Straighten", command=self.editor.straighten)
        self.menu_process.add_separator()
        self.menu_process.add_command(label="Knowledge Inference",
                                      command=self.controller.knowledge_inference)

        self.menu_help = Menu(self.menu_main)
        self.menu_main.add_cascade(label="Help", menu=self.menu_help)
        self.menu_help.add_command(label="About...", command=self.about)

        # Bind Events
        self.root.bind_all("<Control-s>", lambda x: self.controller.save_annotation())
        self.root.bind_all("<Control-r>", lambda x: self.controller.open_file())
        self.root.bind_all("<Control-e>", lambda x: self.editor.toggle_dragging())
        self.root.bind_all("<Prior>", lambda x: self.file_bar.select_file(index_shift=-1))
        self.root.bind_all("<Next>", lambda x: self.file_bar.select_file())

        self.root.bind_all("<Control-F1>", lambda x: self.set_editor_color("rectangleColor"))
        self.root.bind_all("<Control-F2>", lambda x: self.set_editor_color("shapeColor"))
        self.root.bind_all("<Control-F3>", lambda x: self.set_editor_color("symbolColor"))
        self.root.bind_all("<Control-F4>", lambda x: self.set_editor_color("textColor"))
        self.root.bind_all("<F1>", lambda x: self.editor.set_rendering("rectangles"))
        self.root.bind_all("<F2>", lambda x: self.editor.set_rendering("shapes"))
        self.root.bind_all("<F3>", lambda x: self.editor.set_rendering("symbol"))
        self.root.bind_all("<F4>", lambda x: self.editor.set_rendering("text"))
        self.root.bind_all("<F5>", lambda x: self.editor.set_rendering("drawNodeType"))
        self.root.bind_all("<F6>", lambda x: self.editor.set_rendering("drawRotation"))
        self.root.bind_all("<F7>", lambda x: self.editor.set_rendering("portOwner"))
        self.root.bind_all("<F8>", lambda x: self.editor.set_rendering("portType"))

        self.root.bind_all("<F9>", lambda x: self.file_bar.toggle())
        self.root.bind_all("<F10>", lambda x: self.side_bar.toggle())
        self.root.bind_all("<F11>", lambda x: self.toggleFullscreen())
        self.root.bind_all("<F12>", lambda x: self.status_bar.toggle())

    def set_editor_color(self, setting: str) -> None:
        """Prompts a Color Picker and assigns the result as Graph Rendering Parameter"""

        init = self.editor.get_rendering(setting)
        color = colorchooser.askcolor(title="Choose Color", color=(init[2], init[1], init[0]))[0]

        if color:
            self.editor.set_rendering(setting, (int(color[2]), int(color[1]), int(color[0])))

    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def remove_edge(self):
        """Removes the Currently Selected Edge, if there is one"""

        print("REMOVE EDGE")

    def update(self, caller=None):
        """Main Update Method."""

        self.side_bar.update()
        self.editor.update()

    def about(self):
        """Info Message Box"""

        messagebox.showinfo(title="About Circuitgraph",
                            message="This User interface is part of Circuitgraph, an open-source "
                                    "software for processing circuit diagrams from images. "
                                    "For more information, visit: "
                                    "https://gitlab.com/circuitgraph/")


if __name__ == "__main__":
    mw = MainWindow()
    mw.run()
