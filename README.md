# Circuitgraph
Circuitgraph is a software for extracting electrical graphs from handwritten and printed circuit diagram (schematic) images as well as understanding, explaining and refining them. This repository mainly serves as an aggregation point to get started conveniently. For more details, please refer to the README files of the individual submodules.

## Setup
Firt of all, clone this repo using:

```
git clone https://gitlab.com/circuitgraph/main.git circuitgraph
```

Go to the repo folder:

```
cd circuitgraph
```

and check out all submodules:

```
git submodule update --init
```

Install the dependencies:

```
pip3.6 install -r ui/requirements.txt
```

Dowload the CGHD dataset from [Zenodo](https://zenodo.org/record/8266951) or [Kaggle](https://www.kaggle.com/datasets/johannesbayer/cghd1152) and place the content of the zip file in the `gtdb-hd` folder.

## Starting the Desktop Application

```
python3 -m ui.main
```
