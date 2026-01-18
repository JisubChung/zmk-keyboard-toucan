# Makefile for ZMK Toucan Keyboard

.PHONY: draw parse watch watch-py help

# Parse ZMK keymap and generate SVG
draw: parse
	@echo "Drawing keymap.svg..."
	@keymap -c config.yaml draw keymap.yaml -o keymap.svg
	@echo "✓ Done"

# Parse ZMK keymap to YAML
parse:
	@echo "Parsing config/toucan.keymap..."
	@keymap parse -z config/toucan.keymap -o keymap.yaml
	@python3 -c "import re; f=open('keymap.yaml','r'); c=f.read(); f.close(); c=re.sub(r'layout: \{zmk_keyboard: toucan\}', 'layout:\n  qmk_keyboard: crkbd/rev1\n  layout_name: LAYOUT_split_3x6_3', c); f=open('keymap.yaml','w'); f.write(c); f.close()"

# Watch for changes and regenerate SVG (shell script)
watch:
	@./scripts/watch-keymap.sh

# Watch for changes using Python (cross-platform)
watch-py:
	@python3 scripts/watch-keymap.py

# Help
help:
	@echo "Available targets:"
	@echo "  make draw      - Parse ZMK keymap and generate keymap.svg"
	@echo "  make parse     - Parse config/toucan.keymap to keymap.yaml"
	@echo "  make watch     - Watch for changes and auto-regenerate (requires fswatch/entr)"
	@echo "  make watch-py  - Watch using Python (cross-platform, requires watchdog)"
	@echo ""
	@echo "Requirements:"
	@echo "  pip install keymap-drawer    # For SVG generation"
	@echo "  brew install fswatch         # For shell watcher (macOS)"
	@echo "  pip install watchdog         # For Python watcher"
