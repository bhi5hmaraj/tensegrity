"""
Shared utilities for generating inference scaling visualizations.

Provides common color schemes, styling, and helper functions.
"""

import matplotlib.pyplot as plt

# Color palette for consistency across all charts
COLORS = {
    'velocity': '#2196F3',      # Electric blue
    'quality': '#7B1FA2',       # Deep purple
    'coherence': '#388E3C',     # Emerald green
    'learning': '#F57C00',      # Warm orange
    'scope': '#C2185B',         # Soft pink
    'execution': '#1565C0',     # Dark blue
    'governance': '#EF6C00',    # Orange
    'agent': '#00897B',         # Teal
    'human': '#E91E63',         # Pink
    'neutral': '#757575'        # Gray
}


def setup_style():
    """Apply consistent style to all charts."""
    plt.style.use('seaborn-v0_8-darkgrid')


def save_chart(filename_base):
    """Save chart in both PNG and SVG formats."""
    plt.tight_layout()
    plt.savefig(f'{filename_base}.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{filename_base}.svg', bbox_inches='tight')
    print(f"✓ Generated: {filename_base}.{{png,svg}}")
    plt.close()
