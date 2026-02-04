---
chapter_id: "10"
module: "Module 2"
title: "Control Systems"
word_count_target: 2300
word_count_actual: 6023
status: "draft"
code_examples: ["chapter_10_example_01.py", "chapter_10_example_02.py", "chapter_10_example_03.py"]
references: ["astrom2008", "siciliano2009", "ros2_control_docs", "murray1994", "spong2005"]
last_updated: "2026-02-03"
author: "Content Writing Team"
---

# Chapter 10: Control Systems

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand PID control theory and apply practical tuning methods for robotic systems
- Implement trajectory generation using quintic polynomials and spline interpolation
- Apply feedforward and feedback control strategies for improved tracking performance
- Design cascaded control loops with proper bandwidth separation
- Analyze closed-loop stability and performance using classical control theory techniques

## Introduction

Control systems transform high-level plans into low-level motor commands that actuate humanoid robots. While motion planning determines what motions to execute, control systems determine how to execute them accurately, robustly, and efficiently. Effective control is essential—even perfect plans fail without controllers that can track trajectories despite disturbances, modeling errors, and hardware limitations.

The **control hierarchy** in humanoid robotics typically consists of multiple layers. High-level **task control** translates objectives into desired motions (e.g., "walk forward at 0.5 m/s"). **Trajectory generation** converts these motions into time-parameterized reference trajectories specifying positions, velocities, and accelerations. **Tracking control** computes actuator commands (torques or position setpoints) to follow trajectories. **Low-level control** interfaces with motor drivers, implementing current control and safety monitoring.

Classical control theory provides foundational tools for understanding and designing these systems. **PID (Proportional-Integral-Derivative) control**, despite its simplicity, remains ubiquitous in robotics due to ease of implementation, intuitive tuning, and robust performance across a wide range of applications. Modern extensions incorporate feedforward compensation, adaptive gains, and model-based components, but PID forms the core of most robot controllers.

For humanoid robots, control challenges are particularly demanding. Balance requires tight control loops with millisecond latencies. Manipulation tasks demand precise position control against varying loads and contact forces. Walking controllers must coordinate dozens of joints while maintaining dynamic stability. These requirements necessitate understanding both theoretical principles and practical implementation strategies.

This chapter explores control systems for humanoid robotics, progressing from PID fundamentals through trajectory generation, feedforward-feedback architectures, cascaded control loops, and stability analysis. The material emphasizes practical implementation while maintaining theoretical rigor, preparing you to design, tune, and deploy control systems for complex robotic platforms.

## Section 1: PID Fundamentals

**PID control** computes control signals as weighted sums of proportional, integral, and derivative error terms. Given error $e(t) = r(t) - y(t)$ between reference $r(t)$ and measured output $y(t)$, the PID control law is:

$$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

The **proportional term** $K_p e(t)$ provides immediate corrective action proportional to current error. Larger $K_p$ increases responsiveness but risks overshoot and oscillation. The **integral term** $K_i \int e(\tau) d\tau$ accumulates error over time, eliminating steady-state error caused by constant disturbances or model mismatch. However, integral action can cause windup and slow response. The **derivative term** $K_d \dot{e}(t)$ anticipates future error by reacting to error rate of change, providing damping that reduces overshoot. Derivative action amplifies noise, requiring filtering in practice.

**Discrete-time implementation** approximates continuous PID for digital controllers sampling at interval $\Delta t$:

$$u[k] = K_p e[k] + K_i \sum_{i=0}^k e[i] \Delta t + K_d \frac{e[k] - e[k-1]}{\Delta t}$$

The integral term accumulates error samples, and the derivative approximates $\dot{e}$ via finite differences. Low-pass filtering of the derivative term reduces noise sensitivity: $\dot{e}_{filtered} = \alpha \dot{e}_{raw} + (1-\alpha) \dot{e}_{previous}$.

**Anti-windup mechanisms** prevent integral term growth during actuator saturation. When output saturates (motor reaches maximum torque), error continues accumulating even though additional control action is ineffective. This leads to windup—excessive integral term that causes large overshoot when saturation ends. Conditional integration stops updating the integral when output saturates. Back-calculation subtracts excess control signal from the integral term. Integrator clamping limits integral magnitude directly.

**Tuning methods** establish gain values that achieve desired performance. The **Ziegler-Nichols method** provides initial gains from open-loop or closed-loop system responses. For open-loop tuning, apply a step input, measure the response curve's delay time $L$ and time constant $T$, then compute $K_p = 1.2T/L$, $K_i = K_p/(2L)$, $K_d = 0.5K_p L$. For closed-loop tuning, increase $K_p$ until sustained oscillation occurs at period $P_u$, then set $K_p = 0.6 K_u$, $K_i = 1.2K_u/P_u$, $K_d = 0.075K_u P_u$.

**Manual tuning** offers intuitive iterative refinement. Start with $K_i = K_d = 0$ and increase $K_p$ until reasonable tracking with acceptable overshoot. Add derivative gain $K_d$ to reduce overshoot and improve transient response. Finally add integral gain $K_i$ to eliminate steady-state error. Iterate adjustments, observing step responses and disturbance rejection. Manual tuning requires experience but produces controllers well-matched to specific applications.

**Performance metrics** quantify controller quality. **Rise time** measures speed (time to reach 90% of setpoint). **Overshoot** quantifies stability (maximum deviation beyond setpoint). **Settling time** indicates response duration (time to remain within 2% band). **Steady-state error** measures accuracy (persistent deviation from setpoint). These metrics guide tuning trade-offs—faster rise time often increases overshoot; eliminating steady-state error may increase settling time.

### Code Example 1: PID Controller with Tuning Visualization

This implementation demonstrates PID control with interactive tuning.

```python
# chapter_10_example_01.py
# PID controller with tuning visualization
# Run with: python chapter_10_example_01.py
# Expected output: Interactive plots showing PID response for different gain settings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


class PIDController:
    """PID controller with anti-windup and derivative filtering."""

    def __init__(self, kp, ki, kd, dt, output_limits=None, derivative_filter_alpha=0.5):
        """
        Initialize PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            dt: Sample time (seconds)
            output_limits: (min, max) tuple for output saturation
            derivative_filter_alpha: Low-pass filter coefficient for derivative (0-1)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.output_limits = output_limits
        self.derivative_filter_alpha = derivative_filter_alpha

        # State variables
        self.integral = 0.0
        self.previous_error = 0.0
        self.filtered_derivative = 0.0

    def update(self, error):
        """
        Compute control output for given error.

        Args:
            error: Current error (setpoint - measurement)

        Returns:
            control_output: Commanded control signal
        """
        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * self.dt

        # Integral clamping (simple anti-windup)
        if self.output_limits is not None:
            integral_limit = (self.output_limits[1] - self.output_limits[0]) / (2 * self.ki) if self.ki > 0 else 1e6
            self.integral = np.clip(self.integral, -integral_limit, integral_limit)

        i_term = self.ki * self.integral

        # Derivative term with filtering
        derivative = (error - self.previous_error) / self.dt
        self.filtered_derivative = (self.derivative_filter_alpha * derivative +
                                    (1 - self.derivative_filter_alpha) * self.filtered_derivative)
        d_term = self.kd * self.filtered_derivative

        # Compute total output
        output = p_term + i_term + d_term

        # Apply output limits
        if self.output_limits is not None:
            output_saturated = np.clip(output, self.output_limits[0], self.output_limits[1])

            # Back-calculation anti-windup
            if output != output_saturated and self.ki > 0:
                # Compensate integral for saturation
                self.integral -= (output - output_saturated) / self.ki

            output = output_saturated

        # Update state
        self.previous_error = error

        return output

    def reset(self):
        """Reset controller state."""
        self.integral = 0.0
        self.previous_error = 0.0
        self.filtered_derivative = 0.0


class SimpleSystem:
    """Simple first-order system for demonstration."""

    def __init__(self, time_constant=1.0, dt=0.01):
        """
        Initialize system.

        Args:
            time_constant: System time constant (tau)
            dt: Sample time
        """
        self.tau = time_constant
        self.dt = dt
        self.state = 0.0

    def update(self, control_input):
        """
        Update system state given control input.

        Args:
            control_input: Control signal

        Returns:
            output: System output
        """
        # First-order system: dy/dt = (u - y) / tau
        # Discrete approximation: y[k+1] = y[k] + dt/tau * (u[k] - y[k])
        self.state += (self.dt / self.tau) * (control_input - self.state)
        return self.state

    def reset(self):
        """Reset system state."""
        self.state = 0.0


def simulate_pid_response(kp, ki, kd, setpoint=1.0, duration=10.0, dt=0.01):
    """
    Simulate closed-loop PID control.

    Args:
        kp, ki, kd: PID gains
        setpoint: Desired setpoint
        duration: Simulation duration (seconds)
        dt: Sample time (seconds)

    Returns:
        time, output, control, error: Arrays of simulation results
    """
    # Create controller and system
    controller = PIDController(kp, ki, kd, dt, output_limits=(-10, 10))
    system = SimpleSystem(time_constant=1.0, dt=dt)

    # Simulation arrays
    num_steps = int(duration / dt)
    time = np.arange(num_steps) * dt
    output = np.zeros(num_steps)
    control = np.zeros(num_steps)
    error = np.zeros(num_steps)

    # Run simulation
    for i in range(num_steps):
        # Compute error
        error[i] = setpoint - output[i] if i > 0 else setpoint

        # Compute control signal
        control[i] = controller.update(error[i])

        # Update system
        output[i] = system.update(control[i])

    return time, output, control, error


def ziegler_nichols_tuning(ku, pu, method='classic'):
    """
    Compute PID gains using Ziegler-Nichols method.

    Args:
        ku: Ultimate gain (gain at sustained oscillation)
        pu: Ultimate period (oscillation period)
        method: 'classic', 'pessen', 'overshoot', or 'no_overshoot'

    Returns:
        kp, ki, kd: Tuned PID gains
    """
    if method == 'classic':
        kp = 0.6 * ku
        ki = 1.2 * ku / pu
        kd = 0.075 * ku * pu
    elif method == 'pessen':
        kp = 0.7 * ku
        ki = 1.75 * ku / pu
        kd = 0.105 * ku * pu
    elif method == 'overshoot':
        kp = 0.33 * ku
        ki = 0.66 * ku / pu
        kd = 0.11 * ku * pu
    elif method == 'no_overshoot':
        kp = 0.2 * ku
        ki = 0.4 * ku / pu
        kd = 0.067 * ku * pu
    else:
        raise ValueError(f"Unknown method: {method}")

    return kp, ki, kd


def interactive_tuning_demo():
    """Interactive PID tuning demonstration with sliders."""
    # Initial gains
    kp_init = 1.0
    ki_init = 0.5
    kd_init = 0.1

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    plt.subplots_adjust(bottom=0.25)

    # Simulate initial response
    time, output, control, error = simulate_pid_response(kp_init, ki_init, kd_init)

    # Plot initial response
    line_output, = ax1.plot(time, output, 'b-', linewidth=2, label='Output')
    line_setpoint, = ax1.plot(time, np.ones_like(time), 'r--', linewidth=2, label='Setpoint')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Output')
    ax1.set_title('System Response')
    ax1.grid(True)
    ax1.legend()
    ax1.set_ylim(-0.2, 1.5)

    line_control, = ax2.plot(time, control, 'g-', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Control Signal')
    ax2.set_title('Control Signal')
    ax2.grid(True)
    ax2.set_ylim(-5, 5)

    # Create sliders
    ax_kp = plt.axes([0.15, 0.15, 0.7, 0.03])
    ax_ki = plt.axes([0.15, 0.10, 0.7, 0.03])
    ax_kd = plt.axes([0.15, 0.05, 0.7, 0.03])

    slider_kp = Slider(ax_kp, 'Kp', 0.0, 5.0, valinit=kp_init)
    slider_ki = Slider(ax_ki, 'Ki', 0.0, 5.0, valinit=ki_init)
    slider_kd = Slider(ax_kd, 'Kd', 0.0, 2.0, valinit=kd_init)

    def update(val):
        """Update plot when sliders change."""
        kp = slider_kp.val
        ki = slider_ki.val
        kd = slider_kd.val

        time, output, control, error = simulate_pid_response(kp, ki, kd)

        line_output.set_ydata(output)
        line_control.set_ydata(control)

        # Compute performance metrics
        overshoot = (np.max(output) - 1.0) * 100 if np.max(output) > 1.0 else 0.0
        settling_idx = np.where(np.abs(output - 1.0) < 0.02)[0]
        settling_time = time[settling_idx[0]] if len(settling_idx) > 0 else time[-1]
        steady_state_error = np.abs(1.0 - np.mean(output[-100:]))

        ax1.set_title(f'System Response | Overshoot: {overshoot:.1f}% | '
                      f'Settling: {settling_time:.2f}s | SSE: {steady_state_error:.4f}')

        fig.canvas.draw_idle()

    slider_kp.on_changed(update)
    slider_ki.on_changed(update)
    slider_kd.on_changed(update)

    plt.show()


def main():
    """Demonstrate PID control with various configurations."""
    print("=== PID Controller Demonstration ===\n")

    # Test 1: P-only control
    print("Test 1: P-only control (Kp=1.0, Ki=0, Kd=0)")
    time, output, control, error = simulate_pid_response(1.0, 0.0, 0.0)
    print(f"  Steady-state error: {np.abs(1.0 - output[-1]):.4f}")
    print(f"  Max overshoot: {(np.max(output) - 1.0)*100:.1f}%\n")

    # Test 2: PI control
    print("Test 2: PI control (Kp=1.0, Ki=0.5, Kd=0)")
    time, output, control, error = simulate_pid_response(1.0, 0.5, 0.0)
    print(f"  Steady-state error: {np.abs(1.0 - output[-1]):.4f}")
    print(f"  Max overshoot: {(np.max(output) - 1.0)*100:.1f}%\n")

    # Test 3: Full PID control
    print("Test 3: Full PID control (Kp=1.5, Ki=0.5, Kd=0.3)")
    time, output, control, error = simulate_pid_response(1.5, 0.5, 0.3)
    print(f"  Steady-state error: {np.abs(1.0 - output[-1]):.4f}")
    print(f"  Max overshoot: {(np.max(output) - 1.0)*100:.1f}%\n")

    # Test 4: Ziegler-Nichols tuning
    print("Test 4: Ziegler-Nichols tuning")
    ku = 3.0  # Ultimate gain (example)
    pu = 1.5  # Ultimate period (example)
    kp, ki, kd = ziegler_nichols_tuning(ku, pu, method='classic')
    print(f"  Computed gains: Kp={kp:.3f}, Ki={ki:.3f}, Kd={kd:.3f}")
    time, output, control, error = simulate_pid_response(kp, ki, kd)
    print(f"  Steady-state error: {np.abs(1.0 - output[-1]):.4f}")
    print(f"  Max overshoot: {(np.max(output) - 1.0)*100:.1f}%\n")

    # Launch interactive demo
    print("Launching interactive tuning demo...")
    print("Adjust sliders to see real-time PID response changes")
    interactive_tuning_demo()


if __name__ == '__main__':
    main()
```

## Section 2: Trajectory Generation

**Trajectory generation** converts desired motions into smooth, time-parameterized reference signals suitable for controllers to track. Well-designed trajectories respect kinematic and dynamic constraints, minimize jerk (derivative of acceleration), and enable smooth, energy-efficient motion.

**Point-to-point trajectories** connect start and goal configurations through intermediate time instants. The simplest approach uses linear interpolation, but this produces discontinuous velocities at waypoints, causing abrupt actuator commands and vibration. Polynomial trajectories provide smooth motion with continuous derivatives.

**Quintic polynomials** (fifth-order) enable specifying position, velocity, and acceleration at start and goal, producing smooth acceleration profiles. For scalar motion from $q_0$ to $q_f$ in time $T$, the quintic polynomial $q(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5$ satisfies boundary conditions:

$$q(0) = q_0, \quad \dot{q}(0) = v_0, \quad \ddot{q}(0) = a_0$$
$$q(T) = q_f, \quad \dot{q}(T) = v_f, \quad \ddot{q}(T) = a_f$$

Solving this linear system yields coefficients $a_0...a_5$. Typically, initial and final velocities and accelerations are zero for rest-to-rest motion, producing smooth start and smooth stop.

**Spline interpolation** extends polynomial trajectories to multiple waypoints. **Cubic splines** connect waypoints with piecewise cubic polynomials, ensuring continuity of position, velocity, and acceleration across segments. Natural splines set second derivatives to zero at endpoints. Clamped splines specify endpoint derivatives explicitly. Hermite splines interpolate both positions and velocities at waypoints.

**B-splines** provide greater flexibility through basis functions and control points rather than direct waypoint interpolation. B-splines produce smooth curves with local control—moving one control point affects only nearby curve segments. This locality simplifies editing and optimization. Uniform B-splines use equally-spaced knots; non-uniform B-splines (NURBS) allow variable spacing for precise shape control.

**Minimum jerk trajectories** minimize the integral of squared jerk $\int \dddot{q}^2 dt$, producing natural-feeling motions resembling human movement. For scalar motion, the minimum jerk trajectory is a fifth-order polynomial with specific coefficients. Extending to multiple dimensions uses independent scalar trajectories per dimension or coupled optimization considering all dimensions simultaneously.

**Trajectory blending** smooths piecewise trajectories at waypoints. Without blending, robot must decelerate to stop at each waypoint, then accelerate toward the next—inefficient and slow. Blending replaces sharp corners with smooth curves, typically using parabolic or circular arc blends parameterized by blend radius or time. Larger blends improve smoothness but deviate more from nominal waypoints.

### Code Example 2: Quintic Trajectory Generator

This implementation demonstrates smooth trajectory generation.

```python
# chapter_10_example_02.py
# Quintic polynomial trajectory generator
# Run with: python chapter_10_example_02.py
# Expected output: Smooth trajectory plots with continuous derivatives

import numpy as np
import matplotlib.pyplot as plt


class QuinticTrajectory:
    """Quintic polynomial trajectory for smooth motion."""

    def __init__(self, q0, qf, v0=0.0, vf=0.0, a0=0.0, af=0.0, duration=1.0):
        """
        Generate quintic polynomial trajectory.

        Args:
            q0: Initial position
            qf: Final position
            v0: Initial velocity (default 0)
            vf: Final velocity (default 0)
            a0: Initial acceleration (default 0)
            af: Final acceleration (default 0)
            duration: Trajectory duration (seconds)
        """
        self.q0 = q0
        self.qf = qf
        self.v0 = v0
        self.vf = vf
        self.a0 = a0
        self.af = af
        self.T = duration

        # Compute quintic coefficients
        self.coeffs = self._compute_coefficients()

    def _compute_coefficients(self):
        """
        Compute quintic polynomial coefficients.

        Trajectory: q(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5
        """
        # Boundary conditions form linear system: A * coeffs = b
        T = self.T

        # Coefficient matrix for quintic boundary conditions
        A = np.array([
            [1, 0, 0, 0, 0, 0],  # q(0) = q0
            [0, 1, 0, 0, 0, 0],  # v(0) = v0
            [0, 0, 2, 0, 0, 0],  # a(0) = a0
            [1, T, T**2, T**3, T**4, T**5],  # q(T) = qf
            [0, 1, 2*T, 3*T**2, 4*T**3, 5*T**4],  # v(T) = vf
            [0, 0, 2, 6*T, 12*T**2, 20*T**3]  # a(T) = af
        ])

        b = np.array([self.q0, self.v0, self.a0, self.qf, self.vf, self.af])

        # Solve for coefficients
        coeffs = np.linalg.solve(A, b)

        return coeffs

    def position(self, t):
        """Compute position at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return c[0] + c[1]*t + c[2]*t**2 + c[3]*t**3 + c[4]*t**4 + c[5]*t**5

    def velocity(self, t):
        """Compute velocity at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return c[1] + 2*c[2]*t + 3*c[3]*t**2 + 4*c[4]*t**3 + 5*c[5]*t**4

    def acceleration(self, t):
        """Compute acceleration at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return 2*c[2] + 6*c[3]*t + 12*c[4]*t**2 + 20*c[5]*t**3

    def jerk(self, t):
        """Compute jerk at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return 6*c[3] + 24*c[4]*t + 60*c[5]*t**2


def multi_segment_trajectory(waypoints, durations=None):
    """
    Generate multi-segment quintic trajectory through waypoints.

    Args:
        waypoints: List of (position, velocity, acceleration) tuples
        durations: List of segment durations (if None, use equal durations)

    Returns:
        List of QuinticTrajectory segments
    """
    n_segments = len(waypoints) - 1

    if durations is None:
        durations = [1.0] * n_segments

    segments = []
    for i in range(n_segments):
        q0, v0, a0 = waypoints[i]
        qf, vf, af = waypoints[i+1]

        segment = QuinticTrajectory(q0, qf, v0, vf, a0, af, durations[i])
        segments.append(segment)

    return segments


def visualize_trajectory(trajectory, title="Quintic Trajectory"):
    """Visualize trajectory and its derivatives."""
    # Sample trajectory
    t = np.linspace(0, trajectory.T, 200)
    q = np.array([trajectory.position(ti) for ti in t])
    v = np.array([trajectory.velocity(ti) for ti in t])
    a = np.array([trajectory.acceleration(ti) for ti in t])
    j = np.array([trajectory.jerk(ti) for ti in t])

    # Create figure with subplots
    fig, axs = plt.subplots(4, 1, figsize=(10, 10))

    axs[0].plot(t, q, 'b-', linewidth=2)
    axs[0].set_ylabel('Position')
    axs[0].set_title(title)
    axs[0].grid(True)

    axs[1].plot(t, v, 'g-', linewidth=2)
    axs[1].set_ylabel('Velocity')
    axs[1].grid(True)

    axs[2].plot(t, a, 'r-', linewidth=2)
    axs[2].set_ylabel('Acceleration')
    axs[2].grid(True)

    axs[3].plot(t, j, 'm-', linewidth=2)
    axs[3].set_ylabel('Jerk')
    axs[3].set_xlabel('Time (s)')
    axs[3].grid(True)

    plt.tight_layout()
    plt.show()


def compare_trajectory_types():
    """Compare different trajectory generation methods."""
    q0, qf = 0.0, 1.0
    duration = 2.0

    # Generate time vector
    t = np.linspace(0, duration, 200)

    # 1. Linear interpolation (discontinuous velocity)
    q_linear = q0 + (qf - q0) * (t / duration)

    # 2. Cubic polynomial (continuous velocity, discontinuous acceleration)
    # q(t) = a0 + a1*t + a2*t^2 + a3*t^3
    # Boundary: q(0)=q0, q(T)=qf, v(0)=0, v(T)=0
    T = duration
    a0 = q0
    a1 = 0
    a2 = 3 * (qf - q0) / T**2
    a3 = -2 * (qf - q0) / T**3
    q_cubic = a0 + a1*t + a2*t**2 + a3*t**3
    v_cubic = a1 + 2*a2*t + 3*a3*t**2
    a_cubic = 2*a2 + 6*a3*t

    # 3. Quintic polynomial (continuous acceleration)
    traj_quintic = QuinticTrajectory(q0, qf, duration=duration)
    q_quintic = np.array([traj_quintic.position(ti) for ti in t])
    v_quintic = np.array([traj_quintic.velocity(ti) for ti in t])
    a_quintic = np.array([traj_quintic.acceleration(ti) for ti in t])

    # Plot comparison
    fig, axs = plt.subplots(3, 1, figsize=(12, 10))

    axs[0].plot(t, q_linear, 'b--', label='Linear', linewidth=2)
    axs[0].plot(t, q_cubic, 'g--', label='Cubic', linewidth=2)
    axs[0].plot(t, q_quintic, 'r-', label='Quintic', linewidth=2)
    axs[0].set_ylabel('Position')
    axs[0].set_title('Trajectory Comparison')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(t[:-1], np.diff(q_linear)/np.diff(t), 'b--', label='Linear', linewidth=2)
    axs[1].plot(t, v_cubic, 'g--', label='Cubic', linewidth=2)
    axs[1].plot(t, v_quintic, 'r-', label='Quintic', linewidth=2)
    axs[1].set_ylabel('Velocity')
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(t[:-1], np.diff(v_cubic)/np.diff(t), 'g--', label='Cubic', linewidth=2)
    axs[2].plot(t, a_quintic, 'r-', label='Quintic', linewidth=2)
    axs[2].set_ylabel('Acceleration')
    axs[2].set_xlabel('Time (s)')
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()


def main():
    """Demonstrate quintic trajectory generation."""
    print("=== Quintic Trajectory Generation ===\n")

    # Example 1: Simple rest-to-rest motion
    print("Example 1: Rest-to-rest motion (0 to 1 in 2 seconds)")
    traj1 = QuinticTrajectory(q0=0.0, qf=1.0, duration=2.0)
    print(f"  Initial: q={traj1.position(0):.3f}, v={traj1.velocity(0):.3f}, a={traj1.acceleration(0):.3f}")
    print(f"  Final: q={traj1.position(2.0):.3f}, v={traj1.velocity(2.0):.3f}, a={traj1.acceleration(2.0):.3f}")
    print(f"  Max velocity: {np.max([traj1.velocity(t) for t in np.linspace(0, 2, 100)]):.3f}")
    print(f"  Max acceleration: {np.max(np.abs([traj1.acceleration(t) for t in np.linspace(0, 2, 100)])):.3f}\n")

    # Example 2: Motion with non-zero initial velocity
    print("Example 2: Motion with initial velocity (q0=0, v0=0.5, qf=1, vf=0)")
    traj2 = QuinticTrajectory(q0=0.0, qf=1.0, v0=0.5, vf=0.0, duration=2.0)
    visualize_trajectory(traj2, "Quintic with Initial Velocity")

    # Example 3: Multi-segment trajectory
    print("\nExample 3: Multi-segment trajectory through waypoints")
    waypoints = [
        (0.0, 0.0, 0.0),  # (position, velocity, acceleration)
        (0.5, 0.3, 0.0),
        (1.0, 0.0, 0.0),
        (0.5, -0.2, 0.0),
        (0.0, 0.0, 0.0)
    ]
    segments = multi_segment_trajectory(waypoints, durations=[1.0, 1.0, 1.0, 1.0])
    print(f"  Created {len(segments)} trajectory segments")

    # Example 4: Compare trajectory types
    print("\nExample 4: Comparing linear, cubic, and quintic trajectories")
    compare_trajectory_types()


if __name__ == '__main__':
    main()
```

## Section 3: Feedforward and Feedback Control

**Feedforward control** uses models to predict required control inputs, compensating for known disturbances and dynamics before errors occur. **Feedback control** reacts to measured errors, correcting for unmodeled effects and disturbances. Combining feedforward and feedback provides superior performance—feedforward handles predictable dynamics, feedback handles unpredictable disturbances.

For robot manipulators, **gravity compensation** exemplifies feedforward control. Gravity induces joint torques $\tau_g = g(q)$ depending on configuration $q$. A feedforward controller computes $\tau_{ff} = g(q)$ to cancel gravity, enabling the feedback controller to focus on tracking errors rather than fighting gravity. Without feedforward, feedback gains must be large to overcome gravity, leading to poor performance and potential instability.

**Model-based feedforward** extends to full robot dynamics. The equations of motion $\tau = M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q)$ relate joint torques $\tau$ to accelerations $\ddot{q}$, where $M$ is the inertia matrix, $C$ represents Coriolis and centrifugal effects, and $g$ is gravity. Feedforward control computes:

$$\tau_{ff} = M(q)\ddot{q}_d + C(q, \dot{q})\dot{q}_d + g(q)$$

where $\ddot{q}_d, \dot{q}_d$ are desired accelerations and velocities from trajectory generation. This produces the desired motion in the absence of model errors and disturbances.

**Combined feedforward-feedback** control structures add feedback corrections to feedforward commands:

$$\tau = \tau_{ff} + \tau_{fb} = M\ddot{q}_d + C\dot{q}_d + g + K_p(q_d - q) + K_d(\dot{q}_d - \dot{q})$$

The feedforward term $\tau_{ff}$ handles nominal dynamics; the feedback term $K_p e + K_d \dot{e}$ corrects errors. This structure is **computed torque control** or **inverse dynamics control**.

**Robustness** is a critical consideration. Model inaccuracies (errors in $M, C, g$) degrade feedforward performance. If models are significantly wrong, feedforward can worsen rather than improve tracking. Conservative design uses moderate feedforward gains or adaptive feedforward that updates models online based on observed errors.

**Friction compensation** illustrates feedforward complexity. Friction depends nonlinearly on velocity (Coulomb friction, viscous friction, Stribeck effect) and direction (static vs. kinetic). Simple linear viscous models $\tau_f = b\dot{q}$ capture only part of friction behavior. More sophisticated models incorporate Coulomb friction (constant opposing motion) and velocity-dependent effects, significantly improving tracking at low velocities where friction dominates.

## Section 4: Cascaded Control Loops

**Cascaded control** structures multiple nested feedback loops with different bandwidths. The **outer loop** controls slower variables (position), while **inner loops** control faster variables (velocity, current). This hierarchical structure improves performance, enables bandwidth separation, and simplifies tuning.

A typical **position-velocity-torque cascade** for robot joints consists of three layers. The **position controller** (outer loop, 10-100 Hz bandwidth) computes velocity commands from position errors. The **velocity controller** (middle loop, 100-1000 Hz bandwidth) computes torque commands from velocity errors. The **torque controller** (inner loop, 1-10 kHz bandwidth) computes motor currents from torque errors.

**Bandwidth separation** is essential for cascade stability. Each inner loop should be roughly 5-10 times faster than its outer loop. This ensures the inner loop responds quickly relative to outer loop dynamics, allowing the outer loop to treat the inner loop as instantaneous. Insufficient bandwidth separation causes interaction and potential instability.

**Tuning cascaded loops** proceeds from innermost to outermost. First, tune the torque (current) loop with position held constant, achieving fast, stable current tracking. Next, tune the velocity loop with position fixed, treating the torque loop as instantaneous. Finally, tune the position loop with the velocity loop providing fast velocity tracking. This sequential tuning simplifies the process and prevents loop interaction.

**Advantages of cascading** include improved disturbance rejection (inner loops reject high-frequency disturbances before they affect outer loops), simplified tuning (each loop addresses a specific frequency range), and modularity (inner loops can be reused across different robots or tasks).

**Current limiting** in cascaded control provides safety. The torque loop saturates current commands at safe levels, preventing motor overheating or mechanical damage. Position and velocity controllers continue operating, but torque is limited. This graceful degradation enables safe operation even during unexpected events.

### Code Example 3: ROS 2 Joint Trajectory Controller

This example demonstrates trajectory tracking control interface.

```python
# chapter_10_example_03.py
# ROS 2 joint trajectory controller interface
# Run with: ros2 run <package_name> trajectory_controller_demo
# Expected output: Robot executes smooth multi-waypoint trajectory

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import numpy as np


class TrajectoryControllerDemo(Node):
    """Demonstration of ROS 2 joint trajectory controller interface."""

    def __init__(self):
        super().__init__('trajectory_controller_demo')

        # Create action client for joint trajectory controller
        self.action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.get_logger().info('Waiting for trajectory controller action server...')
        self.action_client.wait_for_server()
        self.get_logger().info('Connected to trajectory controller')

        # Joint names (configure for your robot)
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

    def create_trajectory(self, waypoints, durations):
        """
        Create joint trajectory message.

        Args:
            waypoints: List of joint configurations (each is list of joint angles)
            durations: List of time durations to reach each waypoint

        Returns:
            JointTrajectory message
        """
        trajectory = JointTrajectory()
        trajectory.joint_names = self.joint_names

        cumulative_time = 0.0
        for i, (waypoint, duration) in enumerate(zip(waypoints, durations)):
            point = JointTrajectoryPoint()

            # Set positions
            point.positions = waypoint

            # Compute velocities (simple finite difference)
            if i == 0:
                point.velocities = [0.0] * len(waypoint)
            else:
                prev_waypoint = waypoints[i-1]
                prev_duration = durations[i-1]
                point.velocities = [(w - p) / prev_duration
                                   for w, p in zip(waypoint, prev_waypoint)]

            # Set accelerations (simplified - should use proper trajectory generation)
            point.accelerations = [0.0] * len(waypoint)

            # Set timestamp
            cumulative_time += duration
            point.time_from_start = Duration(
                sec=int(cumulative_time),
                nanosec=int((cumulative_time % 1) * 1e9)
            )

            trajectory.points.append(point)

        return trajectory

    def send_trajectory(self, trajectory):
        """
        Send trajectory to controller and wait for execution.

        Args:
            trajectory: JointTrajectory message

        Returns:
            Result of trajectory execution
        """
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory

        self.get_logger().info(f'Sending trajectory with {len(trajectory.points)} waypoints')

        # Send goal
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Trajectory goal rejected')
            return None

        self.get_logger().info('Trajectory goal accepted, executing...')

        # Wait for result
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        self.get_logger().info(f'Trajectory execution completed with error code: {result.error_code}')

        return result

    def feedback_callback(self, feedback_msg):
        """Callback for trajectory execution feedback."""
        feedback = feedback_msg.feedback
        # feedback.actual contains current joint positions
        # feedback.desired contains current desired positions
        # feedback.error contains current tracking error

        # Log progress periodically
        # self.get_logger().info(f'Trajectory progress: {feedback.time_from_start}')

    def execute_circle_trajectory(self, center, radius, num_points=20):
        """
        Generate and execute circular trajectory in joint space.

        Args:
            center: Center configuration (list of joint angles)
            radius: Radius of circular motion in joint space
            num_points: Number of waypoints on circle
        """
        waypoints = []
        durations = []

        for i in range(num_points + 1):  # +1 to close the circle
            angle = 2 * np.pi * i / num_points

            # Generate circular motion in first two joints
            waypoint = center.copy()
            waypoint[0] += radius * np.cos(angle)
            waypoint[1] += radius * np.sin(angle)

            waypoints.append(waypoint)
            durations.append(0.5)  # 0.5 seconds between waypoints

        trajectory = self.create_trajectory(waypoints, durations)
        result = self.send_trajectory(trajectory)

        return result

    def execute_demo_sequence(self):
        """Execute sequence of demonstration trajectories."""
        self.get_logger().info('=== Starting Trajectory Demo Sequence ===')

        # Demo 1: Move to home position
        self.get_logger().info('\n--- Demo 1: Move to home position ---')
        home_position = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
        waypoints = [home_position]
        durations = [3.0]
        trajectory = self.create_trajectory(waypoints, durations)
        self.send_trajectory(trajectory)

        # Demo 2: Multi-waypoint trajectory
        self.get_logger().info('\n--- Demo 2: Multi-waypoint trajectory ---')
        waypoints = [
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.0],
            [0.5, -1.0, 0.5, -2.0, 0.0, 0.0],
            [1.0, -0.5, 1.0, -1.5, 0.5, 0.0],
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]  # Back to home
        ]
        durations = [2.0, 2.0, 2.0, 2.0]
        trajectory = self.create_trajectory(waypoints, durations)
        self.send_trajectory(trajectory)

        # Demo 3: Circular motion
        self.get_logger().info('\n--- Demo 3: Circular motion in joint space ---')
        center = [0.0, -1.0, 0.0, -1.57, 0.0, 0.0]
        self.execute_circle_trajectory(center, radius=0.3, num_points=20)

        self.get_logger().info('\n=== Demo Sequence Complete ===')


def main(args=None):
    """Main function to run trajectory controller demo."""
    rclpy.init(args=args)

    demo = TrajectoryControllerDemo()

    try:
        demo.execute_demo_sequence()
    except KeyboardInterrupt:
        pass
    finally:
        demo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Section 5: Stability Analysis

**Stability** determines whether closed-loop systems remain bounded under perturbations or diverge uncontrollably. Unstable controllers cause oscillations, noise amplification, or complete failure. Stability analysis provides mathematical tools to guarantee safe, predictable behavior.

**Linearization** approximates nonlinear systems around operating points. The nonlinear system $\dot{x} = f(x, u)$ is linearized as $\Delta \dot{x} = A \Delta x + B \Delta u$ where $A = \frac{\partial f}{\partial x}|_{x_0, u_0}$ and $B = \frac{\partial f}{\partial u}|_{x_0, u_0}$. Linear analysis tools then apply to the linearized system, providing local stability guarantees.

**Eigenvalue analysis** examines system stability through the characteristic equation $det(sI - A) = 0$. The system is **asymptotically stable** if all eigenvalues have negative real parts (lie in the left half of the complex plane). Eigenvalues with positive real parts indicate instability. Eigenvalues on the imaginary axis indicate marginal stability with sustained oscillations.

**Routh-Hurwitz criterion** tests stability without computing eigenvalues directly. For a characteristic polynomial $a_n s^n + a_{n-1} s^{n-1} + ... + a_1 s + a_0 = 0$, construct the Routh array and examine the first column. All elements must be positive for stability. Sign changes indicate unstable poles.

**Bode plots** visualize frequency response, plotting magnitude and phase versus frequency. The **gain margin** is the additional gain before instability (measured at phase crossover frequency where phase is -180°). The **phase margin** is the additional phase lag before instability (measured at gain crossover frequency where gain is 0 dB). Typical design targets: gain margin ≥ 6 dB, phase margin ≥ 30-60°.

**Nyquist criterion** provides graphical stability assessment. Plot the open-loop frequency response $G(j\omega)$ in the complex plane. The closed-loop system is stable if the Nyquist plot encircles the -1 point counter-clockwise a number of times equal to the number of open-loop unstable poles. This powerful tool handles systems with delays and right-half-plane poles.

**Passivity-based control** ensures stability through energy considerations. A system is **passive** if energy flow into the system is non-negative: $\int_0^T u^T(t) y(t) dt \geq 0$. Interconnecting passive systems preserves stability—a fundamental result enabling modular controller design. Passivity-based approaches are particularly valuable for complex humanoid robots where complete dynamic models are unavailable.

## Key Concepts Summary

- **PID Control**: Proportional-Integral-Derivative feedback providing baseline control performance with intuitive tuning
- **Anti-Windup**: Mechanisms preventing integral term saturation during actuator limits
- **Quintic Trajectories**: Fifth-order polynomials enabling smooth motion with continuous acceleration
- **Spline Interpolation**: Piecewise polynomial trajectories through multiple waypoints with continuity constraints
- **Feedforward Control**: Model-based compensation for predictable dynamics (gravity, inertia)
- **Cascaded Control**: Hierarchical nested loops with bandwidth separation for improved performance
- **Trajectory Tracking**: Following time-parameterized reference signals with feedback correction
- **Stability Analysis**: Mathematical tools (eigenvalues, Bode, Nyquist) guaranteeing safe closed-loop behavior

## References

[1] Åström, K. J., & Murray, R. M. (2008). *Feedback Systems: An Introduction for Scientists and Engineers*. Princeton University Press. http://www.cds.caltech.edu/~murray/amwiki

[2] Siciliano, B., Sciavicco, L., Villani, L., & Oriolo, G. (2009). *Robotics: Modelling, Planning and Control*. Springer. https://doi.org/10.1007/978-1-84628-642-1

[3] ROS 2 Control Working Group. (2023). *ros2_control Documentation*. Retrieved from https://control.ros.org/

[4] Murray, R. M., Li, Z., & Sastry, S. S. (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press.

[5] Spong, M. W., Hutchinson, S., & Vidyasagar, M. (2005). *Robot Modeling and Control*. John Wiley & Sons.

## Further Reading

- Modern Control Engineering (Ogata) - comprehensive control theory textbook
- ROS 2 Control Tutorials: https://control.ros.org/master/doc/getting_started/getting_started.html
- MoveIt! Servo for real-time control: https://moveit.picknik.ai/main/doc/examples/realtime_servo/realtime_servo_tutorial.html
- Model Predictive Control for Robotics (survey paper)

## Exercises

1. **PID Tuning Exploration**: Implement a PID controller for a simulated 1-DOF system (mass-spring-damper or DC motor). Systematically vary each gain (Kp, Ki, Kd) and observe effects on step response metrics (rise time, overshoot, settling time, steady-state error). Create a 3D visualization showing how performance metrics vary with gain combinations. Compare manual tuning results with Ziegler-Nichols computed gains.

2. **Trajectory Generation Library**: Implement a trajectory generation library supporting: quintic polynomials, cubic splines, B-splines, and minimum jerk trajectories. For a 2-DOF planar arm, generate trajectories through five waypoints using each method. Compare: smoothness (integrated squared jerk), execution time (assuming velocity/acceleration limits), and computational cost. Visualize resulting end-effector paths and joint profiles.

3. **Gravity Compensation**: Simulate a 2-link planar arm under gravity. Implement three controllers: (a) pure PID feedback, (b) gravity feedforward + PID feedback, (c) full inverse dynamics + PID feedback. Command the arm to track a figure-eight trajectory. Compare tracking errors, control efforts (integrated squared torque), and robustness to 20% model errors. Quantify feedforward benefit.

4. **Cascaded Control Implementation**: Implement a three-layer cascade (position→velocity→torque) for a simulated robot joint with realistic dynamics (inertia, friction, torque limits). Tune each loop sequentially. Introduce step disturbances and measure: disturbance rejection bandwidth, steady-state error, and control effort. Compare with single-loop position control. Demonstrate bandwidth separation principle by plotting closed-loop frequency responses.

5. **Stability Analysis**: For a PID-controlled second-order system (e.g., mass-spring-damper with damping ratio $\zeta = 0.3$ and natural frequency $\omega_n = 10$ rad/s), derive the closed-loop characteristic equation. Compute stability boundaries in (Kp, Kd) space using Routh-Hurwitz criterion (with Ki=0 for simplicity). Plot the stable region. For three points (one stable, one marginally stable, one unstable), generate Bode plots and verify gain/phase margins match analytical predictions.

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: Chapter covers control systems from PID fundamentals through advanced topics. Emphasizes practical implementation while maintaining theoretical rigor. Code examples demonstrate real-world ROS 2 integration and industry-standard patterns.
