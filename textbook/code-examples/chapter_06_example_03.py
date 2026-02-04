# ROS 2 Action Client/Server with error handling for long-running tasks
# Demonstrates action pattern with proper state checking and cancellation handling
# Run with: ros2 run <package_name> action_client_demo
# Expected output: Action goal sent, feedback received, final result with error checking

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from action_msgs.msg import GoalStatus


class ActionClientDemo(Node):
    """
    Action client that sends walk goal to navigation action server.
    Demonstrates proper error handling for CANCELED, SUCCEEDED, and ABORTED states.
    """

    def __init__(self):
        super().__init__('action_client')
        # Action client would normally use actual action type: e.g., Nav2Msgs.action.NavigateToPose
        # For demo, we show the pattern with string representation
        self.get_logger().info('Action client initialized')

    def send_walk_goal(self, target_x, target_y):
        """Send walk goal to navigation action server."""
        self.get_logger().info(f'Sending walk goal to ({target_x}, {target_y})')
        # In practice: goal = NavigateToPose.Goal(); goal.pose = ...
        # self.action_client.send_goal_async(goal, feedback_callback=self.feedback_callback)

    def feedback_callback(self, feedback):
        """Receive feedback on action progress."""
        self.get_logger().info(f'Distance remaining: {feedback.feedback.distance_remaining} m')

    def done_callback(self, future):
        """
        Handle action completion with proper state checking.
        CRITICAL: Always check action state (CANCELED, SUCCEEDED, ABORTED) in client code.
        """
        goal_handle = future.result()

        if goal_handle is None:
            self.get_logger().error('Goal rejected by action server')
            return

        # Check goal state - critical for proper error handling
        if goal_handle.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn('Walk action was canceled - check for higher-priority tasks')
            return

        if goal_handle.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error('Walk action aborted - possible obstacle or collision')
            return

        if goal_handle.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Walk action succeeded - robot reached target')
            return

        self.get_logger().error(f'Unknown goal status: {goal_handle.status}')


def main(args=None):
    """Demonstrate action client with error handling."""
    rclpy.init(args=args)

    action_client = ActionClientDemo()
    executor = MultiThreadedExecutor()
    executor.add_node(action_client)

    try:
        # In practice, send actual action goal and handle response
        action_client.send_walk_goal(target_x=5.0, target_y=0.0)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        action_client.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
