#!/usr/bin/env python3
"""
Chapter 21: Competition & Benchmarks - Performance Evaluation
Demonstrates how to evaluate and compare robot performance against competition benchmarks.

Useful for understanding how your robot compares to competition standards.
"""

from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class PerformanceMetric:
    """A single performance metric"""
    name: str
    value: float
    unit: str
    weight: float = 1.0  # Importance weight for overall scoring


@dataclass
class CompetitionBenchmark:
    """Competition benchmark standards"""
    task_name: str
    gold_score: float  # Best possible score
    silver_score: float  # Good score
    bronze_score: float  # Acceptable score
    minimum_score: float  # Minimum to qualify


class PerformanceEvaluator:
    """Evaluate robot performance against benchmarks"""

    def __init__(self, robot_name: str):
        self.robot_name = robot_name
        self.metrics: List[PerformanceMetric] = []
        self.benchmarks: Dict[str, CompetitionBenchmark] = self._init_benchmarks()

    def _init_benchmarks(self) -> Dict[str, CompetitionBenchmark]:
        """Initialize standard competition benchmarks"""
        return {
            "walking_speed": CompetitionBenchmark(
                task_name="Walking Speed (m/s)",
                gold_score=1.5,
                silver_score=1.2,
                bronze_score=0.9,
                minimum_score=0.5
            ),
            "stability_margin": CompetitionBenchmark(
                task_name="Stability Margin (%)",
                gold_score=95,
                silver_score=85,
                bronze_score=75,
                minimum_score=60
            ),
            "kicking_accuracy": CompetitionBenchmark(
                task_name="Kicking Accuracy (%)",
                gold_score=85,
                silver_score=75,
                bronze_score=65,
                minimum_score=50
            ),
            "object_grasping": CompetitionBenchmark(
                task_name="Object Grasping Success (%)",
                gold_score=90,
                silver_score=80,
                bronze_score=70,
                minimum_score=50
            ),
            "recovery_time": CompetitionBenchmark(
                task_name="Recovery Time (seconds)",
                gold_score=2.0,  # Lower is better for time metrics
                silver_score=3.0,
                bronze_score=4.0,
                minimum_score=5.0
            )
        }

    def add_metric(self, name: str, value: float, unit: str, weight: float = 1.0):
        """Add a measured performance metric

        Args:
            name: Metric name (should match a benchmark key)
            value: Measured value
            unit: Unit of measurement
            weight: Importance weight for scoring
        """
        metric = PerformanceMetric(name, value, unit, weight)
        self.metrics.append(metric)

    def evaluate_against_benchmarks(self) -> Dict:
        """Evaluate all metrics against competition benchmarks

        Returns:
            Dictionary with evaluation results
        """
        evaluation = {
            "robot": self.robot_name,
            "metrics": [],
            "overall_ranking": None,
            "qualification_status": "FAIL"
        }

        total_score = 0
        total_weight = 0
        qualified_tasks = 0

        for metric in self.metrics:
            if metric.name not in self.benchmarks:
                continue

            benchmark = self.benchmarks[metric.name]

            # Determine ranking for this metric
            if metric.name == "recovery_time":  # Lower is better
                if metric.value <= benchmark.gold_score:
                    ranking = "GOLD"
                    score = 100
                elif metric.value <= benchmark.silver_score:
                    ranking = "SILVER"
                    score = 75
                elif metric.value <= benchmark.bronze_score:
                    ranking = "BRONZE"
                    score = 50
                elif metric.value <= benchmark.minimum_score:
                    ranking = "QUALIFIED"
                    score = 25
                else:
                    ranking = "UNQUALIFIED"
                    score = 0
            else:  # Higher is better
                if metric.value >= benchmark.gold_score:
                    ranking = "GOLD"
                    score = 100
                elif metric.value >= benchmark.silver_score:
                    ranking = "SILVER"
                    score = 75
                elif metric.value >= benchmark.bronze_score:
                    ranking = "BRONZE"
                    score = 50
                elif metric.value >= benchmark.minimum_score:
                    ranking = "QUALIFIED"
                    score = 25
                else:
                    ranking = "UNQUALIFIED"
                    score = 0

            metric_eval = {
                "name": metric.name,
                "measured_value": metric.value,
                "unit": metric.unit,
                "ranking": ranking,
                "score": score,
                "benchmarks": {
                    "gold": benchmark.gold_score,
                    "silver": benchmark.silver_score,
                    "bronze": benchmark.bronze_score,
                    "minimum": benchmark.minimum_score
                }
            }

            evaluation["metrics"].append(metric_eval)

            # Update overall scoring
            total_score += score * metric.weight
            total_weight += metric.weight

            if score >= 25:  # Qualified threshold
                qualified_tasks += 1

        # Calculate overall ranking
        if total_weight > 0:
            overall_score = total_score / total_weight

            if overall_score >= 75:
                evaluation["overall_ranking"] = "GOLD"
                evaluation["qualification_status"] = "QUALIFIED"
            elif overall_score >= 50:
                evaluation["overall_ranking"] = "SILVER"
                evaluation["qualification_status"] = "QUALIFIED"
            elif overall_score >= 25:
                evaluation["overall_ranking"] = "BRONZE"
                evaluation["qualification_status"] = "QUALIFIED"
            else:
                evaluation["overall_ranking"] = "UNQUALIFIED"
                evaluation["qualification_status"] = "FAIL"

            evaluation["overall_score"] = overall_score
            evaluation["qualified_tasks"] = qualified_tasks

        return evaluation

    def print_evaluation_report(self):
        """Print detailed evaluation report"""

        evaluation = self.evaluate_against_benchmarks()

        print(f"\n{'='*70}")
        print(f"PERFORMANCE EVALUATION REPORT")
        print(f"{'='*70}")
        print(f"Robot: {self.robot_name}")
        print(f"\n{'Metric Name':<30} {'Measured':<15} {'Ranking':<10}")
        print(f"{'-'*70}")

        for metric_eval in evaluation["metrics"]:
            name = metric_eval["name"]
            value = f"{metric_eval['measured_value']:.2f} {metric_eval['unit']}"
            ranking = metric_eval["ranking"]
            print(f"{name:<30} {value:<15} {ranking:<10}")

        print(f"\n{'-'*70}")
        print(f"Overall Score: {evaluation.get('overall_score', 0):.1f}/100")
        print(f"Overall Ranking: {evaluation.get('overall_ranking', 'N/A')}")
        print(f"Qualification: {evaluation['qualification_status']}")
        print(f"Qualified Tasks: {evaluation.get('qualified_tasks', 0)}/{len(evaluation['metrics'])}")
        print(f"{'='*70}\n")

        return evaluation

    def compare_with_competitors(self, competitors: Dict[str, Dict]) -> Dict:
        """Compare robot performance with competitors

        Args:
            competitors: Dictionary of competitor metrics
                Example: {"Team A": {"walking_speed": 1.2, ...}, ...}

        Returns:
            Comparison results
        """
        # Extract our metrics
        our_metrics = {}
        for metric in self.metrics:
            our_metrics[metric.name] = metric.value

        # Create comparison table
        comparison = {
            "benchmark_date": "2024-02-04",
            "competitors": {},
            "rankings": {}
        }

        # Add our robot
        comparison["competitors"][self.robot_name] = our_metrics

        # Add competitors
        for team_name, metrics in competitors.items():
            comparison["competitors"][team_name] = metrics

        # Calculate rankings for each metric
        for metric_name in our_metrics.keys():
            metric_values = []
            for team_name, metrics in comparison["competitors"].items():
                if metric_name in metrics:
                    metric_values.append((team_name, metrics[metric_name]))

            # Sort appropriately
            if metric_name == "recovery_time":
                metric_values.sort(key=lambda x: x[1])  # Lower is better
            else:
                metric_values.sort(key=lambda x: x[1], reverse=True)  # Higher is better

            comparison["rankings"][metric_name] = [
                {"rank": i+1, "team": team, "value": value}
                for i, (team, value) in enumerate(metric_values)
            ]

        return comparison

    def export_report(self, filename: str):
        """Export evaluation report to JSON file

        Args:
            filename: Output JSON file path
        """
        evaluation = self.evaluate_against_benchmarks()

        with open(filename, 'w') as f:
            json.dump(evaluation, f, indent=2)

        print(f"Report exported to {filename}")


def main():
    """Example: Evaluate robot performance"""

    # Create evaluator
    evaluator = PerformanceEvaluator("NAAO_Humanoid_v2")

    # Add measured metrics
    evaluator.add_metric("walking_speed", 1.3, "m/s")
    evaluator.add_metric("stability_margin", 88, "%")
    evaluator.add_metric("kicking_accuracy", 78, "%")
    evaluator.add_metric("object_grasping", 82, "%")
    evaluator.add_metric("recovery_time", 2.5, "seconds")

    # Print evaluation report
    evaluation = evaluator.print_evaluation_report()

    # Export report
    evaluator.export_report("performance_evaluation.json")

    # Compare with competitors
    competitors = {
        "Team_A_Humanoid": {
            "walking_speed": 1.1,
            "stability_margin": 85,
            "kicking_accuracy": 80,
            "object_grasping": 75,
            "recovery_time": 3.0
        },
        "Team_B_Humanoid": {
            "walking_speed": 1.4,
            "stability_margin": 90,
            "kicking_accuracy": 75,
            "object_grasping": 85,
            "recovery_time": 2.0
        }
    }

    print("\nComparing with competitors...")
    comparison = evaluator.compare_with_competitors(competitors)

    # Print rankings
    print(f"\n{'='*50}")
    print("COMPETITION RANKINGS")
    print(f"{'='*50}")
    for metric_name, rankings in comparison["rankings"].items():
        print(f"\n{metric_name}:")
        for ranking in rankings:
            marker = "→" if ranking["team"] == evaluator.robot_name else " "
            print(f"  {marker} {ranking['rank']}. {ranking['team']}: {ranking['value']}")


if __name__ == "__main__":
    main()
