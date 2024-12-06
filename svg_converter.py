import json
from math import cos, radians, sin
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
from utils import invert_y, create_arc_path  # Ensure these are absolute imports

# Your existing code...
def invert_arc_coordinates(arc, max_y):
    """
    Inverts the Y-coordinates for arcs specifically, and recalculates start and end points
    with proper inversion of angles for SVG representation.
    """
    x_center = arc["center"]["x"]
    y_center = invert_y(arc["center"]["y"], max_y)  # Invert the center Y-coordinate

    radius = arc["radius"]
    
    # Invert the start and end Y-coordinates
    start_x = arc["start"]["x"]
    start_y = invert_y(arc["start"]["y"], max_y)
    end_x = arc["end"]["x"]
    end_y = invert_y(arc["end"]["y"], max_y)

    # Adjust the angles for the inverted Y-axis
    start_angle = arc["start_angle"]
    end_angle = arc["end_angle"]

    # Adjust sweep direction because Y-inversion flips the arc direction
    if start_angle > end_angle:
        sweep_flag = 0  # Clockwise direction (after inversion)
    else:
        sweep_flag = 1  # Counter-clockwise (after inversion)
    
    # SVG requires the large arc flag to determine if the larger or smaller arc should be drawn
    angle_diff = (end_angle - start_angle) % 360
    large_arc_flag = 1 if angle_diff > 180 else 0

    # Return updated arc data in SVG path format
    return f"M {start_x},{start_y} A {radius},{radius} 0 {large_arc_flag},{sweep_flag} {end_x},{end_y}"


def create_arc_path(arc, max_y):
    # Adjust angles for SVG coordinate system
    start_angle = arc["start_angle"]
    end_angle = arc["end_angle"]

    radius = arc["radius"]
    x_center = arc["center"]["x"]
    y_center = arc["center"]["y"]
    if start_angle < 0:
        start_angle += 360
    if end_angle < 0:
        end_angle += 360
    # Calculate start and end points based on angles
    start_x = x_center + radius * cos(radians(start_angle))
    start_y = y_center + radius * sin(radians(start_angle))
    end_x = x_center + radius * cos(radians(end_angle))
    end_y = y_center + radius * sin(radians(end_angle))

    # Invert the Y-coordinates (since SVG Y-axis is inverted)
    start_y_inverted = invert_y(start_y, max_y)
    end_y_inverted = invert_y(end_y, max_y)

    # Ensure angles wrap around correctly (e.g., 359 degrees -> 0 degrees)
    angle_diff = (end_angle - start_angle) % 360
    large_arc_flag = 1 if angle_diff > 180 else 0
    sweep_flag = 1 if angle_diff > 0 else 0

    # Return the SVG arc path data
    return f"M {start_x},{start_y_inverted} A {radius},{radius} 0 {large_arc_flag},{sweep_flag} {end_x},{end_y_inverted}"

def convert_to_svg(input_json, output_svg, min_x, max_x, min_y, max_y):
    # Load parsed data
    with open(input_json, "r") as infile:
        data = json.load(infile)

    # Calculate dimensions and add padding
    padding = 20 # Adjust this value as needed
    width = max_x - min_x + 2 * padding
    height = max_y - min_y + 2 * padding

    adjusted_min_x = min_x - padding
    adjusted_min_y = min_y - padding

    # Create SVG root
    svg = Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1")
    svg.set("width", "1000")
    svg.set("height", "1000")
    svg.set("viewBox", f"{adjusted_min_x} {invert_y(max_y, max_y) - padding} {width} {height}")

    # Add Lines
    for line in data["lines"]:
        thickness = line.get("thickness", 0.25)
        # SubElement(svg, 'line', {
        #     "x1": str(line["start"]["x"]),
        #     "y1": str(invert_y(line["start"]["y"], max_y)),
        #     "x2": str(line["end"]["x"]),
        #     "y2": str(invert_y(line["end"]["y"], max_y)),
        #     "stroke": "black",
        #     "stroke-width": str(thickness)
        # })
        SubElement(svg, 'line', {
        "x1": str(line["start"]["x"]),
        "y1": str(invert_y(line["start"]["y"], max_y)),
        "x2": str(line["end"]["x"]),
        "y2": str(invert_y(line["end"]["y"], max_y)),
        "stroke": "black",
        "stroke-width": str(thickness),
        "data-length": str(((line["end"]["x"] - line["start"]["x"])**2 + (line["end"]["y"] - line["start"]["y"])**2)**0.5),
        "data-thickness": str(thickness)
        })


    # Add Circles grouped by radius
    for group in data["circles"]:
        group_element = SubElement(svg, 'g', {"id": f"radius_{group['radius']}"})
        for circle in group["circles"]:
            thickness = circle.get("thickness", 0.25)
            SubElement(group_element, 'circle', {
                # "cx": str(circle["center"]["x"]),
                # "cy": str(invert_y(circle["center"]["y"], max_y)),
                # "r": str(group["radius"]),
                # "stroke": "black",
                # "stroke-width": str(thickness),
                # "fill": "none"
                "cx": str(circle["center"]["x"]),
                "cy": str(invert_y(circle["center"]["y"], max_y)),
                "r": str(group["radius"]),
                "stroke": "black",
                "stroke-width": str(thickness),
                "fill": "none",
                "data-radius": str(group["radius"]),
                "data-thickness": str(thickness)
            })

    # Add Arcs
    for arc in data["arcs"]:
        path_data = create_arc_path(arc, max_y)
        thickness = arc.get("thickness", 0.25)
        SubElement(svg, 'path', {
            # "d": path_data,
            # "stroke": "black",
            # "stroke-width": str(thickness),
            # "fill": "none"
            "d": path_data,
            "stroke": "black",
            "stroke-width": str(thickness),
            "fill": "none",
            "data-arc-info": f"Center: ({arc['center']['x']}, {arc['center']['y']}), Radius: {arc['radius']}",
            "data-thickness": str(thickness)
        })

    # Write SVG to file
    xml_str = tostring(svg)
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_as_str = dom.toprettyxml()

    with open(output_svg, "w") as f:
        f.write(pretty_xml_as_str)
