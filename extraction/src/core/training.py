"""training.py: Main Training Cycle"""

# System Imports
import json
import sys
from datetime import datetime
from os import mkdir
from os.path import join, isdir
from pathlib import Path
from random import shuffle
from subprocess import run
from typing import Callable, Tuple

# Third-Party Imports
import torch
from torchinfo import summary
from halo import Halo

# Project Imports
from extraction.src.core.package_loader import class_from_package, clsstr
from extraction.src.core.visualisation import debug_dump, plot_curve

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023-2024, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"

CUR_ABS_DIR = Path(__file__).resolve().parent


def apply_set(sample_set, model, optimizer, scheduler, loss_fn: Callable, acc_fn: Callable, batch_size: int,
              device, is_training: bool, exp_path: str, vis_fn: Callable, debug: bool) -> Tuple[float, float]:
    """Performs a Batch-Wise Dataset Application to the Model for Training and Evaluation"""

    loss_average = 0
    acc_average = 0
    sample_indices = list(range(len(sample_set)))

    if is_training:
        shuffle(sample_indices)
        model.train()

    else:
        model.eval()

    if vis_fn is not None:
        inputs = torch.stack([sample[0] for sample in sample_set])
        targets = torch.stack([sample[1] for sample in sample_set])
        preds = torch.zeros((len(sample_set),) + sample_set[0][1].shape)
        infos = [sample[2] for sample in sample_set]

    spinner = Halo(text=f"Processing batches...", spinner="monkey")
    spinner.start()

    total_batches = len(sample_set) // batch_size
    for batch_nbr in range(total_batches):
        spinner.text = f"Processing batch {batch_nbr + 1}/{total_batches}"

        batch_sample_indices = sample_indices[batch_nbr * batch_size:(batch_nbr + 1) * batch_size]
        batch = [sample_set[i] for i in batch_sample_indices]
        patch_img = torch.zeros([batch_size] + list(batch[0][0].size()), dtype=torch.float32)
        target = torch.zeros([batch_size] + list(batch[0][1].size()))

        for sample_nbr, (sample_img, sample_target, sample_info) in enumerate(batch):
        # for sample_nbr, (sample_img, sample_target) in enumerate(batch):  # fixme: does not work for object detection
            # patch_img[:] = sample_img
            patch_img[sample_nbr, :] = sample_img
            target[sample_nbr, :] = sample_target
            # TODO rename batch_XXX and add _info

        patch_img = patch_img.to(device)
        target = target.to(device)

        optimizer.zero_grad()
        pred = model(patch_img)
        loss = loss_fn(pred, target)

        if is_training:
            loss.backward()
            optimizer.step()

        if debug:
            debug_dump(patch_img, "input", exp_path)
            debug_dump(target, "target", exp_path)
            debug_dump(pred, "pred", exp_path)

        if vis_fn is not None:
            for pred_index, sample_index in enumerate(batch_sample_indices):
                preds[sample_index] = pred[pred_index].detach().clone()

        loss_average += loss.item() / batch_size
        acc_average += sum([acc_fn(pred[i], target[i]) for i in range(batch_size)]) / batch_size

    spinner.succeed("Batch processing complete.")

    loss_average = loss_average / (len(sample_set) // batch_size)
    acc_average = acc_average / (len(sample_set) // batch_size)

    if is_training:
        scheduler.step()

    if vis_fn is not None:
        if not isdir(join(exp_path, "eval")):
            mkdir(join(exp_path, "eval"))

        vis_fn(inputs, targets, preds, infos, join(exp_path, "eval"), "train" if is_training else "val")

    print(f"{'Train     ' if is_training else 'Validation'}:    loss -> {loss_average}    acc -> {acc_average}")

    return loss_average, acc_average


def train(model_cls, model_args, optim_cls, optim_args, scheduler_cls, scheduler_args,
          data_loader_cls, processor_cls, processor_args, loss_fn, acc_fn,
          set_train, set_val, db_path, save_path, batch_size, epoch_count, name, vis_fn, debug=False):
    """Performs the Model Training"""

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    exp_folder = name + "_" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    mkdir(join(save_path, exp_folder))
    exp_folder = join(save_path, exp_folder)

    with open(join(exp_folder, "config.json"), "w") as config_file:
        config_file.write(json.dumps({'model_class': clsstr(model_cls), 'model_parameter': model_args,
                                      'dataloader_class': clsstr(data_loader_cls),
                                      'processor_class': clsstr(processor_cls), 'processor_parameter': processor_args,
                                      'optimizer_class': clsstr(optim_cls), 'optimizer_parameter': optim_args,
                                      'scheduler_class': clsstr(scheduler_cls), 'scheduler_parameter': scheduler_args,
                                      'training_parameter': {"drafters_set_train": set_train,
                                                             "drafters_set_val": set_val,
                                                             "drafter_set_test": [],
                                                             "db_path": str(db_path),
                                                             "batch_size": batch_size,
                                                             "epochs": epoch_count,
                                                             "name": name,
                                                             "loss_fn": str(loss_fn),
                                                             "acc_fn": str(acc_fn),
                                                             "vis_fn": str(vis_fn),
                                                             "debug": debug}},
                                     indent=2))

    set_train = data_loader_cls(drafters=set_train, db_path=db_path, augment=True,
                                processor_cls=processor_cls, processor_args=processor_args, debug=debug,
                                caching=False)  # fixme: debug, the cached file is over 80GB...
    set_val = data_loader_cls(drafters=set_val, db_path=db_path, augment=False,
                              processor_cls=processor_cls, processor_args=processor_args, debug=debug,
                              caching=False)  # fixme: debug, the cached file is over 80GB...

    model = model_cls(**model_args)
    model.to(device)


    def _normalize_optim_args(optim_args: dict) -> dict:
        args = dict(optim_args or {})
        # Accept both 'lr' and 'learning_rate'
        if 'learning_rate' in args and 'lr' not in args:
            args['lr'] = args.pop('learning_rate')
        return args


    # ... inside train(...)
    optim_args = _normalize_optim_args(config.get('optimizer_parameter', {}))
    optimizer = optim_cls(model.parameters(), **optim_args)
    scheduler = scheduler_cls(optimizer, **scheduler_args)

    if debug:
        print(summary(model))

    curve_train_loss = []
    curve_val_loss = []
    curve_train_acc = []
    curve_val_acc = []

    for epoch_nbr in range(epoch_count):
        print(f"Epoch {epoch_nbr} / {epoch_count}")

        train_loss, train_acc = apply_set(set_train, model, optimizer, scheduler, loss_fn, acc_fn, batch_size,
                                          device, is_training=True, exp_path=exp_folder, vis_fn=vis_fn, debug=debug)
        val_loss, val_acc = apply_set(set_val, model, optimizer, scheduler, loss_fn, acc_fn, batch_size,
                                      device, is_training=False, exp_path=exp_folder, vis_fn=vis_fn, debug=debug)

        curve_train_loss.append(train_loss)
        curve_val_loss.append(val_loss)
        curve_train_acc.append(train_acc)
        curve_val_acc.append(val_acc)

        plot_curve({"Train Loss": curve_train_loss, "Val Loss": curve_val_loss,
                    "Train Acc": curve_train_acc, "Val Acc": curve_val_acc},
                   epoch_count, exp_folder)

        if val_acc == max(curve_val_acc):
            print("Saving Model...", end="", flush=True)
            torch.save(model.state_dict(), join(exp_folder, "model_state.pt"))
            print("Done.")

            if vis_fn is not None:
                if not isdir(join(exp_folder, 'eval-best')):
                    mkdir(join(exp_folder, "eval-best"))

                run(f"cp {join(exp_folder, 'eval', '*')} {join(exp_folder, 'eval-best')}", shell=True)


if __name__ == "__main__":
    test_mode = True  # fixme: debug
    if test_mode:
        print("Running in test mode. Setting up default config file.")

        # # Exp1: Object Detection:
        # config_file = CUR_ABS_DIR / "../../config/object_detection_test.json"  # fixme: debug, use less data

        # Exp2: Segmentation:
        config_file = CUR_ABS_DIR / "../../config/segmentation_test.json"  # fixme: debug, use less data

        # Set the system argument to the config file path:
        sys.argv = [sys.argv[0], str(config_file)]

    if len(sys.argv) != 2:
        print("Error: One config JSON file needs to be provided.")

    else:
        with open(sys.argv[1]) as json_file:
            config = json.loads(json_file.read())

        train(model_cls=class_from_package(config['model_class']),
              model_args=config['model_parameter'],
              optim_cls=class_from_package(config['optimizer_class']),
              optim_args=config["optimizer_parameter"],
              scheduler_cls=class_from_package(config['scheduler_class']),
              scheduler_args=config["scheduler_parameter"],
              data_loader_cls=class_from_package(config['dataloader_class']),
              processor_cls=class_from_package(config['processor_class']),
              processor_args=config['processor_parameter'],
              loss_fn=class_from_package(config['training_parameter']['loss_fn'])(),
              acc_fn=class_from_package(config['training_parameter']['acc_fn']),
              set_train=config['training_parameter']['drafters_set_train'],
              set_val=config['training_parameter']['drafters_set_val'],
              db_path=CUR_ABS_DIR / "../../../" / config['training_parameter']['db_path'],
              save_path=CUR_ABS_DIR / "../../model",
              batch_size=config['training_parameter']['batch_size'],
              epoch_count=config['training_parameter']['epochs'],
              name=config['training_parameter']['name'],
              vis_fn=class_from_package(config['training_parameter']['vis_fn']) if 'vis_fn' in config[
                  'training_parameter'] else None,
              debug=config['training_parameter']['debug'])
