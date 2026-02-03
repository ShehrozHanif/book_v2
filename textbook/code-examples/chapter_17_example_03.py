#!/usr/bin/env python3
"""
Chapter 17, Example 3: Common Bug Examples and Fixes

This example demonstrates:
1. Singularity handling in kinematics
2. Frame transformation errors
3. Synchronization issues in multi-threading
4. Common pitfalls and solutions

Dependencies:
    pip install numpy

Expected Output:
    - Bug demonstrations
    - Fix implementations
    - Best practices
    - Testing strategies

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
from numpy.linalg import LinAlgError
import warnings


class BugDemo:
    """Common robotics bugs and their fixes."""
    
    @staticmethod
    def bug_1_singularity_naive():
        """BUG: Not handling kinematic singularities."""
        print("\n" + "="*70)
        print("Bug 1: Kinematic Singularity (Naive Implementation)")
        print("="*70)
        
        J = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0]  # Singular!
        ])
        
        v_desired = np.array([0.1, 0.1, 0.1])
        
        try:
            q_dot = np.linalg.solve(J, v_desired)
            print(f"Result: {q_dot}")
        except LinAlgError as e:
            print(f"ERROR: {e}")
            print("This crashes when Jacobian is singular!")
    
    @staticmethod
    def fix_1_singularity():
        """FIX: Use damped least squares."""
        print("\n" + "="*70)
        print("Fix 1: Damped Least Squares")
        print("="*70)
        
        J = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0]  # Singular!
        ])
        
        v_desired = np.array([0.1, 0.1, 0.1])
        
        # Damped least squares
        lambda_damping = 0.01
        q_dot = J.T @ np.linalg.solve(
            J @ J.T + lambda_damping**2 * np.eye(3),
            v_desired
        )
        
        print(f"Result: {q_dot}")
        print(f"Achieved velocity: {J @ q_dot}")
        print("Solution found even with singular Jacobian!")
    
    @staticmethod
    def bug_2_frame_mismatch():
        """BUG: Mixing reference frames."""
        print("\n" + "="*70)
        print("Bug 2: Reference Frame Mismatch")
        print("="*70)
        
        # Position in world frame
        p_world = np.array([1.0, 0.5, 0.3])
        
        # Rotation from world to robot base (90° around Z)
        theta = np.pi / 2
        R_world_to_base = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])
        
        # WRONG: Directly using world coordinates
        print(f"World position: {p_world}")
        print("ERROR: Using world frame directly in robot base frame!")
        
        # CORRECT: Transform to robot base frame
        p_base = R_world_to_base.T @ p_world
        print(f"Base frame position (correct): {p_base}")
    
    @staticmethod
    def bug_3_angle_wrapping():
        """BUG: Not wrapping angles properly."""
        print("\n" + "="*70)
        print("Bug 3: Angle Wrapping")
        print("="*70)
        
        # Joint angle near 2π
        current = 6.2
        target = 0.1
        
        # WRONG: Direct subtraction
        error_wrong = target - current
        print(f"Current: {current:.2f} rad, Target: {target:.2f} rad")
        print(f"Error (wrong): {error_wrong:.2f} rad")
        print("This gives a large error instead of small one!")
        
        # CORRECT: Wrap to [-π, π]
        error_correct = np.arctan2(np.sin(target - current), 
                                   np.cos(target - current))
        print(f"Error (correct): {error_correct:.2f} rad")
    
    @staticmethod
    def bug_4_numerical_instability():
        """BUG: Numerical instability in integration."""
        print("\n" + "="*70)
        print("Bug 4: Numerical Instability")
        print("="*70)
        
        # WRONG: Explicit Euler with large dt
        dt_large = 0.1
        k = 10.0  # Stiffness
        x = 1.0
        v = 0.0
        
        print("Explicit Euler with large dt:")
        for i in range(5):
            a = -k * x
            v += a * dt_large
            x += v * dt_large
            print(f"  Step {i}: x={x:.4f}, v={v:.4f}")
        print("Unstable! Explodes due to large dt")
        
        # CORRECT: Use smaller dt or implicit method
        dt_small = 0.01
        x = 1.0
        v = 0.0
        
        print("\nExplicit Euler with small dt:")
        for i in range(50):
            a = -k * x
            v += a * dt_small
            x += v * dt_small
            if i % 10 == 0:
                print(f"  Step {i}: x={x:.4f}, v={v:.4f}")
        print("Stable with appropriate dt!")
    
    @staticmethod
    def bug_5_race_condition():
        """BUG: Race condition in multi-threaded control."""
        print("\n" + "="*70)
        print("Bug 5: Shared State Without Locking")
        print("="*70)
        
        print("WRONG: Accessing shared state without synchronization")
        print("  Thread 1: state.position = sensor.read()")
        print("  Thread 2: controller.compute(state.position)")
        print("  -> Thread 2 may read partially updated state!")
        
        print("\nCORRECT: Use locks or atomic operations")
        print("  lock.acquire()")
        print("  state.position = sensor.read()")
        print("  lock.release()")
        print("  -> Ensures consistent state")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 17, Example 3: Common Bugs and Fixes")
    print("=" * 70)
    
    demo = BugDemo()
    
    # Demonstrate bugs and fixes
    demo.bug_1_singularity_naive()
    demo.fix_1_singularity()
    demo.bug_2_frame_mismatch()
    demo.bug_3_angle_wrapping()
    demo.bug_4_numerical_instability()
    demo.bug_5_race_condition()
    
    print("\n" + "="*70)
    print("Key Takeaways:")
    print("="*70)
    print("1. Always check for singularities (use damped least squares)")
    print("2. Be explicit about reference frames")
    print("3. Wrap angles to [-π, π] for error computation")
    print("4. Choose appropriate integration timestep")
    print("5. Synchronize access to shared state")
    print("="*70)


if __name__ == "__main__":
    main()
