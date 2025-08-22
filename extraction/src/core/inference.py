"""inference.py: Performs Model Inference given an Image and optional Graph Structure"""

import json
# System Imports
import sys
from os.path import join
from pathlib import Path
from typing import Type, Optional, Dict

# Third-Party Imports
import cv2
import torch

# Project Imports
from converter.converter.jsonConverter import JSONConverter
from extraction.src.core.package_loader import class_from_package

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023-2024, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"

CUR_ABS_DIR = Path(__file__).resolve().parent


def inference(model_path: str, model_cls: Type, model_args: Dict,
              path_image: str, path_graph: str,
              processor_cls: Type, processor_args: Dict,
              name: Optional[str] = None, debug: bool = False) -> None:
    """Loads an Image, an EngGraph in Pascal VOC Format, and a Model,
    Performs Preprocessing, Applies the Model to all Tensors, Postprocesses them and Saves the Results"""

    print(f"Performing {name}")

    print("Loading Graph...")
    graph = JSONConverter().load(path_graph)

    print("Loading Image...")
    image = cv2.imread(path_image)

    print("Loading Model...")
    model = model_cls(**model_args)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

    print("Loading Processor...")
    processor = processor_cls(augment=False, train=False, debug=debug, **processor_args)
    processor.set_model(model=model)
    processor.inference(image=image, graph=graph)

    print("Saving Graph...")
    JSONConverter().store(graph, path_graph)

    print("Done.")


if __name__ == "__main__":
    test_mode = True  # fixme: debug
    if test_mode:
        print("Running in test mode. Setting up default config file.")

        # Exp1: Full pipeline:
        path_image = CUR_ABS_DIR / "../../../gtdb-hd/drafter_0/images/C1_D1_P1.png"
        path_graph = CUR_ABS_DIR / "../../../gtdb-hd/drafter_0/annotations/C1_D1_P1.xml"
        config_file = CUR_ABS_DIR / "../../config/object_detection_test.json"  # fixme: debug, use less data

        sys.argv = [sys.argv[0], str(config_file), str(path_image), str(path_graph)]

    if len(sys.argv) != 4:
        print("Error: Must provide paths to files: Image (PNG), Graph (Pascal VOC), Config (JSON)")

    else:
        path_image = sys.argv[2]
        path_graph = sys.argv[3]

        with open(sys.argv[1]) as json_file:
            config = json.loads(json_file.read())

        inference(model_path=join("extraction", "model", config['training_parameter']['name'], "model_state.pt"),
                  model_cls=class_from_package(config['model_class']),
                  model_args=config['model_parameter'],
                  path_image=path_image,
                  path_graph=path_graph,
                  processor_cls=class_from_package(config['processor_class']),
                  processor_args=config['processor_parameter'],
                  name=config['training_parameter']['name'],
                  debug=config['training_parameter']['debug'])
