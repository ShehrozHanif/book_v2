---
chapter_id: "04"
module: "Module 1"
title: "Sensors & Perception"
word_count_target: 2400
word_count_actual: 2407
status: "draft"
code_examples: ["chapter_04_example_01.py", "chapter_04_example_02.py"]
references: ["thrun2005", "siegwart2011", "corke2017", "quigley2009", "woodman2007"]
last_updated: "2026-02-03"
author: "Content Writing Team"
---

# Chapter 4: Sensors & Perception

## Learning Objectives

By the end of this chapter, you will be able to:
- Identify and explain the operating principles of major sensor types used in humanoid robotics (IMU, vision, tactile, odometry)
- Implement ROS 2 sensor interfaces to subscribe to and process sensor data streams
- Apply sensor fusion techniques to combine multiple sensor modalities for improved state estimation
- Understand calibration procedures for IMU and vision sensors
- Develop basic perception pipelines for humanoid robot applications

## Introduction

Sensors are the bridge between the physical world and robotic intelligence. While actuators execute commands, sensors provide the feedback necessary to verify that desired actions occurred and to adapt to changing conditions. A humanoid robot without sensors is like a person blindfolded with earplugs—capable of motion but unable to respond to the environment.

Humanoid robots employ diverse sensor modalities, each providing different types of information. **Inertial Measurement Units (IMUs)** track orientation and acceleration. **Vision systems** capture rich environmental data for object recognition and navigation. **Tactile sensors** enable dexterous manipulation through touch feedback. **Proprioceptive sensors** (joint encoders, force-torque sensors) monitor the robot's internal state. The challenge lies not just in acquiring sensor data but in fusing information from multiple sources to build an accurate, real-time model of the robot and its environment.

This chapter surveys the primary sensor types used in humanoid robotics, explains their operating principles, and demonstrates practical implementation using ROS 2. We explore sensor characteristics (accuracy, noise, bandwidth), calibration procedures, and fusion algorithms. By chapter's end, you will understand how to select appropriate sensors for applications and integrate them into perception systems.

## Section 1: Inertial Measurement Units (IMUs)

An **Inertial Measurement Unit (IMU)** combines accelerometers and gyroscopes to measure linear accelerations and angular velocities. Modern IMUs often include magnetometers for absolute heading reference, forming a 9-axis sensor (3-axis accelerometer + 3-axis gyroscope + 3-axis magnetometer).

### Accelerometers

Accelerometers measure proper acceleration—the acceleration felt in the sensor's reference frame, including gravitational effects. A 3-axis accelerometer provides readings [a_x, a_y, a_z] in m/s².

**Operating Principle**: Most MEMS (Micro-Electro-Mechanical Systems) accelerometers use proof masses suspended by springs. Acceleration causes displacement, measured capacitively or piezoelectrically.

**Key Characteristics**:
- **Range**: Typical ranges are ±2g, ±4g, ±8g, ±16g (where g = 9.81 m/s²)
- **Sensitivity**: Output voltage or digital counts per g
- **Noise**: Random fluctuations; specified as noise density (μg/√Hz)
- **Bandwidth**: Frequency range of measurable accelerations (typically 10-1000 Hz)

**Gravity Sensing**: When stationary, the accelerometer reads gravity. For a sensor aligned with gravity (z-axis up):
```
[a_x, a_y, a_z] = [0, 0, -g] = [0, 0, -9.81] m/s²
```

The negative sign indicates the sensor feels upward acceleration to counteract gravity (Einstein's equivalence principle).

**Orientation from Accelerometer**: For a stationary robot, roll (φ) and pitch (θ) can be computed:
```
φ = atan2(a_y, a_z)
θ = atan2(-a_x, sqrt(a_y² + a_z²))
```

**Numerical Example**: If accelerometer reads [2.5, 1.2, -9.1] m/s²:
```
φ = atan2(1.2, -9.1) = atan2(1.2, -9.1) ≈ -7.5°
θ = atan2(-2.5, sqrt(1.2² + 9.1²)) = atan2(-2.5, 9.18) ≈ -15.3°
```

The sensor is tilted -15.3° in pitch and -7.5° in roll.

### Gyroscopes

Gyroscopes measure angular velocity (ω_x, ω_y, ω_z) in rad/s about three axes.

**Operating Principle**: MEMS gyroscopes exploit the Coriolis effect. Vibrating proof masses experience perpendicular forces when the sensor rotates, measured to determine angular rate.

**Key Characteristics**:
- **Range**: ±250°/s to ±2000°/s
- **Sensitivity**: Output per °/s
- **Bias**: Constant offset error; drifts with temperature
- **Noise**: Random walk; accumulates over time when integrated

**Integration for Orientation**: Angular velocity integrates to orientation:
```
θ(t) = θ(t-Δt) + ω * Δt
```

**Numerical Example**: Starting at θ = 0°, if ω = 30°/s for 2 seconds:
```
θ = 0 + 30 * 2 = 60°
```

**Drift Problem**: Gyroscope bias causes unbounded orientation error. A bias of 0.1°/s accumulates to 360° error in one hour. This necessitates sensor fusion with absolute references (accelerometers, magnetometers).

### Complementary Filter for Sensor Fusion

A **complementary filter** combines accelerometer and gyroscope data, using high-frequency gyroscope data (no gravity interference during motion) and low-frequency accelerometer data (gravity reference, no drift):

```
θ_fused = α * (θ_gyro + ω * Δt) + (1 - α) * θ_accel
```

Where α ≈ 0.98 (high-pass filter for gyroscope, low-pass for accelerometer).

**Numerical Example**: Current θ_fused = 45°, ω = 5°/s, θ_accel = 47°, Δt = 0.01 s, α = 0.98:
```
θ_gyro_new = 45 + 5 * 0.01 = 45.05°
θ_fused = 0.98 * 45.05 + 0.02 * 47
        = 44.149 + 0.94 = 45.089°
```

The filter smoothly incorporates both sensor inputs, mitigating individual weaknesses.

## Section 2: Vision Systems

Vision provides dense environmental information, enabling object recognition, obstacle detection, and visual servoing. Humanoid robots typically use cameras (RGB), depth sensors (RGBD, stereo, LiDAR), or both.

### RGB Cameras

Standard cameras capture color images as arrays of pixels. Key parameters:
- **Resolution**: Pixel count (e.g., 1920×1080 for Full HD)
- **Frame Rate**: Images per second (30 fps, 60 fps)
- **Field of View (FOV)**: Angular extent (e.g., 90° horizontal)
- **Exposure and Gain**: Control brightness and sensitivity

**Pinhole Camera Model**: Projects 3D points to 2D image plane:
```
u = f_x * (X / Z) + c_x
v = f_y * (Y / Z) + c_y
```

Where (X, Y, Z) is the 3D point in camera frame, (u, v) is the image pixel, f_x and f_y are focal lengths, and (c_x, c_y) is the principal point (image center).

**Numerical Example**: f_x = 500 pixels, c_x = 320, point at (0.5, 0.2, 2.0) m:
```
u = 500 * (0.5 / 2.0) + 320 = 500 * 0.25 + 320 = 125 + 320 = 445 pixels
v = 500 * (0.2 / 2.0) + 240 = 500 * 0.1 + 240 = 50 + 240 = 290 pixels
```

The point projects to pixel (445, 290).

### Depth Sensors

Depth sensors measure distance to objects, providing (x, y, depth) information. Types include:

**Stereo Vision**: Two cameras separated by baseline b. Disparity (pixel difference) relates to depth:
```
Z = (f * b) / d
```
Where d is disparity in pixels.

**Time-of-Flight (ToF)**: Measures round-trip time of light pulses:
```
Z = (c * t) / 2
```
Where c is speed of light, t is round-trip time.

**Structured Light**: Projects patterns (e.g., infrared dots) and triangulates depth from distortions. Used in Intel RealSense and Microsoft Kinect.

**LiDAR**: Laser scanners measuring distance via time-of-flight; produce precise 3D point clouds but are expensive and bulky.

**Depth Accuracy**: Stereo and structured light depth error increases quadratically with distance:
```
ΔZ ≈ Z² / (f * b)
```

For f = 500 pixels, b = 0.05 m, Z = 3 m:
```
ΔZ ≈ 3² / (500 * 0.05) = 9 / 25 = 0.36 m
```

Depth uncertainty is 36 cm at 3 meters—significant for navigation.

### Camera Calibration

Cameras exhibit lens distortion (radial and tangential), requiring calibration to obtain accurate 3D measurements. The process involves:
1. Capture multiple images of a calibration pattern (checkerboard)
2. Detect corner points in each image
3. Solve for intrinsic parameters (focal length, principal point, distortion coefficients) and extrinsic parameters (camera pose)

ROS 2 provides `camera_calibration` package for this process. Calibration improves feature detection and depth estimation accuracy significantly.

## Section 3: Tactile and Force-Torque Sensors

Tactile sensors provide touch feedback, essential for manipulation. **Force-torque (F/T) sensors** measure forces and moments at specific locations, typically at wrists, ankles, or fingertips.

### Force-Torque Sensors

An F/T sensor measures three forces [F_x, F_y, F_z] and three torques [τ_x, τ_y, τ_z], forming a 6D wrench. Common technologies:
- **Strain Gauges**: Measure deformation of a compliant structure under load
- **Optical**: Use light transmission changes in loaded materials
- **Capacitive**: Detect capacitance changes from electrode displacement

**Applications**:
- **Grasping**: Measure grip force to prevent slippage or crushing
- **Walking**: Ankle F/T sensors measure ground reaction forces for balance control
- **Assembly**: Detect contact forces during part insertion

**Numerical Example**: During grasping, F/T sensor reads F_z = 15 N, τ_y = 0.3 N·m. If gripper fingers are 0.05 m apart:
```
Grip force per finger ≈ F_z / 2 = 7.5 N
Moment arm ≈ τ_y / F_z = 0.3 / 15 = 0.02 m
```

Object may be slipping; gripper should increase force or adjust grip.

### Tactile Arrays

Tactile arrays provide distributed touch sensing over surfaces. Technologies include:
- **Resistive**: Pressure changes resistance between conductive layers
- **Capacitive**: Pressure changes capacitance
- **Optical**: Pressure deforms light guides, changing transmission

**Resolution**: Number of sensing elements (taxels) per area. High-density arrays (>10 taxels/cm²) enable texture recognition and slip detection.

**Applications**: Robotic skins covering fingers, palms, or whole-body for safe human-robot interaction and refined manipulation.

## Section 4: Proprioceptive Sensors and Odometry

Proprioceptive sensors measure the robot's internal state—joint angles, velocities, torques.

### Joint Encoders

Encoders measure angular position. Types:
- **Incremental**: Count transitions; lose absolute position on power cycle
- **Absolute**: Unique code for each position; retain position without power

**Resolution**: Pulses per revolution. A 2048 PPR encoder on a 100:1 gearbox provides:
```
Angular resolution = 360° / (2048 * 100) = 0.00176° = 6.3 arc-seconds
```

Extremely precise for control.

### Odometry

**Odometry** estimates robot position by integrating motion over time. For wheeled robots, wheel encoder readings give displacement:
```
Δx = (R / 2) * (ΔθR + ΔθL)
Δθ = (R / b) * (ΔθR - ΔθL)
```

Where R is wheel radius, b is wheelbase, ΔθR and ΔθL are right/left wheel rotations.

**Drift**: Odometry accumulates errors from wheel slip, uneven terrain, and encoder noise. Position error grows unbounded without external correction (e.g., from vision, GPS).

For legged robots, odometry is more complex, requiring forward kinematics from all leg joints and contact detection to determine stance phases.

## Section 5: Sensor Fusion and ROS 2 Integration

Individual sensors have limitations; **sensor fusion** combines complementary information for robust state estimation.

### Kalman Filtering

The **Kalman filter** is an optimal estimator for linear Gaussian systems. It maintains a state estimate and uncertainty, updating with each sensor measurement:

**Prediction Step**:
```
x̂⁻ = A * x̂ + B * u
P⁻ = A * P * Aᵀ + Q
```

**Update Step**:
```
K = P⁻ * Hᵀ * (H * P⁻ * Hᵀ + R)⁻¹
x̂ = x̂⁻ + K * (z - H * x̂⁻)
P = (I - K * H) * P⁻
```

Where x̂ is state estimate, P is covariance, A is state transition, H is observation model, Q is process noise, R is measurement noise, K is Kalman gain.

**Extended Kalman Filter (EKF)**: Handles nonlinear systems by linearizing about current estimate. Widely used for robot localization.

**Unscented Kalman Filter (UKF)**: Uses sigma points to propagate probability distributions; more accurate than EKF for highly nonlinear systems.

### ROS 2 Sensor Interfaces

ROS 2 provides standardized message types for sensors:
- **sensor_msgs/Imu**: IMU data (orientation, angular velocity, linear acceleration)
- **sensor_msgs/Image**: Camera images
- **sensor_msgs/PointCloud2**: 3D point clouds from depth sensors
- **sensor_msgs/JointState**: Joint positions, velocities, efforts
- **geometry_msgs/WrenchStamped**: Force-torque measurements

**Example**: Subscribing to IMU data in Python:
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuSubscriber(Node):
    def __init__(self):
        super().__init__('imu_subscriber')
        self.subscription = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)

    def imu_callback(self, msg):
        accel = msg.linear_acceleration
        gyro = msg.angular_velocity
        self.get_logger().info(f'Accel: [{accel.x:.2f}, {accel.y:.2f}, {accel.z:.2f}]')
```

### robot_localization Package

The `robot_localization` ROS 2 package fuses IMU, odometry, and GPS data using EKF or UKF. Configuration specifies:
- Input topics (IMU, wheel odometry, visual odometry)
- Sensor covariances
- Output frame (odom, map)

This enables continuous, drift-corrected pose estimation critical for autonomous navigation.

## Code Examples

This chapter includes two Python examples demonstrating sensor integration:

### Example 1: ROS 2 IMU Subscriber

`chapter_04_example_01.py` implements a complete IMU data processing pipeline:
- Subscribes to IMU messages
- Applies complementary filter for orientation estimation
- Detects and filters noise spikes
- Computes roll, pitch, yaw from accelerometer and gyroscope
- Publishes filtered orientation for downstream use

Users can connect real or simulated IMU sources and observe fusion results.

### Example 2: Sensor Data Visualization

`chapter_04_example_02.py` provides real-time visualization:
- Plots IMU acceleration and angular velocity over time
- Displays camera feed with detected features
- Simulates tactile sensor pressure distribution
- Shows sensor health metrics (noise levels, update rates)

This tool aids in debugging sensor issues and verifying calibration.

## Key Concepts Summary

- **Inertial Measurement Unit (IMU)**: Combines accelerometers (linear acceleration) and gyroscopes (angular velocity); essential for balance and orientation
- **Accelerometer Characteristics**: Measure proper acceleration including gravity; used for tilt sensing when stationary
- **Gyroscope Characteristics**: Measure angular rates; integrate to orientation but accumulate drift over time
- **Complementary Filter**: Fuses accelerometer and gyroscope data, exploiting complementary frequency characteristics
- **Camera Model**: Pinhole projection relates 3D world to 2D image; calibration corrects lens distortion
- **Depth Sensors**: Stereo, time-of-flight, structured light, and LiDAR provide 3D information; accuracy degrades with distance
- **Force-Torque Sensors**: Measure 6D wrenches for manipulation and balance; use strain gauges or other transduction methods
- **Tactile Arrays**: Distributed touch sensing for dexterous manipulation and safe interaction
- **Joint Encoders**: High-resolution position sensing; absolute encoders retain position across power cycles
- **Odometry**: Dead reckoning from wheel or leg encoders; accumulates drift without external correction
- **Sensor Fusion**: Combines multiple sensors using Kalman filtering or similar techniques for robust state estimation
- **ROS 2 Integration**: Standardized message types (sensor_msgs) and tools (robot_localization) simplify sensor interfacing

## References

[1] Thrun, S., Burgard, W., & Fox, D. (2005). *Probabilistic Robotics*. MIT Press. https://mitpress.mit.edu/9780262201629/

[2] Siegwart, R., Nourbakhsh, I. R., & Scaramuzza, D. (2011). *Introduction to Autonomous Mobile Robots* (2nd ed.). MIT Press. https://mitpress.mit.edu/9780262015356/

[3] Corke, P. (2017). *Robotics, Vision and Control: Fundamental Algorithms in MATLAB* (2nd ed.). Springer. https://doi.org/10.1007/978-3-319-54413-7

[4] Quigley, M., et al. (2009). ROS: An open-source Robot Operating System. *ICRA Workshop on Open Source Software*, 3(3.2), 5. http://www.willowgarage.com/papers/ros-open-source-robot-operating-system

[5] Woodman, O. J. (2007). An introduction to inertial navigation. *University of Cambridge Computer Laboratory Technical Report*, 696, 1-37. https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-696.pdf

## Further Reading

- ROS 2 sensor_msgs Documentation: https://docs.ros2.org/foxy/api/sensor_msgs/
- robot_localization Package: https://docs.ros.org/en/humble/p/robot_localization/
- OpenCV Camera Calibration Tutorial: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- IMU Sensor Fusion Tutorial (Madgwick Filter): https://x-io.co.uk/open-source-imu-and-ahrs-algorithms/
- Intel RealSense SDK: https://www.intelrealsense.com/sdk-2/

## Exercises

1. **IMU Orientation Calculation**: An IMU reads accelerometer values [1.5, -2.3, -9.2] m/s² while stationary. Compute roll and pitch angles. What does this orientation indicate?

2. **Complementary Filter Tuning**: Implement the complementary filter equation with α = 0.95 and α = 0.99. Compare response to rapid rotations and slow drifts. Which value provides better performance?

3. **Camera Projection**: A camera with f_x = f_y = 600 pixels, image size 640×480, captures a point at (1.2, -0.5, 3.0) m. Compute the pixel coordinates. Is the point visible in the image?

4. **Depth Sensor Analysis**: For a stereo camera with baseline 0.06 m, focal length 400 pixels, compute depth resolution (minimum detectable depth change) at distances 1 m, 3 m, and 5 m. Assume minimum disparity change is 1 pixel.

5. **ROS 2 Sensor Integration**: Using the provided `chapter_04_example_01.py` script, subscribe to a simulated IMU topic. Modify the complementary filter parameter α and observe effects on orientation stability. Document optimal value for your test scenario.

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: This chapter covers sensors and perception fundamentals for humanoid robots. Code examples demonstrate ROS 2 IMU processing and sensor visualization. Future modules will extend perception to object recognition and environment mapping.
