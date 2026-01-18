# ZMK Config for beekeeb Toucan Keyboard

[The beekeeb Toucan Keyboard](https://beekeeb.com/toucan-keyboard/) is a wireless split 42-key column‑stagger keyboard with a display and a trackpad, featuring an aggressive stagger on the pinky columns.

## Features

- ZMK firmware configuration for Toucan keyboard
- Custom nice_view_gem display shield
- Keymap visualization with SVG/PDF generation
- File watchers for auto-regeneration during development

## Quick Start

### Prerequisites

```bash
# Required: keymap-drawer for SVG generation
pip install keymap-drawer

# Optional: for PDF generation
pip install cairosvg PyPDF2

# Optional: for file watching
pip install watchdog              # Python watcher
brew install fswatch              # Shell watcher (macOS)
```

### Common Commands

```bash
# Generate keymap visualization
make draw                          # Parse keymap and generate SVG

# Watch mode (auto-regenerate on changes)
make watch                         # Shell-based watcher (requires fswatch)
make watch-py                      # Python-based watcher (cross-platform)

# Generate PDFs from SVG
python scripts/svg_to_pdf.py                    # Default: 2 layers per page
python scripts/svg_to_pdf.py --no-colemak       # Exclude COLEMAK layer
python scripts/svg_to_pdf.py -n 3               # 3 layers per page
```

## Project Structure

```
├── config/
│   ├── toucan.keymap          # Main ZMK keymap file (edit this)
│   ├── toucan.conf            # ZMK configuration
│   └── west.yml               # Zephyr west manifest
├── boards/shields/
│   ├── toucan/                # Toucan keyboard shield definition
│   └── nice_view_gem/         # Custom display shield
├── scripts/
│   ├── svg_to_pdf.py          # Convert keymap SVG to multi-page PDF
│   ├── watch-keymap.py        # Python file watcher
│   └── watch-keymap.sh        # Shell file watcher
├── config.yaml                # keymap-drawer styling config
├── keymap.yaml                # Generated intermediate YAML
├── keymap.svg                 # Generated keymap visualization
└── Makefile                   # Build automation
```

## Keymap Workflow

1. Edit `config/toucan.keymap` with your ZMK keymap changes
2. Run `make draw` to regenerate the SVG visualization
3. (Optional) Run `python scripts/svg_to_pdf.py` to create printable PDFs

For active development, use `make watch` or `make watch-py` to automatically regenerate the SVG whenever you save changes to the keymap.

## Build Outputs

The GitHub Actions workflow builds firmware for:
- `toucan_left` with nice_view_gem display and ZMK Studio support
- `toucan_right` with RGB LED adapter
- `settings_reset` utility firmware

## License

The code in this repo is available under the MIT license.

The included shield nice_view_gem is modified from https://github.com/M165437/nice-view-gem licensed under the MIT License.

ZMK code snippets are taken from the ZMK documentation under the MIT license.

The embedded font QuinqueFive is designed by GGBotNet, licensed under the SIL Open Font License, Version 1.1.
