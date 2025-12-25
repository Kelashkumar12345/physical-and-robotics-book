---
sidebar_position: 4
title: "Week 4: Topics, Services & Actions"
---

# Week 4: Topics, Services & Actions

## Learning Objectives

By the end of this week, you will be able to:

- Understand the three primary ROS 2 communication patterns
- Implement publishers and subscribers with QoS profiles
- Create custom service clients and servers
- Build action servers and clients for long-running tasks
- Configure Quality of Service (QoS) settings for different use cases

## 1. ROS 2 Communication Patterns Overview

ROS 2 provides three fundamental communication mechanisms, each designed for specific use cases:

### Topics (Publish/Subscribe)
- **Use Case**: Continuous data streams (sensor data, odometry, camera feeds)
- **Pattern**: One-to-many, asynchronous
- **Direction**: Unidirectional
- **Best For**: High-frequency data that multiple nodes need to consume

### Services (Request/Response)
- **Use Case**: Discrete, synchronous operations (calculate trajectory, trigger action)
- **Pattern**: One-to-one, synchronous
- **Direction**: Bidirectional
- **Best For**: Short-duration computations or state queries

### Actions (Goal-based)
- **Use Case**: Long-running tasks with feedback (navigation, manipulation)
- **Pattern**: One-to-one, asynchronous with feedback
- **Direction**: Bidirectional with status updates
- **Best For**: Tasks that take time and need progress monitoring

## 2. Deep Dive: Topics

### Publisher-Subscriber Architecture

Topics use a publish-subscribe pattern where:
- Publishers send messages without knowing who receives them
- Subscribers receive messages from topics they're interested in
- Multiple publishers and subscribers can exist for a single topic
- Communication is decoupled and asynchronous

### Advanced Topic Examples

#### Creating a Temperature Sensor Publisher

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
import random

class TemperatureSensorNode(Node):
    def __init__(self):
        super().__init__('temperature_sensor')

        # Create publisher
        self.publisher_ = self.create_publisher(
            Temperature,
            'temperature/ambient',
            10  # Queue size
        )

        # Create timer for periodic publishing (1 Hz)
        self.timer = self.create_timer(1.0, self.publish_temperature)

        # Initialize sensor reading
        self.base_temp = 20.0

        self.get_logger().info('Temperature sensor node started')

    def publish_temperature(self):
        msg = Temperature()

        # Simulate temperature reading with noise
        msg.temperature = self.base_temp + random.uniform(-2.0, 2.0)
        msg.variance = 0.5

        # Set header timestamp
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.temperature:.2f}°C')

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureSensorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### Creating a Temperature Monitor Subscriber

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature

class TemperatureMonitorNode(Node):
    def __init__(self):
        super().__init__('temperature_monitor')

        # Create subscriber
        self.subscription = self.create_subscription(
            Temperature,
            'temperature/ambient',
            self.temperature_callback,
            10  # Queue size
        )

        # Track temperature statistics
        self.temp_readings = []
        self.max_readings = 10

        self.get_logger().info('Temperature monitor node started')

    def temperature_callback(self, msg):
        temp = msg.temperature

        # Store reading
        self.temp_readings.append(temp)
        if len(self.temp_readings) > self.max_readings:
            self.temp_readings.pop(0)

        # Calculate statistics
        avg_temp = sum(self.temp_readings) / len(self.temp_readings)
        min_temp = min(self.temp_readings)
        max_temp = max(self.temp_readings)

        # Check for alerts
        if temp > 25.0:
            self.get_logger().warn(f'High temperature alert: {temp:.2f}°C')

        self.get_logger().info(
            f'Current: {temp:.2f}°C | '
            f'Avg: {avg_temp:.2f}°C | '
            f'Range: [{min_temp:.2f}, {max_temp:.2f}]°C'
        )

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureMonitorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 3. Quality of Service (QoS) Profiles

QoS policies allow fine-grained control over message delivery behavior. This is crucial for different types of data and network conditions.

### Key QoS Policies

#### Reliability
- **Reliable**: Guarantees delivery (TCP-like) - use for critical data
- **Best Effort**: No delivery guarantee (UDP-like) - use for high-frequency sensor data

#### Durability
- **Volatile**: Only sends to current subscribers
- **Transient Local**: Stores messages for late-joining subscribers

#### History
- **Keep Last**: Stores last N messages
- **Keep All**: Stores all messages (memory permitting)

#### Deadline
- Expected maximum time between messages

#### Lifespan
- Maximum age of a message before it's considered stale

### QoS Profile Examples

```python
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy

# Sensor data QoS (high frequency, best effort)
sensor_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

# Parameters QoS (reliable, persistent)
parameter_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=100
)

# Services QoS (reliable, no history needed)
services_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)
```

### Using QoS in Publishers and Subscribers

```python
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import LaserScan

class LidarPublisherNode(Node):
    def __init__(self):
        super().__init__('lidar_publisher')

        # Configure QoS for high-frequency sensor data
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5  # Only keep last 5 scans
        )

        self.publisher_ = self.create_publisher(
            LaserScan,
            'scan',
            qos_profile
        )

        # Publish at 10 Hz (typical LiDAR frequency)
        self.timer = self.create_timer(0.1, self.publish_scan)

        self.get_logger().info('LiDAR publisher started with BEST_EFFORT QoS')

    def publish_scan(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'
        msg.angle_min = -3.14
        msg.angle_max = 3.14
        msg.angle_increment = 0.01
        msg.range_min = 0.1
        msg.range_max = 10.0

        # Simulate laser scan data
        msg.ranges = [1.0] * 628  # 628 points for full 360 degrees

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 4. Services: Request/Response Pattern

Services provide synchronous, request-response communication for discrete operations.

### Creating a Custom Service

First, define a service in `my_robot_interfaces/srv/ComputeRectangleArea.srv`:

```
# Request
float64 length
float64 width
---
# Response
float64 area
```

### Service Server Implementation

```python
import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import ComputeRectangleArea

class AreaCalculatorServer(Node):
    def __init__(self):
        super().__init__('area_calculator_server')

        # Create service
        self.srv = self.create_service(
            ComputeRectangleArea,
            'compute_rectangle_area',
            self.compute_area_callback
        )

        self.get_logger().info('Area calculator service ready')

    def compute_area_callback(self, request, response):
        # Validate input
        if request.length <= 0 or request.width <= 0:
            self.get_logger().error('Invalid dimensions received')
            response.area = -1.0
            return response

        # Compute area
        response.area = request.length * request.width

        self.get_logger().info(
            f'Computing area: {request.length} x {request.width} = {response.area}'
        )

        return response

def main(args=None):
    rclpy.init(args=args)
    node = AreaCalculatorServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Service Client Implementation

```python
import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import ComputeRectangleArea
import sys

class AreaCalculatorClient(Node):
    def __init__(self):
        super().__init__('area_calculator_client')

        # Create client
        self.client = self.create_client(
            ComputeRectangleArea,
            'compute_rectangle_area'
        )

        # Wait for service to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

    def send_request(self, length, width):
        # Create request
        request = ComputeRectangleArea.Request()
        request.length = length
        request.width = width

        # Send request asynchronously
        future = self.client.call_async(request)

        return future

def main(args=None):
    rclpy.init(args=args)

    if len(sys.argv) < 3:
        print('Usage: ros2 run my_package area_client <length> <width>')
        return

    length = float(sys.argv[1])
    width = float(sys.argv[2])

    node = AreaCalculatorClient()
    future = node.send_request(length, width)

    # Wait for result
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        response = future.result()
        node.get_logger().info(f'Area: {response.area}')
    else:
        node.get_logger().error('Service call failed')

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 5. Actions: Long-Running Tasks with Feedback

Actions are ideal for tasks that take time and require progress updates, cancellation support, and result reporting.

### Action Definition

Define an action in `my_robot_interfaces/action/Navigate.action`:

```
# Goal
geometry_msgs/PoseStamped target_pose
---
# Result
bool success
float32 total_distance
---
# Feedback
geometry_msgs/PoseStamped current_pose
float32 distance_remaining
float32 estimated_time_remaining
```

### Action Server Implementation

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from my_robot_interfaces.action import Navigate
from geometry_msgs.msg import PoseStamped
import time
import math

class NavigationActionServer(Node):
    def __init__(self):
        super().__init__('navigation_action_server')

        # Create action server
        self._action_server = ActionServer(
            self,
            Navigate,
            'navigate_to_pose',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info('Navigation action server ready')

    def goal_callback(self, goal_request):
        """Accept or reject a client request to begin an action."""
        self.get_logger().info('Received goal request')

        # Could add validation logic here
        # For now, accept all goals
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """Execute the goal."""
        self.get_logger().info('Executing goal...')

        # Extract goal
        target_pose = goal_handle.request.target_pose

        # Simulate navigation
        feedback_msg = Navigate.Feedback()

        # Calculate total distance (simplified 2D)
        total_distance = math.sqrt(
            target_pose.pose.position.x**2 +
            target_pose.pose.position.y**2
        )

        steps = 10
        for i in range(steps):
            # Check if cancellation requested
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')

                result = Navigate.Result()
                result.success = False
                result.total_distance = 0.0
                return result

            # Update feedback
            progress = (i + 1) / steps
            feedback_msg.distance_remaining = total_distance * (1 - progress)
            feedback_msg.estimated_time_remaining = (steps - i - 1) * 0.5

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(
                f'Progress: {progress*100:.1f}% | '
                f'Remaining: {feedback_msg.distance_remaining:.2f}m'
            )

            # Simulate work
            time.sleep(0.5)

        # Mark goal as succeeded
        goal_handle.succeed()

        # Create result
        result = Navigate.Result()
        result.success = True
        result.total_distance = total_distance

        self.get_logger().info(f'Goal succeeded! Distance: {total_distance:.2f}m')

        return result

def main(args=None):
    rclpy.init(args=args)
    node = NavigationActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Action Client Implementation

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.action import Navigate
from geometry_msgs.msg import PoseStamped

class NavigationActionClient(Node):
    def __init__(self):
        super().__init__('navigation_action_client')

        # Create action client
        self._action_client = ActionClient(
            self,
            Navigate,
            'navigate_to_pose'
        )

    def send_goal(self, x, y):
        """Send navigation goal."""
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        # Create goal message
        goal_msg = Navigate.Goal()
        goal_msg.target_pose = PoseStamped()
        goal_msg.target_pose.header.frame_id = 'map'
        goal_msg.target_pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.target_pose.pose.position.x = x
        goal_msg.target_pose.pose.position.y = y
        goal_msg.target_pose.pose.orientation.w = 1.0

        self.get_logger().info(f'Sending goal: ({x}, {y})')

        # Send goal and register callbacks
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle goal acceptance/rejection."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        # Get result
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle feedback from action server."""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Feedback: {feedback.distance_remaining:.2f}m remaining | '
            f'ETA: {feedback.estimated_time_remaining:.1f}s'
        )

    def get_result_callback(self, future):
        """Handle final result."""
        result = future.result().result

        if result.success:
            self.get_logger().info(
                f'Navigation succeeded! Distance: {result.total_distance:.2f}m'
            )
        else:
            self.get_logger().error('Navigation failed')

def main(args=None):
    rclpy.init(args=args)
    node = NavigationActionClient()

    # Send goal to position (5.0, 3.0)
    node.send_goal(5.0, 3.0)

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 6. Practical Exercise: Building a Robot Controller

Create a complete system that combines topics, services, and actions:

### System Architecture

```
┌─────────────────┐
│  Sensor Node    │──(topic)──> /sensor/data
└─────────────────┘

┌─────────────────┐
│ Control Node    │──(service)──> /set_parameters
│                 │──(action)──> /execute_motion
└─────────────────┘

┌─────────────────┐
│ Monitor Node    │──(subscribes)──> /sensor/data
│                 │──(calls service)──> /set_parameters
│                 │──(sends goals)──> /execute_motion
└─────────────────┘
```

### When to Use Each Pattern

**Topics**:
- Sensor data streaming (IMU, cameras, LiDAR)
- Robot state publishing (odometry, joint states)
- Continuous monitoring and visualization
- Broadcasting information to multiple consumers

**Services**:
- Configuration changes (set parameters, change modes)
- State queries (get current position, check status)
- Short computations (inverse kinematics, path validation)
- One-time operations (calibration, reset)

**Actions**:
- Navigation to waypoints
- Manipulation tasks (pick and place)
- Long computations with progress (mapping, planning)
- Cancelable operations (emergency stop support)

## 7. Best Practices

### Topic Design
- Use descriptive, hierarchical names (`/robot/sensor/camera/image`)
- Match QoS between publishers and subscribers
- Keep message sizes reasonable for network efficiency
- Use standard message types when possible

### Service Design
- Keep service calls short (< 1 second)
- Return error codes in responses
- Document expected behavior and constraints
- Consider timeouts for reliability

### Action Design
- Provide meaningful feedback at regular intervals
- Support graceful cancellation
- Use appropriate result types
- Implement proper error handling

### QoS Selection Guide

| Data Type | Reliability | Durability | History |
|-----------|-------------|------------|---------|
| Sensor streams | Best Effort | Volatile | Keep Last (small) |
| Commands | Reliable | Volatile | Keep Last (10-100) |
| Parameters | Reliable | Transient Local | Keep Last (100+) |
| Diagnostic data | Reliable | Volatile | Keep All |

## 8. Debugging and Monitoring

### Command-Line Tools

```bash
# List all topics
ros2 topic list

# Show topic info and QoS
ros2 topic info /my_topic --verbose

# Echo topic messages
ros2 topic echo /my_topic

# Measure topic frequency
ros2 topic hz /my_topic

# Call a service
ros2 service call /compute_area my_robot_interfaces/srv/ComputeRectangleArea "{length: 5.0, width: 3.0}"

# Send action goal
ros2 action send_goal /navigate_to_pose my_robot_interfaces/action/Navigate "{target_pose: {pose: {position: {x: 5.0, y: 3.0}}}}" --feedback

# List all services
ros2 service list

# List all actions
ros2 action list
```

### Introspection in Code

```python
# Check if service is available
if self.client.service_is_ready():
    # Make service call
    pass

# Get number of subscribers
num_subscribers = self.publisher_.get_subscription_count()

# Check action server availability
if self._action_client.wait_for_server(timeout_sec=5.0):
    # Send goal
    pass
```

## Summary

This week covered the three fundamental communication patterns in ROS 2:

1. **Topics** for continuous data streams with flexible QoS configurations
2. **Services** for synchronous request-response interactions
3. **Actions** for long-running tasks with feedback and cancellation

Understanding when to use each pattern and how to configure QoS appropriately is essential for building robust ROS 2 systems. In the next week, we'll explore launch files and parameters to manage complex robot applications.

## Additional Resources

- [ROS 2 Concepts: Topics](https://docs.ros.org/en/humble/Concepts/Basic/About-Topics.html)
- [ROS 2 Concepts: Services](https://docs.ros.org/en/humble/Concepts/Basic/About-Services.html)
- [ROS 2 Concepts: Actions](https://docs.ros.org/en/humble/Concepts/Basic/About-Actions.html)
- [About Quality of Service Settings](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
