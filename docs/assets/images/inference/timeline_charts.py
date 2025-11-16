"""Timeline and scaling comparison visualizations."""

import matplotlib.pyplot as plt
import numpy as np
from chart_utils import COLORS, setup_style, save_chart


def generate_timeline_acceleration():
    """
    Original estimate vs accelerated timeline (METR data).

    Shows how inference scaling + 7-month doubling accelerates adoption.
    """
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    # Timeline quarters
    quarters = ['Q4 2024', 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025',
                'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    x_positions = np.arange(len(quarters))

    # Original estimate (based on Stargate timeline)
    original_adoption = [5, 8, 12, 18, 25, 35, 50, 65, 80]  # % of teams using multi-agent

    # Accelerated estimate (based on METR + inference scaling)
    accelerated_adoption = [10, 20, 35, 50, 65, 78, 88, 95, 98]

    ax.plot(x_positions, original_adoption, 'o-', linewidth=2.5, markersize=8,
            color=COLORS['neutral'], label='Original estimate (Stargate timeline)', alpha=0.7)

    ax.plot(x_positions, accelerated_adoption, 's-', linewidth=2.5, markersize=8,
            color=COLORS['agent'], label='Accelerated (METR + inference scaling)')

    # Shade difference
    ax.fill_between(x_positions, original_adoption, accelerated_adoption,
                   alpha=0.2, color=COLORS['agent'], label='Acceleration gap')

    # Mark key milestones
    ax.axhline(50, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(0, 52, '50% Mainstream Adoption', fontsize=10, color='red', fontweight='bold')

    # Original: Q4 2025
    ax.plot(4, 25, 'o', markersize=15, color=COLORS['neutral'], alpha=0.5)
    ax.annotate('Original:\nQ4 2025\n(25%)', xy=(4, 25), xytext=(2.5, 35),
               fontsize=9, ha='center', color=COLORS['neutral'],
               arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['neutral']))

    # Accelerated: Q3 2025
    ax.plot(3, 50, 's', markersize=15, color=COLORS['agent'])
    ax.annotate('Accelerated:\nQ3 2025\n(50%)', xy=(3, 50), xytext=(5, 60),
               fontsize=9, ha='center', color=COLORS['agent'], fontweight='bold',
               arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['agent']))

    # Crisis zones
    ax.axvspan(3, 5, alpha=0.15, color='orange', label='Crisis window (mainstream adoption)')
    ax.text(4, 90, 'Early adopters\nin crisis', fontsize=10, ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='orange', alpha=0.6))

    ax.set_xlabel('Timeline', fontsize=12, fontweight='bold')
    ax.set_ylabel('Multi-Agent Adoption (%)', fontsize=12, fontweight='bold')
    ax.set_title('Timeline Acceleration: METR Half-Life + Inference Scaling\nMainstream adoption 6 months earlier than expected',
                fontsize=13, fontweight='bold')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(quarters, rotation=45, ha='right')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)

    save_chart('timeline_acceleration')


def generate_inference_vs_training_scaling():
    """
    Training scaling vs inference scaling contribution to capabilities.

    Shows how both contribute, but inference provides immediate jumps.
    """
    setup_style()
    fig, ax = plt.subplots(figsize=(11, 7))

    # Timeline
    months = np.arange(0, 25, 1)  # 0 = late 2024, 24 = late 2026

    # Training scaling: gradual improvement (new models released periodically)
    training_capability = np.array([100] * 25)
    # Jumps at model releases
    training_capability[0:6] = 100
    training_capability[6:12] = 130   # GPT-5 or equivalent (Q2 2025)
    training_capability[12:18] = 160  # Next gen (Q4 2025)
    training_capability[18:] = 200    # Future (Q2 2026)

    # Inference scaling: continuous improvement via more test-time compute
    inference_boost = 100 * (1.08 ** months)  # ~8% monthly improvement via inference scaling

    # Combined capability
    total_capability = training_capability * (inference_boost / 100)

    # Plot
    ax.plot(months, training_capability, 's-', linewidth=2, markersize=6,
            color=COLORS['execution'], label='Training scaling (new models)', alpha=0.7)

    ax.plot(months, total_capability, 'o-', linewidth=2.5, markersize=6,
            color=COLORS['agent'], label='Training + Inference scaling')

    ax.fill_between(months, training_capability, total_capability,
                   alpha=0.2, color=COLORS['learning'],
                   label='Inference scaling contribution')

    # Annotate model releases
    releases = [(6, 130, 'GPT-5 class'), (12, 160, 'Next gen'), (18, 200, 'Future')]
    for month, cap, label in releases:
        ax.annotate(f'{label}\nmodel', xy=(month, cap), xytext=(month + 1, cap - 30),
                   fontsize=9, ha='left', style='italic',
                   arrowprops=dict(arrowstyle='->', lw=1.2, color=COLORS['execution']))

    # Show inference scaling contribution at key points
    key_months = [6, 12, 18]
    for m in key_months:
        diff = total_capability[m] - training_capability[m]
        ax.annotate(f'+{diff:.0f}%\ninference', xy=(m, total_capability[m]),
                   xytext=(m - 1.5, total_capability[m] + 30),
                   fontsize=8, ha='center', color=COLORS['learning'], fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6))

    ax.set_xlabel('Months from Late 2024', fontsize=12, fontweight='bold')
    ax.set_ylabel('Relative Capability', fontsize=12, fontweight='bold')
    ax.set_title('Inference Scaling Provides Continuous Improvement\nBetween Model Releases',
                fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(80, 450)

    save_chart('inference_vs_training_scaling')
