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
