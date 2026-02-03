/**
 * Chapter 12, Example 3: Real-Time Redundancy Resolution in C++
 *
 * This example demonstrates:
 * 1. Null-space projection for redundancy resolution
 * 2. Efficient matrix operations for real-time performance
 * 3. Secondary task execution in null-space
 * 4. Joint limit avoidance using gradient projection
 *
 * Compilation:
 *     g++ -std=c++17 -O3 -o chapter_12_example_03 chapter_12_example_03.cpp
 *
 *     Or with Eigen (recommended):
 *     g++ -std=c++17 -O3 -I/usr/include/eigen3 -o chapter_12_example_03 chapter_12_example_03.cpp
 *
 * Expected Output:
 *     - Primary task velocity (end-effector)
 *     - Secondary task velocity (joint-space)
 *     - Combined joint velocities
 *     - Performance timing
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

// Simple matrix class for demonstration (use Eigen in production)
class Matrix {
public:
    std::vector<std::vector<double>> data;
    size_t rows, cols;

    Matrix(size_t r, size_t c, double init_val = 0.0) : rows(r), cols(c) {
        data.resize(rows, std::vector<double>(cols, init_val));
    }

    double& operator()(size_t i, size_t j) {
        return data[i][j];
    }

    const double& operator()(size_t i, size_t j) const {
        return data[i][j];
    }

    Matrix transpose() const {
        Matrix result(cols, rows);
        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                result(j, i) = data[i][j];
            }
        }
        return result;
    }

    Matrix operator*(const Matrix& other) const {
        if (cols != other.rows) {
            throw std::runtime_error("Matrix dimension mismatch");
        }
        Matrix result(rows, other.cols);
        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < other.cols; ++j) {
                double sum = 0.0;
                for (size_t k = 0; k < cols; ++k) {
                    sum += data[i][k] * other.data[k][j];
                }
                result(i, j) = sum;
            }
        }
        return result;
    }

    std::vector<double> operator*(const std::vector<double>& vec) const {
        if (cols != vec.size()) {
            throw std::runtime_error("Matrix-vector dimension mismatch");
        }
        std::vector<double> result(rows, 0.0);
        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                result[i] += data[i][j] * vec[j];
            }
        }
        return result;
    }

    void print(const std::string& name = "") const {
        if (!name.empty()) {
            std::cout << name << ":\n";
        }
        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                std::cout << std::setw(10) << std::fixed << std::setprecision(4)
                          << data[i][j] << " ";
            }
            std::cout << "\n";
        }
    }
};

/**
 * Compute Moore-Penrose pseudoinverse using SVD-based approach.
 * Simplified implementation for demonstration.
 */
Matrix pseudoinverse(const Matrix& A, double tolerance = 1e-6) {
    // For production, use Eigen's completeOrthogonalDecomposition()
    // This is a simplified damped least-squares approach

    size_t m = A.rows;
    size_t n = A.cols;

    Matrix At = A.transpose();
    Matrix AtA = At * A;

    // Add damping term (damped least squares)
    double lambda = 0.01;
    for (size_t i = 0; i < n; ++i) {
        AtA(i, i) += lambda * lambda;
    }

    // Simple Gauss-Jordan elimination for small matrices
    Matrix augmented(n, 2*n);
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            augmented(i, j) = AtA(i, j);
        }
        augmented(i, n + i) = 1.0;
    }

    // Forward elimination
    for (size_t i = 0; i < n; ++i) {
        double pivot = augmented(i, i);
        for (size_t j = 0; j < 2*n; ++j) {
            augmented(i, j) /= pivot;
        }
        for (size_t k = i + 1; k < n; ++k) {
            double factor = augmented(k, i);
            for (size_t j = 0; j < 2*n; ++j) {
                augmented(k, j) -= factor * augmented(i, j);
            }
        }
    }

    // Back substitution
    for (int i = n - 1; i >= 0; --i) {
        for (int k = i - 1; k >= 0; --k) {
            double factor = augmented(k, i);
            for (size_t j = 0; j < 2*n; ++j) {
                augmented(k, j) -= factor * augmented(i, j);
            }
        }
    }

    // Extract inverse
    Matrix AtA_inv(n, n);
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            AtA_inv(i, j) = augmented(i, n + j);
        }
    }

    return AtA_inv * At;
}

/**
 * Compute null-space projector: N = I - J_pinv * J
 */
Matrix nullspace_projector(const Matrix& J, const Matrix& J_pinv) {
    size_t n = J.cols;

    Matrix I(n, n);
    for (size_t i = 0; i < n; ++i) {
        I(i, i) = 1.0;
    }

    Matrix J_pinv_J = J_pinv * J;

    Matrix N(n, n);
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            N(i, j) = I(i, j) - J_pinv_J(i, j);
        }
    }

    return N;
}

/**
 * Compute gradient for joint limit avoidance.
 * Cost function: H = sum((q_i - q_mid_i)^2 / (q_max_i - q_min_i)^2)
 */
std::vector<double> joint_limit_gradient(
    const std::vector<double>& q,
    const std::vector<double>& q_min,
    const std::vector<double>& q_max
) {
    size_t n = q.size();
    std::vector<double> grad(n);

    for (size_t i = 0; i < n; ++i) {
        double q_mid = (q_min[i] + q_max[i]) / 2.0;
        double q_range = q_max[i] - q_min[i];
        grad[i] = -2.0 * (q[i] - q_mid) / (q_range * q_range);
    }

    return grad;
}

/**
 * Redundancy resolution controller.
 */
class RedundancyResolver {
public:
    size_t n_joints;
    std::vector<double> q_min, q_max;
    double k_null;  // Null-space gain

    RedundancyResolver(size_t n,
                      const std::vector<double>& qmin,
                      const std::vector<double>& qmax,
                      double k = 0.5)
        : n_joints(n), q_min(qmin), q_max(qmax), k_null(k) {}

    /**
     * Resolve redundancy with primary and secondary tasks.
     *
     * q_dot = J_pinv * x_dot_primary + (I - J_pinv*J) * q_dot_secondary
     */
    std::vector<double> resolve(
        const Matrix& J,
        const std::vector<double>& x_dot_des,
        const std::vector<double>& q_current
    ) {
        auto start = std::chrono::high_resolution_clock::now();

        // Compute pseudoinverse
        Matrix J_pinv = pseudoinverse(J);

        // Primary task: end-effector velocity
        std::vector<double> q_dot_primary = J_pinv * x_dot_des;

        // Secondary task: joint limit avoidance
        std::vector<double> grad = joint_limit_gradient(q_current, q_min, q_max);

        // Project secondary task into null-space
        Matrix N = nullspace_projector(J, J_pinv);
        std::vector<double> q_dot_secondary(n_joints);
        for (size_t i = 0; i < n_joints; ++i) {
            double sum = 0.0;
            for (size_t j = 0; j < n_joints; ++j) {
                sum += N(i, j) * grad[j];
            }
            q_dot_secondary[i] = k_null * sum;
        }

        // Combine tasks
        std::vector<double> q_dot(n_joints);
        for (size_t i = 0; i < n_joints; ++i) {
            q_dot[i] = q_dot_primary[i] + q_dot_secondary[i];
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << "Computation time: " << duration.count() << " μs\n";

        return q_dot;
    }
};

void print_vector(const std::vector<double>& vec, const std::string& name) {
    std::cout << name << ": [";
    for (size_t i = 0; i < vec.size(); ++i) {
        std::cout << std::fixed << std::setprecision(4) << vec[i];
        if (i < vec.size() - 1) std::cout << ", ";
    }
    std::cout << "]\n";
}

int main() {
    std::cout << "========================================\n";
    std::cout << "Chapter 12, Example 3: Real-Time\n";
    std::cout << "Redundancy Resolution in C++\n";
    std::cout << "========================================\n\n";

    // 7-DOF arm configuration
    const size_t n_joints = 7;
    const size_t n_task = 3;  // 3D Cartesian space

    // Joint limits (radians)
    std::vector<double> q_min(n_joints, -2.8);
    std::vector<double> q_max(n_joints, 2.8);

    // Current joint configuration
    std::vector<double> q_current = {0.0, 0.3, -0.5, 1.2, 0.1, -0.3, 0.0};

    // Simplified Jacobian (3x7) for demonstration
    Matrix J(n_task, n_joints);
    J(0, 0) = 0.1;  J(0, 1) = 0.3;  J(0, 2) = -0.2; J(0, 3) = 0.15;
    J(0, 4) = 0.08; J(0, 5) = 0.05; J(0, 6) = 0.02;

    J(1, 0) = 0.2;  J(1, 1) = -0.1; J(1, 2) = 0.25; J(1, 3) = 0.1;
    J(1, 4) = 0.06; J(1, 5) = 0.03; J(1, 6) = 0.01;

    J(2, 0) = 0.05; J(2, 1) = 0.2;  J(2, 2) = 0.3;  J(2, 3) = -0.15;
    J(2, 4) = 0.1;  J(2, 5) = 0.08; J(2, 6) = 0.04;

    // Desired end-effector velocity (m/s)
    std::vector<double> x_dot_des = {0.05, 0.02, -0.01};

    std::cout << "Configuration:\n";
    std::cout << "  Joints: " << n_joints << "\n";
    std::cout << "  Task space dimensions: " << n_task << "\n\n";

    J.print("Jacobian Matrix");
    std::cout << "\n";

    print_vector(q_current, "Current joint angles (rad)");
    print_vector(x_dot_des, "Desired EE velocity (m/s)");
    std::cout << "\n";

    // Create resolver
    RedundancyResolver resolver(n_joints, q_min, q_max, 0.3);

    // Resolve redundancy
    std::cout << "Resolving redundancy...\n";
    std::vector<double> q_dot = resolver.resolve(J, x_dot_des, q_current);

    std::cout << "\nResults:\n";
    print_vector(q_dot, "Joint velocities (rad/s)");

    // Verify primary task
    std::vector<double> x_dot_actual = J * q_dot;
    print_vector(x_dot_actual, "Achieved EE velocity (m/s)");

    // Compute error
    double error = 0.0;
    for (size_t i = 0; i < n_task; ++i) {
        error += std::pow(x_dot_actual[i] - x_dot_des[i], 2);
    }
    error = std::sqrt(error);

    std::cout << "\nPrimary task error: " << std::scientific
              << std::setprecision(6) << error << " m/s\n";

    // Performance benchmark
    std::cout << "\n--- Performance Benchmark ---\n";
    const int n_iterations = 1000;
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < n_iterations; ++i) {
        resolver.resolve(J, x_dot_des, q_current);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    double avg_time = duration.count() / (double)n_iterations;

    std::cout << "Average computation time: " << std::fixed << std::setprecision(2)
              << avg_time << " μs\n";
    std::cout << "Max control frequency: " << std::fixed << std::setprecision(0)
              << 1e6 / avg_time << " Hz\n";

    std::cout << "\n========================================\n";
    std::cout << "Real-time redundancy resolution complete!\n";
    std::cout << "========================================\n";

    return 0;
}
