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
