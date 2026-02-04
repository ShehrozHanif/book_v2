# Launch file starting Gazebo server, spawning robot, and launching RViz
# Run with: ros2 launch <package_name> gazebo_rviz_demo.launch.py
# Expected output: Gazebo and RViz windows open with synchronized robot visualization

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    """
    Generate launch description for Gazebo + RViz demo.
    Starts Gazebo, spawns humanoid robot, launches RViz with robot model.
    """

    # Path to robot URDF (replace with actual package/file)
    # urdf_file = PathJoinSubstitution([
    #     FindPackageShare('humanoid_description'),
    #     'urdf',
    #     'humanoid.urdf'
    # ])

    # For demonstration, using a simple URDF path
    urdf_file = '/path/to/your/robot.urdf'

    # Path to world file
    # world_file = PathJoinSubstitution([
    #     FindPackageShare('humanoid_gazebo'),
    #     'worlds',
    #     'humanoid_test_world.world'
    # ])
    world_file = '/path/to/your/world.sdf'

    # Path to RViz config
    # rviz_config = PathJoinSubstitution([
    #     FindPackageShare('humanoid_description'),
    #     'config',
    #     'view_robot.rviz'
    # ])
    rviz_config = '/path/to/your/config.rviz'

    # Start Gazebo server (physics simulation without GUI)
    gazebo_server = ExecuteProcess(
        cmd=['gzserver',
             '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             world_file],
        output='screen',
        name='gazebo_server'
    )

    # Start Gazebo client (GUI)
    gazebo_client = ExecuteProcess(
        cmd=['gzclient'],
        output='screen',
        name='gazebo_client'
    )

    # Read robot description from URDF file
    robot_description_content = Command(
        [FindExecutable(name='cat'), ' ', urdf_file]
    )

    # Publish robot description to parameter server
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', 'humanoid_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '1.0',  # Spawn 1 meter above ground
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0'
        ]
    )

    # Joint state publisher (for manually controlling joints in RViz)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # Launch RViz for visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}]
    )

    # Create launch description
    return LaunchDescription([
        # Start Gazebo server first
        gazebo_server,

        # Start Gazebo client after server
        gazebo_client,

        # Publish robot description
        robot_state_publisher,

        # Spawn robot after Gazebo is ready (simplified timing)
        spawn_robot,

        # Launch visualization tools
        joint_state_publisher_gui,
        rviz_node
    ])
