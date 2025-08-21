"""User Interface for Graph Visualisation and Editing"""

# System Imports
from typing import List

# Project Imports
from converter.core.engineeringGraph import EngGraph
from converter.core.boundingbox import BoundingBox
from converter.core.renderer import Renderer
from converter.core.geometry import Point, Line, Rectangle, Circle, Polygon, Text
from ui.utils import encode_color, bbox_to_pos, pos_to_bbox

# Third-Party Imports
from tkinter import Canvas, NW, Event
from PIL import ImageTk, Image, ImageOps

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022-2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



class GraphEditor:
    """User Interface for Graph Visualisation and Editing"""

    ZOOM_MIN = 0.2
    ZOOM_MAX = 3
    ZOOM_STEP = 1.1
    NODE_SHIFT_STEP = 10
    cursor_assign = {"HL-T": "top_side",
                     "HL-B": "bottom_side",
                     "HL-L": "left_side",
                     "HL-R": "right_side",
                     "HL-LT": "top_left_corner",
                     "HL-RT": "top_right_corner",
                     "HL-LB": "bottom_left_corner",
                     "HL-RB": "bottom_right_corner"}

    def __init__(self, parent) -> None:
        """Creates the Main Drawing Canvas"""

        # Create Sub-Components
        self.parent = parent
        self.renderer = Renderer()
        self.img_raw: Union[Image, None] = None
        self.img_scaled = None

        # Create UI Elements
        self.canvas = Canvas(self.parent.root, width=800, height=600, bg='white', cursor='cross',
                             xscrollincrement=1, yscrollincrement=1)
        self.canvas.pack(fill="both", expand=True)

        # Bind Mouse Events
        self.canvas.bind('<ButtonPress-1>', lambda event: self.mouse_down(event))
        self.canvas.bind("<B1-Motion>", lambda event: self.mouse_drag(event))
        self.canvas.bind("<Motion>", lambda event: self.mouse_move(event))
        self.canvas.bind('<ButtonRelease-1>', lambda event: self.mouse_up(event))
        self.canvas.bind('<Double-Button-1>', lambda event: self.mouse_doubleclick(event))
        self.canvas.bind("<MouseWheel>", lambda event: self.zoom(event))  # Support MS-Win
        self.canvas.bind("<Button-4>", lambda event: self.zoom(event))    # Support X11
        self.canvas.bind("<Button-5>", lambda event: self.zoom(event))    # Support X11

        # Bind Node Manipulation
        self.canvas.bind("<r>", lambda x: self.rotate_node())
        self.canvas.bind("<e>", lambda x: self.rotate_node(5))
        self.canvas.bind("<q>", lambda x: self.new_annotation())
        self.canvas.bind("<m>", lambda x: self.new_edge())
        self.canvas.bind("<Control-d>", lambda x: self.duplicate_node())
        self.canvas.bind("<Delete>", lambda x: self.remove_node())

        # Bind Bar Menu Quick Access
        self.canvas.bind("<t>", lambda x: self.parent.side_bar.entry_text.focus_set())
        self.canvas.bind("<w>", lambda x: self.parent.side_bar.spinbox_top.focus_set())
        self.canvas.bind("<a>", lambda x: self.parent.side_bar.spinbox_left.focus_set())
        self.canvas.bind("<s>", lambda x: self.parent.side_bar.spinbox_bottom.focus_set())
        self.canvas.bind("<d>", lambda x: self.parent.side_bar.spinbox_right.focus_set())
        self.canvas.bind("<c>", lambda x: self.parent.side_bar.optionmenu_class.focus_set() or self.parent.side_bar.optionmenu_class.event_generate('<space>'))

        # Bind Navigation Events
        self.canvas.bind("<Tab>", lambda x: self.iter_node())
        self.canvas.bind("<Shift-ISO_Left_Tab>", lambda x: self.iter_node(False))

        self.canvas.bind("<Key-plus>", lambda x: self.zoom("+"))
        self.canvas.bind("<Key-minus>", lambda x: self.zoom("-"))
        self.canvas.bind("0", lambda x: self.fit_view())

        self.canvas.bind('<Escape>', lambda x: self.abort())

        # Bind Node Shift Events
        self.canvas.bind("<Up>", lambda x: self.move_node(0, -self.NODE_SHIFT_STEP))
        self.canvas.bind("<Down>", lambda x: self.move_node(0, self.NODE_SHIFT_STEP))
        self.canvas.bind("<Left>", lambda x: self.move_node(-self.NODE_SHIFT_STEP, 0))
        self.canvas.bind("<Right>", lambda x: self.move_node(self.NODE_SHIFT_STEP, 0))

        # Define Control Members
        self.graph: EngGraph = None
        self.selected_node = None

        self.new_bbox_state = 0
        self.new_polygon_state = False
        self.new_edge_state = 0
        self.polygon: List[Point] = []
        self.p1: Point = Point(0, 0)  # Node BB Creation
        self.source = None            # Edge Creation
        self.source_connector = None  # Edge Creation
        self.cursor_pos: Point = Point(0, 0)
        self.scale = 1.0
        self.update_in_progress = False
        self.mouse_node_manipulation = False  # Node Dragging and Resizing
        self.manipulation_mode = None
        self.renderer_settings = {'rawImage': True,  # This First Parameter is for render_graph() only
                                  'mode': "complex", 'junctionCircles': False, 'shapes': False, 'symbol': False,
                                  'rectangles': True, 'drawRotation': False, 'drawNodeId': False, 'drawNodeType': True,
                                  'portPosition': False, 'portOwner': False, 'portType': False,
                                  'drawEdgePorts': True, 'text': True, 'propOwner': False,
                                  'symbolColor': (255, 0, 0), 'rectangleColor': (255, 130, 0),
                                  'textColor': (255, 50, 255), 'shapeColor': (255, 0, 0), 'edgeColor': (0, 0, 255)}


    def toggle_dragging(self):
        """Enables or Disables the Dragging and Resizing of Nodes by Mouse"""

        self.mouse_node_manipulation = not self.mouse_node_manipulation
        self.canvas.config(cursor='cross')


    def get_rendering(self, parameter: str):
        """Returns a Rendering Parameter"""

        return self.renderer_settings.get(parameter, None)


    def set_rendering(self, parameter: str, value=None):
        """Sets a Rendering Parameter.

        If no Value is given, parameter considered flag and toggled"""

        if type(self.renderer_settings.get(parameter, None)) is bool:
            if type(value) is bool:
                self.renderer_settings[parameter] = value
                
            else:
                self.renderer_settings[parameter] = not self.renderer_settings[parameter]

        else:
            self.renderer_settings[parameter] = value

        self.render_graph()


    def render_graph(self):
        """Renders Both Image and Graph to the Canvas"""

        self.canvas.delete("all")

        if self.img_raw and self.renderer_settings.get('rawImage', False):
            self.canvas.create_image(0, 0, image=self.img_scaled, anchor=NW)

        if self.graph:
            for item in self.renderer.render(self.graph, **self.renderer_settings) + self.overlay():

                if type(item) is Line:
                    self.canvas.create_line(item.a.x, item.a.y, item.b.x, item.b.y, width=item.stroke,
                                            fill=encode_color(item.color), tag=item.nodeId)

                if type(item) is Rectangle:
                    self.canvas.create_rectangle(item.left, item.top, item.right, item.bottom,
                                                 outline=encode_color(item.color),
                                                 fill=encode_color(item.color),  # TODO use proper color
                                                 width=item.stroke, tag=item.nodeId,
                                                 stipple="gray25")

                if type(item) is Circle:
                    self.canvas.create_oval(item.x - item.radius, item.y - item.radius,
                                            item.x + item.radius, item.y + item.radius,
                                            fill=encode_color(item.fillColor), tag=item.nodeId,
                                            outline=encode_color(item.color), width=item.stroke)

                if type(item) is Polygon:
                    self.canvas.create_polygon([nbr for p in item.points for nbr in p],
                                               outline=encode_color(item.color),
                                               fill=encode_color(item.fillColor), tag=item.nodeId,
                                               width=item.stroke)

                if type(item) is Text:
                    self.canvas.create_text(item.x, item.y, text=item.text, anchor=item.anchor, tag=item.nodeId,
                                            fill=encode_color(item.color), angle=item.rotation, font=('Helvetica 15'))

        self.canvas.scale("all", 0, 0, self.scale, self.scale)


    def crosshair(self, pos: Point, color):
        """Horizontal and Vertical Lines Through a Given Point"""

        return [Line(Point(self.canvas.canvasx(0)/self.scale, pos.y),
                     Point(self.canvas.canvasx(self.canvas.winfo_width())/self.scale, pos.y),
                     color, 1, None),
                Line(Point(pos.x, self.canvas.canvasy(0)/self.scale),
                     Point(pos.x, self.canvas.canvasy(self.canvas.winfo_height())/self.scale),
                     color, 1, None)]


    def highlight(self, node_data, color=(230, 230, 0), corner_color=(190, 190, 0), edge=4, corner=5):
        """Highlighting Outline for a Focused Element"""

        corner /= self.scale

        if self.renderer_settings['shapes'] and node_data['shape']:
            return self.polyline([Point(p[0], p[1]) for p in node_data['shape']], corner_radius=corner, close=True)

        left, right, top, bottom, _ = pos_to_bbox(node_data['position'])

        return [Line(Point(left, top), Point(right, top), color, edge, "HL-T"),
                Line(Point(left, bottom), Point(right, bottom), color, edge, "HL-B"),
                Line(Point(left, top), Point(left, bottom), color, edge, "HL-L"),
                Line(Point(right, top), Point(right, bottom), color, edge, "HL-R"),
                Circle(left, top, corner, corner_color, 0, color, "HL-LT"),
                Circle(right, top, corner, corner_color, 0, color, "HL-RT"),
                Circle(left, bottom, corner, corner_color, 0, color, "HL-LB"),
                Circle(right, bottom, corner, corner_color, 0, color, "HL-RB")]


    def polyline(self, poly: List[Point], color_edge=(230, 230, 0), corner_color=(190, 190, 0),
                 corner_radius=5, edge_width=4, close=False):
        """Draws a Polyline with Circles as Corners"""

        lines = []
        corners = [Circle(point.x, point.y, corner_radius, corner_color, 0, corner_color, f"HL-PP{point_nbr}")
                   for point_nbr, point in enumerate(poly)]

        if len(poly) > 1:
            lines = [Line(point_a, point_b, color_edge, edge_width, f"HL-PL{point_nbr}")
                     for point_nbr, (point_a, point_b)
                     in enumerate(zip(poly, poly[1:] + [poly[0]]))]

            if not close:
                lines = lines[:-1]

        return lines + corners


    def overlay(self):
        """Visual Elements for User Interaction"""

        elements = []

        if self.new_bbox_state:
            elements += self.crosshair(self.canvas_coords(), (0, 0, 0))

        if self.new_bbox_state == 2:
            elements += self.crosshair(self.p1, (0, 0, 0))

        if self.new_polygon_state:
            elements += self.polyline(self.polygon)

        if self.selected_node is not None:
            elements += self.highlight(self.graph.nodes[self.selected_node])

        return elements


    def zoom(self, event):
        """Handler for Mouse Wheel Events, Performs Zoom"""

        if not self.update_in_progress and self.graph is not None:
            self.update_in_progress = True
            cursor_old = self.canvas_coords()

            if event == "+" or (type(event) is Event and event.num == 4):
                if self.scale < self.ZOOM_MAX:
                    self.scale *= 1.1

            if event == "-" or (type(event) is Event and event.num == 5):
                if self.scale > self.ZOOM_MIN:
                    self.scale /= self.ZOOM_STEP

            self.update_scaled_image()
            self.render_graph()
            cursor_new = self.canvas_coords()
            self.canvas.xview_scroll(round((cursor_old.x-cursor_new.x)*self.scale), "units")
            self.canvas.yview_scroll(round((cursor_old.y-cursor_new.y)*self.scale), "units")
            self.update_in_progress = False


    def update_scaled_image(self):
        """Refreshs the scaled image (=cache), if Raw Image Exists"""

        if self.img_raw is not None:
            raw_width, raw_height = self.img_raw.size
            img_scaled = self.img_raw.resize((round(raw_width * self.scale), round(raw_height * self.scale)),
                                             Image.NEAREST)
            self.img_scaled = ImageTk.PhotoImage(img_scaled)


    def mouse_down(self, event):
        """Handler for Mouse Down Event on Canvas"""

        self.canvas.focus_set()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.selected_node = None
        self.manipulation_mode = None

        for item in self.canvas.find_overlapping(x-1, y-1, x+1, y+1):
            canvas_tags = self.canvas.gettags(item)

            if canvas_tags and canvas_tags[0] != "current" and not canvas_tags[0].startswith("HL"):
                self.selected_node = int(canvas_tags[0])

            if canvas_tags and canvas_tags[0].startswith("HL"):
                self.manipulation_mode = canvas_tags[0]

        if self.new_bbox_state:
            self.new_bbox_state = 2
            self.p1 = self.canvas_coords()

        self.canvas.scan_mark(event.x, event.y)
        self.parent.update()


    def mouse_up(self, event):
        """Handler for Mouse Up"""

        if self.new_bbox_state:
            self.new_bbox_state = 0

            p2 = self.canvas_coords()
            xmin = min(self.p1.x, p2.x)
            xmax = max(self.p1.x, p2.x)
            ymin = min(self.p1.y, p2.y)
            ymax = max(self.p1.y, p2.y)

            self.selected_node = self.graph.add_node(type="text",
                                                     position=bbox_to_pos(xmin, xmax, ymin, ymax))
            self.parent.update()
            self.parent.status_bar.set("Node created.")

        if self.new_polygon_state:
            if self.polygon and self.canvas_coords().x == self.polygon[0].x and self.canvas_coords().x == self.polygon[0].x:
                self.new_polygon_state = False
                shape = [[p.x, p.y] for p in self.polygon]
                self.selected_node = self.graph.add_node(type="text",
                                                         position=BoundingBox(points=shape).position,
                                                         shape=shape)
                self.parent.update()
                self.parent.status_bar.set("Polygon Node created.")

            else:
                self.polygon += [self.canvas_coords()]
                self.parent.update()
                self.parent.status_bar.set("To Continue the Polygon select more coordinates, click on the first point to finish.")

        if self.new_edge_state:

            if self.source is None:
                self.source, self.source_connector = self.graph.closestPort(self.canvas_coords())
                self.parent.status_bar.set("Click on a Connector to Select Target")

            else:
                target, target_connector = self.graph.closestPort(self.canvas_coords())
                self.graph.add_edge(self.source, target, **{'sourcePort': self.source_connector,
                                                            'targetPort': target_connector})
                self.parent.update()
                self.new_edge_state = 0
                self.parent.status_bar.set("Edge created.")


    def mouse_move(self, event):
        """Handler for Mouse Move (not dragging)"""

        self.cursor_pos = Point(event.x, event.y)

        if self.new_bbox_state:
            self.render_graph()

        else:
            if self.img_raw:
                pos = self.canvas_coords()
                self.parent.status_bar.set(f"({round(pos.x)},{round(pos.y)})")

        if self.mouse_node_manipulation:
            cursor_set = False
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

            for item in self.canvas.find_overlapping(x-1, y-1, x+1, y+1):
                canvas_tags = self.canvas.gettags(item)

                if canvas_tags and canvas_tags[0] in self.cursor_assign.keys():
                    self.canvas.config(cursor=self.cursor_assign[canvas_tags[0]])
                    cursor_set = True

            if not cursor_set:
                self.canvas.config(cursor='cross')


    def mouse_drag(self, event):
        """Handler for Mouse Drag on Canvas"""

        p_old = self.canvas_coords()
        self.cursor_pos = Point(event.x, event.y)

        if self.new_bbox_state:
            self.render_graph()

        if self.mouse_node_manipulation and self.selected_node is not None:
            p_new = self.canvas_coords()

            if self.manipulation_mode is None: # TODO Make nicer than None
                self.graph.move_node(self.selected_node,
                                     round(p_new.x - p_old.x),
                                     round(p_new.y - p_old.y))

            else:
                left, right, top, bottom, rotation = pos_to_bbox(self.graph.nodes[self.selected_node]['position'])

                if self.manipulation_mode == "HL-L" or self.manipulation_mode == "HL-LT" or self.manipulation_mode == "HL-LB":
                    left += round(p_new.x - p_old.x)

                if self.manipulation_mode == "HL-R" or self.manipulation_mode == "HL-RT" or self.manipulation_mode == "HL-RB":
                    right += round(p_new.x - p_old.x)

                if self.manipulation_mode == "HL-T" or self.manipulation_mode == "HL-LT" or self.manipulation_mode == "HL-RT":
                    top += round(p_new.y - p_old.y)

                if self.manipulation_mode == "HL-B" or self.manipulation_mode == "HL-LB" or self.manipulation_mode == "HL-RB":
                    bottom += round(p_new.y - p_old.y)

                self.graph.nodes[self.selected_node]['position'] = bbox_to_pos(left, right, top, bottom, rotation)

                if type(self.manipulation_mode) is str and self.manipulation_mode.startswith("HL-PP"):
                    corner = self.graph.nodes[self.selected_node]['shape'][int(self.manipulation_mode[5:])]
                    corner[0] += round(p_new.x - p_old.x)
                    corner[1] += round(p_new.y - p_old.y)
                    self.graph.nodes[self.selected_node]['position'] = BoundingBox(points=self.graph.nodes[self.selected_node]['shape']).position

            self.parent.update()

        if not self.new_bbox_state and not (self.mouse_node_manipulation and self.selected_node is not None):
            self.canvas.scan_dragto(event.x, event.y, gain=1)


    def mouse_doubleclick(self, event):
        """Handler for Mouse Double Click on Canvas"""

        if type(self.manipulation_mode) is str and self.manipulation_mode.startswith("HL-PL"):
            p_new = self.canvas_coords()
            polygon = self.graph.nodes[self.selected_node]['shape']
            corner_nbr = int(self.manipulation_mode[5:])
            polygon.insert(corner_nbr+1, [p_new.x, p_new.y])
            self.parent.update()


    def set_graph(self, graph: EngGraph):
        """Sets a New Graph"""

        self.graph = graph
        self.selected_node = None
        # TODO restructuring required: Scale reset has to be done on graph load....


    def fit_view(self):
        """Aligns Image Size and Position to Canvas"""

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        img_width, img_height = self.img_raw.size
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.scale = min(canvas_width / img_width, canvas_height / img_height)
        self.update_scaled_image()
        self.render_graph()


    def set_image(self, img_raw: Image, fit_view: bool = True):
        """Sets a new (Background) Image"""

        self.img_raw = ImageOps.exif_transpose(img_raw)

        if fit_view:
            self.fit_view()

        else:
            self.update_scaled_image()
            self.render_graph()


    def new_annotation(self):
        """Activates the Mechanism of Annotation Adding, i.e. draws Crosshair"""

        if self.renderer_settings['shapes']:
            self.polygon = []
            self.new_polygon_state = True
            self.new_bbox_state = 0
            msg = "Click on any position in the Image to start drawing a polygon."

        else:
            self.new_polygon_state = False
            self.new_bbox_state = 1
            msg = "Press and Hold Mouse Button to Create an Annotation."

        self.new_edge_state = 0
        self.render_graph()
        self.parent.status_bar.set(msg)


    def abort(self):
        """Aborts the Current User Action"""

        self.new_bbox_state = 0
        self.new_edge_state = 0
        self.render_graph()
        self.parent.status_bar.set("Aborted.")


    def duplicate_node(self, copy_offset=5):
        """Duplicates the currently Selected Node, if there is one"""

        if self.selected_node is not None:
            self.selected_node = self.graph.duplicate_node(self.selected_node)
            self.graph.move_node(self.selected_node, copy_offset, copy_offset)
            self.parent.update()


    def iter_node(self, next_node=True):
        """Iterates the Currently Selected Node"""

        if self.graph and self.graph.number_of_nodes():

            if self.selected_node is None:
                self.selected_node = list(self.graph)[0]

            else:
                offset = 1 if next_node else -1
                node_count = self.graph.number_of_nodes()
                node_index = list(self.graph.nodes).index(self.selected_node)
                self.selected_node = list(self.graph.nodes)[(node_index + offset) % node_count]

            self.parent.update()

        return "break"


    def new_edge(self):
        """Activates the Mechanism of Edge Adding"""

        self.new_bbox_state = 0
        self.new_polygon_state = False
        self.source = None
        self.source_connector = None
        self.new_edge_state = 1
        self.render_graph()
        self.parent.status_bar.set("Click on a Connector to Select Source")


    def move_node(self, x: int, y: int):
        """Moves the currently Selected Node, if there is one"""

        if self.mouse_node_manipulation and self.selected_node is not None:
            self.graph.move_node(self.selected_node, x, y)
            self.parent.update()


    def rotate_node(self, degree=45):
        """Rotates the currently Selected Node, if there is one"""

        if self.selected_node is not None:
            self.graph.nodes[self.selected_node]['position']['rotation'] += degree
            self.graph.nodes[self.selected_node]['position']['rotation'] %= 360
            self.parent.update()


    def remove_node(self):
        """Removes the Currently Selected Node, if there is one"""

        if self.selected_node is not None:
            self.graph.remove_node(self.selected_node)
            self.selected_node = None
            self.update()
            self.parent.status_bar.set("Removed Node")


    def update(self):
        """Triggers the Re-Rendering of the Editor"""

        self.render_graph()


    def canvas_coords(self, point: Point = None) -> Point:
        """Translate Point from Canvas into Absolute (Image) Space"""

        if point is None:
            point = self.cursor_pos

        return Point(self.canvas.canvasx(point.x)/self.scale,
                     self.canvas.canvasy(point.y)/self.scale)



    def resolve_text_nodes(self):
        """Calls the Respective EngGraph Method and Updates The Parent"""

        if self.graph:
            self.graph.resolve_text_nodes()
            self.parent.update()
            self.parent.status_bar.set("Resolved text nodes.")


    def encapsulate_text_nodes(self):
        """Calls the Respective EngGraph Method and Updates The Parent"""

        if self.graph:
            self.graph.encapsulate_text_nodes()
            self.parent.update()
            self.parent.status_bar.set("Encapsulated text nodes.")


    def resolve_wire_hops(self):
        """Calls the Respective EngGraph Method and Updates The Parent"""

        if self.graph:
            self.graph.resolve_wire_hops()
            self.parent.update()
            self.parent.status_bar.set("Resolved wire hops.")


    def encapsulate_wire_hops(self):
        """Calls the Respective EngGraph Method and Updates The Parent"""

        if self.graph:
            self.graph.encapsulate_wire_hops()
            self.parent.update()
            self.parent.status_bar.set("Encapsulated wire hops.")


    def shake(self):
        """Calls the Respective EngGraph Method and Updates The Parent"""

        if self.graph:
            self.graph.shake()
            self.parent.update()
            self.parent.status_bar.set("Shook graph.")


    def straighten(self):
        """Calls the Respective EngGraph Method and Updates The Parent"""

        if self.graph:
            self.graph.straighten()
            self.parent.update()
            self.parent.status_bar.set("Straightened graph.")
