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
