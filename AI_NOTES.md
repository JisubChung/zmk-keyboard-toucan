# AI Assistant Notes

This file contains context and guidelines for AI assistants working on this repository.

## Repository Purpose

This is a ZMK firmware configuration repository for the beekeeb Toucan split keyboard. The main user workflow is:
1. Edit keymap in `config/toucan.keymap`
2. Push to GitHub to trigger firmware build
3. Download firmware artifacts from GitHub Actions

## Key Files to Understand

### Primary Files (Most Frequently Edited)

| File | Purpose |
|------|---------|
| `config/toucan.keymap` | **Main keymap file** - ZMK keymap syntax, contains all layers and behaviors |
| `config/toucan.conf` | ZMK configuration options (mouse support, display settings, etc.) |
| `config.yaml` | keymap-drawer styling configuration for SVG output |

### Build Configuration

| File | Purpose |
|------|---------|
| `build.yaml` | GitHub Actions matrix - defines which firmware variants to build |
| `.github/workflows/build.yml` | CI workflow that builds firmware on push |
| `config/west.yml` | Zephyr west manifest - ZMK and module dependencies |

### Visualization Scripts

| File | Purpose |
|------|---------|
| `scripts/svg_to_pdf.py` | Converts `keymap.svg` to multi-page PDF. Options: `--no-colemak`, `--layers-per-page N` |
| `scripts/watch-keymap.py` | Python file watcher - auto-regenerates SVG on keymap changes |
| `scripts/watch-keymap.sh` | Shell file watcher - same as above, uses fswatch/entr/inotifywait |
| `split_keymap.py` | Splits SVG into separate page files (3 layers per page, excludes COLEMAK) |

### Generated Files (Do Not Edit Directly)

| File | Purpose |
|------|---------|
| `keymap.yaml` | Intermediate file generated from `config/toucan.keymap` by keymap-drawer |
| `keymap.svg` | Generated keymap visualization |
| `keymap*.pdf` | Generated PDF files |

## Common Tasks

### Modifying the Keymap

1. Edit `config/toucan.keymap` using ZMK keymap syntax
2. Run `make draw` to regenerate visualization
3. The keymap uses crkbd/rev1 layout for visualization (42-key split)

### Regenerating Visualizations

```bash
make draw                           # Parse and draw SVG
python scripts/svg_to_pdf.py        # Generate PDF (after SVG exists)
```

### Understanding the Toucan Layout

- 42 keys total (6x3 + 3 thumb keys per side)
- Uses LAYOUT_split_3x6_3 (Corne-compatible layout)
- The keymap-drawer tool doesn't have native Toucan support, so we map it to crkbd

## ZMK Keymap Syntax Reference

The keymap file uses ZMK's devicetree syntax:

```c
/ {
    keymap {
        compatible = "zmk,keymap";
        
        layer_name {
            bindings = <
                // Row 1 (6 keys left, 6 keys right)
                &kp TAB   &kp Q  &kp W  &kp E  &kp R  &kp T    &kp Y  &kp U  &kp I     &kp O    &kp P     &kp BSPC
                // Row 2
                &kp LCTRL &kp A  &kp S  &kp D  &kp F  &kp G    &kp H  &kp J  &kp K     &kp L    &kp SEMI  &kp SQT
                // Row 3
                &kp LSHFT &kp Z  &kp X  &kp C  &kp V  &kp B    &kp N  &kp M  &kp COMMA &kp DOT  &kp FSLH  &kp ESC
                // Thumb row (3 keys left, 3 keys right)
                                    &kp LGUI &mo 1  &kp SPACE   &kp RET &mo 2 &kp RALT
            >;
        };
    };
};
```

### Common ZMK Behaviors

- `&kp KEY` - Key press
- `&mo N` - Momentary layer N
- `&lt N KEY` - Layer-tap (tap for KEY, hold for layer N)
- `&mt MOD KEY` - Mod-tap (tap for KEY, hold for modifier)
- `&to N` - Toggle to layer N
- `&trans` - Transparent (pass through to lower layer)
- `&none` - No action

## Display Shield (nice_view_gem)

Located in `boards/shields/nice_view_gem/`. This is a custom display widget that shows:
- Current layer
- Battery status (central and peripheral)
- Output mode (USB/BLE)
- BLE profile

The display uses a custom font (QuinqueFive) and custom graphics defined in the `assets/` folder.

## Build System

### Local Development

No local ZMK build is required. The user edits files and pushes to GitHub, where the CI workflow builds the firmware.

### GitHub Actions

The `build.yaml` file defines the build matrix:
- `toucan_left` - Main half with display, ZMK Studio enabled
- `toucan_right` - Peripheral half with RGB LED adapter
- `settings_reset` - Utility firmware for resetting BLE bonds

## Dependencies

### For Keymap Visualization

```bash
pip install keymap-drawer          # Required for SVG generation
pip install cairosvg PyPDF2        # Required for PDF generation
pip install watchdog               # Required for Python file watcher
```

### For Shell Watcher

One of: `fswatch` (macOS), `entr`, or `inotifywait` (Linux)

## File Relationships

```
config/toucan.keymap
        │
        ▼ (keymap parse)
   keymap.yaml
        │
        ▼ (keymap draw with config.yaml)
   keymap.svg
        │
        ▼ (svg_to_pdf.py)
   keymap.pdf / keymap_page*.pdf
```

## Tips for AI Assistants

1. **Always read `config/toucan.keymap` first** when asked about the current keymap configuration
2. **The keymap visualization may be out of date** - regenerate with `make draw` if needed
3. **Don't edit `keymap.yaml` directly** - it's generated from `config/toucan.keymap`
4. **The Toucan uses Corne layout** for visualization purposes (crkbd/rev1)
5. **ZMK documentation** is at https://zmk.dev/docs
6. **After keymap changes**, remind user to push to GitHub to trigger firmware build
