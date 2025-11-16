"""Adversarial optimization and verification visualizations."""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from chart_utils import COLORS, setup_style, save_chart


def generate_adversarial_optimization():
    """
    AlphaEvolve lesson: agents exploit verification vulnerabilities.

    Shows how agents optimize against verification, not intent.
    """
    setup_style()
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
    save_chart('adversarial_optimization')
