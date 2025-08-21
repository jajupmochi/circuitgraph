# Circuitgraph Extraction

This repository contains scripts for training and inferencing models that serve the process of extracting electrical graphs from raster images.

## Structure
The folder structure is made up as follows:

```
extraction
│   README.md                  # This File
└───config                     # Setup Files for Training and Inferencing
│   └   ...
└───src                        # Code Base
│   └───core                   # Core Functionality
│   │   │   inference.py       # General Inferencing
│   │   │   package_loader.py  # Class Loader
│   │   └   training.py        # Task-Agnostic Training Cycle
│   └───loader                 # Dataset Loader Classes
│   │   └   ...
│   └───models                 # Model Definition Classes
│   │   └   ...
│   └───processor              # Pre/Post Processors
│       └   ...
│   └───utils                  # Ausiliary Functions
│       └   ...
└───model                      # Trained Models
        └   ...
```

### Config Files
Config files are places in `extraction/config`. Every config file and describes a setup that can be used for both model training and inference.

### Loaders
The task of a loader is to read data from a folder structure of a dataset and provide them to an aggregated processor for generating a list of `(input, target)` pairs (both `input` and `target` have to be of type `torch.Tensor`). Loaders are places under `extraction/src/loaders`.

### Models
Models, are defined as PyTorch Module in `extraction/src/models` and trained models are stored under `extraction/model`.

### Processors
The main task of a processor (placed in `extraction/src/processor`) is to provide functionality for handling **a single sample** ("one circuit", e.g. a pair of graph and image). More Precisely, the Processor is responsible for:

 - Data Augmentation
 - Generation of Model Input
   - Generation of a list of pairs of `torch.Tensor` that serve as model input and target during training
 - Interpretation of model's output

### Utils
Simple encoder/decoder, accuracy metrics and other auxiliary functions are places in `extraction/src/utils`.

## Training
The Training Pipeline is designed in an universal and modular fashion, in which `model` and `dataloader` classes need to be combined by a `config` file. For example, in order to perform handwriting recognition training, the training cycle need to be called as follows:

```
python3 -m extraction.src.core.training extraction/config/text.json
```

## Inference
Similar to the training process, inference relies on the provision of a `config` file. Apart from that, an input image as well as an input graph have to be provided:

```
python3 -m extraction.src.core.inference extraction/config/text.json temp_x/image.png temp_x/graph.xml
```

