"""nodeSnippetProcessor.py: Pre-/Post-Processing for Object Detection"""

# System Imports
from typing import Tuple, List, Union

# Project Imports
from converter.core.engineeringGraph import EngGraph
from converter.core.boundingbox import BoundingBox
from extraction.src.core.processor import Processor

# Third-Party Imports
from numpy import ndarray
from torch import Tensor
from torchvision import transforms

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class ObjectDetectionProcessor(Processor):
    """Pre-/Post-Processing for Object Detection"""

    def __init__(self, augment: bool, train: bool, debug: bool, classes: List[str], score_threshold: float):
        super().__init__(augment, train, debug)

        self.classes = classes
        self.transformer = transforms.ToTensor()
        self.score_threshold = score_threshold


    def pre_process(self, image: ndarray, graph: EngGraph) -> List[Tuple[Tensor, Union[Tensor, any]]]:
        """Turns ONE Raw Image and ONE Graph Structure into a List of Tuples of Input and Target Tensors"""

        if self.train:
            target = {'boxes': [], 'labels': []}

            # x_min=999999, y_min=999999, x_max=-999999, y_max=-999999,

            return [(self.transformer(image), target)]

        else:
            return [(self.transformer(image), None, None)]


    def post_process(self, pred_list: List[Tuple[Tensor, any]], graph: EngGraph):
        """Integrates a List of Prediction and Info Tensors into a Graph Structure"""

        boxes = pred_list[0][0]['boxes'].tolist()
        labels = pred_list[0][0]['labels'].tolist()
        scores = pred_list[0][0]['scores'].tolist()

        for box, label, score in zip(boxes, labels, scores):
            if score > self.score_threshold:
                graph.add_node(type=self.classes[label],
                               position=BoundingBox(box[0], box[1], box[2], box[3]).position)
