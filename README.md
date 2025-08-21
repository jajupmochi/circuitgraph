# Circuitgraph

Circuitgraph is a software for extracting electrical graphs from handwritten and printed circuit diagram (schematic) images as well as understanding, explaining and refining them. This repository mainly serves as an aggregation point to get started conveniently. For more details, please refer to the README files of the individual submodules.

**Attention: this repo was originally forked from `Circuitgraph/Extraction` [(link)](https://gitlab.com/circuitgraph/extraction).**
**We thank the authors who generously provided the codes, which maks this repo possible.)**
**Since the license of the original repo is not clear (which is annotated as CC in files), this repo is only for research and educational purposes and is thus issued with a GPL-3.0 license.**
**Please use it as caution.**

## Setup
Firt of all, clone this repo using:

```
git clone https://gitlab.com/circuitgraph/main.git circuitgraph
```

Go to the repo folder:

```
cd circuitgraph
```

and check out all submodules (deprecated, no need to do this anymore, since the submodules are now included in the main repo):

```
git submodule update --init
```

Install the dependencies by

```bash
uv sync --no-cache
```

or

```
pip install [-e] .
```

Notice this will install all the dependencies for all submodules, which is listed in [`pyproject.toml`](pyproject.toml) file.

Dowload the CGHD dataset from [Zenodo](https://zenodo.org/record/8266951) or [Kaggle](https://www.kaggle.com/datasets/johannesbayer/cghd1152), unzip it, and place the content of the zip file in the `gtdb-hd` folder.

## Desktop Application Usage

For Linux users, make sure you have `python3-tk` installed in your system:

```bash
sudo apt-get update
sudo apt-get install python3-tk
# Check if it is installed:
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

While being in the root folder of the `main` repository, run:

```
python3 -m ui.main
```
