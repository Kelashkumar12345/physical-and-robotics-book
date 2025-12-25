---
sidebar_position: 1
title: "Week 1: Introduction to Physical AI"
---

# Week 1: Introduction to Physical AI

## What is Physical AI?

Physical AI represents the convergence of artificial intelligence and the physical world through embodied systems. Unlike traditional AI that operates purely in digital environments, Physical AI enables machines to perceive, reason about, and interact with the real world through sensors, actuators, and intelligent decision-making.

### Key Characteristics of Physical AI

1. **Embodied Intelligence**: AI that exists in a physical form (robots, drones, autonomous vehicles)
2. **Real-time Perception**: Processing sensor data to understand the environment
3. **Physical Interaction**: Manipulating objects and navigating spaces
4. **Autonomous Decision-Making**: Making decisions based on real-world constraints

### The Bridge Between Digital AI and Physical World

Physical AI systems act as a bridge connecting:

- **Digital Intelligence**: Neural networks, machine learning models, planning algorithms
- **Physical Reality**: Sensors (cameras, LiDAR, IMUs), actuators (motors, servos), mechanical systems

This bridge involves several critical challenges:

#### 1. The Perception Problem
Translating raw sensor data (images, point clouds, IMU readings) into meaningful representations that AI can process.

```python
# Example: Raw sensor data → Structured representation
camera_image = [[[255, 128, 64], ...]]  # Raw RGB pixels
object_detection = {"car": [x, y, w, h], "person": [...]}  # Semantic understanding
```

#### 2. The Reality Gap
Simulated environments don't perfectly match the real world. Physical AI must handle:
- Sensor noise and uncertainty
- Unpredictable environmental conditions
- Physical constraints (friction, inertia, manufacturing tolerances)

#### 3. Real-time Constraints
Unlike offline AI processing, Physical AI requires:
- Low latency decision-making (milliseconds, not seconds)
- Continuous sensor processing
- Safe failure modes

## ROS 2 Overview and Ecosystem

**ROS 2 (Robot Operating System 2)** is the industry-standard middleware framework for building robot applications. It's not an operating system in the traditional sense, but rather a collection of software libraries and tools that help developers build robot applications.

### Why ROS 2?

1. **Distributed Architecture**: Run components across multiple computers
2. **Language Flexibility**: Python, C++, and other languages
3. **Rich Ecosystem**: Thousands of pre-built packages for navigation, perception, manipulation
4. **Industry Adoption**: Used by companies like Amazon, BMW, NASA, and more
5. **Open Source**: Free and community-driven

### Core ROS 2 Concepts

#### Nodes
Independent processes that perform specific tasks (e.g., reading a camera, planning a path, controlling motors).

#### Topics
Named buses over which nodes exchange messages asynchronously (publish-subscribe pattern).

#### Services
Synchronous request-response communication between nodes.

#### Actions
For long-running tasks with feedback (e.g., "navigate to goal" with progress updates).

### The ROS 2 Ecosystem

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│   (Your Robot-Specific Logic)           │
└─────────────────────────────────────────┘
           ↓                ↑
┌─────────────────────────────────────────┐
│         ROS 2 Packages                  │
│  Navigation │ Perception │ Manipulation │
└─────────────────────────────────────────┘
           ↓                ↑
┌─────────────────────────────────────────┐
│         ROS 2 Core (rclpy/rclcpp)       │
│    Communication │ Node Management      │
└─────────────────────────────────────────┘
           ↓                ↑
┌─────────────────────────────────────────┐
│         DDS (Data Distribution)         │
│    Middleware for Communication         │
└─────────────────────────────────────────┘
```

## Setting Up Your Development Environment

### Prerequisites

- **Operating System**: Ubuntu 22.04 (recommended) or Ubuntu 24.04
- **ROS 2 Distribution**: Humble Hawksbill (LTS) or Jazzy Jalisco
- **Python**: 3.10 or higher

### Installation Steps

#### 1. Set up ROS 2 Repository

```bash
# Set locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 apt repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

#### 2. Install ROS 2 Humble

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop python3-colcon-common-extensions
```

#### 3. Configure Environment

Add to your `~/.bashrc`:

```bash
source /opt/ros/humble/setup.bash
```

#### 4. Create a Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### Verify Installation

```bash
# Terminal 1: Start a talker
ros2 run demo_nodes_py talker

# Terminal 2: Start a listener
ros2 run demo_nodes_py listener
```

You should see messages being published and received!

## Your First ROS 2 Node

Let's create a simple ROS 2 node that demonstrates the basic structure.

### Example: Hello Physical AI Node

```python
#!/usr/bin/env python3
"""
A simple ROS 2 node that publishes status messages about a Physical AI system.
This demonstrates the basic structure of a ROS 2 node in Python.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time


class PhysicalAINode(Node):
    """
    A basic ROS 2 node for a Physical AI system.

    This node:
    - Publishes status messages every second
    - Simulates a simple state machine (IDLE → SENSING → PROCESSING → ACTING)
    - Demonstrates node initialization, timers, and publishing
    """

    def __init__(self):
        # Initialize the node with name 'physical_ai_node'
        super().__init__('physical_ai_node')

        # Create a publisher for status messages
        self.publisher = self.create_publisher(
            String,           # Message type
            'ai_status',      # Topic name
            10                # Queue size (QoS)
        )

        # Create a timer that calls our callback every 1 second
        self.timer_period = 1.0  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Initialize our simple state machine
        self.states = ['IDLE', 'SENSING', 'PROCESSING', 'ACTING']
        self.current_state_index = 0
        self.iteration = 0

        # Log that the node has started
        self.get_logger().info('Physical AI Node has started!')

    def timer_callback(self):
        """
        Called every timer period (1 second).
        Publishes the current state and advances to the next state.
        """
        # Get current state
        current_state = self.states[self.current_state_index]

        # Create and populate message
        msg = String()
        msg.data = f'Iteration {self.iteration}: State = {current_state}, Timestamp = {time.time()}'

        # Publish the message
        self.publisher.publish(msg)

        # Log to console
        self.get_logger().info(f'Publishing: "{msg.data}"')

        # Advance to next state (cycle through states)
        self.current_state_index = (self.current_state_index + 1) % len(self.states)
        self.iteration += 1


def main(args=None):
    """
    Main function - entry point for the ROS 2 node.
    """
    # Initialize ROS 2 Python client library
    rclpy.init(args=args)

    # Create our node
    node = PhysicalAINode()

    try:
        # Keep the node running and processing callbacks
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        node.get_logger().info('Shutting down Physical AI Node...')
    finally:
        # Clean up
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### How to Run This Node

1. **Save the file** as `physical_ai_node.py` in your workspace:
   ```bash
   mkdir -p ~/ros2_ws/src/physical_ai_intro/physical_ai_intro
   # Save the file to ~/ros2_ws/src/physical_ai_intro/physical_ai_intro/physical_ai_node.py
   ```

2. **Make it executable**:
   ```bash
   chmod +x ~/ros2_ws/src/physical_ai_intro/physical_ai_intro/physical_ai_node.py
   ```

3. **Create a package**:
   ```bash
   cd ~/ros2_ws/src/physical_ai_intro
   ```

   Create `setup.py`:
   ```python
   from setuptools import setup

   package_name = 'physical_ai_intro'

   setup(
       name=package_name,
       version='0.0.1',
       packages=[package_name],
       install_requires=['setuptools'],
       zip_safe=True,
       maintainer='Your Name',
       maintainer_email='your.email@example.com',
       description='Physical AI Introduction Package',
       license='Apache License 2.0',
       entry_points={
           'console_scripts': [
               'physical_ai_node = physical_ai_intro.physical_ai_node:main',
           ],
       },
   )
   ```

4. **Build the package**:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select physical_ai_intro
   source install/setup.bash
   ```

5. **Run the node**:
   ```bash
   ros2 run physical_ai_intro physical_ai_node
   ```

### Monitoring the Node

While the node is running, open a new terminal and try these commands:

```bash
# List all active nodes
ros2 node list

# Get info about our node
ros2 node info /physical_ai_node

# Listen to the messages being published
ros2 topic echo /ai_status

# Check the topic info
ros2 topic info /ai_status
```

## Understanding the Code

### Node Initialization
```python
super().__init__('physical_ai_node')
```
Every ROS 2 node needs a unique name. This is how it's identified in the ROS 2 graph.

### Publishers
```python
self.publisher = self.create_publisher(String, 'ai_status', 10)
```
- `String`: The message type (from `std_msgs`)
- `'ai_status'`: The topic name
- `10`: Queue size for Quality of Service (QoS)

### Timers
```python
self.timer = self.create_timer(self.timer_period, self.timer_callback)
```
Timers allow periodic execution of callbacks. Essential for control loops!

### Logging
```python
self.get_logger().info('Message here')
```
ROS 2 provides integrated logging at different levels: DEBUG, INFO, WARN, ERROR, FATAL.

## Key Takeaways

1. **Physical AI** bridges digital intelligence with the physical world through embodied systems
2. **ROS 2** is the industry-standard framework for building robot applications
3. **Nodes** are the fundamental building blocks - independent processes that communicate via topics
4. **The development workflow** involves: create package → write code → build → run
5. **Real-time constraints** and **sensor uncertainty** are unique challenges in Physical AI

## Exercises

1. **Modify the state machine**: Add a new state (e.g., 'ERROR') and transition to it randomly with 10% probability
2. **Add parameters**: Make the timer period configurable via ROS 2 parameters
3. **Create a subscriber**: Write a second node that subscribes to `/ai_status` and logs received messages
4. **Experiment with QoS**: Change the queue size and observe behavior when publishing rapidly

## Next Week

In Week 2, we'll dive deep into **Sensor Systems** - exploring how robots perceive the world through LiDAR, cameras, and IMUs, and how to process this data in ROS 2.

## Additional Resources

- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Python API (rclpy)](https://docs.ros2.org/latest/api/rclpy/)
- [Understanding ROS 2 Nodes](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html)
- [Physical AI Overview - NVIDIA](https://www.nvidia.com/en-us/ai-data-science/products/physical-ai/)
