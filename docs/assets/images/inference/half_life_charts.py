"""METR half-life model visualizations."""

import matplotlib.pyplot as plt
import numpy as np
from chart_utils import COLORS, setup_style, save_chart


def generate_half_life_progression():
    """
    METR half-life model: 7-month doubling of task horizon.

    Shows exponential growth in task duration agents can handle at 50% success rate.
    """
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    # Timeline from late 2024 to 2027
    months_since_baseline = np.arange(0, 36, 1)  # 0 = late 2024, 36 = late 2027

    # Baseline: ~4 minutes at 50% success (METR current finding)
    baseline_minutes = 4
    doubling_months = 7

    # Half-life in minutes: doubles every 7 months
    half_life_minutes = baseline_minutes * (2 ** (months_since_baseline / doubling_months))

    # Convert to hours for readability
    half_life_hours = half_life_minutes / 60

    # Timeline labels
    dates = ['Late 2024', 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025',
             'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026', 'Q1 2027', 'Q2 2027', 'Q3 2027']
    date_positions = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]

    ax.plot(months_since_baseline, half_life_hours, linewidth=3, color=COLORS['agent'],
            label='Task horizon (50% success rate)')
    ax.fill_between(months_since_baseline, 0, half_life_hours, alpha=0.15, color=COLORS['agent'])

    # Mark key milestones
    milestones = [
        (0, baseline_minutes/60, '4 min\n(Today)'),
        (7, 8/60, '8 min\n(+7 mo)'),
        (14, 16/60, '16 min\n(+14 mo)'),
        (21, 32/60, '32 min\n(+21 mo)'),
        (28, 64/60, '1 hr\n(+28 mo)'),
    ]

    for month, hours, label in milestones:
        ax.plot(month, hours, 'o', color='red', markersize=10, zorder=5)
        ax.annotate(label, xy=(month, hours), xytext=(month, hours + 0.5),
                   fontsize=9, ha='center', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7))

    # Capability zones
    ax.axhspan(0, 0.25, alpha=0.1, color='green', label='Current agents excel')
    ax.axhspan(0.25, 1, alpha=0.1, color='orange', label='Emerging capability')
    ax.axhspan(1, 10, alpha=0.1, color='red', label='Future capability')

    ax.set_xlabel('Timeline', fontsize=12, fontweight='bold')
    ax.set_ylabel('Task Duration (Hours of Expert Work)', fontsize=12, fontweight='bold')
    ax.set_title('METR Half-Life Model: Agent Task Horizon Doubles Every 7 Months',
                fontsize=14, fontweight='bold')
    ax.set_xticks(date_positions)
    ax.set_xticklabels(dates, rotation=45, ha='right')
    ax.set_yscale('log')
    ax.set_ylim(0.05, 10)
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='upper left', fontsize=10)

    # Add annotation
    ax.text(18, 5, 'Exponential growth:\n7-month doubling', fontsize=11, ha='center',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='lightblue', alpha=0.6),
            fontweight='bold')

    save_chart('half_life_progression')


def generate_task_horizon_capabilities():
    """
    What agents can do at different task horizons.

    Maps task duration to concrete software engineering capabilities.
    """
    setup_style()
    fig, ax = plt.subplots(figsize=(10, 8))

    # Task durations and capabilities
    tasks = [
        ('5 min', 0.08, '100%', 'Single function\nimplementation'),
        ('15 min', 0.25, '90%', 'Feature with tests\n(small scope)'),
        ('30 min', 0.5, '70%', 'Multi-file feature\nwith integration'),
        ('1 hour', 1, '50%', 'Complete feature:\ncode + tests + docs'),
        ('2 hours', 2, '30%', 'Cross-module feature\nwith refactoring'),
        ('4 hours', 4, '15%', 'Epic implementation\nacross subsystems'),
        ('8 hours', 8, '5%', 'Full day development:\ndesign + implement'),
    ]

    y_positions = np.arange(len(tasks))
    durations = [t[1] for t in tasks]
    success_rates = [int(t[2].strip('%')) for t in tasks]

    # Bar chart showing success rates
    bars = ax.barh(y_positions, success_rates, height=0.6,
                   color=[COLORS['agent'] if sr >= 50 else COLORS['neutral'] for sr in success_rates],
                   alpha=0.7)

    # Add duration and capability labels
    for i, (label, dur, sr, capability) in enumerate(tasks):
        # Duration label on the left
        ax.text(-10, i, label, fontsize=10, ha='right', va='center', fontweight='bold')

        # Success rate inside bar
        ax.text(success_rates[i] - 5, i, sr, fontsize=10, ha='right', va='center',
                color='white', fontweight='bold')

        # Capability on the right
        ax.text(105, i, capability, fontsize=9, ha='left', va='center',
                style='italic')

    # Mark current frontier (50% line)
    ax.axvline(50, color='red', linestyle='--', linewidth=2, label='50% success threshold')
    ax.text(50, len(tasks) - 0.5, 'Current frontier →', fontsize=10, ha='right',
            color='red', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7))

    ax.set_xlabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Task Duration (Expert Work)', fontsize=12, fontweight='bold')
    ax.set_title('Agent Capabilities by Task Horizon\n(Current Frontier: ~1 hour at 50% success)',
                fontsize=13, fontweight='bold')
    ax.set_yticks([])
    ax.set_xlim(-15, 120)
    ax.grid(axis='x', alpha=0.3)
    ax.legend(loc='lower right', fontsize=10)

    save_chart('task_horizon_capabilities')
