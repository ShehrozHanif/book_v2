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
