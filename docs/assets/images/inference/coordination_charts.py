"""Multi-agent coordination complexity visualizations."""

import matplotlib.pyplot as plt
import numpy as np
from chart_utils import COLORS, setup_style, save_chart


def generate_multi_agent_complexity():
    """
    Coordination complexity grows with specialized agent roles.

    Shows 1 agent vs 5-agent system vs 20-agent system.
    """
    setup_style()
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # Single agent
    ax1.add_patch(plt.Circle((0.5, 0.5), 0.15, color=COLORS['agent'], alpha=0.8))
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
        ax2.add_patch(plt.Circle((x, y), 0.08, color=COLORS['agent'], alpha=0.8))
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
        ax3.add_patch(plt.Circle((x, y), 0.04, color=COLORS['agent'], alpha=0.6))

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
    save_chart('multi_agent_complexity')
