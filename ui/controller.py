"""controller.py: File Loading/Storing/Supplying to Editor"""

# System Imports
import subprocess
from os import remove, mkdir
from os.path import join, split, normpath, isfile, exists

# Project Imports
from converter.core.engineeringGraph import EngGraph
from converter.converter.pascalVocConverter import PascalVocConverter
from converter.converter.labelmeConverter import LabelMeConverter
from converter.converter.svgConverter import SvgConverter
from converter.converter.pngConverter import PngConverter
from converter.converter.kicadConverter import KiCadConverter
from converter.converter.kicad6Converter import KiCad6Converter
from converter.converter.rdfConverter import RdfConverter
from converter.converter.jsonConverter import JSONConverter

# Third-Party Imports
import cv2
from tkinter import filedialog
from PIL import Image

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class Controller:
    """File Loading/Storing/Supplying to Editor"""

    def __init__(self, parent):

        self.main = parent
        self.editor = parent.editor
        self.status_bar = parent.status_bar
        self.cam = cv2.VideoCapture(0)
        self.converters = {"png": (PngConverter(), "Portable Network Graphics"),
                           "svg": (SvgConverter(), "Scalable Vector Graphics"),
                           "xml": (PascalVocConverter(), "Pascal VOC"),
                           "json": (LabelMeConverter(), "LabelME"),
                           "sch": (KiCadConverter(), "KiCad 5"),
                           "kicad_sch": (KiCad6Converter(), "KiCad 6"),
                           "ttl": (RdfConverter(), "Turtle"),
                           "internal": (JSONConverter(), "NetworkX JSON")}

        self.graph_file = ""

        self.editor.set_graph(EngGraph(name="", width=int(1000), height=int(1000), image=""))


    def new_file(self):
        print("New File!")


    def read_cam(self):
        """Starts a Webcam Feed"""

        self.editor.set_image(Image.fromarray(cv2.cvtColor(self.cam.read()[1], cv2.COLOR_BGR2RGB)), fit_view=False)
        self.editor.render_graph()
        self.editor.canvas.after(20, self.read_cam)


    def safe_annotation_file(self, file_name=None):
        """Selects the Annotation File Writer and Writes the File"""

        if file_name is None:
            file_name = self.graph_file

        if file_name is None:
            return

        suffix = file_name.split(".")[-1]

        if suffix in self.converters.keys():
            self.converters[suffix][0].store(self.editor.graph, file_name)
            self.status_bar.set(f"Saved File {file_name}")


    def save_annotation(self):
        """Save Annotation Handler"""

        if self.graph_file:
            self.safe_annotation_file()

        else:
            self.save_annotation_as()


    def save_annotation_as(self):
        """Save Annotation As Handler"""

        file_name = filedialog.asksaveasfilename(title="Save Annotation",
                                                 filetypes=[(suffix, self.converters[suffix][1])
                                                            for suffix in self.converters],
                                                 initialfile="".join(self.editor.graph.graph['name']),
                                                 defaultextension=".xml")

        if file_name:
            self.safe_annotation_file(file_name)


    def save_image_file(self, filename: str = ""):
        """Save's the current Image as Image File"""

        self.editor.img_raw.save(filename if filename else self.editor.graph['name'])


    def open_file(self, file_name=None):
        """Open File Handler"""

        if not file_name:
            file_name = filedialog.askopenfilename(title="Open File", filetypes=[("Image", ".png .jpg .jpeg"),
                                                                                 ("Pascal VOC", ".xml"),
                                                                                 ("LabelME", ".json"),
                                                                                 ("KiCad 5", ".sch"),
                                                                                 ("KiCad 6", ".kicad_sch")])

        if file_name:

            img_path = ""
            graph_path = ""
            graph = None
            img = Image.new(mode="RGB", size=(100, 100))

            if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                graph = EngGraph(name=split(file_name)[-1].split(".")[:-1],
                                 width=int(1000), height=int(1000), image=file_name)
                img_path = file_name

            if file_name.endswith(".xml"):
                graph = self.converters["xml"][0].load(file_name)
                img_path = normpath(join(split(file_name)[0], "../images", graph.graph['name']))
                graph_path = file_name

            if file_name.endswith(".json"):
                graph = self.converters["json"][0].load(file_name)
                img_path = normpath(join(split(file_name)[0], graph.graph['name']))
                graph_path = file_name

            if file_name.endswith(".sch"):
                graph = self.converters["sch"][0].load(file_name)
                graph_path = file_name

            if file_name.endswith(".kicad_sch"):
                graph = self.converters["kicad_sch"][0].load(file_name)
                graph_path = file_name

            if isfile(img_path):
                img = Image.open(img_path)

            self.graph_file = graph_path
            self.editor.set_graph(graph)
            self.editor.set_image(img)
            self.main.update()
            self.status_bar.set(f"Loaded File {file_name}")
            self.editor.canvas.focus_set()


    def apply_extraction(self, cmd, cmd_name):
        """Applies External Image Understanding from the Extraction Repo"""

        # Prepare Directory
        if exists("temp_x"):
            subprocess.run(f"rm -rf temp_x", shell=True)

        mkdir("temp_x")

        # Save Data
        self.save_image_file(join("temp_x", "image.png"))
        self.converters["internal"][0].store(self.editor.graph, join("temp_x", "graph.json"))

        # Run External Script
        subprocess.run(cmd, shell=True)

        # Load Graph
        self.editor.set_graph(self.converters["internal"][0].load(join("temp_x", "graph.json")))

        # Clean up
        subprocess.run(f"rm -rf temp_x",
                       shell=True)

        # Refresh Window
        self.main.update()
        self.status_bar.set(f"Applied {cmd_name}.")


    def object_detection(self):
        """Performs Object Detection"""

        self.apply_extraction(
            "python3 -m extraction.src.core.inference extraction/config/object_detection.json temp_x/image.png temp_x/graph.json",
            "Object Detection")


    def rotation_recognition(self):

        self.apply_extraction(
            "python3 -m extraction.src.core.inference extraction/config/rotation_ta.json temp_x/image.png temp_x/graph.json",
            "Rotation Recognition")


    def text_recognition(self):

        self.apply_extraction(
            "python3 -m extraction.src.core.inference extraction/config/text_lstm.json temp_x/image.png temp_x/graph.json",
            "Text Recognition")


    def connection_recognition(self):

        self.apply_extraction(
            "python3 -m extraction.src.core.inference extraction/config/segmentation.json temp_x/image.png temp_x/graph.json",
            "Connection Recognition")


    def knowledge_inference(self):
        """Applies the external Forward Chaining Rule Engine to the Current Graph"""

        self.converters['ttl'][0].store(self.editor.graph, "temp_in.ttl")
        subprocess.run(f"cd insights &&"
                       f"java -jar engine/target/circuit-inference-0.0.1.jar "
                       f"--input=../temp_in.ttl --output=../temp_out.ttl",
                       shell=True)
        self.editor.set_graph(self.converters["ttl"][0].load("temp_out.ttl"))
        remove("temp_in.ttl")
        remove("temp_out.ttl")

        self.main.update()
        self.status_bar.set(f"Applied Knowledge Inference.")
