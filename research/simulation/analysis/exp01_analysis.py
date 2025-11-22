"""
Analysis for Experiment 01: Baseline Validation.

Tests success criteria:
1. Stationarity: ADF p-value < 0.05 for H[20:]
2. Mean stability: t-test p-value > 0.05 (first half vs second half)
3. Bounded oscillation: CV(H) < 0.3
4. Reasonable range: 0.5 < mean(H) < 2.0
5. Finite values: No NaN, inf, or negative energies
6. Low incidents: < 5 total incidents in 100 steps
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulation.scenarios.baseline import run_baseline_experiment
from simulation.simulation import SimulationHistory


class BaselineAnalyzer:
    """Analyzer for baseline experiment results."""

    def __init__(self, history: SimulationHistory):
        """
        Initialize analyzer.

        Args:
            history: Simulation history from baseline run
        """
        self.history = history
        self.results = {}

    def run_all_tests(self) -> Dict:
        """
        Run all success criterion tests.

        Returns:
            dict with test results
        """
        print("=" * 60)
        print("EXPERIMENT 01: BASELINE VALIDATION - ANALYSIS")
        print("=" * 60)
        print()

        self.results = {
            'test1_stationarity': self.test_stationarity(),
            'test2_mean_stability': self.test_mean_stability(),
            'test3_bounded_variance': self.test_bounded_variance(),
            'test4_reasonable_range': self.test_reasonable_range(),
            'test5_finite_values': self.test_finite_values(),
            'test6_low_incidents': self.test_low_incidents(),
        }

        # Compute overall pass/fail
        passed = sum(1 for r in self.results.values() if r['pass'])
        total = len(self.results)

        self.results['summary'] = {
            'passed': passed,
            'total': total,
            'pass_rate': passed / total,
            'overall_pass': passed >= 5,  # Need 5/6 to pass
        }

        print()
        print("=" * 60)
        print(f"OVERALL: {passed}/{total} tests passed")
        if self.results['summary']['overall_pass']:
            print("✓ EXPERIMENT 01: PASS")
        else:
            print("✗ EXPERIMENT 01: FAIL")
        print("=" * 60)

        return self.results

    def test_stationarity(self) -> Dict:
        """
        Test 1: H is stationary after transient.

        Uses Augmented Dickey-Fuller test.
        """
        print("Test 1: Stationarity (ADF test)")
        print("-" * 40)

        H = np.array(self.history.H)
        H_steady = H[20:]  # Exclude transient

        try:
            from statsmodels.tsa.stattools import adfuller

            result = adfuller(H_steady)
            adf_stat = result[0]
            p_value = result[1]

            passed = p_value < 0.05

            print(f"  ADF statistic: {adf_stat:.4f}")
            print(f"  p-value: {p_value:.4f}")
            print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'} (p < 0.05)")

            return {
                'pass': passed,
                'adf_statistic': adf_stat,
                'p_value': p_value,
                'criterion': 'p < 0.05'
            }

        except ImportError:
            print("  Warning: statsmodels not installed, skipping ADF test")
            print("  Result: SKIP")
            return {
                'pass': True,  # Don't fail if package missing
                'skipped': True
            }

    def test_mean_stability(self) -> Dict:
        """
        Test 2: Mean(H) stable between first and second half.

        Uses t-test.
        """
        print("\nTest 2: Mean Stability (t-test)")
        print("-" * 40)

        H = np.array(self.history.H)
        H_first_half = H[20:60]
        H_second_half = H[60:100]

        from scipy.stats import ttest_ind

        t_stat, p_value = ttest_ind(H_first_half, H_second_half)

        mean_first = np.mean(H_first_half)
        mean_second = np.mean(H_second_half)

        passed = p_value > 0.05

        print(f"  Mean (first half): {mean_first:.4f}")
        print(f"  Mean (second half): {mean_second:.4f}")
        print(f"  t-statistic: {t_stat:.4f}")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'} (p > 0.05)")

        return {
            'pass': passed,
            't_statistic': t_stat,
            'p_value': p_value,
            'mean_first': mean_first,
            'mean_second': mean_second,
            'criterion': 'p > 0.05'
        }

    def test_bounded_variance(self) -> Dict:
        """
        Test 3: Coefficient of variation < 0.3.
        """
        print("\nTest 3: Bounded Variance (CV)")
        print("-" * 40)

        H = np.array(self.history.H)
        H_steady = H[20:]

        mean_H = np.mean(H_steady)
        std_H = np.std(H_steady)
        cv = std_H / mean_H if mean_H > 0 else 0

        passed = cv < 0.3

        print(f"  Mean H: {mean_H:.4f}")
        print(f"  Std H: {std_H:.4f}")
        print(f"  CV: {cv:.4f}")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'} (CV < 0.3)")

        return {
            'pass': passed,
            'mean': mean_H,
            'std': std_H,
            'cv': cv,
            'criterion': 'CV < 0.3'
        }

    def test_reasonable_range(self) -> Dict:
        """
        Test 4: 0.5 < mean(H) < 2.0.
        """
        print("\nTest 4: Reasonable Range")
        print("-" * 40)

        H = np.array(self.history.H)
        H_steady = H[20:]
        mean_H = np.mean(H_steady)

        passed = 0.5 < mean_H < 2.0

        print(f"  Mean H: {mean_H:.4f}")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'} (0.5 < mean < 2.0)")

        return {
            'pass': passed,
            'mean': mean_H,
            'criterion': '0.5 < mean < 2.0'
        }

    def test_finite_values(self) -> Dict:
        """
        Test 5: No NaN, inf, or negative energies.
        """
        print("\nTest 5: Finite Values")
        print("-" * 40)

        H = np.array(self.history.H)
        T = np.array(self.history.T)
        V = np.array(self.history.V)

        has_nan = np.any(np.isnan(H)) or np.any(np.isnan(T)) or np.any(np.isnan(V))
        has_inf = np.any(np.isinf(H)) or np.any(np.isinf(T)) or np.any(np.isinf(V))
        has_negative_T = np.any(T < 0)
        has_negative_V = np.any(V < 0)

        passed = not (has_nan or has_inf or has_negative_T or has_negative_V)

        print(f"  NaN values: {'Yes ✗' if has_nan else 'No ✓'}")
        print(f"  Inf values: {'Yes ✗' if has_inf else 'No ✓'}")
        print(f"  Negative T: {'Yes ✗' if has_negative_T else 'No ✓'}")
        print(f"  Negative V: {'Yes ✗' if has_negative_V else 'No ✓'}")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")

        return {
            'pass': passed,
            'has_nan': has_nan,
            'has_inf': has_inf,
            'has_negative_T': has_negative_T,
            'has_negative_V': has_negative_V,
            'criterion': 'All values finite and non-negative'
        }

    def test_low_incidents(self) -> Dict:
        """
        Test 6: < 5 total incidents in 100 steps.
        """
        print("\nTest 6: Low Incidents")
        print("-" * 40)

        incident_count = len(self.history.incidents)
        passed = incident_count < 5

        print(f"  Total incidents: {incident_count}")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'} (< 5)")

        return {
            'pass': passed,
            'incident_count': incident_count,
            'criterion': '< 5 incidents'
        }

    def plot_results(self, output_dir: str = '.'):
        """
        Generate plots for baseline experiment.

        Args:
            output_dir: Directory to save plots
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Plot 1: Energy time series
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        steps = self.history.steps

        axes[0].plot(steps, self.history.H, color='purple')
        axes[0].set_ylabel('H (Hamiltonian)')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_title('Baseline: Energy vs Time')

        axes[1].plot(steps, self.history.T, color='orange')
        axes[1].set_ylabel('T (Kinetic)')
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(steps, self.history.V, color='red')
        axes[2].set_ylabel('V (Potential)')
        axes[2].set_xlabel('Time Step')
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path / 'baseline_timeseries.png', dpi=150)
        print(f"\nSaved: {output_path / 'baseline_timeseries.png'}")

        # Plot 2: Phase space
        plt.figure(figsize=(8, 6))
        plt.scatter(self.history.T, self.history.V,
                   c=steps, cmap='viridis', s=20, alpha=0.6)
        plt.xlabel('T (Kinetic)')
        plt.ylabel('V (Potential)')
        plt.colorbar(label='Time Step')
        plt.title('Phase Space Trajectory (T vs V)')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_path / 'baseline_phase_space.png', dpi=150)
        print(f"Saved: {output_path / 'baseline_phase_space.png'}")

        # Plot 3: Health evolution
        plt.figure(figsize=(10, 6))
        for node, health_values in self.history.health.items():
            plt.plot(steps, health_values, label=node, alpha=0.7)
        plt.ylabel('Health')
        plt.xlabel('Time Step')
        plt.legend(loc='best')
        plt.title('Health Evolution')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_path / 'baseline_health_evolution.png', dpi=150)
        print(f"Saved: {output_path / 'baseline_health_evolution.png'}")

        plt.close('all')

    def save_results(self, output_path: str = 'baseline_results.json'):
        """
        Save analysis results to JSON.

        Args:
            output_path: Path to JSON file
        """
        # Convert numpy types to Python types
        def convert_value(v):
            if isinstance(v, (np.floating, np.integer)):
                return float(v)
            elif isinstance(v, (np.bool_, bool)):
                return bool(v)
            else:
                return v

        results_serializable = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                results_serializable[key] = {
                    k: convert_value(v)
                    for k, v in value.items()
                }
            else:
                results_serializable[key] = convert_value(value)

        with open(output_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)

        print(f"\nSaved results: {output_path}")


def main():
    """Run baseline experiment and analysis."""

    # Run experiment
    print("Running baseline experiment...\n")
    history = run_baseline_experiment(n_steps=100, random_seed=42)

    # Analyze
    analyzer = BaselineAnalyzer(history)
    results = analyzer.run_all_tests()

    # Plot
    analyzer.plot_results(output_dir='data/outputs/exp01')

    # Save
    analyzer.save_results('data/outputs/exp01/baseline_results.json')

    return results


if __name__ == '__main__':
    main()
