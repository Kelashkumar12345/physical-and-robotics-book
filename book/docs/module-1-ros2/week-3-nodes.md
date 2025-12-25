---
sidebar_position: 3
title: "Week 3: ROS 2 Architecture & Nodes"
---

# Week 3: ROS 2 Architecture & Nodes

## Understanding the ROS 2 Graph

ROS 2 is fundamentally a **distributed computing framework**. Rather than a single monolithic program, a ROS 2 system consists of multiple independent processes (nodes) that communicate with each other to accomplish complex tasks.

### The ROS 2 Computational Graph

```
┌─────────────┐      topic:/camera/image     ┌──────────────┐
│   Camera    │─────────────────────────────>│  Detector    │
│   Driver    │                              │     Node     │
└─────────────┘                              └──────────────┘
                                                     │
                                                     │ topic:/detections
                                                     v
┌─────────────┐      topic:/cmd_vel          ┌──────────────┐
│   Motor     │<─────────────────────────────│   Planner    │
│  Controller │                              │     Node     │
└─────────────┘                              └──────────────┘
```

### Graph Components

1. **Nodes**: Independent processes that perform computation
2. **Topics**: Named buses for asynchronous data streams (publisher-subscriber)
3. **Services**: Synchronous request-reply interactions
4. **Actions**: Long-running tasks with feedback and cancellation
5. **Parameters**: Configuration values for nodes

### Why This Architecture?

#### Modularity
Each node has a single, well-defined responsibility. Easy to develop, test, and debug independently.

#### Reusability
Nodes can be reused across different robots and projects.

#### Scalability
Nodes can run on different computers, enabling distributed systems.

#### Fault Tolerance
If one node crashes, others continue running.

## Creating Nodes with rclpy

### The Node Lifecycle

```
┌──────────────┐
│ Unconfigured │
└──────────────┘
       │
       │ configure()
       v
┌──────────────┐
│   Inactive   │
└──────────────┘
       │
       │ activate()
       v
┌──────────────┐
│    Active    │ ←─── Main operational state
└──────────────┘
       │
       │ deactivate()
       v
┌──────────────┐
│   Inactive   │
└──────────────┘
       │
       │ cleanup()
       v
┌──────────────┐
│ Unconfigured │
└──────────────┘
```

For most nodes, we use the simplified lifecycle where nodes start in the "Active" state immediately.

### Basic Node Structure

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node_name')
        # Initialize publishers, subscribers, timers, etc.

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Node Best Practices

1. **Single Responsibility**: One node, one job
2. **Descriptive Names**: Use clear, unique node names
3. **Namespacing**: Use namespaces for multiple instances
4. **Graceful Shutdown**: Always clean up resources
5. **Logging**: Use the built-in logger, not print()

## Publishers and Subscribers

The **publish-subscribe pattern** is the most common communication mechanism in ROS 2.

### How It Works

```
Publisher Node              Topic              Subscriber Node(s)
     │                       │                        │
     │───── publish() ──────>│                        │
     │                       │───── callback() ──────>│
     │                       │                        │
     │───── publish() ──────>│                        │
     │                       │───── callback() ──────>│
     │                       │───── callback() ──────>│ (multiple subscribers)
```

### Key Characteristics

- **Asynchronous**: Publishers don't wait for subscribers
- **One-to-Many**: Multiple subscribers can listen to one topic
- **Many-to-One**: Multiple publishers can publish to one topic (less common)
- **Decoupled**: Publishers and subscribers don't know about each other

### Message Types

ROS 2 provides standard message types in various packages:

```python
from std_msgs.msg import String, Int32, Float64, Bool
from geometry_msgs.msg import Twist, Pose, Point
from sensor_msgs.msg import Image, LaserScan, Imu
from nav_msgs.msg import Odometry, Path
```

## Complete Publisher/Subscriber Example

Let's build a realistic robotics system: a **temperature monitoring and control system** for a robot with heat-sensitive components.

### Scenario

- **Temperature Sensor Node**: Reads temperature and publishes readings
- **Thermal Controller Node**: Subscribes to temperature, publishes fan control commands
- **Fan Driver Node**: Subscribes to fan commands, simulates fan control

### 1. Temperature Sensor Node (Publisher)

```python
#!/usr/bin/env python3
"""
Temperature Sensor Node

Simulates a temperature sensor on a robot that publishes
temperature readings at regular intervals.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random
import math


class TemperatureSensorNode(Node):
    """
    Publishes simulated temperature readings.

    This node simulates a temperature sensor that:
    - Reads temperature every 0.5 seconds
    - Temperature varies sinusoidally with random noise
    - Publishes to /robot/temperature topic
    """

    def __init__(self):
        super().__init__('temperature_sensor')

        # Create publisher
        self.publisher = self.create_publisher(
            Float32,
            '/robot/temperature',
            10  # QoS queue size
        )

        # Timer for periodic publishing (500ms = 0.5 seconds)
        self.timer_period = 0.5
        self.timer = self.create_timer(self.timer_period, self.publish_temperature)

        # Simulation parameters
        self.time_elapsed = 0.0
        self.base_temperature = 45.0  # Celsius
        self.amplitude = 10.0          # Variation amplitude
        self.noise_level = 2.0         # Random noise

        self.get_logger().info('Temperature Sensor Node Started')
        self.get_logger().info('Publishing to topic: /robot/temperature')

    def publish_temperature(self):
        """
        Read simulated temperature and publish.
        """
        # Simulate temperature with sinusoidal variation + noise
        # This mimics real thermal dynamics (heating/cooling cycles)
        sinusoidal_variation = self.amplitude * math.sin(self.time_elapsed * 0.1)
        noise = random.uniform(-self.noise_level, self.noise_level)
        temperature = self.base_temperature + sinusoidal_variation + noise

        # Create and publish message
        msg = Float32()
        msg.data = temperature
        self.publisher.publish(msg)

        # Log every 2 seconds (every 4th reading)
        if int(self.time_elapsed / self.timer_period) % 4 == 0:
            self.get_logger().info(f'Publishing temperature: {temperature:.2f}°C')

        self.time_elapsed += self.timer_period


def main(args=None):
    rclpy.init(args=args)
    node = TemperatureSensorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Temperature Sensor Node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 2. Thermal Controller Node (Subscriber + Publisher)

```python
#!/usr/bin/env python3
"""
Thermal Controller Node

Subscribes to temperature readings and publishes fan control commands
to maintain safe operating temperature.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, UInt8


class ThermalControllerNode(Node):
    """
    Controls cooling fan based on temperature readings.

    Temperature Zones:
    - < 40°C: Fan OFF (0%)
    - 40-50°C: Fan LOW (30%)
    - 50-60°C: Fan MEDIUM (60%)
    - > 60°C: Fan HIGH (100%)
    """

    def __init__(self):
        super().__init__('thermal_controller')

        # Subscribe to temperature
        self.temperature_sub = self.create_subscription(
            Float32,
            '/robot/temperature',
            self.temperature_callback,
            10
        )

        # Publisher for fan speed (0-100%)
        self.fan_pub = self.create_publisher(
            UInt8,
            '/robot/fan_speed',
            10
        )

        # State
        self.current_temperature = 0.0
        self.current_fan_speed = 0
        self.temperature_readings = []  # Rolling buffer for averaging

        # Control parameters
        self.temp_thresholds = {
            'off': 40.0,
            'low': 50.0,
            'medium': 60.0,
            'high': 70.0
        }

        self.fan_speeds = {
            'off': 0,
            'low': 30,
            'medium': 60,
            'high': 100
        }

        # Hysteresis to prevent rapid switching
        self.hysteresis = 2.0  # degrees

        # Timer for control loop (runs independently of sensor rate)
        self.create_timer(1.0, self.control_loop)

        self.get_logger().info('Thermal Controller Node Started')
        self.get_logger().info('Subscribed to: /robot/temperature')
        self.get_logger().info('Publishing to: /robot/fan_speed')

    def temperature_callback(self, msg):
        """
        Receive temperature reading.

        Args:
            msg: Float32 message with temperature in Celsius
        """
        self.current_temperature = msg.data

        # Maintain rolling average (last 5 readings)
        self.temperature_readings.append(msg.data)
        if len(self.temperature_readings) > 5:
            self.temperature_readings.pop(0)

        # Log occasionally
        if len(self.temperature_readings) % 10 == 0:
            avg_temp = sum(self.temperature_readings) / len(self.temperature_readings)
            self.get_logger().debug(
                f'Received temperature: {msg.data:.2f}°C (avg: {avg_temp:.2f}°C)'
            )

    def control_loop(self):
        """
        Main control logic - runs every 1 second.
        """
        if not self.temperature_readings:
            return

        # Use averaged temperature for more stable control
        avg_temp = sum(self.temperature_readings) / len(self.temperature_readings)

        # Determine target fan speed with hysteresis
        target_fan_speed = self.calculate_fan_speed(avg_temp)

        # Only update if fan speed needs to change
        if target_fan_speed != self.current_fan_speed:
            self.current_fan_speed = target_fan_speed

            # Publish new fan speed
            msg = UInt8()
            msg.data = target_fan_speed
            self.fan_pub.publish(msg)

            self.get_logger().info(
                f'Temperature: {avg_temp:.2f}°C → Fan speed: {target_fan_speed}%'
            )

            # Warnings for critical temperatures
            if avg_temp > self.temp_thresholds['high']:
                self.get_logger().warn(
                    f'CRITICAL TEMPERATURE: {avg_temp:.2f}°C! Fan at maximum.'
                )

    def calculate_fan_speed(self, temperature):
        """
        Calculate appropriate fan speed based on temperature.

        Includes hysteresis to prevent rapid switching.

        Args:
            temperature: Current temperature in Celsius

        Returns:
            Fan speed (0-100%)
        """
        # Apply hysteresis: different thresholds for increasing vs decreasing
        if temperature > self.current_temperature:
            # Temperature rising - use normal thresholds
            offset = 0
        else:
            # Temperature falling - add hysteresis
            offset = self.hysteresis

        # Determine zone
        if temperature < self.temp_thresholds['off'] + offset:
            return self.fan_speeds['off']
        elif temperature < self.temp_thresholds['low'] + offset:
            return self.fan_speeds['low']
        elif temperature < self.temp_thresholds['medium'] + offset:
            return self.fan_speeds['medium']
        else:
            return self.fan_speeds['high']


def main(args=None):
    rclpy.init(args=args)
    node = ThermalControllerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Thermal Controller Node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 3. Fan Driver Node (Subscriber)

```python
#!/usr/bin/env python3
"""
Fan Driver Node

Receives fan speed commands and simulates fan control.
In a real system, this would interface with hardware (GPIO, PWM, etc.).
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import UInt8


class FanDriverNode(Node):
    """
    Simulates a fan driver that receives speed commands.

    In a real robot, this would:
    - Interface with hardware (e.g., GPIO pins, motor controller)
    - Set PWM duty cycle for fan speed control
    - Monitor fan tachometer for actual RPM
    """

    def __init__(self):
        super().__init__('fan_driver')

        # Subscribe to fan speed commands
        self.fan_sub = self.create_subscription(
            UInt8,
            '/robot/fan_speed',
            self.fan_callback,
            10
        )

        # State
        self.current_fan_speed = 0
        self.fan_rpm = 0

        # Hardware simulation parameters
        self.max_rpm = 3000  # Maximum fan RPM

        self.get_logger().info('Fan Driver Node Started')
        self.get_logger().info('Subscribed to: /robot/fan_speed')

    def fan_callback(self, msg):
        """
        Receive fan speed command and update hardware.

        Args:
            msg: UInt8 message with fan speed (0-100%)
        """
        commanded_speed = msg.data

        # Validate input
        if commanded_speed > 100:
            self.get_logger().warn(
                f'Invalid fan speed: {commanded_speed}%. Clamping to 100%.'
            )
            commanded_speed = 100

        # Update fan speed
        self.current_fan_speed = commanded_speed

        # Simulate fan RPM (linear relationship for simplicity)
        self.fan_rpm = int((commanded_speed / 100.0) * self.max_rpm)

        # In a real system, this is where you'd set hardware PWM:
        # GPIO.PWM(fan_pin, commanded_speed)

        # Log the change
        if commanded_speed == 0:
            self.get_logger().info('Fan stopped (0 RPM)')
        else:
            self.get_logger().info(
                f'Fan speed set to {commanded_speed}% (~{self.fan_rpm} RPM)'
            )

        # Simulate different fan states
        self.simulate_fan_state(commanded_speed)

    def simulate_fan_state(self, speed):
        """
        Simulate fan behavior at different speeds.

        Args:
            speed: Fan speed percentage (0-100)
        """
        if speed == 0:
            state = "OFF - No airflow"
        elif speed < 40:
            state = "LOW - Quiet operation, minimal airflow"
        elif speed < 70:
            state = "MEDIUM - Moderate airflow, noticeable noise"
        else:
            state = "HIGH - Maximum cooling, loud operation"

        self.get_logger().debug(f'Fan state: {state}')


def main(args=None):
    rclpy.init(args=args)
    node = FanDriverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Fan Driver Node...')
    finally:
        # In a real system, ensure fan stops on shutdown
        # GPIO.PWM(fan_pin, 0)
        node.get_logger().info('Fan safely stopped')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Running the Complete System

### 1. Create the Package

```bash
cd ~/ros2_ws/src
ros2 pkg create thermal_system --build-type ament_python --dependencies rclpy std_msgs
```

### 2. Add the Nodes

Save the three Python files:
- `temperature_sensor.py`
- `thermal_controller.py`
- `fan_driver.py`

In `thermal_system/thermal_system/` directory.

### 3. Update `setup.py`

```python
from setuptools import setup

package_name = 'thermal_system'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Thermal management system for robots',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'temperature_sensor = thermal_system.temperature_sensor:main',
            'thermal_controller = thermal_system.thermal_controller:main',
            'fan_driver = thermal_system.fan_driver:main',
        ],
    },
)
```

### 4. Build and Run

```bash
cd ~/ros2_ws
colcon build --packages-select thermal_system
source install/setup.bash

# Terminal 1: Temperature Sensor
ros2 run thermal_system temperature_sensor

# Terminal 2: Thermal Controller
ros2 run thermal_system thermal_controller

# Terminal 3: Fan Driver
ros2 run thermal_system fan_driver
```

### 5. Monitor the System

```bash
# Terminal 4: Monitor the ROS graph
rqt_graph

# Terminal 5: Echo temperature readings
ros2 topic echo /robot/temperature

# Terminal 6: Echo fan commands
ros2 topic echo /robot/fan_speed

# Check topic info
ros2 topic info /robot/temperature
ros2 topic info /robot/fan_speed

# List all nodes
ros2 node list

# Get info about a specific node
ros2 node info /thermal_controller
```

## Node Lifecycle Management

### Graceful Shutdown

Always clean up resources properly:

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.timer = self.create_timer(1.0, self.callback)

    def destroy_node(self):
        """
        Override destroy_node to add custom cleanup.
        """
        self.get_logger().info('Cleaning up resources...')
        # Stop hardware, close files, etc.
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutdown requested')
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Handling Signals

For production systems, handle signals properly:

```python
import signal
import sys

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\nShutdown signal received. Cleaning up...')
    rclpy.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

### Using Managed Nodes

For more complex lifecycle management, use **Managed Nodes**:

```python
from rclpy.lifecycle import Node, State, TransitionCallbackReturn

class ManagedNode(Node):
    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Configuring...')
        # Initialize resources
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Activating...')
        # Start publishers, timers
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Deactivating...')
        # Stop publishers, timers
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Cleaning up...')
        # Release resources
        return TransitionCallbackReturn.SUCCESS
```

## Quality of Service (QoS)

QoS policies control message delivery behavior. Critical for reliable robotics!

### Common QoS Profiles

```python
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

# 1. Sensor Data (lossy, latest value only)
sensor_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1
)

# 2. Command & Control (reliable, keep last N)
control_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

# 3. Critical Data (reliable, keep all)
critical_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_ALL
)

# Use in publisher/subscriber
self.publisher = self.create_publisher(String, '/topic', sensor_qos)
```

### QoS Compatibility

Publishers and subscribers must have **compatible** QoS settings, or they won't connect!

```bash
# Check QoS settings of a topic
ros2 topic info /robot/temperature --verbose
```

## Advanced Topics

### 1. Topic Remapping

Run nodes with different topic names:

```bash
ros2 run thermal_system temperature_sensor --ros-args -r /robot/temperature:=/sensor1/temperature
```

### 2. Namespacing

Run multiple instances of the same node:

```bash
ros2 run thermal_system temperature_sensor --ros-args -r __ns:=/robot1
ros2 run thermal_system temperature_sensor --ros-args -r __ns:=/robot2
```

### 3. Launch Files

Orchestrate multiple nodes with a launch file:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='thermal_system',
            executable='temperature_sensor',
        ),
        Node(
            package='thermal_system',
            executable='thermal_controller',
        ),
        Node(
            package='thermal_system',
            executable='fan_driver',
        ),
    ])
```

Run with:
```bash
ros2 launch thermal_system thermal_system.launch.py
```

## Key Takeaways

1. **ROS 2 Graph**: System of nodes communicating via topics, services, and actions
2. **Nodes**: Independent processes with single responsibilities
3. **Publishers**: Send messages to topics asynchronously
4. **Subscribers**: Receive messages from topics via callbacks
5. **Decoupling**: Publishers and subscribers don't need to know about each other
6. **QoS**: Controls message delivery reliability and history
7. **Lifecycle Management**: Proper initialization and cleanup is critical

## Exercises

1. **Add Monitoring**: Create a fourth node that subscribes to both `/robot/temperature` and `/robot/fan_speed` and logs their correlation
2. **Implement Filtering**: Add a median filter to the thermal controller to smooth noisy temperature readings
3. **Add Parameters**: Make temperature thresholds configurable via ROS 2 parameters
4. **Create a Service**: Add a service to manually override fan speed for testing
5. **Build a Launch File**: Write a launch file that starts all three nodes with a single command

## Next Module

In **Module 2: AI Perception**, we'll integrate deep learning models for computer vision tasks, building on the sensor and architecture foundations from this module.

## Additional Resources

- [ROS 2 Nodes](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html)
- [ROS 2 Topics](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html)
- [ROS 2 Python (rclpy) API](https://docs.ros2.org/latest/api/rclpy/)
- [Quality of Service](https://docs.ros.org/en/humble/Concepts/About-Quality-of-Service-Settings.html)
- [Launch Files](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Managed Nodes](https://design.ros2.org/articles/node_lifecycle.html)
