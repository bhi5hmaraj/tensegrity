#!/usr/bin/env python3
"""
Generate economic theory visualizations for Tensegrity strategic notes.

Illustrates:
- Linear Programming feasible region (constraint shift)
- Shadow prices (before vs after agents)
- Baumol cost disease (governance becoming expensive)
- Jevons paradox (efficiency → consumption increase)
- Combined effects timeline
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
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
    'neutral': '#757575'        # Gray
}


def generate_lp_constraint_shift():
    """
    Generate 2D LP feasible region showing constraint shift.

    Before agents: Execution is tight constraint, governance has slack
    After agents: Governance is tight constraint, execution has slack
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Before agents: Execution constraint is tight
    ax1.set_xlim(0, 12)
    ax1.set_ylim(0, 12)
    ax1.set_xlabel('Software Value Delivered', fontsize=11)
    ax1.set_ylabel('Code Volume Produced', fontsize=11)
    ax1.set_title('Before AI Agents:\nExecution Constraint is Tight', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Execution constraint (tight) - steep slope, close to origin
    exec_x = np.array([0, 6])
    exec_y = np.array([10, 0])
    ax1.plot(exec_x, exec_y, color=colors['execution'], linewidth=2.5, label='Execution Constraint (tight)')
    ax1.fill_between(exec_x, 0, exec_y, alpha=0.15, color=colors['execution'])

    # Governance constraint (loose) - gentle slope, far from origin
    gov_x = np.array([0, 11])
    gov_y = np.array([11, 0])
    ax1.plot(gov_x, gov_y, color=colors['governance'], linewidth=2, linestyle='--', alpha=0.6, label='Governance Constraint (slack)')

    # Feasible region (bounded by execution)
    feasible = np.array([[0, 0], [6, 0], [6, 0], [3, 7], [0, 10]])
    ax1.add_patch(Polygon(feasible[:4], alpha=0.25, facecolor=colors['execution'], edgecolor='none'))

    # Optimal point (on execution constraint)
    ax1.plot(3, 7, 'o', color='red', markersize=12, markeredgewidth=2, markeredgecolor='darkred', label='Optimal (on execution edge)', zorder=5)
    ax1.annotate('Limited by\nhuman execution', xy=(3, 7), xytext=(5.5, 9),
                 fontsize=10, ha='center',
                 arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))

    ax1.legend(loc='upper right', fontsize=9)

    # After agents: Governance constraint is tight
    ax2.set_xlim(0, 12)
    ax2.set_ylim(0, 12)
    ax2.set_xlabel('Software Value Delivered', fontsize=11)
    ax2.set_ylabel('Code Volume Produced', fontsize=11)
    ax2.set_title('After AI Agents:\nGovernance Constraint is Tight', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Execution constraint (now loose) - gentle slope, far from origin
    exec_x2 = np.array([0, 11])
    exec_y2 = np.array([11, 0])
    ax2.plot(exec_x2, exec_y2, color=colors['execution'], linewidth=2, linestyle='--', alpha=0.6, label='Execution Constraint (slack)')

    # Governance constraint (now tight) - steeper slope, closer
    gov_x2 = np.array([0, 7.5])
    gov_y2 = np.array([10, 0])
    ax2.plot(gov_x2, gov_y2, color=colors['governance'], linewidth=2.5, label='Governance Constraint (tight)')
    ax2.fill_between(gov_x2, 0, gov_y2, alpha=0.15, color=colors['governance'])

    # Feasible region (now bounded by governance)
    feasible2 = np.array([[0, 0], [7.5, 0], [4, 6.5], [0, 10]])
    ax2.add_patch(Polygon(feasible2[:4], alpha=0.25, facecolor=colors['governance'], edgecolor='none'))

    # Optimal point (on governance constraint)
    ax2.plot(4, 6.5, 'o', color='red', markersize=12, markeredgewidth=2, markeredgecolor='darkred', label='Optimal (on governance edge)', zorder=5)
    ax2.annotate('Limited by\ngovernance capacity', xy=(4, 6.5), xytext=(7, 9),
                 fontsize=10, ha='center',
                 arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))

    ax2.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    plt.savefig('lp_constraint_shift.png', dpi=300, bbox_inches='tight')
    plt.savefig('lp_constraint_shift.svg', bbox_inches='tight')
    print("✓ Generated: lp_constraint_shift.{png,svg}")
    plt.close()


def generate_shadow_prices():
    """
    Shadow price comparison: value of relaxing constraints before vs after agents.

    Shadow price = marginal value of one more unit of constraint capacity
    Before: High shadow price on execution (valuable to add human capacity)
    After: High shadow price on governance (valuable to automate governance)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    constraints = ['Execution\nCapacity', 'Governance\nCapacity', 'Quality\nThreshold', 'Scope\nLimits']
    before_prices = [45, 5, 8, 12]  # Before: execution bottleneck
    after_prices = [3, 60, 15, 10]   # After: governance bottleneck

    x = np.arange(len(constraints))
    width = 0.35

    bars1 = ax.bar(x - width/2, before_prices, width, label='Before AI Agents', color=colors['execution'], alpha=0.8)
    bars2 = ax.bar(x + width/2, after_prices, width, label='After AI Agents', color=colors['governance'], alpha=0.8)

    ax.set_ylabel('Shadow Price ($/unit)', fontsize=12, fontweight='bold')
    ax.set_title('Shadow Prices: Marginal Value of Relaxing Constraints', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(constraints, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.0f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Add annotations
    ax.annotate('Execution was\nthe bottleneck', xy=(0 - width/2, 45), xytext=(-0.8, 55),
                fontsize=10, ha='center', color=colors['execution'],
                arrowprops=dict(arrowstyle='->', lw=1.5, color=colors['execution']))

    ax.annotate('Governance is now\nthe bottleneck', xy=(1 + width/2, 60), xytext=(1.8, 70),
                fontsize=10, ha='center', color=colors['governance'],
                arrowprops=dict(arrowstyle='->', lw=1.5, color=colors['governance']))

    plt.tight_layout()
    plt.savefig('shadow_prices.png', dpi=300, bbox_inches='tight')
    plt.savefig('shadow_prices.svg', bbox_inches='tight')
    print("✓ Generated: shadow_prices.{png,svg}")
    plt.close()


def generate_baumol_cost_disease():
    """
    Baumol's Cost Disease: Sectors with low productivity growth become expensive.

    Execution: Productivity increased 10-100x (AI agents)
    Governance: Productivity mostly unchanged (still human-driven)
    Result: Governance costs dominate
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Cost structure before agents
    labels1 = ['Execution\nCost', 'Governance\nCost', 'Other']
    sizes1 = [60, 25, 15]
    colors1 = [colors['execution'], colors['governance'], colors['neutral']]

    wedges1, texts1, autotexts1 = ax1.pie(sizes1, labels=labels1, colors=colors1, autopct='%1.0f%%',
                                            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Before AI Agents:\nCost Structure', fontsize=13, fontweight='bold')

    # Make percentage text more visible
    for autotext in autotexts1:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')

    # Right: Cost structure after agents
    labels2 = ['Execution\nCost', 'Governance\nCost', 'Other']
    sizes2 = [15, 70, 15]
    colors2 = [colors['execution'], colors['governance'], colors['neutral']]

    wedges2, texts2, autotexts2 = ax2.pie(sizes2, labels=labels2, colors=colors2, autopct='%1.0f%%',
                                            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('After AI Agents:\nCost Structure (Baumol Effect)', fontsize=13, fontweight='bold')

    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')

    # Add explanation text
    fig.text(0.5, 0.05,
             'Execution productivity increased 10-100x, but governance productivity unchanged.\n' +
             'Result: Governance costs now dominate (Baumol Cost Disease)',
             ha='center', fontsize=11, style='italic', wrap=True)

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig('baumol_cost_disease.png', dpi=300, bbox_inches='tight')
    plt.savefig('baumol_cost_disease.svg', bbox_inches='tight')
    print("✓ Generated: baumol_cost_disease.{png,svg}")
    plt.close()


def generate_jevons_paradox():
    """
    Jevons Paradox: Efficiency improvements increase total consumption.

    Cheaper execution → More code written → More governance needed
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Timeline from 2020 to 2026
    years = np.array([2020, 2021, 2022, 2023, 2024, 2025, 2026])

    # Execution cost per line (decreasing due to AI)
    exec_cost = np.array([100, 95, 85, 60, 30, 15, 10])  # Relative cost

    # Code volume (increasing because it's cheaper)
    code_volume = np.array([100, 110, 130, 200, 400, 700, 1000])  # Relative volume

    # Total execution spend (initially decreases, then increases)
    total_exec = exec_cost * code_volume / 100

    ax2 = ax.twinx()

    # Plot execution cost (left y-axis)
    line1 = ax.plot(years, exec_cost, marker='o', linewidth=2.5, markersize=8,
                    color=colors['execution'], label='Cost per Line of Code')
    ax.set_ylabel('Cost per Line (Relative)', fontsize=12, fontweight='bold', color=colors['execution'])
    ax.tick_params(axis='y', labelcolor=colors['execution'])
    ax.set_ylim(0, 120)

    # Plot code volume (right y-axis)
    line2 = ax2.plot(years, code_volume, marker='s', linewidth=2.5, markersize=8,
                     color=colors['governance'], label='Total Code Volume', linestyle='--')
    ax2.set_ylabel('Code Volume Produced (Relative)', fontsize=12, fontweight='bold', color=colors['governance'])
    ax2.tick_params(axis='y', labelcolor=colors['governance'])
    ax2.set_ylim(0, 1200)

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_title('Jevons Paradox: Cheaper Execution → More Code → More Governance',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add annotations
    ax.annotate('AI agents make\nexecution 10x cheaper', xy=(2024, 30), xytext=(2022.5, 60),
                fontsize=10, ha='center', color=colors['execution'],
                arrowprops=dict(arrowstyle='->', lw=1.5, color=colors['execution']))

    ax2.annotate('But code volume\nincreases 10x', xy=(2025, 700), xytext=(2023.5, 900),
                 fontsize=10, ha='center', color=colors['governance'],
                 arrowprops=dict(arrowstyle='->', lw=1.5, color=colors['governance']))

    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left', fontsize=10)

    plt.tight_layout()
    plt.savefig('jevons_paradox.png', dpi=300, bbox_inches='tight')
    plt.savefig('jevons_paradox.svg', bbox_inches='tight')
    print("✓ Generated: jevons_paradox.{png,svg}")
    plt.close()


def generate_combined_effects():
    """
    Combined timeline showing all effects together.

    Shows: execution cost down, code volume up, governance burden up
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    years = np.array([2020, 2021, 2022, 2023, 2024, 2025, 2026])

    # Normalized metrics (0-100 scale for comparison)
    exec_productivity = np.array([10, 12, 18, 35, 60, 85, 100])  # AI improves execution
    gov_productivity = np.array([10, 11, 12, 13, 14, 15, 16])     # Governance barely improves
    code_volume = np.array([10, 12, 15, 25, 45, 70, 100])        # More code written
    gov_burden = code_volume / gov_productivity * 10              # Governance burden increases

    ax.plot(years, exec_productivity, marker='o', linewidth=2.5, markersize=8,
            color=colors['execution'], label='Execution Productivity (AI-driven)')

    ax.plot(years, gov_productivity, marker='s', linewidth=2.5, markersize=8,
            color=colors['governance'], label='Governance Productivity (human-limited)', linestyle='--')

    ax.plot(years, code_volume, marker='^', linewidth=2.5, markersize=8,
            color=colors['velocity'], label='Code Volume (Jevons effect)')

    ax.plot(years, gov_burden, marker='D', linewidth=2.5, markersize=8,
            color='red', label='Governance Burden (crisis!)', linestyle=':')

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Relative Index (2020 = 10)', fontsize=12, fontweight='bold')
    ax.set_title('The Governance Crisis: Combined Effects of Jevons + Baumol',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)

    # Highlight crisis zone
    ax.axvspan(2024, 2026, alpha=0.15, color='red', label='Crisis zone')
    ax.text(2025, 80, 'Governance burden\nexplodes!', fontsize=11, ha='center',
            color='red', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

    # Add Tensegrity solution
    ax.annotate('', xy=(2025.5, 40), xytext=(2025.5, 70),
                arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
    ax.text(2025.7, 55, 'Tensegrity:\nAutomate\ngovernance', fontsize=10, ha='left',
            color='green', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.5))

    plt.tight_layout()
    plt.savefig('combined_effects.png', dpi=300, bbox_inches='tight')
    plt.savefig('combined_effects.svg', bbox_inches='tight')
    print("✓ Generated: combined_effects.{png,svg}")
    plt.close()


def generate_simplex_vertex_walk():
    """
    Illustrate simplex algorithm as vertex walk on polytope.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-0.5, 10)
    ax.set_xlabel('Velocity Force', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quality Force', fontsize=12, fontweight='bold')
    ax.set_title('Simplex Algorithm: Walking Vertices to Find Equilibrium',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Feasible region (polytope)
    vertices = np.array([[0, 0], [8, 0], [7, 5], [4, 8], [0, 9]])
    poly = Polygon(vertices, alpha=0.15, facecolor=colors['velocity'], edgecolor=colors['velocity'], linewidth=2)
    ax.add_patch(poly)

    # Simplex path (vertex walk)
    path = np.array([[0, 0], [8, 0], [7, 5], [4, 8]])
    ax.plot(path[:, 0], path[:, 1], 'o-', color='red', linewidth=2.5, markersize=10,
            markeredgewidth=2, markeredgecolor='darkred', label='Simplex path')

    # Label vertices
    for i, (x, y) in enumerate(path):
        if i == 0:
            label = 'Start\n(basic feasible)'
        elif i == len(path) - 1:
            label = 'Optimal\n(equilibrium)'
        else:
            label = f'Iteration {i}'

        ax.annotate(label, xy=(x, y), xytext=(x + 0.5, y + 0.8),
                   fontsize=10, ha='center', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7))

    # Draw constraint lines
    ax.plot([0, 8], [9, 0], color=colors['quality'], linewidth=1.5, linestyle='--',
            alpha=0.6, label='Quality constraint')
    ax.plot([0, 10], [8, 0], color=colors['coherence'], linewidth=1.5, linestyle='--',
            alpha=0.6, label='Coherence constraint')

    ax.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig('simplex_vertex_walk.png', dpi=300, bbox_inches='tight')
    plt.savefig('simplex_vertex_walk.svg', bbox_inches='tight')
    print("✓ Generated: simplex_vertex_walk.{png,svg}")
    plt.close()


if __name__ == '__main__':
    print("Generating economic theory visualizations...\n")

    generate_lp_constraint_shift()
    generate_shadow_prices()
    generate_baumol_cost_disease()
    generate_jevons_paradox()
    generate_combined_effects()
    generate_simplex_vertex_walk()

    print("\n✓ All visualizations generated successfully!")
    print("  Location: docs/assets/images/economics/")
    print("  Formats: PNG (300 DPI) and SVG (vector)")
