"""fasterrcnn.py: Wrapped torchvision Implementation of Faster RCNN"""

# Third-Party Imports
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.faster_rcnn import FasterRCNN as TVFasterRCNN
from torchvision.models.detection.backbone_utils import resnet_fpn_backbone

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class FasterRCNN(TVFasterRCNN):
    """Wrapped torchvision Implementation of Faster RCNN"""

    def __init__(self, num_classes: int, pretrained_backbone: bool, backbone: str,
                 box_detections: int, trainable_backbone_layers: int):

        super().__init__(resnet_fpn_backbone(backbone,
                                             pretrained_backbone,
                                             trainable_layers=_validate_trainable_layers(pretrained_backbone,
                                                                                         trainable_backbone_layers,
                                                                                         5, 3)),
                         num_classes)

        self.roi_heads.box_predictor = FastRCNNPredictor(self.roi_heads.box_predictor.cls_score.in_features,
                                                         num_classes)


def _validate_trainable_layers(pretrained, trainable_backbone_layers, max_value, default_value):
    """
    copied from latest torchvision.models.detection.backbone_utils as backport solution,
    due to missing function in current version on cluster!
    """
    # dont freeze any layers if pretrained model or backbone is not used
    if not pretrained:
        if trainable_backbone_layers is not None:
            warnings.warn(
                "Changing trainable_backbone_layers has not effect if "
                "neither pretrained nor pretrained_backbone have been set to True, "
                "falling back to trainable_backbone_layers={} so that all layers are trainable".format(max_value))
        trainable_backbone_layers = max_value

    # by default freeze first blocks
    if trainable_backbone_layers is None:
        trainable_backbone_layers = default_value
    assert 0 <= trainable_backbone_layers <= max_value
    return trainable_backbone_layers
