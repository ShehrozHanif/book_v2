/**
 * Motor Control in C++
 *
 * This example demonstrates low-level motor control including:
 * - PWM generation for speed control
 * - Current sensing and limiting
 * - PID feedback controller for position/velocity
 * - Thermal monitoring and protection
 *
 * Compatible with: C++17, Linux/Ubuntu 22.04
 * Hardware: Assumes motor driver with PWM input and current/temp sensors
 *
 * Compilation:
 *   g++ -std=c++17 -o motor_control chapter_05_example_01.cpp -lpthread
 *
 * Usage:
 *   sudo ./motor_control
 *
 * Educational Purpose:
 * - Shows real-time control loop implementation
 * - Demonstrates safety features (current/thermal limiting)
 * - Illustrates PID controller design
 * - Provides foundation for actuator control in humanoid robots
 */

#include <iostream>
#include <cmath>
#include <chrono>
#include <thread>
#include <atomic>
#include <fstream>
#include <vector>
#include <iomanip>

/**
 * PID Controller
 *
 * Implements discrete-time PID control:
 * u(t) = Kp*e(t) + Ki*∫e(τ)dτ + Kd*de(t)/dt
 */
class PIDController {
public:
    PIDController(double kp, double ki, double kd, double dt,
                  double output_min = -100.0, double output_max = 100.0)
        : kp_(kp), ki_(ki), kd_(kd), dt_(dt),
          output_min_(output_min), output_max_(output_max),
          integral_(0.0), prev_error_(0.0) {}

    /**
     * Compute control output
     *
     * @param setpoint Desired value
     * @param measurement Current value
     * @return Control output
     */
    double compute(double setpoint, double measurement) {
        // Error
        double error = setpoint - measurement;

        // Integral term with anti-windup
        integral_ += error * dt_;

        // Clamp integral to prevent windup
        double max_integral = output_max_ / (ki_ + 1e-6);
        integral_ = std::clamp(integral_, -max_integral, max_integral);

        // Derivative term
        double derivative = (error - prev_error_) / dt_;

        // PID output
        double output = kp_ * error + ki_ * integral_ + kd_ * derivative;

        // Clamp output
        output = std::clamp(output, output_min_, output_max_);

        prev_error_ = error;

        return output;
    }

    /**
     * Reset controller state
     */
    void reset() {
        integral_ = 0.0;
        prev_error_ = 0.0;
    }

    /**
     * Update gains
     */
    void setGains(double kp, double ki, double kd) {
        kp_ = kp;
        ki_ = ki;
        kd_ = kd;
    }

private:
    double kp_, ki_, kd_;
    double dt_;
    double output_min_, output_max_;
    double integral_;
    double prev_error_;
};

/**
 * Motor Controller
 *
 * Manages motor operation with safety features
 */
class MotorController {
public:
    MotorController(double control_rate_hz = 100.0,
                   double max_current = 10.0,
                   double max_temperature = 80.0)
        : control_rate_hz_(control_rate_hz),
          dt_(1.0 / control_rate_hz),
          max_current_(max_current),
          max_temperature_(max_temperature),
          pid_(2.0, 0.5, 0.1, dt_, -100.0, 100.0),  // Kp, Ki, Kd
          running_(false),
          current_position_(0.0),
          current_velocity_(0.0),
          current_current_(0.0),
          temperature_(25.0),
          pwm_duty_cycle_(0.0),
          emergency_stop_(false) {}

    /**
     * Start control loop
     */
    void start() {
        running_ = true;
        control_thread_ = std::thread(&MotorController::controlLoop, this);
        std::cout << "Motor controller started at " << control_rate_hz_ << " Hz\n";
    }

    /**
     * Stop control loop
     */
    void stop() {
        running_ = false;
        if (control_thread_.joinable()) {
            control_thread_.join();
        }
        std::cout << "Motor controller stopped\n";
    }

    /**
     * Set position setpoint
     */
    void setPositionSetpoint(double position) {
        target_position_ = position;
        control_mode_ = ControlMode::POSITION;
    }

    /**
     * Set velocity setpoint
     */
    void setVelocitySetpoint(double velocity) {
        target_velocity_ = velocity;
        control_mode_ = ControlMode::VELOCITY;
    }

    /**
     * Emergency stop
     */
    void emergencyStop() {
        emergency_stop_ = true;
        pwm_duty_cycle_ = 0.0;
        std::cerr << "EMERGENCY STOP ACTIVATED\n";
    }

    /**
     * Get current state
     */
    void getState(double& position, double& velocity, double& current, double& temp) const {
        position = current_position_;
        velocity = current_velocity_;
        current = current_current_;
        temp = temperature_;
    }

    /**
     * Print status
     */
    void printStatus() const {
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Position: " << std::setw(8) << current_position_ << " rad | "
                  << "Velocity: " << std::setw(8) << current_velocity_ << " rad/s | "
                  << "Current: " << std::setw(6) << current_current_ << " A | "
                  << "Temp: " << std::setw(6) << temperature_ << " °C | "
                  << "PWM: " << std::setw(6) << pwm_duty_cycle_ << " %\n";
    }

private:
    enum class ControlMode { POSITION, VELOCITY, TORQUE };

    /**
     * Main control loop
     */
    void controlLoop() {
        auto next_tick = std::chrono::steady_clock::now();

        while (running_) {
            // Read sensors
            readSensors();

            // Check safety limits
            if (!checkSafety()) {
                emergencyStop();
                continue;
            }

            // Compute control output
            double control_output = 0.0;

            if (!emergency_stop_) {
                if (control_mode_ == ControlMode::POSITION) {
                    control_output = pid_.compute(target_position_, current_position_);
                } else if (control_mode_ == ControlMode::VELOCITY) {
                    control_output = pid_.compute(target_velocity_, current_velocity_);
                }
            }

            // Current limiting
            control_output = applyCurrentLimit(control_output);

            // Set PWM
            setPWM(control_output);

            // Update motor physics (simulation)
            updateMotorPhysics();

            // Sleep until next control cycle
            next_tick += std::chrono::microseconds(static_cast<long>(dt_ * 1e6));
            std::this_thread::sleep_until(next_tick);
        }
    }

    /**
     * Read sensor values (simulated)
     */
    void readSensors() {
        // In real implementation, read from hardware
        // Here we simulate sensor readings from physics model

        // Add sensor noise
        current_position_ += (rand() % 100 - 50) * 0.0001;
        current_velocity_ += (rand() % 100 - 50) * 0.001;
        current_current_ += (rand() % 100 - 50) * 0.01;

        // Temperature increases with current squared (I²R losses)
        double heat_generation = 0.1 * current_current_ * current_current_;
        double heat_dissipation = 0.05 * (temperature_ - 25.0);  // Cooling
        temperature_ += (heat_generation - heat_dissipation) * dt_;
    }

    /**
     * Check safety limits
     */
    bool checkSafety() {
        if (std::abs(current_current_) > max_current_) {
            std::cerr << "WARNING: Current limit exceeded: " << current_current_ << " A\n";
            return false;
        }

        if (temperature_ > max_temperature_) {
            std::cerr << "WARNING: Temperature limit exceeded: " << temperature_ << " °C\n";
            return false;
        }

        return true;
    }

    /**
     * Apply current limiting
     */
    double applyCurrentLimit(double control_output) {
        // Estimate current from control output (simplified model)
        double estimated_current = std::abs(control_output) * 0.1;

        if (estimated_current > max_current_) {
            // Scale down control output
            double scale = max_current_ / estimated_current;
            control_output *= scale;
        }

        return control_output;
    }

    /**
     * Set PWM duty cycle
     */
    void setPWM(double control_output) {
        pwm_duty_cycle_ = std::clamp(control_output, -100.0, 100.0);

        // In real implementation, write to hardware PWM generator
        // e.g., write to /sys/class/pwm/pwmchip0/pwm0/duty_cycle
    }

    /**
     * Update simulated motor physics
     */
    void updateMotorPhysics() {
        // Simple motor model:
        // τ = Kt * I
        // J * α = τ - B * ω - τ_load

        const double Kt = 0.1;      // Torque constant (N·m/A)
        const double Ke = 0.1;      // Back-EMF constant (V·s/rad)
        const double R = 2.0;       // Armature resistance (Ω)
        const double J = 0.001;     // Rotor inertia (kg·m²)
        const double B = 0.01;      // Viscous friction (N·m·s/rad)

        // Voltage from PWM (12V max)
        double voltage = (pwm_duty_cycle_ / 100.0) * 12.0;

        // Current: I = (V - Ke*ω) / R
        double back_emf = Ke * current_velocity_;
        current_current_ = (voltage - back_emf) / R;

        // Torque
        double torque = Kt * current_current_;

        // Angular acceleration: α = (τ - B*ω) / J
        double angular_accel = (torque - B * current_velocity_) / J;

        // Integrate to get velocity and position
        current_velocity_ += angular_accel * dt_;
        current_position_ += current_velocity_ * dt_;
    }

    // Configuration
    double control_rate_hz_;
    double dt_;
    double max_current_;
    double max_temperature_;

    // Controller
    PIDController pid_;
    ControlMode control_mode_;
    double target_position_;
    double target_velocity_;

    // State
    std::atomic<bool> running_;
    std::atomic<bool> emergency_stop_;
    double current_position_;
    double current_velocity_;
    double current_current_;
    double temperature_;
    double pwm_duty_cycle_;

    // Thread
    std::thread control_thread_;
};

/**
 * Main function demonstrating motor control
 */
int main() {
    std::cout << "========================================\n";
    std::cout << "MOTOR CONTROL DEMO\n";
    std::cout << "Chapter 5 Example: PWM Control with PID\n";
    std::cout << "========================================\n\n";

    // Create motor controller
    MotorController motor(100.0, 10.0, 80.0);  // 100 Hz, 10A max, 80°C max

    // Start controller
    motor.start();

    // Test 1: Position control
    std::cout << "\nTest 1: Position Control to 2.0 rad\n";
    std::cout << "------------------------------------\n";
    motor.setPositionSetpoint(2.0);

    for (int i = 0; i < 50; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        motor.printStatus();
    }

    // Test 2: Velocity control
    std::cout << "\nTest 2: Velocity Control to 5.0 rad/s\n";
    std::cout << "--------------------------------------\n";
    motor.setVelocitySetpoint(5.0);

    for (int i = 0; i < 50; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        motor.printStatus();
    }

    // Test 3: Return to zero
    std::cout << "\nTest 3: Return to Zero Position\n";
    std::cout << "--------------------------------\n";
    motor.setPositionSetpoint(0.0);

    for (int i = 0; i < 50; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        motor.printStatus();
    }

    // Stop controller
    motor.stop();

    std::cout << "\n========================================\n";
    std::cout << "Motor control demo complete\n";
    std::cout << "========================================\n";

    return 0;
}

/**
 * Expected Output:
 * ========================================
 * MOTOR CONTROL DEMO
 * Chapter 5 Example: PWM Control with PID
 * ========================================
 *
 * Motor controller started at 100 Hz
 *
 * Test 1: Position Control to 2.0 rad
 * ------------------------------------
 * Position:    0.123 rad | Velocity:    1.234 rad/s | Current:  2.456 A | Temp: 25.100 °C | PWM: 45.678 %
 * Position:    0.456 rad | Velocity:    1.567 rad/s | Current:  2.789 A | Temp: 25.234 °C | PWM: 43.210 %
 * ...
 * Position:    1.987 rad | Velocity:    0.123 rad/s | Current:  0.234 A | Temp: 27.890 °C | PWM:  5.678 %
 *
 * Test 2: Velocity Control to 5.0 rad/s
 * --------------------------------------
 * ...
 *
 * Test 3: Return to Zero Position
 * --------------------------------
 * ...
 *
 * Motor controller stopped
 * ========================================
 * Motor control demo complete
 * ========================================
 *
 * CMakeLists.txt Integration:
 * ---------------------------
 * add_executable(motor_control chapter_05_example_01.cpp)
 * target_compile_features(motor_control PRIVATE cxx_std_17)
 * target_link_libraries(motor_control pthread)
 */
