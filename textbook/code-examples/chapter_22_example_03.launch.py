#!/usr/bin/env python3
"""
Chapter 22, Example 3: ROS 2 Launch File

This launch file orchestrates:
1. Gazebo server configuration
2. Walker-Bot robot spawn
3. Controller node launch
4. Parameter server setup
5. RViz visualization configuration

Usage:
    ros2 launch walker_bot_description chapter_22_example_03.launch.py

Expected Behavior:
    - Gazebo launches with empty world
    - Walker-Bot spawns at origin
    - Standing controller activates
    - RViz displays robot model
    - All transforms published correctly

Author: Physical AI & Humanoid Robotics Textbook
Platform: ROS 2 Humble, Gazebo Fortress
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Generate launch description for Walker-Bot simulation."""

    # Package directories
    pkg_gazebo_ros = FindPackageShare('gazebo_ros')
    pkg_walker_bot = FindPackageShare('walker_bot_description')

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')
    world = LaunchConfiguration('world', default='empty')

    # URDF file path
    # In practice, this would be in your walker_bot_description package
    urdf_file = os.path.join(
        os.path.dirname(__file__),
        'chapter_22_example_01.urdf'
    )

    # Read URDF content
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_gui_cmd = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Launch Gazebo GUI if true'
    )

    # Gazebo server
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': world,
            'gui': gui,
            'server_required': 'true',
        }.items()
    )

    # Spawn Walker-Bot
    spawn_walker_bot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'walker_bot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.8',  # Start above ground so it drops into stance
        ],
        output='screen'
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc
        }]
    )

    # Joint state publisher (for non-controlled joints if any)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Walker-Bot controller
    walker_controller = Node(
        package='walker_bot_control',  # You would create this package
        executable='chapter_22_example_02.py',
        name='walker_bot_controller',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # RViz for visualization
    rviz_config = os.path.join(
        os.path.dirname(__file__),
        'walker_bot_rviz.rviz'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(gui)
    )

    # Create and return launch description
    ld = LaunchDescription()

    # Declare launch arguments
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_gui_cmd)

    # Add nodes
    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher)
    ld.add_action(joint_state_publisher)
    ld.add_action(spawn_walker_bot)
    ld.add_action(walker_controller)
    ld.add_action(rviz)

    return ld


if __name__ == '__main__':
    generate_launch_description()
