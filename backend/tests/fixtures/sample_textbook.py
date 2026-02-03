"""Sample textbook data for testing embedding and indexing."""

# Sample textbook chunks for ROS 2 and Humanoid Robotics textbook
SAMPLE_CHUNKS = [
    {
        "content": "ROS 2 (Robot Operating System 2) is a flexible middleware for writing robot software. It is a collection of tools and libraries that help you build robot applications across a wide variety of robotic platforms. ROS 2 is built on top of DDS (Data Distribution Service), which provides a pub-sub model for inter-process communication.",
        "module": "Module 1",
        "chapter": "Chapter 1: Fundamentals",
        "section": "1.1 Introduction to ROS 2",
    },
    {
        "content": "The core concept in ROS 2 is the ability to design complex robot software systems by composing reusable software components. ROS 2 promotes the development of robust and modular robot software by using communication patterns that are well-established in other domains of engineering.",
        "module": "Module 1",
        "chapter": "Chapter 1: Fundamentals",
        "section": "1.2 Core Concepts",
    },
    {
        "content": "A ROS 2 node is a basic unit of ROS computation. Nodes are processes that perform computation. ROS 2 is designed to enable scalable, flexible, and dynamic software for robotics by allowing these computational units to be loosely coupled, easily discoverable, and capable of communicating over heterogeneous transport layers.",
        "module": "Module 1",
        "chapter": "Chapter 2: Nodes and Topics",
        "section": "2.1 Understanding Nodes",
    },
    {
        "content": "Topics are named buses over which nodes exchange messages. In ROS 2, a topic is a named channel to which nodes can both publish and subscribe. This is the primary mechanism for intra-process communication in ROS 2. Topics use a many-to-many communication pattern where multiple nodes can both publish and subscribe to the same topic.",
        "module": "Module 1",
        "chapter": "Chapter 2: Nodes and Topics",
        "section": "2.2 Topic-Based Communication",
    },
    {
        "content": "Services provide a synchronous request-response communication model in ROS 2. Unlike topics which are asynchronous, services are useful for scenarios where a node needs a response to a request. Services follow a client-server pattern where the service client sends a request and waits for the server to send a response.",
        "module": "Module 1",
        "chapter": "Chapter 3: Services and Actions",
        "section": "3.1 Service-Based Communication",
    },
    {
        "content": "Humanoid robotics is the field of robotics that focuses on designing and developing robots with a human-like form factor. Humanoid robots typically have a head, torso, two arms, and two legs, mimicking the morphology of humans. This design allows humanoid robots to interact with human environments and tools designed for human use.",
        "module": "Module 2",
        "chapter": "Chapter 4: Humanoid Robotics Basics",
        "section": "4.1 Introduction to Humanoid Robots",
    },
    {
        "content": "Forward kinematics is the process of calculating the end-effector position and orientation from the joint angles of a robotic arm. Given a set of joint angles, we can use forward kinematics to determine where the end-effector (e.g., gripper) is located in three-dimensional space. This is fundamental to motion planning and control in robotics.",
        "module": "Module 2",
        "chapter": "Chapter 5: Kinematics",
        "section": "5.1 Forward Kinematics",
    },
    {
        "content": "Inverse kinematics is the process of calculating the joint angles required to position the end-effector at a desired location and orientation. Unlike forward kinematics, which has a unique solution, inverse kinematics can have multiple solutions or no solution depending on the robot configuration and the desired position.",
        "module": "Module 2",
        "chapter": "Chapter 5: Kinematics",
        "section": "5.2 Inverse Kinematics",
    },
    {
        "content": "Dynamic walking is one of the most challenging aspects of humanoid robotics. Humanoid robots must maintain balance while walking, which requires active control of the center of mass and careful coordination of leg movements. Various walking algorithms such as the linear inverted pendulum model and zero moment point (ZMP) control are used to achieve stable locomotion.",
        "module": "Module 2",
        "chapter": "Chapter 6: Locomotion",
        "section": "6.1 Dynamic Walking",
    },
    {
        "content": "Grasping and manipulation are essential capabilities for humanoid robots to interact with objects in their environment. A robust grasp requires considering the geometry of the object, the capabilities of the gripper, and the forces that can be exerted. Motion planning algorithms are used to plan trajectories for the arm and gripper to achieve desired grasps.",
        "module": "Module 3",
        "chapter": "Chapter 7: Manipulation",
        "section": "7.1 Grasping Strategies",
    },
    {
        "content": "Sensor fusion combines data from multiple sensors to provide a more accurate and robust perception of the environment. In humanoid robots, sensor fusion can combine data from cameras, depth sensors, tactile sensors, and inertial measurement units (IMUs) to create a comprehensive understanding of the robot's surroundings and its own state.",
        "module": "Module 3",
        "chapter": "Chapter 8: Perception",
        "section": "8.1 Sensor Fusion",
    },
    {
        "content": "Motion planning is the process of finding a collision-free path for the robot to move from an initial configuration to a goal configuration. Common motion planning algorithms include RRT (Rapidly-exploring Random Trees), PRM (Probabilistic Roadmap), and various sampling-based approaches. These algorithms must consider the robot's kinematics, dynamics, and constraints.",
        "module": "Module 3",
        "chapter": "Chapter 9: Motion Planning",
        "section": "9.1 Path Planning Algorithms",
    },
]

# Test chunk for embedding endpoint
SINGLE_TEST_CHUNK = {
    "content": "This is a test chunk about ROS 2. ROS 2 is a modern robotics middleware that enables flexible robot software development.",
    "module": "Module 1",
    "chapter": "Chapter 1",
    "section": "1.0 Test Section",
}

# Minimal chunks for quick testing
MINIMAL_CHUNKS = [
    {
        "content": "ROS 2 is a robotics middleware.",
        "module": "Module 1",
        "chapter": "Chapter 1",
        "section": "1.1 Introduction",
    },
    {
        "content": "Humanoid robots have a human-like form factor.",
        "module": "Module 2",
        "chapter": "Chapter 4",
        "section": "4.1 Introduction",
    },
]
