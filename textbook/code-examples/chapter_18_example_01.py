#!/usr/bin/env python3
"""
Chapter 18 Example 1: Economic ROI Calculator for Humanoid Robot Deployment

This module provides tools for calculating the Return on Investment (ROI) for
deploying humanoid robots in industrial settings. It models capital costs,
operational expenses, benefits, and performs sensitivity analysis.

Dependencies:
    - numpy>=1.21.0
    - matplotlib>=3.5.0
    - pandas>=1.3.0

Author: Physical AI & Humanoid Robotics Textbook
License: MIT
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import pandas as pd


@dataclass
class DeploymentCosts:
    """Capital and operational costs for humanoid robot deployment."""

    # Capital Costs (one-time)
    robot_unit_cost: float = 150000.0  # USD per robot
    num_robots: int = 10
    infrastructure_cost: float = 50000.0  # charging stations, safety systems
    integration_cost: float = 75000.0  # software integration, testing
    training_cost: float = 25000.0  # operator training

    # Operational Costs (annual)
    maintenance_cost_per_robot: float = 15000.0  # per year
    energy_cost_per_robot: float = 2500.0  # per year
    software_licensing: float = 10000.0  # per year
    insurance: float = 20000.0  # per year
    support_staff_cost: float = 120000.0  # 2 technicians at $60k each

    def total_capital_cost(self) -> float:
        """Calculate total upfront capital investment."""
        return (
            self.robot_unit_cost * self.num_robots +
            self.infrastructure_cost +
            self.integration_cost +
            self.training_cost
        )

    def annual_operational_cost(self) -> float:
        """Calculate total annual operational expenses."""
        return (
            self.maintenance_cost_per_robot * self.num_robots +
            self.energy_cost_per_robot * self.num_robots +
            self.software_licensing +
            self.insurance +
            self.support_staff_cost
        )


@dataclass
class DeploymentBenefits:
    """Economic benefits from humanoid robot deployment."""

    # Labor savings
    human_workers_replaced: int = 15
    avg_worker_salary: float = 55000.0  # USD per year
    benefits_overhead: float = 0.30  # 30% for benefits, taxes, etc.

    # Productivity improvements
    productivity_increase: float = 0.20  # 20% increase
    annual_production_value: float = 2000000.0  # USD

    # Quality improvements
    defect_rate_reduction: float = 0.15  # 15% reduction
    cost_per_defect: float = 500.0  # USD
    annual_defects_baseline: int = 1000

    # Safety improvements
    workplace_injury_reduction: int = 8  # injuries prevented per year
    avg_injury_cost: float = 50000.0  # medical, lost time, legal

    # Operating hours advantage
    robot_daily_hours: float = 20.0  # robots can work longer shifts
    human_daily_hours: float = 8.0

    def annual_labor_savings(self) -> float:
        """Calculate annual savings from labor replacement."""
        cost_per_worker = self.avg_worker_salary * (1 + self.benefits_overhead)
        return cost_per_worker * self.human_workers_replaced

    def annual_productivity_gains(self) -> float:
        """Calculate value from increased productivity."""
        return self.annual_production_value * self.productivity_increase

    def annual_quality_savings(self) -> float:
        """Calculate savings from improved quality."""
        defects_prevented = self.annual_defects_baseline * self.defect_rate_reduction
        return defects_prevented * self.cost_per_defect

    def annual_safety_savings(self) -> float:
        """Calculate savings from workplace injury reduction."""
        return self.workplace_injury_reduction * self.avg_injury_cost

    def total_annual_benefits(self) -> float:
        """Calculate total annual economic benefits."""
        return (
            self.annual_labor_savings() +
            self.annual_productivity_gains() +
            self.annual_quality_savings() +
            self.annual_safety_savings()
        )


class ROICalculator:
    """Calculate ROI metrics for humanoid robot deployment."""

    def __init__(self, costs: DeploymentCosts, benefits: DeploymentBenefits,
                 discount_rate: float = 0.08, analysis_years: int = 10):
        """
        Initialize ROI calculator.

        Args:
            costs: Deployment cost structure
            benefits: Expected benefits structure
            discount_rate: Annual discount rate for NPV calculation (default 8%)
            analysis_years: Time horizon for analysis (default 10 years)
        """
        self.costs = costs
        self.benefits = benefits
        self.discount_rate = discount_rate
        self.analysis_years = analysis_years

    def calculate_annual_cash_flow(self) -> np.ndarray:
        """
        Calculate annual cash flows over the analysis period.

        Returns:
            Array of annual cash flows (negative for year 0, positive thereafter)
        """
        cash_flows = np.zeros(self.analysis_years + 1)

        # Year 0: Initial capital investment (negative cash flow)
        cash_flows[0] = -self.costs.total_capital_cost()

        # Years 1-N: Annual benefits minus operational costs
        annual_net_benefit = (
            self.benefits.total_annual_benefits() -
            self.costs.annual_operational_cost()
        )

        cash_flows[1:] = annual_net_benefit

        return cash_flows

    def calculate_npv(self) -> float:
        """
        Calculate Net Present Value (NPV) of the investment.

        Returns:
            NPV in USD (positive indicates profitable investment)
        """
        cash_flows = self.calculate_annual_cash_flow()

        # Discount each year's cash flow
        npv = 0.0
        for year, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + self.discount_rate) ** year)

        return npv

    def calculate_irr(self) -> float:
        """
        Calculate Internal Rate of Return (IRR).

        Returns:
            IRR as a decimal (e.g., 0.15 = 15%)
        """
        cash_flows = self.calculate_annual_cash_flow()
        return np.irr(cash_flows)

    def calculate_payback_period(self) -> float:
        """
        Calculate payback period in years.

        Returns:
            Years until cumulative cash flow becomes positive
        """
        cash_flows = self.calculate_annual_cash_flow()
        cumulative = np.cumsum(cash_flows)

        # Find where cumulative becomes positive
        positive_indices = np.where(cumulative > 0)[0]

        if len(positive_indices) == 0:
            return float('inf')  # Never pays back

        payback_year = positive_indices[0]

        # Linear interpolation for fractional year
        if payback_year > 0:
            prev_cumulative = cumulative[payback_year - 1]
            curr_cumulative = cumulative[payback_year]
            fraction = -prev_cumulative / (curr_cumulative - prev_cumulative)
            return payback_year - 1 + fraction

        return 0.0

    def calculate_roi_percentage(self) -> float:
        """
        Calculate simple ROI as a percentage.

        Returns:
            ROI percentage over the analysis period
        """
        total_investment = self.costs.total_capital_cost()
        total_benefits = self.benefits.total_annual_benefits() * self.analysis_years
        total_op_costs = self.costs.annual_operational_cost() * self.analysis_years

        net_profit = total_benefits - total_op_costs - total_investment

        return (net_profit / total_investment) * 100


class SensitivityAnalyzer:
    """Perform sensitivity analysis on ROI calculations."""

    def __init__(self, base_calculator: ROICalculator):
        """
        Initialize sensitivity analyzer.

        Args:
            base_calculator: Baseline ROI calculator
        """
        self.base_calc = base_calculator

    def analyze_parameter(self, param_name: str, param_range: np.ndarray,
                         metric: str = 'npv') -> np.ndarray:
        """
        Analyze sensitivity to a single parameter.

        Args:
            param_name: Name of parameter to vary (e.g., 'robot_unit_cost')
            param_range: Array of values to test
            metric: Metric to calculate ('npv', 'irr', 'payback', 'roi')

        Returns:
            Array of metric values corresponding to param_range
        """
        results = []

        for value in param_range:
            # Create a copy of the calculator with modified parameter
            calc = self._create_modified_calculator(param_name, value)

            # Calculate the requested metric
            if metric == 'npv':
                results.append(calc.calculate_npv())
            elif metric == 'irr':
                results.append(calc.calculate_irr())
            elif metric == 'payback':
                results.append(calc.calculate_payback_period())
            elif metric == 'roi':
                results.append(calc.calculate_roi_percentage())
            else:
                raise ValueError(f"Unknown metric: {metric}")

        return np.array(results)

    def _create_modified_calculator(self, param_name: str,
                                   value: float) -> ROICalculator:
        """Create a calculator with one modified parameter."""
        # Deep copy the costs and benefits
        import copy
        costs = copy.deepcopy(self.base_calc.costs)
        benefits = copy.deepcopy(self.base_calc.benefits)

        # Modify the specified parameter
        if hasattr(costs, param_name):
            setattr(costs, param_name, value)
        elif hasattr(benefits, param_name):
            setattr(benefits, param_name, value)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")

        return ROICalculator(
            costs, benefits,
            self.base_calc.discount_rate,
            self.base_calc.analysis_years
        )

    def create_sensitivity_report(self, parameters: Dict[str, np.ndarray],
                                 metric: str = 'npv') -> pd.DataFrame:
        """
        Create a comprehensive sensitivity report.

        Args:
            parameters: Dict mapping parameter names to ranges to test
            metric: Metric to analyze

        Returns:
            DataFrame with sensitivity analysis results
        """
        results = {}

        for param_name, param_range in parameters.items():
            values = self.analyze_parameter(param_name, param_range, metric)
            results[param_name] = values

        return pd.DataFrame(results)


def visualize_cash_flows(calculator: ROICalculator):
    """
    Visualize annual cash flows and cumulative cash flow.

    Args:
        calculator: ROI calculator instance
    """
    cash_flows = calculator.calculate_annual_cash_flow()
    cumulative = np.cumsum(cash_flows)
    years = np.arange(len(cash_flows))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Annual cash flows
    colors = ['red' if cf < 0 else 'green' for cf in cash_flows]
    ax1.bar(years, cash_flows / 1000, color=colors, alpha=0.7)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Cash Flow ($K)')
    ax1.set_title('Annual Cash Flows')
    ax1.grid(True, alpha=0.3)

    # Cumulative cash flow
    ax2.plot(years, cumulative / 1000, 'b-', linewidth=2, marker='o')
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax2.fill_between(years, 0, cumulative / 1000,
                     where=(cumulative >= 0), alpha=0.3, color='green',
                     label='Positive ROI')
    ax2.fill_between(years, 0, cumulative / 1000,
                     where=(cumulative < 0), alpha=0.3, color='red',
                     label='Negative ROI')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Cumulative Cash Flow ($K)')
    ax2.set_title('Cumulative Cash Flow Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('roi_cash_flows.png', dpi=300, bbox_inches='tight')
    print("Cash flow visualization saved to 'roi_cash_flows.png'")


def visualize_sensitivity(analyzer: SensitivityAnalyzer):
    """
    Create sensitivity analysis visualizations.

    Args:
        analyzer: Sensitivity analyzer instance
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Define parameters to analyze
    sensitivity_params = {
        'robot_unit_cost': {
            'range': np.linspace(100000, 200000, 20),
            'label': 'Robot Unit Cost ($)',
            'ax': axes[0, 0]
        },
        'productivity_increase': {
            'range': np.linspace(0.05, 0.35, 20),
            'label': 'Productivity Increase (%)',
            'ax': axes[0, 1]
        },
        'human_workers_replaced': {
            'range': np.arange(5, 25, 1),
            'label': 'Workers Replaced',
            'ax': axes[1, 0]
        },
        'maintenance_cost_per_robot': {
            'range': np.linspace(5000, 25000, 20),
            'label': 'Annual Maintenance Cost per Robot ($)',
            'ax': axes[1, 1]
        }
    }

    for param_name, config in sensitivity_params.items():
        param_range = config['range']
        npv_values = analyzer.analyze_parameter(param_name, param_range, 'npv')

        ax = config['ax']
        ax.plot(param_range, npv_values / 1000, 'b-', linewidth=2)
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
        ax.fill_between(param_range, 0, npv_values / 1000,
                       where=(npv_values >= 0), alpha=0.3, color='green')
        ax.fill_between(param_range, 0, npv_values / 1000,
                       where=(npv_values < 0), alpha=0.3, color='red')
        ax.set_xlabel(config['label'])
        ax.set_ylabel('NPV ($K)')
        ax.set_title(f'NPV Sensitivity to {config["label"]}')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('roi_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    print("Sensitivity analysis saved to 'roi_sensitivity_analysis.png'")


def generate_roi_report(calculator: ROICalculator) -> str:
    """
    Generate a comprehensive ROI report.

    Args:
        calculator: ROI calculator instance

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 70)
    report.append("HUMANOID ROBOT DEPLOYMENT - ROI ANALYSIS REPORT")
    report.append("=" * 70)
    report.append("")

    # Investment Summary
    report.append("INVESTMENT SUMMARY")
    report.append("-" * 70)
    report.append(f"Number of Robots: {calculator.costs.num_robots}")
    report.append(f"Total Capital Investment: ${calculator.costs.total_capital_cost():,.2f}")
    report.append(f"  - Robot Units: ${calculator.costs.robot_unit_cost * calculator.costs.num_robots:,.2f}")
    report.append(f"  - Infrastructure: ${calculator.costs.infrastructure_cost:,.2f}")
    report.append(f"  - Integration: ${calculator.costs.integration_cost:,.2f}")
    report.append(f"  - Training: ${calculator.costs.training_cost:,.2f}")
    report.append("")
    report.append(f"Annual Operational Costs: ${calculator.costs.annual_operational_cost():,.2f}")
    report.append("")

    # Benefits Summary
    report.append("EXPECTED BENEFITS (ANNUAL)")
    report.append("-" * 70)
    report.append(f"Labor Savings: ${calculator.benefits.annual_labor_savings():,.2f}")
    report.append(f"  - Workers Replaced: {calculator.benefits.human_workers_replaced}")
    report.append(f"Productivity Gains: ${calculator.benefits.annual_productivity_gains():,.2f}")
    report.append(f"Quality Improvements: ${calculator.benefits.annual_quality_savings():,.2f}")
    report.append(f"Safety Improvements: ${calculator.benefits.annual_safety_savings():,.2f}")
    report.append(f"TOTAL ANNUAL BENEFITS: ${calculator.benefits.total_annual_benefits():,.2f}")
    report.append("")

    # ROI Metrics
    report.append("ROI METRICS")
    report.append("-" * 70)

    npv = calculator.calculate_npv()
    irr = calculator.calculate_irr()
    payback = calculator.calculate_payback_period()
    roi_pct = calculator.calculate_roi_percentage()

    report.append(f"Net Present Value (NPV): ${npv:,.2f}")
    report.append(f"Internal Rate of Return (IRR): {irr*100:.2f}%")
    report.append(f"Payback Period: {payback:.2f} years")
    report.append(f"ROI over {calculator.analysis_years} years: {roi_pct:.2f}%")
    report.append("")

    # Investment Recommendation
    report.append("INVESTMENT RECOMMENDATION")
    report.append("-" * 70)

    if npv > 0 and payback < 5:
        recommendation = "STRONGLY RECOMMENDED"
        reasoning = "Positive NPV and rapid payback indicate excellent investment."
    elif npv > 0:
        recommendation = "RECOMMENDED"
        reasoning = "Positive NPV indicates profitable investment over time."
    elif npv > -100000:
        recommendation = "BORDERLINE - Further Analysis Needed"
        reasoning = "NPV close to breakeven. Consider sensitivity analysis."
    else:
        recommendation = "NOT RECOMMENDED"
        reasoning = "Negative NPV indicates investment may not be profitable."

    report.append(f"Decision: {recommendation}")
    report.append(f"Reasoning: {reasoning}")
    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    """Demonstrate ROI calculator with example scenario."""

    print("\n" + "="*70)
    print("HUMANOID ROBOT DEPLOYMENT - ROI CALCULATOR DEMO")
    print("="*70 + "\n")

    # Define baseline deployment scenario
    costs = DeploymentCosts(
        robot_unit_cost=150000.0,
        num_robots=10,
        infrastructure_cost=50000.0,
        integration_cost=75000.0,
        training_cost=25000.0,
        maintenance_cost_per_robot=15000.0,
        energy_cost_per_robot=2500.0,
        software_licensing=10000.0,
        insurance=20000.0,
        support_staff_cost=120000.0
    )

    benefits = DeploymentBenefits(
        human_workers_replaced=15,
        avg_worker_salary=55000.0,
        benefits_overhead=0.30,
        productivity_increase=0.20,
        annual_production_value=2000000.0,
        defect_rate_reduction=0.15,
        cost_per_defect=500.0,
        annual_defects_baseline=1000,
        workplace_injury_reduction=8,
        avg_injury_cost=50000.0
    )

    # Create calculator
    calculator = ROICalculator(
        costs=costs,
        benefits=benefits,
        discount_rate=0.08,
        analysis_years=10
    )

    # Generate and print report
    report = generate_roi_report(calculator)
    print(report)

    # Visualize cash flows
    print("\nGenerating visualizations...")
    visualize_cash_flows(calculator)

    # Perform sensitivity analysis
    analyzer = SensitivityAnalyzer(calculator)
    visualize_sensitivity(analyzer)

    # Create sensitivity data table
    print("\nSENSITIVITY ANALYSIS - NPV vs Robot Cost")
    print("-" * 70)
    robot_costs = np.linspace(100000, 200000, 11)
    npv_values = analyzer.analyze_parameter('robot_unit_cost', robot_costs, 'npv')

    for cost, npv in zip(robot_costs, npv_values):
        status = "Profitable" if npv > 0 else "Unprofitable"
        print(f"Robot Cost: ${cost:,.0f} -> NPV: ${npv:,.2f} ({status})")

    print("\n" + "="*70)
    print("Analysis complete! Check generated PNG files for visualizations.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
