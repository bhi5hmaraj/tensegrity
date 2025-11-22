#!/bin/bash
# Generate SVG diagrams from DOT files
# Requires: graphviz (install with: brew install graphviz or apt-get install graphviz)

set -e

DIAGRAMS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Generating SVG diagrams from DOT files..."

# Check if dot command is available
if ! command -v dot &> /dev/null; then
    echo "Error: 'dot' command not found. Please install graphviz:"
    echo "  macOS: brew install graphviz"
    echo "  Ubuntu/Debian: sudo apt-get install graphviz"
    echo "  Fedora: sudo dnf install graphviz"
    exit 1
fi

# Generate SVGs from all DOT files
count=0
for dot_file in "$DIAGRAMS_DIR"/*.dot; do
    if [ -f "$dot_file" ]; then
        svg_file="${dot_file%.dot}.svg"
        echo "  Generating: $(basename "$svg_file")"
        dot -Tsvg "$dot_file" -o "$svg_file"
        ((count++))
    fi
done

echo "Done! Generated $count SVG files."
echo ""
echo "Generated files:"
ls -lh "$DIAGRAMS_DIR"/*.svg
