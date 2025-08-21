"""segmentationProcessor.py: Processor for Semantic Segmentation on Patches"""

# System Imports
from typing import Tuple, List, Union
from random import randint

# Project Imports
from converter.core.engineeringGraph import EngGraph
from extraction.src.core.processor import Processor

# Third-Party Imports
import cv2
import torch
import numpy as np
from torch import Tensor
from torchvision import transforms

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class GaussianNoise(object):  # TODO CAREFULLY move this an similar definitions to utils

    def __init__(self, p=1.0):
        self.p = p

    def __call__(self, img):
        if torch.rand(1).item() < self.p:
            return img

        return img + torch.randn(img.shape) * 0.15


class SegmentationProcessor(Processor):
    """Processor for Semantic Segmentation on Patches"""

    transform = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize((0.5,), (0.5,))])
    transform_augment = transforms.Compose([GaussianNoise(0.5),
                                            transforms.RandomGrayscale(),
                                            transforms.RandomInvert()])

    def __init__(self, augment: bool, train: bool, debug: bool, patch_size: int, samples_per_image: int):
        super().__init__(augment, train, debug)

        self.patch_size = patch_size
        self.samples_per_image = samples_per_image


    @staticmethod
    def sample(img: np.ndarray, patch_size: int, offset_x: int, offset_y: int, rotation: int, zoom: int) -> Tensor:

        patch = img[offset_y:offset_y + patch_size, offset_x:offset_x + patch_size]

        if rotation == 90:
            patch = cv2.rotate(patch, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if rotation == 180:
            patch = cv2.rotate(patch, cv2.ROTATE_180)

        if rotation == 270:
            patch = cv2.rotate(patch, cv2.ROTATE_90_CLOCKWISE)

        return SegmentationProcessor.transform(patch)


    @staticmethod
    def sample_likewise(img_raw: np.ndarray, img_map: np.ndarray, patch_size: int,
                        offset_x: int = None, offset_y: int = None, rotation: int = None,
                        zoom: int = 1, augment_transform: bool = True) -> Tuple[Tensor, Tensor, any]:
        """Crops and Processes Patches from two images similarly"""

        img_height, img_width, _ = img_raw.shape

        if offset_x is None:
            offset_x = randint(0, img_width - patch_size)

        if offset_y is None:
            offset_y = randint(0, img_height - patch_size)

        if rotation is None:
            rotation = randint(0, 3)*90

        patch_raw = SegmentationProcessor.sample(img_raw, patch_size, offset_x, offset_y, rotation, zoom)
        patch_map = SegmentationProcessor.sample(img_map, patch_size, offset_x, offset_y, rotation, zoom)

        if augment_transform and randint(0, 1):
            patch_raw = SegmentationProcessor.transform_augment(patch_raw)

        return patch_raw, patch_map, None


    def pre_process(self, img_raw: np.ndarray, img_map: np.ndarray) -> List[Tuple[Tensor, Tensor, any]]:
        """Turns ONE Raw Image and ONE Graph Structure into a List of Tuples of Input and Target/Info Tensors"""

        samples = []
        img_height, img_width, _ = img_raw.shape

        if self.train:

            for _ in range(self.samples_per_image):
                if self.augment:
                    samples += [self.sample_likewise(img_raw, img_map, self.patch_size)]

                else:
                    samples += [self.sample_likewise(img_raw, img_map, self.patch_size,
                                                     rotation=0, zoom=1, augment_transform=False)]

        else:
            for x in range(img_width // self.patch_size):
                for y in range(img_height // self.patch_size):
                    start_x = x * self.patch_size
                    end_x = start_x + self.patch_size
                    start_y = y * self.patch_size
                    end_y = start_y + self.patch_size
                    samples += [(self.transform(img_raw[start_y: end_y, start_x:end_x]),
                                 None,
                                 (start_x, start_y, end_x, end_y, img_width, img_height))]

                    start_y = img_height - self.patch_size - y * self.patch_size
                    end_y = start_y + self.patch_size
                    samples += [(self.transform(img_raw[start_y: end_y, start_x:end_x]),
                                 None,
                                 (start_x, start_y, end_x, end_y, img_width, img_height))]

                    start_x = img_width - self.patch_size - x * self.patch_size
                    end_x = start_x + self.patch_size
                    samples += [(self.transform(img_raw[start_y: end_y, start_x:end_x]),
                                 None,
                                 (start_x, start_y, end_x, end_y, img_width, img_height))]

        return samples


    def post_process(self, pred_list: List[Tuple[Tensor, any]], graph: EngGraph) -> None:
        """Integrates a List of Prediction and Info Tensors into a Graph Structure"""

        _, _, _, _, img_width, img_height = pred_list[0][1]
        seg_map = np.ones((img_height, img_width), dtype=np.float32)

        for tensor, (start_x, start_y, end_x, end_y, _, _) in pred_list:
            seg_map_patch = tensor[0].detach().numpy()
            seg_map[start_y:end_y, start_x:end_x] = np.minimum(seg_map_patch,seg_map[start_y:end_y, start_x:end_x])

        seg_map_thres = (255 * (seg_map > 0)).astype(np.uint8)

        if self.debug:
            cv2.imwrite("seg_map.png", (255 * seg_map).astype(np.uint8))
            cv2.imwrite("seg_map_thes.png", seg_map_thres)

        self.extract_edges(graph, seg_map_thres)


    def extract_edges(self, graph: EngGraph, seg_map_thres: np.ndarray,
                      cnt_area_min: int = 50, cnt_area_max: int = 100000, margin: int = 5, add_ports: bool = True):

        node_bbs = []

        for node_id, node_data in graph.nodes.items():
            top = int(node_data['position']["y"] - node_data['position']["height"] / 2)
            bottom = int(node_data['position']["y"] + node_data['position']["height"] / 2)
            left = int(node_data['position']["x"] - node_data['position']["width"] / 2)
            right = int(node_data['position']["x"] + node_data['position']["width"] / 2)
            seg_map_thres[top:bottom, left: right] = 255
            node_bbs += [(top, bottom, left, right, node_id)]

        cv2.imwrite("seg_map_node_free.png", seg_map_thres)

        contours, hierarchy = cv2.findContours(seg_map_thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours = [contour for contour in contours if cnt_area_min < cv2.contourArea(contour) < cnt_area_max]

        img_height, img_width = seg_map_thres.shape
        contour_img = cv2.drawContours(np.zeros((img_height, img_width, 3), dtype=np.uint8),
                                       contours, -1, (0, 255, 0), 3)

        if self.debug:
            cv2.imwrite("seg_map_thes_kp.png", contour_img)

        for contour in contours:
            nodes_id = []
            ports_x = []
            ports_y = []

            for [[x, y]] in contour:
                for top, bottom, left, right, node_id in node_bbs:
                    if node_id not in nodes_id:
                        if (((abs(y-top) < margin or abs(y-bottom) < margin) and (left-margin < x < right+margin)) or
                            ((abs(x-left) < margin or abs(x-right) < margin) and (top-margin < y < bottom+margin))):
                            nodes_id += [node_id]
                            ports_x += [x]
                            ports_y += [y]

            if len(nodes_id) == 2:
                source_node_id, target_node_id = nodes_id
                source_port_x, target_port_x = ports_x
                source_port_y, target_port_y = ports_y
                edge_args = {}

                if add_ports and graph.nodes[source_node_id]['type'] not in ("junction", "crossover"):
                    source_port = graph.add_port(source_node_id, {'x': int(source_port_x), 'y': int(source_port_y)})
                    edge_args['sourcePort'] = source_port

                if add_ports and graph.nodes[target_node_id]['type'] not in ("junction", "crossover"):
                    target_port = graph.add_port(target_node_id, {'x': int(target_port_x), 'y': int(target_port_y)})
                    edge_args['targetPort'] = target_port

                graph.add_edge(source=source_node_id, target=target_node_id, **edge_args)
