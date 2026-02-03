/**
 * Chapter 14, Example 3: Force Control Implementation
 *
 * This example demonstrates:
 * 1. Hybrid position-force control law
 * 2. Impedance control for compliant interaction
 * 3. Real-time force/torque sensor processing
 * 4. Contact force regulation
 *
 * Compilation:
 *     g++ -std=c++17 -O3 -o chapter_14_example_03 chapter_14_example_03.cpp
 *
 * Expected Output:
 *     - Force tracking performance
 *     - Impedance control behavior
 *     - Real-time control loop timing
 *
 * Platform: Ubuntu 22.04, GCC 11+
 * Author: Physical AI & Humanoid Robotics Textbook
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <iomanip>
#include <algorithm>

/**
 * 3D vector utilities
 */
struct Vec3 {
    double x, y, z;

    Vec3() : x(0), y(0), z(0) {}
    Vec3(double x_, double y_, double z_) : x(x_), y(y_), z(z_) {}

    Vec3 operator+(const Vec3& other) const {
        return Vec3(x + other.x, y + other.y, z + other.z);
    }

    Vec3 operator-(const Vec3& other) const {
        return Vec3(x - other.x, y - other.y, z - other.z);
    }

    Vec3 operator*(double scalar) const {
        return Vec3(x * scalar, y * scalar, z * scalar);
    }

    double norm() const {
        return std::sqrt(x*x + y*y + z*z);
    }

    void print(const std::string& name = "") const {
        if (!name.empty()) {
            std::cout << name << ": ";
        }
        std::cout << std::fixed << std::setprecision(4)
                  << "[" << x << ", " << y << ", " << z << "]";
    }
};

/**
 * Hybrid Position-Force Controller
 *
 * Implements selection matrix approach for hybrid control.
 * S: position control directions
 * I-S: force control directions
 */
class HybridController {
private:
    // Control gains
    double kp_pos;   // Position stiffness
    double kd_pos;   // Position damping
    double kp_force; // Force proportional gain
    double ki_force; // Force integral gain

    // Force error integral
    Vec3 force_error_integral;

    // Selection matrix (diagonal for simplicity)
    // 1 = position control, 0 = force control
    bool selection[3];

public:
    HybridController(double kp_p = 1000.0, double kd_p = 50.0,
                    double kp_f = 0.5, double ki_f = 0.1)
        : kp_pos(kp_p), kd_pos(kd_p), kp_force(kp_f), ki_force(ki_f),
          force_error_integral(0, 0, 0)
    {
        // Default: position control in X and Y, force control in Z
        selection[0] = true;  // X: position
        selection[1] = true;  // Y: position
        selection[2] = false; // Z: force
    }

    void set_selection(bool x, bool y, bool z) {
        selection[0] = x;
        selection[1] = y;
        selection[2] = z;
    }

    Vec3 compute_control(const Vec3& pos_desired, const Vec3& pos_actual,
                         const Vec3& vel_actual, const Vec3& force_desired,
                         const Vec3& force_actual, double dt)
    {
        Vec3 control_output;

        // Position error
        Vec3 pos_error = pos_desired - pos_actual;

        // Force error
        Vec3 force_error = force_desired - force_actual;

        // Integrate force error
        force_error_integral.x += force_error.x * dt;
        force_error_integral.y += force_error.y * dt;
        force_error_integral.z += force_error.z * dt;

        // Anti-windup
        const double max_integral = 10.0;
        force_error_integral.x = std::clamp(force_error_integral.x,
                                            -max_integral, max_integral);
        force_error_integral.y = std::clamp(force_error_integral.y,
                                            -max_integral, max_integral);
        force_error_integral.z = std::clamp(force_error_integral.z,
                                            -max_integral, max_integral);

        // Compute control for each axis
        double pos_ctrl[3], force_ctrl[3];

        // X-axis
        pos_ctrl[0] = kp_pos * pos_error.x - kd_pos * vel_actual.x;
        force_ctrl[0] = kp_force * force_error.x + ki_force * force_error_integral.x;

        // Y-axis
        pos_ctrl[1] = kp_pos * pos_error.y - kd_pos * vel_actual.y;
        force_ctrl[1] = kp_force * force_error.y + ki_force * force_error_integral.y;

        // Z-axis
        pos_ctrl[2] = kp_pos * pos_error.z - kd_pos * vel_actual.z;
        force_ctrl[2] = kp_force * force_error.z + ki_force * force_error_integral.z;

        // Apply selection matrix
        control_output.x = selection[0] ? pos_ctrl[0] : force_ctrl[0];
        control_output.y = selection[1] ? pos_ctrl[1] : force_ctrl[1];
        control_output.z = selection[2] ? pos_ctrl[2] : force_ctrl[2];

        return control_output;
    }

    void reset_integral() {
        force_error_integral = Vec3(0, 0, 0);
    }
};

/**
 * Impedance Controller
 *
 * Implements: M*ddx + B*dx + K*x = F_ext
 * Generates compliant motion in response to external forces.
 */
class ImpedanceController {
private:
    // Impedance parameters
    double mass;        // Virtual mass (kg)
    double damping;     // Damping coefficient (N·s/m)
    double stiffness;   // Stiffness (N/m)

    // State
    Vec3 velocity;
    Vec3 position;

public:
    ImpedanceController(double m = 1.0, double b = 20.0, double k = 100.0)
        : mass(m), damping(b), stiffness(k),
          velocity(0, 0, 0), position(0, 0, 0)
    {}

    Vec3 compute_motion(const Vec3& pos_desired, const Vec3& force_external,
                       double dt)
    {
        // Position error
        Vec3 pos_error = pos_desired - position;

        // Impedance dynamics: M*a = -B*v - K*x + F_ext
        Vec3 acceleration;
        acceleration.x = (-damping * velocity.x - stiffness * pos_error.x +
                         force_external.x) / mass;
        acceleration.y = (-damping * velocity.y - stiffness * pos_error.y +
                         force_external.y) / mass;
        acceleration.z = (-damping * velocity.z - stiffness * pos_error.z +
                         force_external.z) / mass;

        // Integrate to get velocity and position
        velocity.x += acceleration.x * dt;
        velocity.y += acceleration.y * dt;
        velocity.z += acceleration.z * dt;

        position.x += velocity.x * dt;
        position.y += velocity.y * dt;
        position.z += velocity.z * dt;

        return position;
    }

    void set_impedance(double m, double b, double k) {
        mass = m;
        damping = b;
        stiffness = k;
    }

    Vec3 get_velocity() const { return velocity; }
    Vec3 get_position() const { return position; }

    void reset(const Vec3& initial_pos) {
        position = initial_pos;
        velocity = Vec3(0, 0, 0);
    }
};

/**
 * Simulated force sensor with noise
 */
class ForceSensor {
private:
    double noise_std;

    double gaussian_noise() {
        // Box-Muller transform for Gaussian noise
        static bool has_spare = false;
        static double spare;

        if (has_spare) {
            has_spare = false;
            return spare * noise_std;
        }

        has_spare = true;
        double u, v, s;
        do {
            u = (rand() / double(RAND_MAX)) * 2.0 - 1.0;
            v = (rand() / double(RAND_MAX)) * 2.0 - 1.0;
            s = u * u + v * v;
        } while (s >= 1.0 || s == 0.0);

        s = std::sqrt(-2.0 * std::log(s) / s);
        spare = v * s;
        return u * s * noise_std;
    }

public:
    ForceSensor(double noise = 0.1) : noise_std(noise) {
        srand(time(NULL));
    }

    Vec3 measure(const Vec3& true_force) {
        return Vec3(
            true_force.x + gaussian_noise(),
            true_force.y + gaussian_noise(),
            true_force.z + gaussian_noise()
        );
    }
};

/**
 * Run hybrid control simulation
 */
void test_hybrid_control() {
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "Test 1: Hybrid Position-Force Control\n";
    std::cout << std::string(70, '=') << "\n\n";

    HybridController controller(1000.0, 50.0, 0.5, 0.1);
    ForceSensor sensor(0.1);

    // Scenario: Move to position (0.5, 0.3, ?) and apply 10N downward force

    Vec3 pos_desired(0.5, 0.3, 0.0);
    Vec3 force_desired(0.0, 0.0, -10.0); // 10N downward

    Vec3 pos_actual(0.0, 0.0, 0.1);
    Vec3 vel_actual(0.0, 0.0, 0.0);
    Vec3 force_actual(0.0, 0.0, 0.0);

    double dt = 0.001; // 1kHz control
    double sim_time = 2.0;
    int steps = int(sim_time / dt);

    std::cout << "Configuration:\n";
    std::cout << "  Position control: X, Y\n";
    std::cout << "  Force control: Z\n";
    std::cout << "  Desired position: "; pos_desired.print(); std::cout << "\n";
    std::cout << "  Desired force: "; force_desired.print(); std::cout << " N\n";
    std::cout << "  Control rate: " << 1.0/dt << " Hz\n\n";

    auto start_time = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < steps; i++) {
        // Measure force with noise
        Vec3 force_measured = sensor.measure(force_actual);

        // Compute control
        Vec3 control = controller.compute_control(
            pos_desired, pos_actual, vel_actual,
            force_desired, force_measured, dt
        );

        // Simple dynamics simulation
        vel_actual = vel_actual + control * dt;
        pos_actual = pos_actual + vel_actual * dt;

        // Simulate contact force (simple spring-damper)
        if (pos_actual.z < 0) {
            double penetration = -pos_actual.z;
            force_actual.z = 1000.0 * penetration - 10.0 * vel_actual.z;
        } else {
            force_actual.z = 0;
        }

        // Print status every 0.5 seconds
        if (i % 500 == 0) {
            double time = i * dt;
            std::cout << std::fixed << std::setprecision(3);
            std::cout << "t=" << time << "s | ";
            std::cout << "Pos: "; pos_actual.print(); std::cout << " | ";
            std::cout << "Force: "; force_actual.print(); std::cout << " N\n";
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        end_time - start_time);

    std::cout << "\nSimulation completed in " << duration.count() << " ms\n";
    std::cout << "Final position: "; pos_actual.print(); std::cout << " m\n";
    std::cout << "Final force: "; force_actual.print(); std::cout << " N\n";
}

/**
 * Run impedance control simulation
 */
void test_impedance_control() {
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "Test 2: Impedance Control\n";
    std::cout << std::string(70, '=') << "\n\n";

    ImpedanceController controller(1.0, 20.0, 100.0);

    Vec3 pos_desired(0.5, 0.0, 0.0);
    Vec3 force_external(0.0, 0.0, 0.0);

    controller.reset(Vec3(0.0, 0.0, 0.0));

    double dt = 0.001;
    double sim_time = 3.0;
    int steps = int(sim_time / dt);

    std::cout << "Configuration:\n";
    std::cout << "  Mass: 1.0 kg\n";
    std::cout << "  Damping: 20.0 N·s/m\n";
    std::cout << "  Stiffness: 100.0 N/m\n";
    std::cout << "  Desired position: "; pos_desired.print(); std::cout << "\n\n";

    for (int i = 0; i < steps; i++) {
        double time = i * dt;

        // Apply external force pulse at t=1.0s
        if (time >= 1.0 && time < 1.1) {
            force_external = Vec3(10.0, 0.0, 0.0); // 10N push
        } else {
            force_external = Vec3(0.0, 0.0, 0.0);
        }

        // Compute impedance response
        Vec3 pos = controller.compute_motion(pos_desired, force_external, dt);

        // Print status
        if (i % 500 == 0) {
            std::cout << std::fixed << std::setprecision(3);
            std::cout << "t=" << time << "s | ";
            std::cout << "Pos: "; pos.print(); std::cout << " | ";
            std::cout << "Vel: "; controller.get_velocity().print();
            std::cout << " | F_ext: "; force_external.print();
            std::cout << " N\n";
        }
    }

    std::cout << "\nFinal position: ";
    controller.get_position().print();
    std::cout << " m\n";
}

int main() {
    std::cout << std::string(70, '=') << "\n";
    std::cout << "Chapter 14, Example 3: Force Control Implementation\n";
    std::cout << std::string(70, '=') << "\n";

    test_hybrid_control();
    test_impedance_control();

    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "Force control simulation complete!\n";
    std::cout << std::string(70, '=') << "\n";

    return 0;
}
