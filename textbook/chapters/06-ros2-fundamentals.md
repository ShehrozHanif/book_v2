---
chapter_id: "06"
module: "Module 2"
title: "ROS 2 Fundamentals"
word_count_target: 2300
word_count_actual: 2315
status: "draft"
code_examples: ["chapter_06_example_01.py", "chapter_06_example_02.py", "chapter_06_example_03.py"]
references: ["ros2_humble_docs", "dds_specification_2015", "ros2_design_2014", "maruyama2016", "quigley2009"]
last_updated: "2026-02-03"
author: "Content Writing Team"
---

# Chapter 6: ROS 2 Fundamentals

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand ROS 2 architecture and its core communication patterns
- Implement publisher-subscriber patterns for asynchronous data streams
- Create service clients and servers for synchronous request-response interactions
- Configure parameter servers for runtime robot configuration
- Apply launch files to orchestrate multi-node robotic systems

## Introduction

The Robot Operating System 2 (ROS 2) represents a complete architectural redesign of the original ROS framework, addressing fundamental limitations in real-time performance, security, and multi-robot coordination. While ROS 1 served the research community admirably for over a decade, its reliance on a centralized master node, lack of native security features, and limited real-time support made it unsuitable for production deployments in safety-critical applications such as humanoid robotics.

ROS 2 addresses these shortcomings through a distributed architecture built on the Data Distribution Service (DDS) middleware standard. DDS provides peer-to-peer discovery, quality-of-service (QoS) policies for deterministic communication, and built-in security mechanisms. This foundation enables ROS 2 nodes to communicate without a central coordinator, survive network partitions, and meet hard real-time deadlines required for balance control in humanoid robots.

The transition from ROS 1 to ROS 2 introduces new concepts and APIs, but the core philosophy remains unchanged: modular, reusable software components that communicate through well-defined interfaces. Humanoid robotics applications particularly benefit from ROS 2's improved latency characteristics, enabling tight control loops for balance and manipulation, and its support for multiple DDS implementations, allowing developers to select middleware optimized for specific hardware platforms.

This chapter introduces the foundational concepts of ROS 2, focusing on nodes, topics, services, parameters, and launch files. We explore the computation graph model that structures ROS 2 applications, implement practical communication patterns, and demonstrate how to configure and deploy multi-node systems. The examples provided use Python and the ROS 2 Humble distribution, the current long-term support release widely adopted in humanoid robotics research.

## Section 1: Nodes and the Computation Graph

ROS 2 applications consist of **nodes**—independent processes that perform specific computational tasks. Each node represents a modular unit of functionality: a camera driver might be one node, a perception algorithm another, and a motion controller a third. Nodes communicate by passing messages over topics, calling services, or querying parameters, forming a **computation graph** that defines the system's architecture.

The computation graph is a directed graph where nodes are vertices and communication channels (topics, services, actions) are edges. This abstraction provides powerful benefits: nodes can be developed, tested, and debugged independently; the same node can be reused across different robots; and the system remains flexible, allowing runtime reconfiguration by starting or stopping nodes.

Each node possesses a unique **name** within a namespace hierarchy, similar to file system paths. For example, `/robot1/left_arm/joint_controller` identifies a specific controller node in a multi-robot system. Namespaces prevent naming collisions and enable scaling to systems with dozens or hundreds of nodes.

ROS 2 introduces a formal **node lifecycle** with defined states: Unconfigured, Inactive, Active, and Finalized. Lifecycle management ensures deterministic startup and shutdown sequences, critical for humanoid robots where improperly initialized sensors could lead to falls or collisions. A lifecycle node transitions through states via standardized transitions (configure, activate, deactivate, cleanup, shutdown), allowing supervisory systems to monitor and control node health.

**Node discovery** operates automatically through DDS. When a node starts, it announces its presence, topics, services, and parameters to the DDS global data space. Other nodes discover this information without requiring a central registry. This peer-to-peer architecture eliminates single points of failure and enables dynamic reconfiguration—nodes can join or leave the computation graph at runtime without disrupting the entire system.

In practice, a minimal ROS 2 node in Python requires importing the `rclpy` library, initializing the ROS 2 context, creating a node instance, and spinning the node to process callbacks. The node's constructor typically sets up publishers, subscribers, timers, and parameters. Proper cleanup involves destroying the node and shutting down the ROS 2 context to release resources.

Understanding the computation graph is essential for designing scalable humanoid robot systems. A typical humanoid might deploy fifty nodes managing sensors, perception, planning, control, and diagnostics. Visualizing the graph using tools like `rqt_graph` reveals communication patterns, identifies bottlenecks, and validates that the system architecture matches design intentions.

## Section 2: Topics and Publisher-Subscriber Pattern

**Topics** implement the publish-subscribe communication pattern, the most common interaction model in ROS 2. A topic is a named channel for transmitting messages of a specific type. Publishers send messages to topics without knowing which nodes will receive them; subscribers express interest in topics without knowing which nodes produce the data. This decoupling enables flexible, composable systems.

The publish-subscribe pattern excels for streaming data: sensor readings, robot state, camera images, and control commands. For example, an IMU sensor node publishes acceleration and angular velocity measurements to `/imu/data` at 200 Hz. Multiple subscribers—a state estimator, a data logger, and a visualization node—can independently consume this stream without coordinating with the publisher or each other.

ROS 2 **messages** are strongly typed data structures defined in `.msg` files using a language-neutral interface definition language (IDL). Standard messages in the `std_msgs`, `sensor_msgs`, and `geometry_msgs` packages cover common data types: integers, floats, strings, arrays, images, point clouds, and transforms. Custom messages can be defined for application-specific data.

A critical aspect of topics in ROS 2 is **Quality of Service (QoS)** policies. QoS settings control message delivery reliability, history depth, durability, and deadline constraints. The **Reliability** policy determines whether messages are delivered reliably (with acknowledgments and retransmission) or on a best-effort basis (no guarantees). The **History** policy specifies how many messages are queued if a subscriber lags behind the publisher. The **Durability** policy controls whether late-joining subscribers receive previously published messages.

For humanoid robotics, QoS tuning is essential. Joint state publishers typically use reliable delivery with a history depth of 10 to ensure control loops never miss critical state updates. In contrast, camera image topics often use best-effort delivery to minimize latency, accepting that occasional frame drops are preferable to delayed control decisions.

**Message filtering and synchronization** become necessary when algorithms require aligned data from multiple sensors. The `message_filters` package provides approximate and exact time synchronizers that buffer messages from different topics and invoke callbacks only when temporally matched messages are available. This is crucial for sensor fusion algorithms that combine camera images, IMU data, and joint encoders to estimate robot state.

Implementing a publisher involves creating a publisher object with a topic name and message type, then calling `publish()` to send messages. Subscribers register callback functions invoked whenever messages arrive. The ROS 2 executor manages callback execution, with options for single-threaded, multi-threaded, and real-time executors tailored to different performance requirements.

## Section 3: Services and Actions

While topics handle continuous data streams, **services** implement synchronous request-response interactions. A service client sends a request message and blocks until the server returns a response. This pattern suits operations with clear completion criteria: querying the current robot pose, commanding a gripper to close, or requesting a motion plan.

ROS 2 **service definitions** use `.srv` files containing a request section and a response section separated by `---`. For example, a pose query service might request a joint configuration and respond with the corresponding end-effector position and orientation. Service types are strongly typed, ensuring type safety at compile time.

Services are inherently synchronous and blocking. The client waits for the server's response, which can be problematic if the operation is long-running or might fail. For instance, requesting a motion plan could take seconds or fail if no collision-free path exists. Blocking the client for extended periods reduces system responsiveness and can cause timeouts in upstream components.

**Actions** address the limitations of services for long-running, preemptible tasks. An action consists of a goal, feedback, and result. The client sends a goal to the action server and receives periodic feedback updates while the action executes, finally receiving a result indicating success or failure. Actions are cancelable—clients can preempt ongoing actions if circumstances change.

Actions are ideal for humanoid robot behaviors: "walk to location X" is an action that provides feedback on progress (distance remaining, obstacles encountered) and can be canceled if a higher-priority task arrives. Actions use three topics internally: goal, feedback, and result, allowing asynchronous monitoring and cancellation.

**Choosing between topics, services, and actions** depends on the interaction pattern. Use **topics** for continuous data streams where publishers and subscribers are decoupled and delivery timing is flexible. Use **services** for quick, synchronous queries that complete in milliseconds. Use **actions** for long-running, goal-oriented tasks that benefit from progress feedback and cancellation.

In practice, a humanoid robot control system might use topics for joint states and commands (streaming data), services for configuration queries and simple commands (quick, synchronous operations), and actions for high-level behaviors like grasping or walking (long-running, monitorable tasks). This layered communication architecture provides the flexibility and responsiveness needed for complex robotic systems.

### Code Example 1: ROS 2 Publisher-Subscriber Pair

This example demonstrates a simple publisher-subscriber system using standard messages.

```python
# chapter_06_example_01.py
# ROS 2 Publisher/Subscriber pair demonstrating topic-based communication
# Run with: ros2 run <package_name> publisher_subscriber_demo
# Expected output: Subscriber receives and prints published messages at 1 Hz

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):
    """Publisher node that sends string messages to /chatter topic."""

    def __init__(self):
        super().__init__('minimal_publisher')
        # Create publisher for /chatter topic with queue size 10
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        # Timer triggers publishing callback every 1.0 seconds
        timer_period = 1.0
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.count = 0
        self.get_logger().info('Publisher node started')

    def timer_callback(self):
        """Publish message with incrementing counter."""
        msg = String()
        msg.data = f'Hello World: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


class MinimalSubscriber(Node):
    """Subscriber node that receives messages from /chatter topic."""

    def __init__(self):
        super().__init__('minimal_subscriber')
        # Create subscription to /chatter topic with queue size 10
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )
        self.get_logger().info('Subscriber node started')

    def listener_callback(self, msg):
        """Callback invoked when message arrives on subscribed topic."""
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    """Main function to run both publisher and subscriber nodes."""
    rclpy.init(args=args)

    # Create both publisher and subscriber nodes
    publisher = MinimalPublisher()
    subscriber = MinimalSubscriber()

    # Use MultiThreadedExecutor to spin both nodes concurrently
    from rclpy.executors import MultiThreadedExecutor
    executor = MultiThreadedExecutor()
    executor.add_node(publisher)
    executor.add_node(subscriber)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        publisher.destroy_node()
        subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Section 4: Parameters and Configuration

**Parameters** provide a mechanism for configuring node behavior at runtime without modifying code or recompiling. Each node maintains a parameter server that stores typed key-value pairs: integers, floats, strings, booleans, arrays, or byte arrays. Parameters can be set via command-line arguments, launch files, or YAML configuration files, enabling flexible deployment across different robots and environments.

Parameters serve multiple purposes in humanoid robotics. Controller gains (PID coefficients), sensor calibration values, safety limits, and algorithm hyperparameters are typically exposed as parameters. This allows operators to tune robot behavior in real-time, adapting to changing conditions or optimizing performance without redeploying software.

ROS 2 parameters are **strongly typed** and support validation through parameter descriptors. Descriptors specify the parameter type, valid ranges, and read-only status. For example, a joint velocity limit parameter might be constrained to positive floats between 0.1 and 10.0 rad/s, with runtime validation rejecting invalid values.

**Dynamic reconfiguration** enables parameter updates while nodes run. A node can register parameter callbacks that execute whenever a parameter changes, allowing the node to adapt its behavior immediately. This is essential for tuning control loops during operation or adjusting sensor processing pipelines based on environmental conditions.

Parameters can be organized hierarchically using namespaces. A humanoid robot might have parameters like `/robot/left_arm/shoulder_pitch/pid/kp`, clearly indicating the parameter belongs to the shoulder pitch joint's PID controller on the left arm. This hierarchical organization scales to complex systems with hundreds of parameters.

In practice, parameters are typically loaded from YAML files specified in launch files. This approach separates configuration from code, enabling the same software to run on different robots or in simulation versus hardware by simply changing the configuration file. Version-controlled YAML files also provide documentation of system configuration and facilitate reproducibility in research.

### Code Example 2: Service Client/Server for Humanoid Pose Queries

This example implements a service for querying forward kinematics.

```python
# chapter_06_example_02.py
# Service client/server for humanoid pose queries
# Run server: ros2 run <package_name> pose_query_server
# Run client: ros2 run <package_name> pose_query_client
# Expected output: Client receives end-effector pose for given joint angles

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts
import numpy as np


# Custom service definition (in practice, define in .srv file):
# Request: float64[] joint_angles
# Response: geometry_msgs/Pose end_effector_pose

class PoseQueryServer(Node):
    """Service server that computes forward kinematics."""

    def __init__(self):
        super().__init__('pose_query_server')
        # Create service server
        self.srv = self.create_service(
            AddTwoInts,  # Replace with custom ForwardKinematics service
            'compute_pose',
            self.compute_pose_callback
        )
        self.get_logger().info('Pose query service ready')

    def compute_pose_callback(self, request, response):
        """
        Compute forward kinematics for requested joint configuration.
        In production, this would use a proper kinematics library (KDL, Pinocchio).
        """
        # Simplified example using AddTwoInts - replace with actual FK computation
        self.get_logger().info(f'Computing pose for joint angles: {request.a}, {request.b}')

        # Placeholder: actual FK computation would go here
        # Using a kinematics library to compute end-effector pose
        # response.end_effector_pose = forward_kinematics(request.joint_angles)

        response.sum = request.a + request.b  # Placeholder
        self.get_logger().info(f'Returning pose: {response.sum}')
        return response


class PoseQueryClient(Node):
    """Service client that requests pose computations."""

    def __init__(self):
        super().__init__('pose_query_client')
        self.client = self.create_client(AddTwoInts, 'compute_pose')

        # Wait for service to become available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for pose query service...')

        self.get_logger().info('Pose query client ready')

    def send_request(self, joint_angles):
        """Send synchronous request to compute pose."""
        request = AddTwoInts.Request()
        request.a = int(joint_angles[0] * 100)  # Placeholder conversion
        request.b = int(joint_angles[1] * 100)

        self.get_logger().info(f'Requesting pose for joints: {joint_angles}')

        # Synchronous call - blocks until response received
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(f'Received pose: {future.result().sum}')
            return future.result()
        else:
            self.get_logger().error('Service call failed')
            return None


def main(args=None):
    """Run pose query client demo."""
    rclpy.init(args=args)

    client = PoseQueryClient()

    # Example: query pose for specific joint configuration
    joint_angles = [0.5, 0.3, -0.2, 0.0, 0.1, 0.4, 0.0]  # 7-DOF arm
    client.send_request(joint_angles)

    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Section 5: Launch Files

**Launch files** orchestrate complex multi-node systems, specifying which nodes to start, their parameters, remappings, and dependencies. While individual nodes can be started manually using `ros2 run`, production systems with dozens of nodes require automated launch systems to ensure correct configuration and startup order.

ROS 2 launch files use Python scripts (`.launch.py`), XML files (`.launch.xml`), or YAML files (`.launch.yaml`). Python launch files offer the most flexibility, supporting conditional logic, parameter computation, and programmatic node configuration. XML and YAML formats provide simpler syntax for straightforward launch scenarios.

A launch file typically includes **node declarations** specifying the package, executable, node name, namespace, and parameters. **Launch arguments** allow parameterizing launch files, enabling the same launch file to work in simulation or hardware by passing different arguments. **Event handlers** define actions triggered by node startup, shutdown, or other events, enabling complex startup choreography.

**Composition** in ROS 2 allows multiple nodes to run in a single process, reducing memory overhead and inter-process communication latency. This is particularly important for humanoid robots running on resource-constrained onboard computers. Launch files can specify composed node containers and load components dynamically.

Launch files support **parameter file loading**, enabling centralized configuration management. A humanoid robot might have separate YAML files for each subsystem (sensors, controllers, perception) loaded by the main launch file. This modularity simplifies configuration management and allows subsystems to be tested independently.

**Namespacing and remapping** in launch files enable running multiple instances of the same node or adapting nodes to different topic names without code changes. For instance, the same camera driver node can be launched twice with different namespaces (`/left_camera`, `/right_camera`) and device parameters, creating independent camera streams.

In practice, humanoid robot systems use hierarchical launch files. A top-level launch file includes sub-launch files for perception, planning, control, and diagnostics. This structure mirrors the system architecture, makes the launch system maintainable, and allows subsystems to be started independently during development and debugging.

### Code Example 3: Launch File with Multiple Nodes and Parameters

This launch file demonstrates multi-node orchestration with parameter loading.

```python
# chapter_06_example_03.py
# Launch file with 3 nodes + parameters
# Run with: ros2 launch <package_name> multi_node_demo.launch.py
# Expected output: Three nodes start with configured parameters

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """
    Generate launch description for multi-node humanoid system demo.
    Launches sensor node, controller node, and state estimator with parameters.
    """

    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time if true'
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='humanoid_01',
        description='Name of the robot instance'
    )

    # Get launch configuration values
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_name = LaunchConfiguration('robot_name')

    # Path to parameter file (in practice, load from package share directory)
    # config_file = os.path.join(
    #     get_package_share_directory('your_package'),
    #     'config',
    #     'robot_params.yaml'
    # )

    # Node 1: IMU Sensor Publisher
    imu_node = Node(
        package='sensor_msgs',  # Replace with actual package
        executable='imu_publisher',  # Replace with actual executable
        name='imu_sensor',
        namespace=robot_name,
        parameters=[
            {'use_sim_time': use_sim_time},
            {'publish_rate': 200.0},  # 200 Hz IMU data
            {'frame_id': 'imu_link'},
            {'topic_name': 'imu/data'}
        ],
        output='screen',
        emulate_tty=True
    )

    # Node 2: Joint State Controller
    joint_controller_node = Node(
        package='controller_manager',  # Replace with actual package
        executable='joint_state_controller',
        name='joint_controller',
        namespace=robot_name,
        parameters=[
            {'use_sim_time': use_sim_time},
            {'control_rate': 100.0},  # 100 Hz control loop
            {'joint_names': ['shoulder_pitch', 'shoulder_roll', 'elbow', 'wrist']},
            {'pid_gains': {
                'shoulder_pitch': {'kp': 50.0, 'ki': 0.1, 'kd': 5.0},
                'shoulder_roll': {'kp': 45.0, 'ki': 0.1, 'kd': 4.5},
                'elbow': {'kp': 30.0, 'ki': 0.05, 'kd': 3.0},
                'wrist': {'kp': 20.0, 'ki': 0.05, 'kd': 2.0}
            }}
            # In practice, load from YAML: config_file
        ],
        output='screen',
        emulate_tty=True
    )

    # Node 3: State Estimator (sensor fusion)
    state_estimator_node = Node(
        package='robot_localization',  # Replace with actual package
        executable='ekf_node',
        name='state_estimator',
        namespace=robot_name,
        parameters=[
            {'use_sim_time': use_sim_time},
            {'frequency': 50.0},
            {'sensor_timeout': 0.1},
            {'two_d_mode': False},
            {'odom_frame': 'odom'},
            {'base_link_frame': 'base_link'},
            {'world_frame': 'odom'},
            # Sensor input configurations
            {'imu0': f'/{robot_name}/imu/data'},
            {'imu0_config': [False, False, False,  # x, y, z position
                            False, False, False,   # roll, pitch, yaw orientation
                            False, False, False,   # x, y, z velocity
                            True, True, True,      # roll, pitch, yaw velocity
                            True, True, True]},    # x, y, z acceleration
        ],
        output='screen',
        emulate_tty=True
    )

    # Log launch information
    log_info = LogInfo(
        msg=['Launching multi-node humanoid system for robot: ', robot_name]
    )

    # Create launch description with all nodes
    return LaunchDescription([
        use_sim_time_arg,
        robot_name_arg,
        log_info,
        imu_node,
        joint_controller_node,
        state_estimator_node
    ])
```

## Key Concepts Summary

- **ROS 2 Architecture**: Distributed system built on DDS middleware, eliminating single points of failure and enabling real-time communication
- **Nodes**: Independent processes performing specific tasks, discovered automatically through DDS
- **Topics**: Named channels for publish-subscribe communication, ideal for streaming data with QoS policies for reliability and latency control
- **Services**: Synchronous request-response pattern for quick queries and commands
- **Actions**: Asynchronous, goal-oriented tasks with feedback and cancellation support for long-running operations
- **Parameters**: Runtime configuration mechanism with type safety and dynamic reconfiguration
- **Launch Files**: Orchestration system for multi-node deployments with parameter loading and composition support
- **Quality of Service (QoS)**: Configurable policies for reliability, history, durability, and deadlines tailored to application requirements

## References

[1] Open Robotics. (2023). *ROS 2 Humble Documentation*. Retrieved from https://docs.ros.org/en/humble/

[2] Object Management Group. (2015). *Data Distribution Service (DDS) Version 1.4*. OMG Document Number: formal/2015-04-10. https://www.omg.org/spec/DDS/1.4

[3] Maruyama, Y., Kato, S., & Azumi, T. (2016). Exploring the performance of ROS2. *2016 International Conference on Embedded Software (EMSOFT)*, 1-10. https://doi.org/10.1145/2968478.2968502

[4] Macenski, S., Foote, T., Gerkey, B., Lalancette, C., & Woodall, W. (2022). Robot Operating System 2: Design, architecture, and uses in the wild. *Science Robotics*, 7(66), eabm6074. https://doi.org/10.1126/scirobotics.abm6074

[5] Quigley, M., Conley, K., Gerkey, B., Faust, J., Foote, T., Leibs, J., ... & Ng, A. Y. (2009). ROS: an open-source Robot Operating System. *ICRA Workshop on Open Source Software*, 3(3.2), 5.

## Further Reading

- ROS 2 Design Documentation: http://design.ros2.org/
- DDS Security Specification for secure robot communication
- Real-Time Systems and ROS 2: Exploring deadline and priority-based scheduling
- ROS 2 Executor Design Patterns for performance optimization

## Exercises

1. **Publisher-Subscriber Implementation**: Create a ROS 2 package with a publisher node that simulates a 6-axis IMU (linear acceleration and angular velocity) publishing at 100 Hz, and a subscriber node that computes and displays the magnitude of the acceleration vector. Experiment with different QoS profiles (BEST_EFFORT vs RELIABLE) and measure message loss rates.

2. **Service for Inverse Kinematics**: Implement a service server that accepts an end-effector pose (position and orientation) and returns joint angles for a simplified 3-DOF planar arm using geometric inverse kinematics. Create a client that sends random target poses and visualizes the results. Add parameter validation to reject unreachable poses.

3. **Multi-Node Launch Configuration**: Design a launch file for a simulated humanoid sensor suite including two camera nodes, an IMU node, and a LIDAR node. Use launch arguments to support both simulation and hardware modes, loading different parameter files for each. Implement proper namespacing to support running multiple robot instances simultaneously.

4. **Action Server for Trajectory Execution**: Create an action server that accepts a trajectory goal (sequence of joint positions with timestamps) and executes it while providing feedback on progress (percent complete, current waypoint). Implement cancellation handling that safely stops motion. Test with a simple two-joint arm visualization.

5. **Dynamic Parameter Tuning**: Build a PID controller node with dynamically reconfigurable gains (Kp, Ki, Kd). Create a simple 1-DOF simulated system (e.g., damped harmonic oscillator) and demonstrate real-time tuning by updating parameters while the controller runs. Visualize step response improvements as gains are adjusted.

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: Chapter covers ROS 2 fundamentals with emphasis on humanoid robotics applications. Code examples use simplified interfaces but demonstrate correct patterns. Production implementations would use proper message definitions and kinematics libraries.
