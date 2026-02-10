---
id: chapter-07
title: "Robot Description & URDF"
sidebar_label: "Ch 07: Robot Description & URDF"
sidebar_position: 7
chapter_id: 7
---


# Chapter 7: Robot Description & URDF

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the URDF XML structure and syntax for describing robot kinematics and geometry
- Create comprehensive robot descriptions including links, joints, collision models, and visual meshes
- Integrate CAD meshes and materials for photorealistic visualization
- Configure Gazebo simulation plugins for sensors and actuators
- Validate URDF files for kinematic correctness and physics simulation readiness

## Introduction

The Unified Robot Description Format (URDF) serves as the lingua franca for robot modeling in the ROS ecosystem. URDF provides a standardized XML-based format for describing robot kinematics, dynamics, geometry, and sensor placement. Every major robotics simulation environment—Gazebo, MoveIt!, RViz—relies on URDF as the canonical representation of robot structure.

For humanoid robotics, URDF files play an essential role throughout the development pipeline. During design, URDF models enable visualization and kinematic validation before physical prototyping. During simulation, URDF files define the robot's physics properties, enabling realistic dynamic simulation. During deployment, URDF descriptions inform motion planning, collision checking, and controller configuration. A well-constructed URDF is foundational to reliable robot software.

URDF's design reflects a balance between expressiveness and simplicity. The format represents robots as kinematic trees: links (rigid bodies) connected by joints (kinematic constraints). Each link possesses visual geometry (for rendering), collision geometry (for physics and planning), and inertial properties (mass, center of mass, inertia tensor). Joints define the kinematic relationships between links, including joint types (revolute, prismatic, fixed), motion limits, and dynamics parameters.

This chapter provides comprehensive coverage of URDF construction, from basic two-link arms to complex humanoid torsos with sensors and actuators. We explore URDF structure and syntax, kinematic trees, inertial properties, mesh integration, material definitions, and Gazebo plugin configuration. The examples progress from minimal educational URDFs to production-ready robot descriptions suitable for simulation and hardware deployment.

## Section 1: URDF Structure and Links

A URDF file consists of a **robot** root element containing multiple **link** and **joint** elements. Links represent rigid bodies, while joints define kinematic relationships between links. The XML structure follows a hierarchical format with clear parent-child relationships encoded in joint definitions.

Each **link** element can contain three primary components: visual, collision, and inertial properties. The **visual** element defines geometry for rendering in visualization tools like RViz. This might be a simple geometric primitive (box, cylinder, sphere) or a complex mesh loaded from a COLLADA (.dae) or STL (.stl) file. Visual geometry should be detailed for realistic visualization but need not exactly match collision geometry.

The **collision** element specifies geometry used for collision detection in physics simulation and motion planning. Collision meshes are typically simplified versions of visual meshes, using convex approximations or bounding volumes to accelerate collision checking algorithms. Overly detailed collision meshes drastically slow simulation and planning, while overly simplified meshes may permit unphysical interpenetration.

**Geometric primitives** in URDF include boxes (specified by length, width, height), cylinders (radius, length), and spheres (radius). These primitives are computationally efficient for collision detection and should be preferred over meshes when adequate. Complex robots often use a hybrid approach: primitives for structural components like torsos and limbs, meshes for intricate geometries like hands and heads.

The **origin** element specifies the pose (position and orientation) of geometric elements relative to the link's reference frame. This allows offsetting visual and collision geometry from the link origin, essential for aligning meshes created in CAD software where the coordinate frame might not match the kinematic reference point.

**Materials** define appearance properties for visualization. A material element specifies a name and color (RGBA values). Materials can be defined inline within a link or globally within the robot element and referenced by name. Advanced visualization systems support texture mapping, but basic URDF materials use only solid colors.

In practice, link reference frames are conventionally placed at joint centers or centers of mass, following modified Denavit-Hartenberg conventions or other kinematic frameworks. Consistent frame placement conventions simplify forward kinematics computation and improve URDF readability.

A minimal link definition might specify only visual geometry for visualization-only robots. A complete link for physics simulation must include all three components: visual (for rendering), collision (for physics), and inertial (for dynamics). Missing or incorrect inertial properties lead to unstable or unrealistic simulation behavior.

## Section 2: Joints and Kinematic Chains

**Joints** define kinematic relationships between links, transforming URDF from a collection of geometric shapes into a structured kinematic chain. Each joint connects a parent link to a child link, specifying the joint's type, axis of motion, position, and limits.

ROS supports six **joint types**: **revolute** (hinge joint with angle limits), **continuous** (unlimited rotation hinge), **prismatic** (slider with linear limits), **fixed** (rigid connection), **floating** (unconstrained 6-DOF), and **planar** (constrained to 2D plane). Humanoid robots primarily use revolute joints for articulated limbs, fixed joints for rigid assemblies, and occasionally prismatic joints for extensible mechanisms.

The **parent** and **child** attributes establish the kinematic tree structure. The parent link is the "base" of the joint transformation, while the child link is transformed relative to the parent. This parent-child hierarchy creates a tree rooted at a single base link, typically representing the robot's torso or base platform.

The **origin** element in a joint specifies the transformation from the parent link's frame to the joint's frame, defined by XYZ position and RPY (roll-pitch-yaw) orientation. This transformation positions the joint relative to the parent link. The child link's frame is then positioned at the joint frame, displaced by the joint variable (angle for revolute, translation for prismatic).

The **axis** element defines the joint's axis of motion in the joint frame, specified as a unit vector (typically [1, 0, 0], [0, 1, 0], or [0, 0, 1]). For revolute joints, the axis defines the rotation axis; for prismatic joints, the translation direction.

**Joint limits** constrain the range of motion using **lower** and **upper** bounds (in radians for revolute, meters for prismatic), **effort** limits (maximum force or torque), and **velocity** limits (maximum angular or linear velocity). These limits are critical for safety and realistic simulation. Physics engines enforce position limits and can enforce velocity and effort limits depending on configuration.

**Joint dynamics** parameters include **damping** (energy dissipation proportional to velocity) and **friction** (constant energy dissipation opposing motion). These parameters improve simulation realism, particularly for systems with gearboxes, cables, or other mechanical transmission elements that introduce energy losses.

Constructing a kinematic chain requires careful attention to frame placement and joint definition. A common pattern for a humanoid arm: shoulder joints (3-DOF shoulder for pitch, roll, yaw), elbow joint (1-DOF revolute), wrist joints (2-DOF or 3-DOF), and gripper joints (typically prismatic or underactuated). The resulting chain enables computing forward kinematics (joint angles to end-effector pose) and inverse kinematics (desired pose to joint angles).

### Code Example 1: 2-Link Arm with Revolute Joints

This URDF defines a simple planar 2-DOF arm for educational purposes.

```xml
<!-- chapter_07_example_01.urdf -->
<!-- 2-link robotic arm with revolute joints -->
<!-- Visualize with: ros2 launch urdf_tutorial display.launch.py model:=chapter_07_example_01.urdf -->

<?xml version="1.0"?>
<robot name="two_link_arm">

  <!-- Base link (fixed to world) -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0"
               iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Link 1 (first arm segment) -->
  <link name="link_1">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.5"/>
      </geometry>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <material name="blue">
        <color rgba="0.2 0.2 0.8 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.03" length="0.5"/>
      </geometry>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <!-- Inertia for solid cylinder: Ixx = Iyy = m(3r^2 + h^2)/12, Izz = mr^2/2 -->
      <inertia ixx="0.021" ixy="0.0" ixz="0.0"
               iyy="0.021" iyz="0.0" izz="0.00045"/>
    </inertial>
  </link>

  <!-- Joint 1 (shoulder joint connecting base to link_1) -->
  <joint name="joint_1" type="revolute">
    <parent link="base_link"/>
    <child link="link_1"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>  <!-- Rotation about Y-axis -->
    <limit lower="-1.57" upper="1.57" effort="10.0" velocity="1.0"/>
    <dynamics damping="0.5" friction="0.1"/>
  </joint>

  <!-- Link 2 (second arm segment) -->
  <link name="link_2">
    <visual>
      <geometry>
        <cylinder radius="0.025" length="0.4"/>
      </geometry>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <material name="red">
        <color rgba="0.8 0.2 0.2 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.025" length="0.4"/>
      </geometry>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <inertia ixx="0.011" ixy="0.0" ixz="0.0"
               iyy="0.011" iyz="0.0" izz="0.00025"/>
    </inertial>
  </link>

  <!-- Joint 2 (elbow joint connecting link_1 to link_2) -->
  <joint name="joint_2" type="revolute">
    <parent link="link_1"/>
    <child link="link_2"/>
    <origin xyz="0 0 0.5" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>  <!-- Rotation about Y-axis -->
    <limit lower="-2.0" upper="2.0" effort="8.0" velocity="1.0"/>
    <dynamics damping="0.3" friction="0.08"/>
  </joint>

  <!-- End-effector link (for reference point) -->
  <link name="end_effector">
    <visual>
      <geometry>
        <sphere radius="0.03"/>
      </geometry>
      <material name="green">
        <color rgba="0.2 0.8 0.2 1.0"/>
      </material>
    </visual>
  </link>

  <!-- Fixed joint to end-effector -->
  <joint name="joint_ee" type="fixed">
    <parent link="link_2"/>
    <child link="end_effector"/>
    <origin xyz="0 0 0.4" rpy="0 0 0"/>
  </joint>

</robot>
```

## Section 3: Inertial Properties

Accurate **inertial properties** are essential for realistic physics simulation. Each link's inertial element specifies mass, center of mass location, and inertia tensor. Incorrect inertial properties lead to unstable simulation, unrealistic dynamics, and controllers that fail when transferred from simulation to hardware.

The **mass** element specifies the link's total mass in kilograms. Humanoid robot masses vary widely: lightweight research platforms like NAO weigh around 5 kg, while heavy-duty humanoids like Atlas exceed 80 kg. Individual link masses range from grams for fingertips to tens of kilograms for torsos.

The **origin** element within inertial properties specifies the center of mass position relative to the link frame. The center of mass is the point where the total mass can be considered concentrated for translational dynamics. For symmetric objects, this is the geometric center; for asymmetric links, it must be computed from CAD models or measured experimentally.

The **inertia tensor** is a 3x3 symmetric matrix describing the link's resistance to rotational acceleration about the three principal axes. URDF specifies six unique elements: ixx, iyy, izz (diagonal moments of inertia), and ixy, ixz, iyz (products of inertia). The inertia tensor depends on both the mass distribution and the reference frame.

For common geometric primitives, inertia tensors can be computed analytically. A solid cylinder of mass m, radius r, and height h rotating about its central axis has Izz = mr²/2 and Ixx = Iyy = m(3r² + h²)/12. A solid sphere of radius r has I = 2mr²/5 for all axes. A box with dimensions x, y, z has Ixx = m(y² + z²)/12, Iyy = m(x² + z²)/12, Izz = m(x² + y²)/12.

For complex geometries defined by meshes, inertial properties must be computed using CAD software or mesh processing libraries. Tools like MeshLab can compute inertia tensors from mesh files assuming uniform density. More accurate results require density-weighted integration over the mesh volume.

**Inertia tensor validation** is critical. The tensor must be positive definite (all diagonal elements positive) and physically realizable. Common errors include swapped axes, incorrect units (kg·m² not kg·cm²), or unrealistic values relative to link dimensions. The parallel axis theorem allows transforming inertia tensors to different reference points: I_new = I_cm + m(d² - dd^T), where d is the offset vector from center of mass to the new origin.

In practice, obtaining accurate inertial properties for humanoid robots is challenging. Physical robots require careful weighing of components and measurement of mass distributions. Simulated robots can compute properties from CAD models, but component-level detail (motors, sensors, wiring) may be missing from kinematic models. Conservative approaches use measured values for critical links (torso, thighs) and analytical approximations for less critical components.

## Section 4: Meshes and Visualization

While geometric primitives suffice for simple robots, realistic humanoid visualization requires **mesh geometry**. URDF supports loading 3D mesh files in COLLADA (.dae) and STL (.stl) formats, enabling photorealistic rendering of complex shapes.

**COLLADA** (Collaborative Design Activity) is an XML-based format supporting geometry, materials, textures, animations, and physics properties. COLLADA files can include embedded textures and material definitions, making them ideal for visualization. Most 3D modeling software (Blender, SolidWorks, Fusion 360) exports COLLADA with full material information preserved.

**STL** (Stereolithography) is a simpler format representing surfaces as triangular meshes without material or texture information. STL files are lightweight and widely supported but require separate material definitions in URDF. STL is often preferred for collision geometry due to its simplicity.

Integrating meshes into URDF requires specifying the **mesh filename** as a URI. ROS packages use the `package://` URI scheme: `package://my_robot_description/meshes/torso.dae` resolves to the meshes directory within the specified package. Absolute file paths and `file://` URIs are also supported but reduce portability.

The **scale** attribute allows resizing meshes, specified as a three-component vector [x, y, z]. This is useful when mesh units don't match URDF's meter convention or when reusing meshes at different scales. However, non-uniform scaling (different scale factors per axis) can distort geometries and should be avoided when possible.

**Mesh optimization** for simulation is crucial. High-polygon visualization meshes cause performance degradation in collision detection and physics engines. Best practice separates visual and collision meshes: detailed meshes for visual elements, simplified convex decompositions for collision elements. Tools like Blender's decimate modifier or MeshLab's simplification algorithms reduce polygon counts while preserving overall shape.

**Convex decomposition** breaks concave meshes into multiple convex components, dramatically accelerating collision detection. Convex shapes enable efficient algorithms like Gilbert-Johnson-Keerthi (GJK) for distance computation. The V-HACD (Volumetric Hierarchical Approximate Convex Decomposition) algorithm automates this process, balancing decomposition quality against computational cost.

**Texture mapping** in COLLADA files applies images to mesh surfaces, creating photorealistic appearances. Textures are referenced within the COLLADA file's material library and should be packaged with the mesh file. RViz and Gazebo support textured meshes, though rendering performance degrades with high-resolution textures or many textured objects.

### Code Example 2: Humanoid Torso with IMU Plugin

This URDF demonstrates a more complex structure with sensor plugins.

```xml
<!-- chapter_07_example_02.urdf -->
<!-- Humanoid torso with IMU sensor plugin for Gazebo -->
<!-- Launch in Gazebo: ros2 launch gazebo_ros spawn_entity.launch.py -entity humanoid_torso -file chapter_07_example_02.urdf -->

<?xml version="1.0"?>
<robot name="humanoid_torso" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Torso link -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.25 0.15 0.40"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="white">
        <color rgba="0.9 0.9 0.9 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.25 0.15 0.40"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="8.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <!-- Inertia for box: I = m(h^2 + d^2)/12 -->
      <inertia ixx="0.127" ixy="0.0" ixz="0.0"
               iyy="0.175" iyz="0.0" izz="0.070"/>
    </inertial>
  </link>

  <!-- IMU sensor link (child of torso) -->
  <link name="imu_link">
    <visual>
      <geometry>
        <box size="0.02 0.02 0.01"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1.0"/>
      </material>
    </visual>
    <inertial>
      <mass value="0.01"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.00001" ixy="0.0" ixz="0.0"
               iyy="0.00001" iyz="0.0" izz="0.00001"/>
    </inertial>
  </link>

  <!-- IMU mount joint -->
  <joint name="imu_joint" type="fixed">
    <parent link="torso"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
  </joint>

  <!-- Shoulder pitch joint (left arm) -->
  <link name="left_shoulder">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.08"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 1.5708 0"/>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.08"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 1.5708 0"/>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 0" rpy="0 1.5708 0"/>
      <inertia ixx="0.0005" ixy="0.0" ixz="0.0"
               iyy="0.0005" iyz="0.0" izz="0.0004"/>
    </inertial>
  </link>

  <joint name="left_shoulder_pitch" type="revolute">
    <parent link="torso"/>
    <child link="left_shoulder"/>
    <origin xyz="0 0.12 0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.8" upper="1.8" effort="50.0" velocity="2.0"/>
    <dynamics damping="1.0" friction="0.5"/>
  </joint>

  <!-- Upper arm link -->
  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.30"/>
      </geometry>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <material name="blue">
        <color rgba="0.3 0.3 0.7 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.03" length="0.30"/>
      </geometry>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="1.2"/>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <inertia ixx="0.009" ixy="0.0" ixz="0.0"
               iyy="0.009" iyz="0.0" izz="0.0005"/>
    </inertial>
  </link>

  <joint name="left_shoulder_roll" type="revolute">
    <parent link="left_shoulder"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.04 0 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.5" upper="2.5" effort="40.0" velocity="2.0"/>
    <dynamics damping="0.8" friction="0.4"/>
  </joint>

  <!-- Gazebo IMU plugin -->
  <gazebo reference="imu_link">
    <sensor name="imu_sensor" type="imu">
      <always_on>true</always_on>
      <update_rate>200.0</update_rate>
      <imu>
        <angular_velocity>
          <x>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.0002</stddev>
            </noise>
          </x>
          <y>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.0002</stddev>
            </noise>
          </y>
          <z>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.0002</stddev>
            </noise>
          </z>
        </angular_velocity>
        <linear_acceleration>
          <x>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.01</stddev>
            </noise>
          </x>
          <y>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.01</stddev>
            </noise>
          </y>
          <z>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.01</stddev>
            </noise>
          </z>
        </linear_acceleration>
      </imu>
      <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>~/out:=imu/data</remapping>
        </ros>
        <frame_name>imu_link</frame_name>
        <initial_orientation_as_reference>false</initial_orientation_as_reference>
      </plugin>
    </sensor>
  </gazebo>

</robot>
```

## Section 5: Gazebo Plugins

**Gazebo plugins** extend URDF functionality, adding sensors, actuators, and environmental interactions to simulated robots. Plugins are specified within `<gazebo>` tags in URDF files, referencing specific links or joints and configuring plugin parameters.

Gazebo supports three plugin categories: **model plugins** (apply to entire robot), **sensor plugins** (implement specific sensors), and **visual plugins** (control rendering). Common sensor plugins include cameras, depth sensors, IMUs, GPS, and force-torque sensors. Actuator plugins provide differential drive controllers, joint controllers, and gripper controllers.

The **IMU sensor plugin** simulates inertial measurement units, publishing linear acceleration and angular velocity. Configuration parameters include update rate, noise models (Gaussian, uniform), and bias parameters. Realistic IMU simulation incorporates measurement noise, bias drift, and reference frame transformations, essential for developing robust state estimation algorithms.

**Camera plugins** simulate RGB cameras, publishing image messages compatible with ROS image transport. Parameters include resolution, field of view, update rate, distortion coefficients, and optical frame definitions. Advanced camera plugins support depth cameras (RGB-D sensors like Kinect), stereo cameras, and 360-degree panoramic cameras.

**LiDAR/laser scanner plugins** simulate range-finding sensors, publishing LaserScan messages containing distance measurements. Configuration includes angular range, angular resolution, maximum range, and noise characteristics. Multi-layer LiDARs (Velodyne-style 3D scanners) use specialized plugins publishing PointCloud2 messages.

**Actuator plugins** interface with Gazebo's physics engine to control joint motion. The **differential drive plugin** simulates wheeled robots, accepting velocity commands and publishing odometry. The **joint state controller** publishes current joint positions and velocities. The **joint trajectory controller** executes trajectory commands, enabling integration with motion planning systems like MoveIt!.

Plugin configuration within URDF uses XML elements specific to each plugin. The **ros** element specifies ROS namespaces and topic remappings, enabling multiple robot instances without topic name collisions. The **frame_name** specifies the reference frame for sensor data, critical for coordinate frame transformations in sensor fusion.

**Noise models** improve simulation realism. Sensors in the real world exhibit measurement noise, bias, and drift. Gaussian noise models are most common, specified by mean (bias) and standard deviation. More sophisticated models include bias random walk (slowly varying bias) and scale factor errors (measurement proportional to true value).

### Code Example 3: URDF Validation Script

This Python script validates URDF structure and computes kinematic properties.

```python
# chapter_07_example_03.py
# URDF validation and analysis script
# Run with: python chapter_07_example_03.py <urdf_file>
# Expected output: Validation report with link/joint analysis and kinematic chain structure

import sys
import xml.etree.ElementTree as ET
import numpy as np


class URDFValidator:
    """Validates URDF files for common errors and computes kinematic properties."""

    def __init__(self, urdf_file):
        """Load and parse URDF file."""
        self.tree = ET.parse(urdf_file)
        self.root = self.tree.getroot()
        self.robot_name = self.root.get('name', 'unnamed')
        self.links = {}
        self.joints = {}
        self.errors = []
        self.warnings = []

    def validate(self):
        """Run all validation checks."""
        print(f"\n=== URDF Validation Report for '{self.robot_name}' ===\n")

        self._parse_links()
        self._parse_joints()
        self._check_kinematic_tree()
        self._validate_inertial_properties()
        self._validate_joint_limits()

        self._print_report()

    def _parse_links(self):
        """Extract and validate all links."""
        for link in self.root.findall('link'):
            name = link.get('name')
            if not name:
                self.errors.append("Link found without name attribute")
                continue

            self.links[name] = {
                'has_visual': link.find('visual') is not None,
                'has_collision': link.find('collision') is not None,
                'has_inertial': link.find('inertial') is not None,
                'element': link
            }

        print(f"Found {len(self.links)} links:")
        for name, props in self.links.items():
            visual_marker = "✓" if props['has_visual'] else "✗"
            collision_marker = "✓" if props['has_collision'] else "✗"
            inertial_marker = "✓" if props['has_inertial'] else "✗"
            print(f"  - {name:20s} [V:{visual_marker} C:{collision_marker} I:{inertial_marker}]")

            # Check for missing collision geometry
            if props['has_visual'] and not props['has_collision']:
                self.warnings.append(f"Link '{name}' has visual but no collision geometry")

    def _parse_joints(self):
        """Extract and validate all joints."""
        for joint in self.root.findall('joint'):
            name = joint.get('name')
            joint_type = joint.get('type', 'unknown')

            if not name:
                self.errors.append("Joint found without name attribute")
                continue

            parent_elem = joint.find('parent')
            child_elem = joint.find('child')

            if parent_elem is None or child_elem is None:
                self.errors.append(f"Joint '{name}' missing parent or child")
                continue

            parent = parent_elem.get('link')
            child = child_elem.get('link')

            self.joints[name] = {
                'type': joint_type,
                'parent': parent,
                'child': child,
                'axis': self._get_joint_axis(joint),
                'limits': self._get_joint_limits(joint),
                'element': joint
            }

        print(f"\nFound {len(self.joints)} joints:")
        for name, props in self.joints.items():
            print(f"  - {name:20s} [{props['type']:10s}] {props['parent']} -> {props['child']}")

    def _get_joint_axis(self, joint):
        """Extract joint axis vector."""
        axis_elem = joint.find('axis')
        if axis_elem is not None:
            xyz_str = axis_elem.get('xyz', '1 0 0')
            return [float(x) for x in xyz_str.split()]
        return [1, 0, 0]

    def _get_joint_limits(self, joint):
        """Extract joint limits."""
        limit_elem = joint.find('limit')
        if limit_elem is not None:
            return {
                'lower': float(limit_elem.get('lower', '0')),
                'upper': float(limit_elem.get('upper', '0')),
                'effort': float(limit_elem.get('effort', '0')),
                'velocity': float(limit_elem.get('velocity', '0'))
            }
        return None

    def _check_kinematic_tree(self):
        """Validate kinematic tree structure (no cycles, single root)."""
        print("\n=== Kinematic Tree Structure ===")

        # Find root links (links that are not children of any joint)
        child_links = {j['child'] for j in self.joints.values()}
        root_links = [name for name in self.links.keys() if name not in child_links]

        if len(root_links) == 0:
            self.errors.append("No root link found (cyclic kinematic tree)")
        elif len(root_links) > 1:
            self.warnings.append(f"Multiple root links found: {root_links}")
            print(f"Root links: {', '.join(root_links)}")
        else:
            print(f"Root link: {root_links[0]}")
            self._print_kinematic_tree(root_links[0], indent=0)

    def _print_kinematic_tree(self, link_name, indent=0):
        """Recursively print kinematic tree structure."""
        children = [(j_name, j['child'], j['type'])
                   for j_name, j in self.joints.items()
                   if j['parent'] == link_name]

        for joint_name, child_name, joint_type in children:
            print(f"  {'  ' * indent}└─ [{joint_type:10s}] {joint_name} -> {child_name}")
            self._print_kinematic_tree(child_name, indent + 1)

    def _validate_inertial_properties(self):
        """Check inertial properties for physics validity."""
        print("\n=== Inertial Properties Validation ===")

        for name, props in self.links.items():
            if not props['has_inertial']:
                continue

            inertial = props['element'].find('inertial')
            mass_elem = inertial.find('mass')
            inertia_elem = inertial.find('inertia')

            if mass_elem is None:
                self.errors.append(f"Link '{name}' has inertial but no mass")
                continue

            mass = float(mass_elem.get('value', '0'))
            if mass <= 0:
                self.errors.append(f"Link '{name}' has non-positive mass: {mass}")

            if inertia_elem is None:
                self.errors.append(f"Link '{name}' has inertial but no inertia tensor")
                continue

            # Extract inertia tensor
            ixx = float(inertia_elem.get('ixx', '0'))
            iyy = float(inertia_elem.get('iyy', '0'))
            izz = float(inertia_elem.get('izz', '0'))

            # Check for positive diagonal elements
            if ixx <= 0 or iyy <= 0 or izz <= 0:
                self.errors.append(f"Link '{name}' has non-positive inertia diagonal: [{ixx}, {iyy}, {izz}]")

            print(f"  {name:20s} mass={mass:6.3f} kg, I_diag=[{ixx:.6f}, {iyy:.6f}, {izz:.6f}]")

    def _validate_joint_limits(self):
        """Validate joint limits for revolute and prismatic joints."""
        print("\n=== Joint Limits Validation ===")

        for name, props in self.joints.items():
            if props['type'] not in ['revolute', 'prismatic']:
                continue

            limits = props['limits']
            if limits is None:
                self.errors.append(f"Joint '{name}' ({props['type']}) missing limit specification")
                continue

            if limits['lower'] >= limits['upper']:
                self.errors.append(f"Joint '{name}' has invalid limits: [{limits['lower']}, {limits['upper']}]")

            if limits['effort'] <= 0:
                self.warnings.append(f"Joint '{name}' has zero or negative effort limit")

            if limits['velocity'] <= 0:
                self.warnings.append(f"Joint '{name}' has zero or negative velocity limit")

            print(f"  {name:20s} pos:[{limits['lower']:6.2f}, {limits['upper']:6.2f}] "
                  f"eff:{limits['effort']:6.1f} vel:{limits['velocity']:6.2f}")

    def _print_report(self):
        """Print summary of validation results."""
        print("\n" + "=" * 60)
        print(f"Validation Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 60)

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ! {warning}")

        if not self.errors and not self.warnings:
            print("\n✓ URDF validation passed with no errors or warnings!")


def main():
    """Main function to run URDF validation."""
    if len(sys.argv) != 2:
        print("Usage: python chapter_07_example_03.py <urdf_file>")
        sys.exit(1)

    urdf_file = sys.argv[1]

    try:
        validator = URDFValidator(urdf_file)
        validator.validate()
    except FileNotFoundError:
        print(f"Error: URDF file '{urdf_file}' not found")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing URDF file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Key Concepts Summary

- **URDF Structure**: XML-based format defining robots as kinematic trees with links (rigid bodies) and joints (kinematic constraints)
- **Links**: Possess visual geometry (rendering), collision geometry (physics/planning), and inertial properties (dynamics)
- **Joints**: Connect links with defined types (revolute, prismatic, fixed), axes, limits, and dynamics parameters
- **Kinematic Trees**: Hierarchical parent-child structure rooted at base link, enabling forward kinematics computation
- **Inertial Properties**: Mass, center of mass, and inertia tensor required for physics simulation and dynamics analysis
- **Mesh Integration**: COLLADA and STL files provide detailed geometry, separated into visual (detailed) and collision (simplified) meshes
- **Gazebo Plugins**: Extend simulation with sensors (IMU, camera, LiDAR) and actuators, configured within URDF files
- **Validation**: Essential to check kinematic tree structure, inertial property validity, and joint limit consistency

## References

[1] ROS Wiki. (2023). *URDF XML Specification*. Retrieved from http://wiki.ros.org/urdf/XML

[2] Open Source Robotics Foundation. (2023). *Gazebo Plugins Documentation*. Retrieved from https://gazebosim.org/api/gazebo/6.0/namespacegz_1_1sim_1_1systems.html

[3] Smits, R. (2012). *KDL: Kinematics and Dynamics Library*. Orocos Project. Retrieved from http://www.orocos.org/kdl

[4] Featherstone, R. (2014). *Rigid Body Dynamics Algorithms*. Springer. https://doi.org/10.1007/978-1-4899-7560-7

[5] Schoellig, A. P., & D'Andrea, R. (2020). Optimization-based iterative learning for precise quadrocopter trajectory tracking. *Autonomous Robots*, 33(1-2), 103-127. https://doi.org/10.1007/s10514-012-9283-2

## Further Reading

- URDF Tutorial Series: http://wiki.ros.org/urdf/Tutorials
- Gazebo Simulation Tutorial: http://gazebosim.org/tutorials
- ROS 2 URDF Launch Patterns and best practices
- SDF (Simulation Description Format) as extension of URDF for Gazebo

## Exercises

1. **Multi-DOF Arm URDF**: Create a URDF for a 6-DOF robotic arm suitable for humanoid manipulation. Include appropriate joint limits based on human arm range of motion, realistic inertial properties, and both visual and collision geometry. Visualize in RViz and verify forward kinematics using the `joint_state_publisher_gui`.

2. **Inertia Tensor Computation**: Write a Python script that reads a URDF file and computes the total robot mass and combined inertia tensor about the base frame. Validate your implementation against analytically computed values for simple geometric robots. Extend to compute zero moment point (ZMP) for given joint configurations.

3. **Gazebo Sensor Integration**: Extend Example 2's torso URDF with additional sensors: a forward-facing camera (640x480, 60 FPS), a planar LiDAR (270-degree scan, 1-degree resolution), and contact sensors on the feet. Configure realistic noise models for each sensor. Launch in Gazebo and verify sensor data publication.

4. **URDF Optimization**: Take a complex humanoid URDF and optimize it for simulation performance. Create simplified collision meshes using convex decomposition, reduce polygon counts while preserving visual appearance, and validate that collision detection performance improves (measure simulation real-time factor before and after).

5. **Dynamic URDF Generation**: Create a Python script that procedurally generates URDF files for N-link serial manipulators with parameterized link lengths, masses, and joint limits. Implement scaling laws to ensure physically realistic inertial properties. Generate URDFs for 3-DOF, 5-DOF, and 7-DOF arms and compare their workspaces and manipulability ellipsoids.

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: Chapter covers URDF fundamentals with emphasis on humanoid robot modeling. Examples progress from simple educational models to production-ready descriptions with sensor plugins. Validation script provides practical tool for URDF development.
