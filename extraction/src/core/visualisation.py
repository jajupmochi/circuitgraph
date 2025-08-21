"""visualisation.py: Metric and Data Visualisation and Calculation Tools"""

# System Imports
import sys
import json
from os.path import join

# Third-Party Imports
import torch
import numpy as np
import matplotlib.pyplot as plt

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"


def debug_dump(batch_data: torch.Tensor, name: str, debug_path: str):
    """Dumps the First Sample of a batch tensor as a List of 2D Plots"""

    sample = batch_data[0].detach().cpu().numpy()

    if len(sample.shape) == 1:
        sample = sample[np.newaxis, np.newaxis]

    if len(sample.shape) == 2:
        sample = sample[np.newaxis]

    for counter, debug_slice in enumerate(sample):
        plt.clf()
        plt.imshow(debug_slice, cmap='hot', interpolation='nearest', vmin=-1, vmax=1)
        plt.savefig(join(debug_path, f"{name}_{counter}.png"))


def plot_curve(metrics: dict, max_epochs: int, exp_path: str = None, show_max: bool = True):
    """Plots and Saves the Learning Curves"""

    #plt.clf()
    fig, axis_acc = plt.subplots()
    axis_loss = axis_acc.twinx()

    axis_acc.axis(xmin=0, xmax=max_epochs, ymin=0, ymax=1.0)
    axis_loss.axis(xmin=0, xmax=max_epochs, ymin=0, ymax=0.1)
    axis_acc.grid()

    plt.title("Learning Curve")
    axis_acc.set_xlabel("Epoch")
    axis_acc.set_ylabel("Accuracy")
    axis_loss.set_ylabel("Loss")

    if show_max:
        max_val_acc = max(metrics['Val Acc'])
        max_val_acc_epoch = metrics['Val Acc'].index(max_val_acc)
        axis_acc.axhline(y=max_val_acc, color="grey", linewidth=1)
        plt.axvline(x=max_val_acc_epoch, color="grey", linewidth=1)

        axis_acc.text(0.5, max_val_acc+0.005, f"{max_val_acc:.4f}", color="grey")
        axis_acc.text(max_val_acc_epoch+0.5, 0.005, f"{max_val_acc_epoch}", color="grey")

    for metric_name, metric_curve in metrics.items():
        axis = axis_loss if "Loss" in metric_name else axis_acc
        axis.plot(metric_curve, label=metric_name,
                  color="tab:blue" if "Train" in metric_name else "tab:orange",
                  linestyle="solid" if "Acc" in metric_name else "dotted")

    axis_acc.legend(loc="upper left")
    axis_loss.legend(loc="upper right")
    fig.tight_layout()

    if exp_path:
        plt.savefig(join(exp_path, "learning_curve.png"), dpi=400)

        with open(join(exp_path, "learning_curve.json"), "w") as logfile:
            logfile.write(json.dumps(metrics, indent=4))

    else:
        plt.show()

    plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: One metrics JSON file needs to be provided")

    else:
        with open(sys.argv[1]) as json_file:
            metrics_vis = json.loads(json_file.read())
            plot_curve(metrics_vis, max_epochs=max([len(metric) for metric in metrics_vis.values()]))
