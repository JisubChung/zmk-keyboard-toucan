#!/usr/bin/env python3
"""
Watch keymap files and regenerate SVG on changes.
Cross-platform Python implementation using watchdog.
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Installing watchdog...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler


class Colors:
    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"


PROJECT_ROOT = Path(__file__).parent.parent
ZMK_KEYMAP = PROJECT_ROOT / "config" / "toucan.keymap"
KEYMAP_YAML = PROJECT_ROOT / "keymap.yaml"
CONFIG_YAML = PROJECT_ROOT / "config.yaml"
OUTPUT_SVG = PROJECT_ROOT / "keymap.svg"

# Files to watch (relative paths for display)
WATCH_FILES = {
    "toucan.keymap": ZMK_KEYMAP,
    "config.yaml": CONFIG_YAML,
}


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


def generate_svg():
    """Parse ZMK keymap and generate SVG"""
    print(f"{Colors.YELLOW}[{timestamp()}]{Colors.NC} Change detected, regenerating SVG...")
    
    try:
        # Step 1: Parse ZMK keymap to YAML
        parse_result = subprocess.run(
            ["keymap", "parse", "-z", str(ZMK_KEYMAP), "-o", str(KEYMAP_YAML)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        
        if parse_result.returncode != 0:
            print(f"{Colors.RED}[{timestamp()}] ✗ Failed to parse ZMK keymap{Colors.NC}")
            if parse_result.stderr:
                print(f"  Error: {parse_result.stderr.strip()}")
            print()
            return
        
        # Step 2: Fix layout (toucan uses crkbd layout)
        yaml_content = KEYMAP_YAML.read_text()
        yaml_content = yaml_content.replace(
            "layout: {zmk_keyboard: toucan}",
            "layout:\n  qmk_keyboard: crkbd/rev1\n  layout_name: LAYOUT_split_3x6_3"
        )
        KEYMAP_YAML.write_text(yaml_content)
        
        # Step 3: Draw SVG from YAML
        draw_result = subprocess.run(
            ["keymap", "-c", str(CONFIG_YAML), "draw", str(KEYMAP_YAML), "-o", str(OUTPUT_SVG)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        
        if draw_result.returncode == 0:
            print(f"{Colors.GREEN}[{timestamp()}]{Colors.NC} ✓ keymap.svg updated successfully")
        else:
            print(f"{Colors.RED}[{timestamp()}] ✗ Failed to generate SVG{Colors.NC}")
            if draw_result.stderr:
                print(f"  Error: {draw_result.stderr.strip()}")
        print()
        
    except FileNotFoundError:
        print(f"{Colors.RED}[{timestamp()}] ✗ 'keymap' command not found{Colors.NC}")
        print("  Install keymap-drawer: pip install keymap-drawer")
        print()


class KeymapHandler(FileSystemEventHandler):
    """Handle file system events for keymap files"""
    
    def __init__(self):
        self.last_modified = 0
        self.debounce_seconds = 0.5
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        event_path = Path(event.src_path)
        
        # Check if modified file is one we care about
        should_trigger = False
        for watch_path in WATCH_FILES.values():
            if event_path.resolve() == watch_path.resolve():
                should_trigger = True
                break
        
        if not should_trigger:
            return
        
        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_seconds:
            return
        self.last_modified = current_time
        
        generate_svg()


def main():
    print(f"{Colors.CYAN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.CYAN}║     Keymap SVG Watcher - Toucan Keyboard   ║{Colors.NC}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    
    # Initial generation
    print(f"{Colors.YELLOW}Generating initial SVG...{Colors.NC}")
    generate_svg()
    
    print(f"{Colors.CYAN}Watching for changes in:{Colors.NC}")
    print(f"  • config/toucan.keymap")
    print(f"  • config.yaml")
    print()
    print(f"{Colors.CYAN}Press Ctrl+C to stop watching{Colors.NC}")
    print()
    
    # Set up file watchers for both directories
    event_handler = KeymapHandler()
    observer = Observer()
    observer.schedule(event_handler, str(PROJECT_ROOT), recursive=False)
    observer.schedule(event_handler, str(PROJECT_ROOT / "config"), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print(f"{Colors.CYAN}Stopping watcher...{Colors.NC}")
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    main()
