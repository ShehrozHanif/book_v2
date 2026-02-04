#!/usr/bin/env python3
"""
Chapter 21: Competition & Benchmarks - Benchmark Execution Framework
Demonstrates how to execute and track benchmark performance across multiple runs.

Useful for competition preparation and performance tuning.
"""

import json
from datetime import datetime
from typing import Dict, List
import statistics


class BenchmarkExecutor:
    """Execute and track benchmark performance across multiple runs"""

    def __init__(self, benchmark_name: str, robot_name: str):
        self.benchmark_name = benchmark_name
        self.robot_name = robot_name
        self.runs: List[Dict] = []
        self.execution_log: List[str] = []

    def execute_run(self, run_number: int, parameters: Dict) -> Dict:
        """Execute a single benchmark run with given parameters

        Args:
            run_number: Sequential run identifier
            parameters: Benchmark parameters (e.g., walking speed, obstacle height)

        Returns:
            Dictionary with run results
        """
        timestamp = datetime.now().isoformat()

        # Simulate benchmark execution with parameter variations
        result = {
            "run_number": run_number,
            "timestamp": timestamp,
            "parameters": parameters,
            "metrics": self._calculate_metrics(parameters),
            "status": "completed"
        }

        self.runs.append(result)
        self.execution_log.append(
            f"[Run {run_number}] {self.benchmark_name} - {timestamp}"
        )

        return result

    def _calculate_metrics(self, parameters: Dict) -> Dict:
        """Calculate performance metrics based on parameters"""

        # Simulated metrics calculation
        speed = parameters.get("walking_speed", 0.5)
        stability = parameters.get("stability_mode", "normal")

        metrics = {
            "success_rate": min(95, 70 + speed * 10),
            "completion_time": max(5, 20 - speed * 5),
            "energy_consumption": 100 - (speed * 5),
            "stability_index": {
                "low": 0.7,
                "normal": 0.85,
                "high": 0.95
            }.get(stability, 0.85)
        }

        return metrics

    def run_parameter_sweep(self, param_ranges: Dict) -> List[Dict]:
        """Execute benchmark with parameter sweep for optimization

        Args:
            param_ranges: Dictionary with parameter names and value ranges
                Example: {"walking_speed": [0.3, 0.5, 0.7], "stability_mode": ["low", "normal"]}

        Returns:
            List of results from all combinations
        """
        results = []
        run_count = 0

        # Generate parameter combinations
        speeds = param_ranges.get("walking_speed", [0.5])
        stability_modes = param_ranges.get("stability_mode", ["normal"])

        for speed in speeds:
            for stability in stability_modes:
                run_count += 1
                params = {
                    "walking_speed": speed,
                    "stability_mode": stability
                }
                result = self.execute_run(run_count, params)
                results.append(result)

                print(f"Run {run_count}: speed={speed}, stability={stability}")
                print(f"  Success Rate: {result['metrics']['success_rate']:.1f}%")
                print(f"  Time: {result['metrics']['completion_time']:.1f}s")
                print(f"  Energy: {result['metrics']['energy_consumption']:.1f}%")

        return results

    def get_statistics(self) -> Dict:
        """Calculate statistics across all runs"""

        if not self.runs:
            return {}

        success_rates = [r["metrics"]["success_rate"] for r in self.runs]
        completion_times = [r["metrics"]["completion_time"] for r in self.runs]

        stats = {
            "total_runs": len(self.runs),
            "success_rate": {
                "mean": statistics.mean(success_rates),
                "median": statistics.median(success_rates),
                "stdev": statistics.stdev(success_rates) if len(success_rates) > 1 else 0,
                "min": min(success_rates),
                "max": max(success_rates)
            },
            "completion_time": {
                "mean": statistics.mean(completion_times),
                "median": statistics.median(completion_times),
                "stdev": statistics.stdev(completion_times) if len(completion_times) > 1 else 0,
                "min": min(completion_times),
                "max": max(completion_times)
            }
        }

        return stats

    def export_results(self, filename: str):
        """Export benchmark results to JSON file

        Args:
            filename: Output JSON file path
        """
        export_data = {
            "benchmark_name": self.benchmark_name,
            "robot_name": self.robot_name,
            "execution_date": datetime.now().isoformat(),
            "total_runs": len(self.runs),
            "runs": self.runs,
            "statistics": self.get_statistics()
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\nResults exported to {filename}")

    def print_summary(self):
        """Print summary of benchmark execution"""

        stats = self.get_statistics()

        print(f"\n{'='*60}")
        print(f"Benchmark Execution Summary")
        print(f"{'='*60}")
        print(f"Benchmark: {self.benchmark_name}")
        print(f"Robot: {self.robot_name}")
        print(f"Total Runs: {stats.get('total_runs', 0)}")

        if "success_rate" in stats:
            sr = stats["success_rate"]
            print(f"\nSuccess Rate:")
            print(f"  Mean: {sr['mean']:.1f}%")
            print(f"  Median: {sr['median']:.1f}%")
            print(f"  Range: {sr['min']:.1f}% - {sr['max']:.1f}%")

        if "completion_time" in stats:
            ct = stats["completion_time"]
            print(f"\nCompletion Time:")
            print(f"  Mean: {ct['mean']:.2f}s")
            print(f"  Median: {ct['median']:.2f}s")
            print(f"  Range: {ct['min']:.2f}s - {ct['max']:.2f}s")

        print(f"{'='*60}\n")


def main():
    """Example: Execute benchmark with parameter sweep"""

    # Create executor
    executor = BenchmarkExecutor(
        benchmark_name="RoboCup TeenSize Qualification",
        robot_name="NAAO_Humanoid_v2"
    )

    # Define parameter ranges to test
    param_ranges = {
        "walking_speed": [0.3, 0.5, 0.7],
        "stability_mode": ["low", "normal", "high"]
    }

    print(f"Starting parameter sweep for {executor.benchmark_name}")
    print(f"Robot: {executor.robot_name}\n")

    # Run parameter sweep
    results = executor.run_parameter_sweep(param_ranges)

    # Print summary statistics
    executor.print_summary()

    # Export results
    executor.export_results("benchmark_results.json")

    # Find best configuration
    best_run = max(executor.runs, key=lambda r: r["metrics"]["success_rate"])
    print(f"\nBest Configuration:")
    print(f"  Success Rate: {best_run['metrics']['success_rate']:.1f}%")
    print(f"  Parameters: {best_run['parameters']}")


if __name__ == "__main__":
    main()
