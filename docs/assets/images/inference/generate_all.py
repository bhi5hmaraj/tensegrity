#!/usr/bin/env python3
"""
Generate all inference scaling and multi-agent visualizations.

Modular chart generation system:
- chart_utils.py: Shared colors and styling
- half_life_charts.py: METR half-life model charts
- coordination_charts.py: Multi-agent complexity
- verification_charts.py: Adversarial optimization
- timeline_charts.py: Timeline and scaling comparisons

Run this script to generate all charts at once.
"""

from half_life_charts import (
    generate_half_life_progression,
    generate_task_horizon_capabilities
)
from coordination_charts import generate_multi_agent_complexity
from verification_charts import generate_adversarial_optimization
from timeline_charts import (
    generate_timeline_acceleration,
    generate_inference_vs_training_scaling
)


def main():
    """Generate all visualizations."""
    print("Generating inference scaling and multi-agent visualizations...\n")

    print("Half-life model charts...")
    generate_half_life_progression()
    generate_task_horizon_capabilities()

    print("\nCoordination complexity charts...")
    generate_multi_agent_complexity()

    print("\nVerification and adversarial optimization charts...")
    generate_adversarial_optimization()

    print("\nTimeline and scaling charts...")
    generate_timeline_acceleration()
    generate_inference_vs_training_scaling()

    print("\n" + "="*60)
    print("✓ All visualizations generated successfully!")
    print("  Location: docs/assets/images/inference/")
    print("  Formats: PNG (300 DPI) and SVG (vector)")
    print("="*60)


if __name__ == '__main__':
    main()
