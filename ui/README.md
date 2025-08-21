# Circuitgraph UI
This repository contains a desktop-based graphical user interface for viewing and editing images annotations in a graph-based manner.

## Setup
In order to run the application, this `ui` repository and the `converter` repository need to be checked out locally inside a common parent directory. The required python libraries are listed in `requirements.txt` and can conveniently be installed using:

```
pip install -r requirements.txt
```

Please note that this has been tested with version 3.6.15 only.

## Usage
Run the following command from this parent directory:

```
python3 -m ui.main
```

The vast majority of functions is available both in the menu and as shortcuts (which are also stated in the menu). The status bar at the bottom of the main window can be used as guidance for complex operations.


### Shortcuts
To speed-up graph editing, the user interface provides a variety of shortcuts:

#### Editor Shortcuts
The following shortcuts are **only active while the the main editor element is selected**:

|Shortcut   | Function                          |
|-----------|-----------------------------------|
| R         | Rotate Selected Node by 45 Degree |
| E         | Rotate Selected Node by 5 Degree  |
| S         | New Edge                          |
| A         | New Node (Annotation)             |
| T         | Jump to Text Entry                |
| Del       | Delete Selected Node              |
| Tab       | Select Next Node                  |
| Shift+Tab | Select Previous Node              |
| +         | Zoom in                           |
| -         | Zoom out                          |
| 0         | Scale Image to Window             |
| Up        | Move Selected Node Up             |
| Down      | Move Selected Node Down           |
| Left      | Move Selected Node Left           |
| Right     | Move Selected Node Right          |


#### General Shortcuts
The following shortcuts are **always** active:

|Shortcut   | Function                                    |
|-----------|---------------------------------------------|
| CTRL-S    | Save File                                   |
| CTRL-R    | Open File                                   |
| CTRL-E    | Mouse-Based BB Manipulation (Node Dragging) |
| PG-UP     | Load Previous File                          |
| PG-DOWN   | Load Next File                              |
| CTRL-F1   | Set BB Color                                |
| CTRL-F2   | Set Shape Color                             |
| CTRL-F3   | Set Symbol Color                            |
| CTRL-F4   | Set Text Color                              |
| F1        | Toggle BB Visibility                        |
| F2        | Toggle Shape Visibility                     |
| F3        | Toggle Symbol Visibility                    |
| F4        | Toggle Text Visibility                      |
| F5        | Toggle Node Type Visibility                 |
| F6        | Toggle Node Rotation Visibility             |
| F7        | Toggle Port Owner Visibility                |
| F8        | Toggle Port Description Visibility          |
| F9        | Toggle File Bar                             |
| F10       | Toggle Side Bar                             |
| F11       | Toggle Fullscreen                           |
| F12       | Toggle Status Bar                           |

## Feedback
In case of questions, bug reports or feedback use the respective ticket functions of this repository's source or write to <johannes.bayer@dfki.de>.

## Programmer's Guide
The structure of this module is mainly based on two methods:
   - `update()`: receives updates and displays them in the component itself
   - `set()`: Generates updates itself, has to call `parent.update()`
