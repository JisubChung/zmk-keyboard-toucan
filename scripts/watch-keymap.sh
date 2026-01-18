#!/bin/bash
# Watch keymap files and regenerate SVG on changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Keymap SVG Watcher - Toucan Keyboard   ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to generate SVG
generate_svg() {
    echo -e "${YELLOW}[$(date +%H:%M:%S)]${NC} Change detected, regenerating SVG..."
    
    # Step 1: Parse ZMK keymap to YAML
    if ! keymap parse -z config/toucan.keymap -o keymap.yaml 2>&1; then
        echo -e "${RED}[$(date +%H:%M:%S)] ✗ Failed to parse ZMK keymap${NC}"
        echo ""
        return 1
    fi
    
    # Step 2: Fix layout (toucan uses crkbd layout)
    python3 -c "import re; f=open('keymap.yaml','r'); c=f.read(); f.close(); c=re.sub(r'layout: \{zmk_keyboard: toucan\}', 'layout:\n  qmk_keyboard: crkbd/rev1\n  layout_name: LAYOUT_split_3x6_3', c); f=open('keymap.yaml','w'); f.write(c); f.close()"
    
    # Step 3: Draw SVG from YAML
    if keymap -c config.yaml draw keymap.yaml -o keymap.svg 2>&1; then
        echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} ✓ keymap.svg updated successfully"
    else
        echo -e "${RED}[$(date +%H:%M:%S)] ✗ Failed to generate SVG${NC}"
    fi
    echo ""
}

# Initial generation
echo -e "${YELLOW}Generating initial SVG...${NC}"
generate_svg

# Watch for changes
echo -e "${CYAN}Watching for changes in:${NC}"
echo "  • config/toucan.keymap"
echo "  • config.yaml"
echo ""
echo -e "${CYAN}Press Ctrl+C to stop watching${NC}"
echo ""

# Check which watch tool is available
if command -v fswatch &> /dev/null; then
    fswatch -o config/toucan.keymap config.yaml | while read; do
        generate_svg
    done
elif command -v entr &> /dev/null; then
    while true; do
        echo config/toucan.keymap config.yaml | tr ' ' '\n' | entr -d -p sh -c "$(declare -f generate_svg); generate_svg"
    done
elif command -v inotifywait &> /dev/null; then
    while inotifywait -e modify config/toucan.keymap config.yaml; do
        generate_svg
    done
else
    echo -e "${RED}No file watcher found!${NC}"
    echo ""
    echo "Please install one of the following:"
    echo "  • fswatch:     brew install fswatch"
    echo "  • entr:        brew install entr"
    echo ""
    echo "Or use the Python watcher instead:"
    echo "  python scripts/watch-keymap.py"
    exit 1
fi
