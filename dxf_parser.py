import ezdxf
import json
from utils import handle_entity
import logging

def parse_dxf(filename, scaling_factor=1.0):
    parsed_data = {"lines": [], "circles": [], "arcs": []}
    all_x_coords = []
    all_y_coords = []

    try:
        doc = ezdxf.readfile(filename)
    except ezdxf.DXFStructureError as e:
        logging.error(f"DXF structure error: {e}")
        raise ValueError(f"The DXF file is corrupted. Problem: {e}")
    except ezdxf.DXFVersionError as e:
        logging.error(f"Unsupported DXF version: {e}")
        raise ValueError(f"The DXF file version is not supported. Problem: {e}")
    except Exception as e:
        logging.error(f"Failed to read DXF file: {e}")
        raise ValueError(f"An unknown error occurred while reading the DXF file. Problem: {e}")

    msp = doc.modelspace()

    for entity in msp:
        try:
            handle_entity(entity, parsed_data)
        except AttributeError as e:
            logging.warning(f"Entity missing attributes: {e}")
            raise ValueError(f"Corrupted entity found. Problem: {e}")
        except Exception as e:
            logging.warning(f"Error processing entity: {e}")
            raise ValueError(f"An error occurred while processing entities. Problem: {e}")

        if entity.dxftype() == 'LINE':
            all_x_coords.extend([entity.dxf.start.x, entity.dxf.end.x])
            all_y_coords.extend([entity.dxf.start.y, entity.dxf.end.y])
        elif entity.dxftype() in ['CIRCLE', 'ARC']:
            all_x_coords.append(entity.dxf.center.x)
            all_y_coords.append(entity.dxf.center.y)

    # Check if no valid geometry was parsed
    if not all_x_coords or not all_y_coords:
        raise ValueError("No valid geometry found in the DXF file. The file might be empty or corrupted.")

    # Find the bounding box (min and max coordinates)
    try:
        min_x, max_x = min(all_x_coords), max(all_x_coords)
        min_y, max_y = min(all_y_coords), max(all_y_coords)
    except ValueError as e:
        logging.error(f"Error calculating bounding box: {e}")
        raise ValueError(f"Error calculating the bounding box. Problem: {e}")

    return min_x, max_x, min_y, max_y, parsed_data
