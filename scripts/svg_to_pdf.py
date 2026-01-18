#!/usr/bin/env python3
"""
Generate a multi-page PDF from the keymap SVG at native scale.

Usage:
    python scripts/svg_to_pdf.py [OPTIONS]

Options:
    --no-colemak        Exclude the COLEMAK layer from output
    --output FILE       Output PDF filename (default: keymap.pdf)
    --input FILE        Input SVG filename (default: keymap.svg)
    --layers-per-page N Number of layers per page (default: 2)

Requirements:
    - rsvg-convert (install via: brew install librsvg)
    - PyPDF2 (install via: pip install PyPDF2)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Check for required tools
def check_requirements():
    """Check if required tools are available."""
    # Check rsvg-convert
    if not shutil.which('rsvg-convert'):
        print("Error: rsvg-convert not found.")
        print("Install it with: brew install librsvg")
        sys.exit(1)
    
    # Check PyPDF2
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        print("Error: PyPDF2 not found.")
        print("Install it with: pip install PyPDF2")
        sys.exit(1)

check_requirements()
from PyPDF2 import PdfMerger


# US Letter dimensions in points (72 points per inch)
LETTER_WIDTH_PT = 612   # 8.5 inches
LETTER_HEIGHT_PT = 792  # 11 inches


def parse_transform(transform_str):
    """Extract x, y from a translate(x, y) transform string."""
    match = re.search(r'translate\s*\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)', transform_str)
    if match:
        return float(match.group(1)), float(match.group(2))
    return 0, 0


def get_layer_info(root):
    """Extract layer information from SVG root."""
    layers = []
    
    # Find all top-level groups with layer-* class
    for elem in root:
        if elem.tag.endswith('}g') or elem.tag == 'g':
            class_name = elem.get('class', '')
            if class_name.startswith('layer-'):
                transform = elem.get('transform', '')
                x, y = parse_transform(transform)
                layer_name = class_name.replace('layer-', '')
                layers.append({
                    'name': layer_name,
                    'class': class_name,
                    'y_offset': y,
                    'element': elem
                })
    
    return layers


def calculate_layer_heights(layers, total_height):
    """Calculate the height of each layer based on positions."""
    for i, layer in enumerate(layers):
        if i < len(layers) - 1:
            layer['height'] = layers[i + 1]['y_offset'] - layer['y_offset']
        else:
            # Last layer - estimate from total height
            layer['height'] = total_height - layer['y_offset']
    return layers


def create_page_svg(original_svg_path, svg_width, y_start, page_height, exclude_layers=None):
    """
    Create an SVG string for a single page by modifying the viewBox.
    
    The viewBox approach keeps all content but shows only the visible portion.
    """
    # Register namespaces
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    
    tree = ET.parse(original_svg_path)
    root = tree.getroot()
    
    # Remove excluded layers if specified
    if exclude_layers:
        layers_to_remove = []
        for elem in root:
            if elem.tag.endswith('}g') or elem.tag == 'g':
                class_name = elem.get('class', '')
                if any(f'layer-{name}' == class_name for name in exclude_layers):
                    layers_to_remove.append(elem)
        for elem in layers_to_remove:
            root.remove(elem)
    
    # Modify viewBox to show only this page's content
    root.set('viewBox', f'0 {y_start} {svg_width} {page_height}')
    root.set('width', str(svg_width))
    root.set('height', str(page_height))
    
    return ET.tostring(root, encoding='unicode')


def create_layer_svg(original_svg_path, svg_width, layer_info, all_layers, exclude_layers=None):
    """
    Create an SVG string containing specific layers.
    """
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    
    tree = ET.parse(original_svg_path)
    root = tree.getroot()
    
    # Get included layer names
    included_names = set(l['name'] for l in layer_info)
    if exclude_layers:
        included_names -= set(exclude_layers)
    
    # Remove non-included layers
    layers_to_remove = []
    for elem in list(root):
        if elem.tag.endswith('}g') or elem.tag == 'g':
            class_name = elem.get('class', '')
            if class_name.startswith('layer-'):
                layer_name = class_name.replace('layer-', '')
                if layer_name not in included_names:
                    layers_to_remove.append(elem)
    
    for elem in layers_to_remove:
        root.remove(elem)
    
    # Calculate the viewBox for this page
    # Must span from first layer's y to last layer's y + height
    if layer_info:
        y_start = layer_info[0]['y_offset']
        last_layer = layer_info[-1]
        y_end = last_layer['y_offset'] + last_layer['height']
        total_height = y_end - y_start
        
        # Modify viewBox
        root.set('viewBox', f'0 {y_start} {svg_width} {total_height}')
        root.set('width', str(svg_width))
        root.set('height', str(total_height))
    
    return ET.tostring(root, encoding='unicode')


def svg_to_pdf(svg_content, output_path, page_width_pt=LETTER_WIDTH_PT, page_height_pt=LETTER_HEIGHT_PT):
    """
    Convert SVG content to PDF using rsvg-convert, scaling to fit page.
    """
    # Get SVG dimensions from content
    root = ET.fromstring(svg_content)
    svg_width = float(root.get('width', '960'))
    svg_height = float(root.get('height', '792'))
    
    # Calculate scale to fit width while maintaining aspect ratio
    scale = page_width_pt / svg_width
    output_height = svg_height * scale
    
    # If scaled height exceeds page height, scale by height instead
    if output_height > page_height_pt:
        scale = page_height_pt / svg_height
    
    output_width = svg_width * scale
    output_height = svg_height * scale
    
    # Use rsvg-convert to create PDF
    cmd = [
        'rsvg-convert',
        '-f', 'pdf',
        '-w', str(int(output_width)),
        '-h', str(int(output_height)),
        '-o', str(output_path)
    ]
    
    # Run rsvg-convert with SVG content as stdin
    result = subprocess.run(
        cmd,
        input=svg_content.encode('utf-8'),
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"Error running rsvg-convert: {result.stderr.decode()}")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Generate a multi-page PDF from keymap SVG at native scale.'
    )
    parser.add_argument(
        '--no-colemak', 
        action='store_true',
        help='Exclude the COLEMAK layer from output'
    )
    parser.add_argument(
        '--output', '-o',
        default='keymap.pdf',
        help='Output PDF filename (default: keymap.pdf)'
    )
    parser.add_argument(
        '--input', '-i',
        default='keymap.svg',
        help='Input SVG filename (default: keymap.svg)'
    )
    parser.add_argument(
        '--layers-per-page', '-n',
        type=int,
        default=2,
        help='Number of layers per page (default: 2)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = project_root / input_path
    
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = project_root / output_path
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"Reading: {input_path}")
    
    # Parse SVG
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    
    tree = ET.parse(input_path)
    root = tree.getroot()
    
    # Get SVG dimensions
    svg_width = int(root.get('width', '960'))
    svg_height = int(root.get('height', '2508'))
    
    print(f"SVG dimensions: {svg_width} x {svg_height}")
    
    # Get layer information
    layers = get_layer_info(root)
    layers = calculate_layer_heights(layers, svg_height)
    
    print(f"Found {len(layers)} layers:")
    for layer in layers:
        print(f"  - {layer['name']}: y={layer['y_offset']}, height≈{layer['height']:.0f}")
    
    # Filter out COLEMAK if requested
    exclude_layers = []
    if args.no_colemak:
        exclude_layers.append('COLEMAK')
        print(f"Excluding COLEMAK layer (--no-colemak)")
        layers = [l for l in layers if l['name'] != 'COLEMAK']
    
    # Group layers for pages
    layers_per_page = args.layers_per_page
    pages = []
    for i in range(0, len(layers), layers_per_page):
        pages.append(layers[i:i + layers_per_page])
    
    print(f"\nGenerating {len(pages)} page(s) with up to {layers_per_page} layer(s) per page...")
    
    # Create temporary PDF files for each page
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_files = []
        
        for page_num, page_layers in enumerate(pages, 1):
            layer_names = ', '.join(l['name'] for l in page_layers)
            print(f"  Page {page_num}: {layer_names}")
            
            # Create SVG for this page
            svg_content = create_layer_svg(
                input_path, svg_width, page_layers, layers, exclude_layers
            )
            
            # Convert to PDF
            tmp_pdf_path = os.path.join(tmpdir, f'page_{page_num}.pdf')
            if not svg_to_pdf(svg_content, tmp_pdf_path):
                print(f"Error creating page {page_num}")
                sys.exit(1)
            
            pdf_files.append(tmp_pdf_path)
        
        # Merge all pages into final PDF
        print(f"\nMerging pages into: {output_path}")
        merger = PdfMerger()
        for pdf_file in pdf_files:
            merger.append(pdf_file)
        
        merger.write(str(output_path))
        merger.close()
    
    print(f"\nDone! Created {output_path}")
    print(f"  - {len(pages)} page(s)")
    print(f"  - {len(layers)} layer(s)")


if __name__ == '__main__':
    main()
