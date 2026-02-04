#!/usr/bin/env python3
"""
Chapter 15, Example 2: QP-Based Whole-Body Controller

This example demonstrates:
1. Quadratic Programming formulation for whole-body control
2. Constraint handling (joint limits, contacts, CoM)
3. Task priority via QP weights
4. Real-time QP solving using cvxpy

Dependencies:
    pip install numpy matplotlib cvxpy scipy

Expected Output:
    - QP formulation and solution
    - Constraint satisfaction verification
    - Joint velocities respecting all constraints
    - Performance metrics

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    print("Warning: cvxpy not installed. Install with: pip install cvxpy")
    CVXPY_AVAILABLE = False


class WholeBodyQPController:
    """
    QP-based whole-body controller with multiple tasks and constraints.

    Formulation:
        minimize: ||J_1*q_dot - v_1||²_W1 + ||J_2*q_dot - v_2||²_W2 + ...
        subject to:
            q_dot_min <= q_dot <= q_dot_max
            A_eq * q_dot = b_eq (equality constraints)
            A_ineq * q_dot <= b_ineq (inequality constraints)
    """

    def __init__(self, n_joints):
        """
        Initialize QP controller.

        Args:
            n_joints: Number of robot joints
        """
        self.n = n_joints
        self.tasks = []
        self.eq_constraints = []
        self.ineq_constraints = []

    def add_task(self, jacobian, desired_velocity, weight=1.0, name="Task"):
        """
        Add a task to the QP.

        Args:
            jacobian: Task Jacobian (m x n)
            desired_velocity: Desired task velocity (m,)
            weight: Task weight (higher = more important)
            name: Task name
        """
        self.tasks.append({
            'J': np.array(jacobian),
            'v_des': np.array(desired_velocity).flatten(),
            'weight': weight,
            'name': name
        })

    def add_equality_constraint(self, A, b, name="Equality"):
        """
        Add equality constraint: A * q_dot = b

        Args:
            A: Constraint matrix
            b: Constraint vector
            name: Constraint name
        """
        self.eq_constraints.append({
            'A': np.array(A),
            'b': np.array(b).flatten(),
            'name': name
        })

    def add_inequality_constraint(self, A, b, name="Inequality"):
        """
        Add inequality constraint: A * q_dot <= b

        Args:
            A: Constraint matrix
            b: Constraint vector
            name: Constraint name
        """
        self.ineq_constraints.append({
            'A': np.array(A),
            'b': np.array(b).flatten(),
            'name': name
        })

    def solve(self, q_dot_min=None, q_dot_max=None, verbose=False):
        """
        Solve the QP problem.

        Args:
            q_dot_min: Minimum joint velocities
            q_dot_max: Maximum joint velocities
            verbose: Print solver output

        Returns:
            Optimal joint velocities
        """
        if not CVXPY_AVAILABLE:
            print("Error: cvxpy not available. Using fallback solution.")
            return self._solve_fallback()

        # Decision variable
        q_dot = cp.Variable(self.n)

        # Objective: sum of weighted task errors
        objective = 0
        for task in self.tasks:
            J = task['J']
            v_des = task['v_des']
            w = task['weight']

            error = J @ q_dot - v_des
            objective += w * cp.sum_squares(error)

        # Constraints
        constraints = []

        # Joint velocity limits
        if q_dot_min is not None:
            constraints.append(q_dot >= q_dot_min)
        if q_dot_max is not None:
            constraints.append(q_dot <= q_dot_max)

        # Equality constraints
        for eq in self.eq_constraints:
            constraints.append(eq['A'] @ q_dot == eq['b'])

        # Inequality constraints
        for ineq in self.ineq_constraints:
            constraints.append(ineq['A'] @ q_dot <= ineq['b'])

        # Solve QP
        problem = cp.Problem(cp.Minimize(objective), constraints)

        try:
            problem.solve(verbose=verbose, solver=cp.OSQP)

            if problem.status == 'optimal':
                return q_dot.value
            else:
                print(f"Warning: QP solver status: {problem.status}")
                return np.zeros(self.n)
        except Exception as e:
            print(f"QP solver error: {e}")
            return self._solve_fallback()

    def _solve_fallback(self):
        """Fallback solution using least squares."""
        if not self.tasks:
            return np.zeros(self.n)

        # Use highest-weight task
        task = max(self.tasks, key=lambda t: t['weight'])
        J = task['J']
        v_des = task['v_des']

        # Damped least squares
        lambda_damping = 1e-4
        q_dot = np.linalg.solve(
            J.T @ J + lambda_damping * np.eye(self.n),
            J.T @ v_des
        )
        return q_dot

    def verify_solution(self, q_dot):
        """
        Verify that solution satisfies constraints.

        Args:
            q_dot: Solution to verify

        Returns:
            Dictionary of verification results
        """
        results = {
            'tasks': {},
            'equality': {},
            'inequality': {}
        }

        # Check tasks
        for task in self.tasks:
            v_achieved = task['J'] @ q_dot
            error = np.linalg.norm(task['v_des'] - v_achieved)
            results['tasks'][task['name']] = {
                'desired': task['v_des'],
                'achieved': v_achieved,
                'error': error
            }

        # Check equality constraints
        for eq in self.eq_constraints:
            residual = eq['A'] @ q_dot - eq['b']
            satisfied = np.allclose(residual, 0, atol=1e-4)
            results['equality'][eq['name']] = {
                'residual': residual,
                'satisfied': satisfied
            }

        # Check inequality constraints
        for ineq in self.ineq_constraints:
            values = ineq['A'] @ q_dot
            satisfied = np.all(values <= ineq['b'] + 1e-4)
            results['inequality'][ineq['name']] = {
                'values': values,
                'limits': ineq['b'],
                'satisfied': satisfied
            }

        return results


def example_humanoid_control():
    """
    Example: Humanoid robot whole-body control with QP.
    """
    print("\n" + "="*70)
    print("Humanoid Whole-Body QP Control Example")
    print("="*70)

    n_joints = 10  # Simplified humanoid: 5 joints per leg

    controller = WholeBodyQPController(n_joints)

    # Task 1: CoM velocity (high priority)
    J_com = np.random.randn(2, n_joints) * 0.1
    J_com[:, :5] += 0.5  # Left leg
    J_com[:, 5:] += 0.5  # Right leg
    v_com_des = np.array([0.1, 0.0])  # Move forward

    controller.add_task(J_com, v_com_des, weight=100.0, name="CoM")

    # Task 2: Foot position (medium priority)
    J_foot = np.zeros((3, n_joints))
    J_foot[:, :5] = np.random.randn(3, 5) * 0.3
    v_foot_des = np.array([0.0, 0.0, 0.05])  # Lift foot

    controller.add_task(J_foot, v_foot_des, weight=50.0, name="Foot")

    # Task 3: Posture (low priority)
    J_posture = np.eye(n_joints)
    q_nominal = np.array([0.0, 0.1, -0.2, 0.15, -0.3] * 2)
    v_posture_des = 0.2 * q_nominal

    controller.add_task(J_posture, v_posture_des, weight=1.0, name="Posture")

    # Constraint 1: Contact (equality) - right foot stationary
    A_contact = np.zeros((3, n_joints))
    A_contact[:, 5:] = np.random.randn(3, 5) * 0.3
    b_contact = np.zeros(3)

    controller.add_equality_constraint(A_contact, b_contact, name="Contact")

    # Constraint 2: Joint limits (inequality)
    q_dot_min = np.ones(n_joints) * -1.0  # -1 rad/s
    q_dot_max = np.ones(n_joints) * 1.0   # +1 rad/s

    # Constraint 3: CoM stability (inequality)
    # CoM must stay within support polygon
    A_stability = J_com[1:2, :]  # Y-direction
    b_stability = np.array([0.05])  # Max 5cm/s lateral

    controller.add_inequality_constraint(A_stability, b_stability, name="Stability")

    # Solve
    print("\nSolving QP...")
    q_dot = controller.solve(q_dot_min, q_dot_max, verbose=False)

    if q_dot is None:
        print("QP failed to solve!")
        return

    print(f"\nSolution found!")
    print(f"Joint velocities: {q_dot}")
    print(f"Magnitude: {np.linalg.norm(q_dot):.4f} rad/s")

    # Verify solution
    print("\n" + "="*70)
    print("Verification")
    print("="*70)

    results = controller.verify_solution(q_dot)

    print("\nTasks:")
    for name, res in results['tasks'].items():
        print(f"  {name}:")
        print(f"    Desired:  {res['desired']}")
        print(f"    Achieved: {res['achieved']}")
        print(f"    Error:    {res['error']:.6f}")

    print("\nEquality Constraints:")
    for name, res in results['equality'].items():
        status = "✓ SATISFIED" if res['satisfied'] else "✗ VIOLATED"
        print(f"  {name}: {status}")
        print(f"    Residual: {np.linalg.norm(res['residual']):.6f}")

    print("\nInequality Constraints:")
    for name, res in results['inequality'].items():
        status = "✓ SATISFIED" if res['satisfied'] else "✗ VIOLATED"
        print(f"  {name}: {status}")

    # Visualize
    visualize_qp_solution(controller, q_dot, results)

    return controller, q_dot, results


def visualize_qp_solution(controller, q_dot, results):
    """Visualize QP solution."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Joint velocities
    ax1 = axes[0, 0]
    joints = np.arange(len(q_dot))
    ax1.bar(joints, q_dot, color='steelblue')
    ax1.set_xlabel('Joint Index')
    ax1.set_ylabel('Velocity (rad/s)')
    ax1.set_title('Joint Velocities')
    ax1.grid(True, alpha=0.3, axis='y')

    # Task errors
    ax2 = axes[0, 1]
    task_names = list(results['tasks'].keys())
    errors = [results['tasks'][name]['error'] for name in task_names]
    weights = [task['weight'] for task in controller.tasks]

    x = np.arange(len(task_names))
    ax2.bar(x, errors, color='coral')
    ax2.set_xticks(x)
    ax2.set_xticklabels(task_names)
    ax2.set_ylabel('Error Norm')
    ax2.set_title('Task Achievement Errors')
    ax2.grid(True, alpha=0.3, axis='y')

    # Task weights vs errors
    ax3 = axes[1, 0]
    ax3.scatter(weights, errors, s=100, alpha=0.6)
    for i, name in enumerate(task_names):
        ax3.annotate(name, (weights[i], errors[i]),
                    xytext=(5, 5), textcoords='offset points')
    ax3.set_xlabel('Task Weight')
    ax3.set_ylabel('Error Norm')
    ax3.set_title('Weight vs Error')
    ax3.set_xscale('log')
    ax3.grid(True, alpha=0.3)

    # Constraint satisfaction
    ax4 = axes[1, 1]
    constraint_types = ['Equality', 'Inequality']
    satisfied_counts = [
        sum(1 for r in results['equality'].values() if r['satisfied']),
        sum(1 for r in results['inequality'].values() if r['satisfied'])
    ]
    total_counts = [len(results['equality']), len(results['inequality'])]

    x = np.arange(len(constraint_types))
    width = 0.35
    ax4.bar(x - width/2, satisfied_counts, width, label='Satisfied', color='green', alpha=0.7)
    ax4.bar(x + width/2, total_counts, width, label='Total', color='gray', alpha=0.5)
    ax4.set_xticks(x)
    ax4.set_xticklabels(constraint_types)
    ax4.set_ylabel('Count')
    ax4.set_title('Constraint Satisfaction')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 15, Example 2: QP-Based Whole-Body Control")
    print("=" * 70)

    if not CVXPY_AVAILABLE:
        print("\nWarning: cvxpy not installed.")
        print("Install with: pip install cvxpy")
        print("Running with fallback least-squares solver...\n")

    example_humanoid_control()

    print("\n" + "="*70)
    print("QP control complete!")
    print("="*70)


if __name__ == "__main__":
    main()
