from math import cos, sin, radians

def handle_entity(entity, parsed_data):
    entity_type = entity.dxftype()
    if entity_type == 'LINE':
        thickness = entity.dxf.lineweight / 100 if entity.dxf.hasattr('lineweight') else 0.25
        parsed_data["lines"].append({
            "start": {"x": entity.dxf.start.x, "y": entity.dxf.start.y},
            "end": {"x": entity.dxf.end.x, "y": entity.dxf.end.y},
            "thickness": thickness
        })
    elif entity_type == 'CIRCLE':
        radius = entity.dxf.radius
        thickness = entity.dxf.lineweight / 100 if entity.dxf.hasattr('lineweight') else 0.25

        # Check if a group for this radius already exists
        found = False
        for group in parsed_data["circles"]:
            if group["radius"] == radius:
                group["circles"].append({
                    "center": {"x": entity.dxf.center.x, "y": entity.dxf.center.y},
                    "thickness": thickness
                })
                found = True
                break

        # If no group exists, create a new one
        if not found:
            parsed_data["circles"].append({
                "radius": radius,
                "circles": [{
                    "center": {"x": entity.dxf.center.x, "y": entity.dxf.center.y},
                    "thickness": thickness
                }]
            })
    elif entity_type == 'ARC':
        thickness = entity.dxf.lineweight / 100 if entity.dxf.hasattr('lineweight') else 0.25
        parsed_data["arcs"].append({
            "center": {"x": entity.dxf.center.x, "y": entity.dxf.center.y},
            "radius": entity.dxf.radius,
            "start_angle": entity.dxf.start_angle,
            "end_angle": entity.dxf.end_angle,
            "thickness": thickness
        })



def invert_y(y, max_y):
    """
    Inverts the Y-coordinate for SVG coordinate systems.
    """
    return max_y - y

def create_arc_path(arc, max_y):
    """
    Creates an SVG path string for an arc.
    """
    start_angle = arc["start_angle"]
    end_angle = arc["end_angle"]

    radius = arc["radius"]
    x_center = arc["center"]["x"]
    y_center = arc["center"]["y"]

    start_x = x_center + radius * cos(radians(start_angle))
    start_y = y_center + radius * sin(radians(start_angle))
    end_x = x_center + radius * cos(radians(end_angle))
    end_y = y_center + radius * sin(radians(end_angle))

    start_y_inverted = invert_y(start_y, max_y)
    end_y_inverted = invert_y(end_y, max_y)

    angle_diff = (end_angle - start_angle) % 360
    large_arc_flag = 1 if angle_diff > 180 else 0
    sweep_flag = 1 if angle_diff > 0 else 0

    return f"M {start_x},{start_y_inverted} A {radius},{radius} 0 {large_arc_flag},{sweep_flag} {end_x},{end_y_inverted}"
