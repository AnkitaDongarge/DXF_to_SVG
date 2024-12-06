import ezdxf

# Create a new DXF document
doc = ezdxf.new()
msp = doc.modelspace()

# Water molecule layout: Simple circles for atoms and lines for bonds
# Oxygen atom at the origin (O)
oxygen_center = (0, 0)
oxygen_radius = 2

# Hydrogen atoms' positions
hydrogen1 = (5, 4)
hydrogen2 = (5, -4)

# Drawing circles for the atoms
msp.add_circle(oxygen_center, oxygen_radius)  # Oxygen
msp.add_circle(hydrogen1, 1)  # Hydrogen 1
msp.add_circle(hydrogen2, 1)  # Hydrogen 2

# Drawing lines to represent bonds (O-H bonds)
msp.add_line(oxygen_center, hydrogen1)
msp.add_line(oxygen_center, hydrogen2)

# Save to a DXF file
file_path = "water_molecule.dxf"
doc.saveas(file_path)

print(f"DXF file saved to {file_path}")
