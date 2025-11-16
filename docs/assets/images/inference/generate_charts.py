#!/usr/bin/env python3
"""
Generate visualizations for inference scaling, half-life model, and multi-agent systems.

Illustrates:
- METR half-life progression (7-month doubling)
- Task horizon timeline (what agents can do when)
- Multi-agent coordination complexity
- Adversarial optimization / verification exploitation
- Accelerated timeline vs original estimates
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

# Set style for clean, professional charts
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
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


def generate_half_life_progression():
    """
    METR half-life model: 7-month doubling of task horizon.

    Shows exponential growth in task duration agents can handle at 50% success rate.
    """
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

    ax.plot(months_since_baseline, half_life_hours, linewidth=3, color=colors['agent'],
            label='Task horizon (50% success rate)')
    ax.fill_between(months_since_baseline, 0, half_life_hours, alpha=0.15, color=colors['agent'])

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

    plt.tight_layout()
    plt.savefig('half_life_progression.png', dpi=300, bbox_inches='tight')
    plt.savefig('half_life_progression.svg', bbox_inches='tight')
    print("✓ Generated: half_life_progression.{png,svg}")
    plt.close()


def generate_task_horizon_capabilities():
    """
    What agents can do at different task horizons.

    Maps task duration to concrete software engineering capabilities.
    """
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
                   color=[colors['agent'] if sr >= 50 else colors['neutral'] for sr in success_rates],
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

    plt.tight_layout()
    plt.savefig('task_horizon_capabilities.png', dpi=300, bbox_inches='tight')
    plt.savefig('task_horizon_capabilities.svg', bbox_inches='tight')
    print("✓ Generated: task_horizon_capabilities.{png,svg}")
    plt.close()


def generate_multi_agent_complexity():
    """
    Coordination complexity grows with specialized agent roles.

    Shows 1 agent vs 5-agent system vs 20-agent system.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # Single agent
    ax1.add_patch(plt.Circle((0.5, 0.5), 0.15, color=colors['agent'], alpha=0.8))
    ax1.text(0.5, 0.5, 'Agent', ha='center', va='center', fontsize=11,
             color='white', fontweight='bold')
    ax1.text(0.5, 0.1, 'Coordination:\n1 entity', ha='center', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.6))
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('Single Agent\n(Simple)', fontsize=12, fontweight='bold')

    # 5-agent multi-agent system
    agent_positions = [(0.5, 0.7), (0.3, 0.4), (0.7, 0.4), (0.35, 0.15), (0.65, 0.15)]
    agent_labels = ['Arch', 'Code', 'Test', 'Review', 'Integrate']

    for i, (x, y) in enumerate(agent_positions):
        ax2.add_patch(plt.Circle((x, y), 0.08, color=colors['agent'], alpha=0.8))
        ax2.text(x, y, agent_labels[i], ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')

    # Draw connections (coordination links)
    for i, (x1, y1) in enumerate(agent_positions):
        for j, (x2, y2) in enumerate(agent_positions[i+1:], start=i+1):
            ax2.plot([x1, x2], [y1, y2], 'k-', alpha=0.2, linewidth=1)

    connections = len(agent_positions) * (len(agent_positions) - 1) // 2
    ax2.text(0.5, 0.05, f'Coordination:\n{connections} connections', ha='center', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.6))
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('Multi-Agent (5)\n(Moderate)', fontsize=12, fontweight='bold')

    # 20-agent swarm
    np.random.seed(42)
    num_agents = 20
    agent_x = np.random.uniform(0.1, 0.9, num_agents)
    agent_y = np.random.uniform(0.15, 0.9, num_agents)

    for x, y in zip(agent_x, agent_y):
        ax3.add_patch(plt.Circle((x, y), 0.04, color=colors['agent'], alpha=0.6))

    # Draw subset of connections (too many to show all)
    for i in range(min(50, num_agents * 2)):
        i1, i2 = np.random.choice(num_agents, 2, replace=False)
        ax3.plot([agent_x[i1], agent_x[i2]], [agent_y[i1], agent_y[i2]],
                'k-', alpha=0.1, linewidth=0.5)

    total_connections = num_agents * (num_agents - 1) // 2
    ax3.text(0.5, 0.05, f'Coordination:\n{total_connections} connections', ha='center', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='red', alpha=0.5),
             color='white', fontweight='bold')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_aspect('equal')
    ax3.axis('off')
    ax3.set_title('Agent Swarm (20)\n(Complex)', fontsize=12, fontweight='bold')

    fig.suptitle('Coordination Complexity: O(n²) Growth', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('multi_agent_complexity.png', dpi=300, bbox_inches='tight')
    plt.savefig('multi_agent_complexity.svg', bbox_inches='tight')
    print("✓ Generated: multi_agent_complexity.{png,svg}")
    plt.close()


def generate_adversarial_optimization():
    """
    AlphaEvolve lesson: agents exploit verification vulnerabilities.

    Shows how agents optimize against verification, not intent.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Naive verification (exploitable)
    ax1.text(0.5, 0.9, 'Naive Verification', ha='center', fontsize=13, fontweight='bold')

    # Verification checks
    checks = ['Tests pass', 'Coverage >80%', 'Linter clean', 'Performance OK']
    y_pos = 0.7
    for check in checks:
        ax1.add_patch(Rectangle((0.1, y_pos - 0.05), 0.8, 0.08,
                                facecolor='lightgreen', edgecolor='black', linewidth=1))
        ax1.text(0.5, y_pos, f'✓ {check}', ha='center', va='center', fontsize=10)
        y_pos -= 0.15

    # Agent exploitation
    ax1.text(0.5, 0.2, 'Agent finds loopholes:', ha='center', fontsize=11,
             fontweight='bold', color='red')
    exploits = ['• Tests pass but miss intent', '• Coverage via trivial tests', '• Linter rules gamed']
    y_pos = 0.12
    for exploit in exploits:
        ax1.text(0.5, y_pos, exploit, ha='center', fontsize=9, color='red', style='italic')
        y_pos -= 0.05

    ax1.arrow(0.5, 0.35, 0, -0.1, head_width=0.05, head_length=0.02, fc='red', ec='red')

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')

    # Right: Robust verification (Tensegrity approach)
    ax2.text(0.5, 0.9, 'Robust Verification (Tensegrity)', ha='center', fontsize=13, fontweight='bold')

    # Robust checks
    robust_checks = [
        ('Semantic verification', 'Intent-based invariants'),
        ('Human comprehension', 'Prediction challenges'),
        ('Adversarial testing', 'Mutation testing'),
        ('Architecture constraints', 'Coupling metrics'),
    ]
    y_pos = 0.7
    for check, detail in robust_checks:
        ax2.add_patch(Rectangle((0.05, y_pos - 0.05), 0.9, 0.08,
                                facecolor='lightblue', edgecolor='black', linewidth=1))
        ax2.text(0.15, y_pos, f'✓ {check}', ha='left', va='center', fontsize=10, fontweight='bold')
        ax2.text(0.85, y_pos, detail, ha='right', va='center', fontsize=8, style='italic')
        y_pos -= 0.15

    # Defense mechanisms
    ax2.text(0.5, 0.15, 'Defense against exploitation:', ha='center', fontsize=11,
             fontweight='bold', color='green')
    defenses = ['✓ Multiple verification layers', '✓ Human-in-loop for ambiguity', '✓ Adaptive thresholds']
    y_pos = 0.08
    for defense in defenses:
        ax2.text(0.5, y_pos, defense, ha='center', fontsize=9, color='green')
        y_pos -= 0.04

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')

    fig.suptitle('Adversarial Optimization: Agents Exploit Verification (Tao\'s AlphaEvolve Lesson)',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('adversarial_optimization.png', dpi=300, bbox_inches='tight')
    plt.savefig('adversarial_optimization.svg', bbox_inches='tight')
    print("✓ Generated: adversarial_optimization.{png,svg}")
    plt.close()


def generate_timeline_acceleration():
    """
    Original estimate vs accelerated timeline (METR data).

    Shows how inference scaling + 7-month doubling accelerates adoption.
    """
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
            color=colors['neutral'], label='Original estimate (Stargate timeline)', alpha=0.7)

    ax.plot(x_positions, accelerated_adoption, 's-', linewidth=2.5, markersize=8,
            color=colors['agent'], label='Accelerated (METR + inference scaling)')

    # Shade difference
    ax.fill_between(x_positions, original_adoption, accelerated_adoption,
                   alpha=0.2, color=colors['agent'], label='Acceleration gap')

    # Mark key milestones
    ax.axhline(50, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(0, 52, '50% Mainstream Adoption', fontsize=10, color='red', fontweight='bold')

    # Original: Q4 2025
    ax.plot(4, 25, 'o', markersize=15, color=colors['neutral'], alpha=0.5)
    ax.annotate('Original:\nQ4 2025\n(25%)', xy=(4, 25), xytext=(2.5, 35),
               fontsize=9, ha='center', color=colors['neutral'],
               arrowprops=dict(arrowstyle='->', lw=1.5, color=colors['neutral']))

    # Accelerated: Q3 2025
    ax.plot(3, 50, 's', markersize=15, color=colors['agent'])
    ax.annotate('Accelerated:\nQ3 2025\n(50%)', xy=(3, 50), xytext=(5, 60),
               fontsize=9, ha='center', color=colors['agent'], fontweight='bold',
               arrowprops=dict(arrowstyle='->', lw=2, color=colors['agent']))

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

    plt.tight_layout()
    plt.savefig('timeline_acceleration.png', dpi=300, bbox_inches='tight')
    plt.savefig('timeline_acceleration.svg', bbox_inches='tight')
    print("✓ Generated: timeline_acceleration.{png,svg}")
    plt.close()


def generate_inference_vs_training_scaling():
    """
    Training scaling vs inference scaling contribution to capabilities.

    Shows how both contribute, but inference provides immediate jumps.
    """
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
            color=colors['execution'], label='Training scaling (new models)', alpha=0.7)

    ax.plot(months, total_capability, 'o-', linewidth=2.5, markersize=6,
            color=colors['agent'], label='Training + Inference scaling')

    ax.fill_between(months, training_capability, total_capability,
                   alpha=0.2, color=colors['learning'],
                   label='Inference scaling contribution')

    # Annotate model releases
    releases = [(6, 130, 'GPT-5 class'), (12, 160, 'Next gen'), (18, 200, 'Future')]
    for month, cap, label in releases:
        ax.annotate(f'{label}\nmodel', xy=(month, cap), xytext=(month + 1, cap - 30),
                   fontsize=9, ha='left', style='italic',
                   arrowprops=dict(arrowstyle='->', lw=1.2, color=colors['execution']))

    # Show inference scaling contribution at key points
    key_months = [6, 12, 18]
    for m in key_months:
        diff = total_capability[m] - training_capability[m]
        ax.annotate(f'+{diff:.0f}%\ninference', xy=(m, total_capability[m]),
                   xytext=(m - 1.5, total_capability[m] + 30),
                   fontsize=8, ha='center', color=colors['learning'], fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6))

    ax.set_xlabel('Months from Late 2024', fontsize=12, fontweight='bold')
    ax.set_ylabel('Relative Capability', fontsize=12, fontweight='bold')
    ax.set_title('Inference Scaling Provides Continuous Improvement\nBetween Model Releases',
                fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(80, 450)

    plt.tight_layout()
    plt.savefig('inference_vs_training_scaling.png', dpi=300, bbox_inches='tight')
    plt.savefig('inference_vs_training_scaling.svg', bbox_inches='tight')
    print("✓ Generated: inference_vs_training_scaling.{png,svg}")
    plt.close()


if __name__ == '__main__':
    print("Generating inference scaling and multi-agent visualizations...\n")

    generate_half_life_progression()
    generate_task_horizon_capabilities()
    generate_multi_agent_complexity()
    generate_adversarial_optimization()
    generate_timeline_acceleration()
    generate_inference_vs_training_scaling()

    print("\n✓ All visualizations generated successfully!")
    print("  Location: docs/assets/images/inference/")
    print("  Formats: PNG (300 DPI) and SVG (vector)")
