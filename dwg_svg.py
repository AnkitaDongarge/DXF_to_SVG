import ezdxf
import json
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
from math import cos, sin
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize parsed data structure
parsed_data = {
    "lines": [],
    "circles": [],
    "arcs": []
}

def convert_dwg_to_dxf(dwg_file_path, dxf_file_path):
    # This function is a placeholder for actual DWG to DXF conversion logic
    # Implement the logic to convert DWG to DXF here
    # You may use a library or a command-line tool to perform this conversion.
    # For example, using dxfwrite or a similar tool if available.

    # Placeholder: create an empty DXF for demonstration
    try:
        # Create a new DXF document
        doc = ezdxf.new()
        msp = doc.modelspace()
        
        # Add lines or other entities to the DXF
        msp.add_line(start=(0, 0), end=(10, 0))
        msp.add_line(start=(0, 0), end=(0, 10))
        msp.add_circle(center=(5, 5), radius=2.5)
        
        # Save the DXF document
        doc.saveas(dxf_file_path)
        logging.info(f"Converted DWG to DXF and saved to {dxf_file_path}")
    except Exception as e:
        logging.error(f"Error converting DWG to DXF: {e}")
        raise

def handle_entity(entity, parsed_data):
    entity_type = entity.dxftype()
    if entity_type == 'LINE':
        x_start, y_start = entity.dxf.start.x, entity.dxf.start.y
        x_end, y_end = entity.dxf.end.x, entity.dxf.end.y
        line_width = entity.dxf.lineweight or 0.25  # Default to 0.25 if not specified
        parsed_data["lines"].append({
            "start": {"x": x_start, "y": y_start},
            "end": {"x": x_end, "y": y_end},
            "line_width": line_width  # Store the line width
        })
    elif entity_type == 'CIRCLE':
        x_center, y_center = entity.dxf.center.x, entity.dxf.center.y
        parsed_data["circles"].append({
            "center": {"x": x_center, "y": y_center},
            "radius": entity.dxf.radius,
            "line_width": entity.dxf.lineweight or 0.25  # Default to 0.25 if not specified
        })
    elif entity_type == 'ARC':
        x_center, y_center = entity.dxf.center.x, entity.dxf.center.y
        parsed_data["arcs"].append({
            "center": {"x": x_center, "y": y_center},
            "radius": entity.dxf.radius,
            "start_angle": entity.dxf.start_angle,
            "end_angle": entity.dxf.end_angle,
            "line_width": entity.dxf.lineweight or 0.25  # Default to 0.25 if not specified
        })
    else:
        logging.warning(f"Skipping unsupported entity type: {entity_type}")


def parse_dxf(filename):
    global parsed_data
    parsed_data = {"lines": [], "circles": [], "arcs": []}
    try:
        doc = ezdxf.readfile(filename)
    except Exception as e:
        logging.error(f"Failed to read DXF file: {e}")
        raise

    msp = doc.modelspace()
    all_x_coords = []
    all_y_coords = []

    for entity in msp:
        handle_entity(entity, parsed_data)
        if entity.dxftype() == 'LINE':
            all_x_coords.extend([entity.dxf.start.x, entity.dxf.end.x])
            all_y_coords.extend([entity.dxf.start.y, entity.dxf.end.y])
        elif entity.dxftype() in ['CIRCLE', 'ARC']:
            all_x_coords.append(entity.dxf.center.x)
            all_y_coords.append(entity.dxf.center.y)

    if all_x_coords and all_y_coords:
        min_x, max_x = min(all_x_coords), max(all_x_coords)
        min_y, max_y = min(all_y_coords), max(all_y_coords)
    else:
        raise ValueError("No valid geometry found in the DXF file.")

    with open('parsed_data.json', 'w') as json_file:
        json.dump(parsed_data, json_file)

    return min_x, max_x, min_y, max_y

def invert_y(y, max_y):
    return max_y - y

def create_arc_path(arc):
    start_angle = arc["start_angle"]
    end_angle = arc["end_angle"]
    radius = arc["radius"]
    x_center = arc["center"]["x"]
    y_center = arc["center"]["y"]
    large_arc_flag = 1 if end_angle - start_angle > 180 else 0
    start_x = x_center + radius * cos(start_angle)
    start_y = y_center + radius * sin(start_angle)
    return f"M {start_x},{invert_y(start_y)} A {radius},{radius} 0 {large_arc_flag},1 {x_center + radius * cos(end_angle)},{invert_y(y_center + radius * sin(end_angle))}"

def convert_to_svg(input_json, output_svg, min_x, max_x, min_y, max_y, min_line_width=0.1):
    with open(input_json, "r") as infile:
        data = json.load(infile)

    width = max_x - min_x
    height = max_y - min_y

    svg = Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1")
    svg.set("width", "1000")
    svg.set("height", "1000")
    svg.set("viewBox", f"{min_x} {invert_y(max_y, max_y)} {width} {height}")

    # Draw lines with a reduced line width
    for line in data["lines"]:
        line_width = max(min_line_width, line["line_width"])  # Set to minimum if original is less
        SubElement(svg, 'line', {
            "x1": str(line["start"]["x"]),
            "y1": str(invert_y(line["start"]["y"], max_y)),
            "x2": str(line["end"]["x"]),
            "y2": str(invert_y(line["end"]["y"], max_y)),
            "stroke": "black",
            "stroke-width": str(line_width)  # Use reduced line width
        })

    # Draw circles with a reduced line width
    for circle in data["circles"]:
        circle_line_width = max(min_line_width, circle["line_width"])  # Set to minimum if original is less
        SubElement(svg, 'circle', {
            "cx": str(circle["center"]["x"]),
            "cy": str(invert_y(circle["center"]["y"], max_y)),
            "r": str(circle["radius"]),
            "stroke": "black",
            "fill": "none",
            "stroke-width": str(circle_line_width)  # Use reduced line width
        })

    # Draw arcs with a reduced line width
    for arc in data["arcs"]:
        arc_line_width = max(min_line_width, arc["line_width"])  # Set to minimum if original is less
        SubElement(svg, 'path', {
            "d": create_arc_path(arc),
            "stroke": "black",
            "fill": "none",
            "stroke-width": str(arc_line_width)  # Use reduced line width
        })

    xml_str = tostring(svg)
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_as_str = dom.toprettyxml()

    with open(output_svg, "w") as f:
        f.write(pretty_xml_as_str)


def main():
    dwg_file_path = r'C:\Users\ankit\OneDrive\Documents\Documents\sem7\Data_Mining lab\Mega_project_sakshi_pc\Mega_project\Mega_project - Copy\Draw1.dwg'  # Replace with your DWG file path
    dxf_file_path = r'temp.dxf'      # Temporary DXF file path
    svg_output_path = r'output.svg'   # Desired SVG output path

    # Convert DWG to DXF
    try:
        convert_dwg_to_dxf(dwg_file_path, dxf_file_path)  # Convert DWG to DXF
    except Exception as e:
        logging.error(f"Error during DWG to DXF conversion: {e}")
        return

    # Parse the DXF and generate SVG
    try:
        min_x, max_x, min_y, max_y = parse_dxf(dxf_file_path)  # Parse DXF and get bounding box
        convert_to_svg('parsed_data.json', svg_output_path, min_x, max_x, min_y, max_y)  # Convert JSON to SVG
        print("SVG created successfully.")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()