"""nodeSnippetProcessor.py: Base Class for Pre-/Post-Processing of Node Snippets"""

# System Imports
from abc import abstractmethod
from typing import Tuple, List, Union
from random import randint

# Project Imports
from converter.core.engineeringGraph import EngGraph
from extraction.src.core.processor import Processor

# Third-Party Imports
from numpy import ndarray
from torch import Tensor

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class NodeSnippetProcessor(Processor):
    """Base Class for Pre-/Post-Processing of Node Snippets"""

    def __init__(self, augment: bool, train: bool, debug: bool, rand_crop: int):
        super().__init__(augment, train, debug)
        self.rand_crop = rand_crop


    @abstractmethod
    def _node_filter(self, node_data: dict) -> bool:
        """Decides Whether a Node Can be Processed"""

        pass


    @abstractmethod
    def _make_input(self, snippet: ndarray, node_data: dict) -> List[Tensor]:
        """"Creates a List of Input Tensors for the Model"""

        pass


    @abstractmethod
    def _make_target(self, node_data: dict) -> List[Tensor]:
        """Creates a List of Target Models for the Model"""

        pass


    @abstractmethod
    def _integrate_data(self, pred: Tensor, node_data: dict) -> None:
        """Integrates the Model's Predictions into the Node's Attributes"""

        pass


    def pre_process(self, image: ndarray, graph: EngGraph) -> List[Tuple[Tensor, Union[Tensor, any]]]:
        """Turns ONE Raw Image and ONE Graph Structure into a List of Tuples of Input and Target/Info Tensors"""

        samples = []

        for node_id, node_data in graph.nodes.items():
            if self._node_filter(node_data):
                top = int(node_data['position']["y"] - node_data['position']["height"]/2)
                bottom = int(node_data['position']["y"] + node_data['position']["height"]/2)
                left = int(node_data['position']["x"] - node_data['position']["width"]/2)
                right = int(node_data['position']["x"] + node_data['position']["width"]/2)
                snippet = image[top:bottom, left: right]

                if self.train:
                    inputs = self._make_input(snippet, node_data)
                    targets = self._make_target(node_data)
                    samples += zip(inputs, targets, [node_data for _ in inputs])

                    if self.augment:
                        top_augment = max(0, top+randint(-self.rand_crop, self.rand_crop))
                        bottom_augment = min(image.shape[0], bottom+randint(-self.rand_crop, self.rand_crop))
                        left_augment = max(0, left+randint(-self.rand_crop, self.rand_crop))
                        right_augment = min(image.shape[1], right+randint(-self.rand_crop, self.rand_crop))
                        snippet_augment = image[top_augment:bottom_augment, left_augment: right_augment]

                        inputs = self._make_input(snippet_augment, node_data)
                        targets = self._make_target(node_data)
                        samples += zip(inputs, targets, [node_data for _ in inputs])

                else:
                    samples += [(snippet, None, node_id) for snippet in self._make_input(snippet, node_data)]

        return samples


    def post_process(self, pred_list: List[Tuple[Tensor, any]], graph: EngGraph) -> None:
        """Integrates a List of Prediction and Info Tensors into a Graph Structure"""

        for pred, node_id in pred_list:
            self._integrate_data(pred, graph.nodes[node_id])
