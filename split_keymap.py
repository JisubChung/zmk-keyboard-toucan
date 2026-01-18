#!/usr/bin/env python3
"""Split keymap SVG into multiple pages with 3 keymaps per page."""

import xml.etree.ElementTree as ET

# Read the original SVG
tree = ET.parse('keymap.svg')
root = tree.getroot()

# Extract the style element and namespace
ns = {'svg': 'http://www.w3.org/2000/svg'}
style = root.find('svg:style', ns)

# Find all layer groups
layers = []
for elem in root.findall('.//svg:g[@class]', ns):
    class_name = elem.get('class', '')
    if 'layer-' in class_name:
        # Skip COLEMAK layer
        if 'layer-COLEMAK' not in class_name:
            layers.append(elem)

print(f"Found {len(layers)} layers (excluding COLEMAK)")

# Group layers: 3 per page
layers_per_page = 3
pages = []
for i in range(0, len(layers), layers_per_page):
    pages.append(layers[i:i+layers_per_page])

# Page dimensions (US Letter)
page_width = 960
page_height = 792  # 11 inches at 72 dpi

# Calculate spacing between layers
layer_spacing = 350  # approximate spacing from original

# Create separate SVG files for each page
for page_num, page_layers in enumerate(pages, 1):
    # Create new SVG root
    new_root = ET.Element('svg', {
        'width': str(page_width),
        'height': str(page_height),
        'viewBox': f'0 0 {page_width} {page_height}',
        'class': 'keymap',
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink'
    })
    
    # Add style
    if style is not None:
        new_root.append(style)
    
    # Add layers with adjusted y positions
    for idx, layer in enumerate(page_layers):
        # Clone the layer
        new_layer = ET.fromstring(ET.tostring(layer))
        
        # Get original transform
        transform = new_layer.get('transform', '')
        
        # Extract original y offset
        if 'translate(30,' in transform:
            # Calculate new y position (evenly spaced on page)
            new_y = 30 + (idx * (page_height - 60) // len(page_layers))
            new_transform = f'translate(30, {new_y})'
            new_layer.set('transform', new_transform)
        
        new_root.append(new_layer)
    
    # Write to file
    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space='  ')
    filename = f'keymap_page{page_num}.svg'
    new_tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f"Created {filename} with {len(page_layers)} layers")

print(f"\nCreated {len(pages)} page(s)")
