---
sidebar_position: 5
title: "Week 5: Launch Files & Parameters"
---

# Week 5: Launch Files & Parameters

## Learning Objectives

By the end of this week, you will be able to:

- Create Python launch files for complex robot systems
- Configure and manage ROS 2 parameters
- Implement dynamic reconfiguration
- Use composable nodes for efficient execution
- Follow best practices for ROS 2 package organization
- Build scalable and maintainable robot applications

## 1. Introduction to Launch Files

Launch files are essential for managing complex ROS 2 systems with multiple nodes, parameters, and dependencies. Unlike ROS 1's XML-based launch files, ROS 2 uses Python for more flexibility and programmatic control.

### Why Use Launch Files?

- Start multiple nodes simultaneously
- Set parameters and arguments
- Configure remappings and namespaces
- Define node dependencies and execution order
- Create reusable, modular configurations
- Support conditional logic and dynamic configuration

### Launch System Architecture

```
Launch File (Python)
    ├── Node Declarations
    ├── Parameter Files (YAML)
    ├── Argument Definitions
    ├── Event Handlers
    └── Conditional Logic
```

## 2. Creating Basic Launch Files

### Simple Launch File Example

Create `my_robot_bringup/launch/robot_basic.launch.py`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """Generate launch description with basic nodes."""

    return LaunchDescription([
        # Camera node
        Node(
            package='usb_cam',
            executable='usb_cam_node',
            name='camera',
            output='screen',
            parameters=[{
                'video_device': '/dev/video0',
                'framerate': 30.0,
                'image_width': 640,
                'image_height': 480,
            }]
        ),

        # Image processing node
        Node(
            package='image_proc',
            executable='image_proc_node',
            name='image_processor',
            output='screen',
            remappings=[
                ('/image_raw', '/camera/image_raw'),
            ]
        ),

        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
        ),
    ])
```

### Running Launch Files

```bash
# Run launch file
ros2 launch my_robot_bringup robot_basic.launch.py

# Run with arguments
ros2 launch my_robot_bringup robot_basic.launch.py camera_device:=/dev/video1

# List available arguments
ros2 launch my_robot_bringup robot_basic.launch.py --show-args
```

## 3. Advanced Launch File Features

### Launch Arguments and Parameters

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Launch file with arguments and parameter files."""

    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='robot1',
        description='Name of the robot'
    )

    log_level_arg = DeclareLaunchArgument(
        'log_level',
        default_value='info',
        description='Logging level (debug, info, warn, error)'
    )

    # Get launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_name = LaunchConfiguration('robot_name')
    log_level = LaunchConfiguration('log_level')

    # Find package share directory
    pkg_share = FindPackageShare('my_robot_bringup')

    # Path to parameter file
    params_file = PathJoinSubstitution([
        pkg_share,
        'config',
        'robot_params.yaml'
    ])

    # Robot controller node
    controller_node = Node(
        package='my_robot_control',
        executable='controller_node',
        name='controller',
        namespace=robot_name,
        output='screen',
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time}
        ],
        arguments=['--ros-args', '--log-level', log_level]
    )

    # Sensor fusion node
    sensor_fusion_node = Node(
        package='my_robot_perception',
        executable='sensor_fusion',
        name='sensor_fusion',
        namespace=robot_name,
        output='screen',
        parameters=[params_file],
        remappings=[
            ('/imu/data', [robot_name, '/imu/data']),
            ('/odom', [robot_name, '/odom']),
        ]
    )

    return LaunchDescription([
        use_sim_time_arg,
        robot_name_arg,
        log_level_arg,
        controller_node,
        sensor_fusion_node,
    ])
```

### Conditional Node Launch

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    """Launch file with conditional node execution."""

    # Declare arguments
    use_camera_arg = DeclareLaunchArgument(
        'use_camera',
        default_value='true',
        description='Enable camera node'
    )

    use_lidar_arg = DeclareLaunchArgument(
        'use_lidar',
        default_value='true',
        description='Enable LiDAR node'
    )

    simulation_arg = DeclareLaunchArgument(
        'simulation',
        default_value='false',
        description='Run in simulation mode'
    )

    # Get configurations
    use_camera = LaunchConfiguration('use_camera')
    use_lidar = LaunchConfiguration('use_lidar')
    simulation = LaunchConfiguration('simulation')

    # Camera node (only if use_camera=true)
    camera_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='camera',
        output='screen',
        condition=IfCondition(use_camera)
    )

    # LiDAR node (only if use_lidar=true)
    lidar_node = Node(
        package='sick_scan',
        executable='sick_generic_caller',
        name='lidar',
        output='screen',
        condition=IfCondition(use_lidar)
    )

    # Hardware driver (only in real robot mode)
    hardware_driver = Node(
        package='my_robot_hw',
        executable='hardware_interface',
        name='hardware_interface',
        output='screen',
        condition=UnlessCondition(simulation)
    )

    # Simulated robot (only in simulation mode)
    gazebo_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'my_robot', '-topic', 'robot_description'],
        output='screen',
        condition=IfCondition(simulation)
    )

    return LaunchDescription([
        use_camera_arg,
        use_lidar_arg,
        simulation_arg,
        camera_node,
        lidar_node,
        hardware_driver,
        gazebo_node,
    ])
```

### Including Other Launch Files

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Master launch file that includes other launch files."""

    # Include navigation launch file
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': PathJoinSubstitution([
                FindPackageShare('my_robot_bringup'),
                'config',
                'nav2_params.yaml'
            ])
        }.items()
    )

    # Include sensor launch file
    sensors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('my_robot_bringup'),
                'launch',
                'sensors.launch.py'
            ])
        ])
    )

    # Include localization launch file
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('my_robot_bringup'),
                'launch',
                'localization.launch.py'
            ])
        ]),
        launch_arguments={'map': '/maps/office.yaml'}.items()
    )

    return LaunchDescription([
        sensors_launch,
        localization_launch,
        navigation_launch,
    ])
```

### Event Handlers and Lifecycle Management

```python
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.events import Shutdown
from launch_ros.actions import Node, LifecycleNode
from launch_ros.events.lifecycle import ChangeState
from launch_ros.event_handlers import OnStateTransition
from lifecycle_msgs.msg import Transition

def generate_launch_description():
    """Launch file with event handlers and lifecycle management."""

    # Critical system node
    system_monitor = Node(
        package='my_robot_system',
        executable='system_monitor',
        name='system_monitor',
        output='screen'
    )

    # Shutdown entire system if monitor exits
    shutdown_handler = RegisterEventHandler(
        OnProcessExit(
            target_action=system_monitor,
            on_exit=[
                EmitEvent(event=Shutdown(reason='System monitor exited'))
            ]
        )
    )

    # Lifecycle node (e.g., camera driver)
    camera_driver = LifecycleNode(
        package='my_camera_driver',
        executable='camera_node',
        name='camera',
        namespace='',
        output='screen'
    )

    # Auto-configure camera when it starts
    configure_camera = RegisterEventHandler(
        OnProcessStart(
            target_action=camera_driver,
            on_start=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node.name == 'camera',
                        transition_id=Transition.TRANSITION_CONFIGURE
                    )
                )
            ]
        )
    )

    # Auto-activate camera after successful configuration
    activate_camera = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=camera_driver,
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node.name == 'camera',
                        transition_id=Transition.TRANSITION_ACTIVATE
                    )
                )
            ]
        )
    )

    return LaunchDescription([
        system_monitor,
        shutdown_handler,
        camera_driver,
        configure_camera,
        activate_camera,
    ])
```

## 4. ROS 2 Parameters

Parameters provide runtime configuration for nodes without code changes.

### Parameter YAML File

Create `my_robot_bringup/config/robot_params.yaml`:

```yaml
# Controller parameters
controller:
  ros__parameters:
    update_rate: 50.0
    max_linear_velocity: 1.0
    max_angular_velocity: 2.0
    wheel_radius: 0.1
    wheel_separation: 0.5

    # PID gains
    linear_pid:
      p: 1.0
      i: 0.1
      d: 0.05

    angular_pid:
      p: 2.0
      i: 0.2
      d: 0.1

# Sensor parameters
sensor_fusion:
  ros__parameters:
    use_imu: true
    use_odometry: true
    imu_topic: "/imu/data"
    odom_topic: "/odom"
    output_frame: "base_link"
    publish_rate: 30.0

# Safety parameters
safety_monitor:
  ros__parameters:
    enable_collision_detection: true
    min_obstacle_distance: 0.3
    emergency_stop_distance: 0.1
    max_tilt_angle: 30.0  # degrees
```

### Using Parameters in Nodes

```python
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller')

        # Declare parameters with descriptors
        self.declare_parameter(
            'update_rate',
            50.0,
            ParameterDescriptor(
                description='Control loop update rate (Hz)',
                read_only=False
            )
        )

        self.declare_parameter(
            'max_linear_velocity',
            1.0,
            ParameterDescriptor(
                description='Maximum linear velocity (m/s)',
                read_only=False
            )
        )

        self.declare_parameter(
            'max_angular_velocity',
            2.0,
            ParameterDescriptor(
                description='Maximum angular velocity (rad/s)',
                read_only=False
            )
        )

        # Declare nested parameters
        self.declare_parameter('linear_pid.p', 1.0)
        self.declare_parameter('linear_pid.i', 0.1)
        self.declare_parameter('linear_pid.d', 0.05)

        # Get parameter values
        self.update_rate = self.get_parameter('update_rate').value
        self.max_linear_vel = self.get_parameter('max_linear_velocity').value
        self.max_angular_vel = self.get_parameter('max_angular_velocity').value

        # Get PID parameters
        self.linear_kp = self.get_parameter('linear_pid.p').value
        self.linear_ki = self.get_parameter('linear_pid.i').value
        self.linear_kd = self.get_parameter('linear_pid.d').value

        # Register parameter callback for dynamic updates
        self.add_on_set_parameters_callback(self.parameter_callback)

        # Create timer with parameter-based rate
        timer_period = 1.0 / self.update_rate
        self.timer = self.create_timer(timer_period, self.control_loop)

        self.get_logger().info(f'Controller initialized with update rate: {self.update_rate} Hz')

    def parameter_callback(self, params):
        """Handle parameter updates."""
        from rcl_interfaces.msg import SetParametersResult

        for param in params:
            if param.name == 'update_rate':
                if param.value > 0 and param.value <= 100:
                    self.update_rate = param.value
                    # Update timer period
                    self.timer.cancel()
                    timer_period = 1.0 / self.update_rate
                    self.timer = self.create_timer(timer_period, self.control_loop)
                    self.get_logger().info(f'Update rate changed to: {param.value} Hz')
                else:
                    return SetParametersResult(successful=False)

            elif param.name == 'max_linear_velocity':
                if param.value > 0:
                    self.max_linear_vel = param.value
                    self.get_logger().info(f'Max linear velocity: {param.value} m/s')
                else:
                    return SetParametersResult(successful=False)

            elif param.name.startswith('linear_pid.'):
                if param.name == 'linear_pid.p':
                    self.linear_kp = param.value
                elif param.name == 'linear_pid.i':
                    self.linear_ki = param.value
                elif param.name == 'linear_pid.d':
                    self.linear_kd = param.value

                self.get_logger().info(
                    f'PID gains updated: Kp={self.linear_kp}, '
                    f'Ki={self.linear_ki}, Kd={self.linear_kd}'
                )

        return SetParametersResult(successful=True)

    def control_loop(self):
        """Main control loop."""
        # Use parameters in control logic
        pass

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Parameter Operations via Command Line

```bash
# List all parameters of a node
ros2 param list /controller

# Get parameter value
ros2 param get /controller update_rate

# Set parameter value
ros2 param set /controller update_rate 100.0

# Dump all parameters to YAML
ros2 param dump /controller --output-dir ./config

# Load parameters from YAML
ros2 param load /controller ./config/controller.yaml

# Describe parameter
ros2 param describe /controller update_rate
```

## 5. Composable Nodes

Composable nodes allow multiple nodes to run in a single process, reducing overhead and improving performance.

### Creating a Composable Node

```python
import rclpy
from rclpy.node import Node

class SensorProcessorComponent(Node):
    """Composable sensor processing node."""

    def __init__(self, options=None):
        super().__init__('sensor_processor', options=options)

        # Declare parameters
        self.declare_parameter('processing_rate', 30.0)
        self.declare_parameter('input_topic', '/sensor/raw')
        self.declare_parameter('output_topic', '/sensor/processed')

        # Get parameters
        rate = self.get_parameter('processing_rate').value
        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        # Create subscriber and publisher
        self.subscription = self.create_subscription(
            String,
            input_topic,
            self.process_callback,
            10
        )

        self.publisher = self.create_publisher(
            String,
            output_topic,
            10
        )

        self.get_logger().info('Sensor processor component initialized')

    def process_callback(self, msg):
        """Process sensor data."""
        # Processing logic here
        processed_msg = String()
        processed_msg.data = f"Processed: {msg.data}"
        self.publisher.publish(processed_msg)

# Required for component loading
def main(args=None):
    rclpy.init(args=args)
    node = SensorProcessorComponent()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Component Registration

Add to `setup.py`:

```python
from setuptools import setup

package_name = 'my_robot_components'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Your Name',
    author_email='you@example.com',
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Robot composable components',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sensor_processor = my_robot_components.sensor_processor:main',
        ],
    },
)
```

### Launch File for Composable Nodes

```python
from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    """Launch composable nodes in a container."""

    container = ComposableNodeContainer(
        name='processing_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            # Sensor processor component
            ComposableNode(
                package='my_robot_components',
                plugin='my_robot_components::SensorProcessorComponent',
                name='sensor_processor',
                parameters=[{
                    'processing_rate': 50.0,
                    'input_topic': '/camera/image_raw',
                    'output_topic': '/camera/image_processed'
                }]
            ),
            # Image filter component
            ComposableNode(
                package='image_proc',
                plugin='image_proc::RectifyNode',
                name='rectify',
                remappings=[
                    ('image', '/camera/image_processed'),
                    ('camera_info', '/camera/camera_info'),
                ]
            ),
            # Feature detector component
            ComposableNode(
                package='vision_opencv',
                plugin='cv_bridge::FeatureDetector',
                name='feature_detector',
                parameters=[{
                    'detector_type': 'ORB',
                    'num_features': 500
                }]
            ),
        ],
        output='screen',
    )

    return LaunchDescription([container])
```

### Benefits of Composable Nodes

- **Reduced IPC overhead**: Intra-process communication is faster
- **Lower memory usage**: Shared memory between components
- **Better performance**: Reduced context switching
- **Easier debugging**: Single process to attach debugger
- **Flexible deployment**: Can be run separately or composed

## 6. Best Practices for ROS 2 Packages

### Package Structure

```
my_robot_bringup/
├── CMakeLists.txt  (for C++ packages)
├── package.xml
├── setup.py  (for Python packages)
├── setup.cfg
├── config/
│   ├── robot_params.yaml
│   ├── nav2_params.yaml
│   └── sensors.yaml
├── launch/
│   ├── robot.launch.py
│   ├── sensors.launch.py
│   ├── navigation.launch.py
│   └── simulation.launch.py
├── rviz/
│   └── robot_view.rviz
├── urdf/
│   ├── robot.urdf.xacro
│   └── sensors.xacro
└── my_robot_bringup/
    ├── __init__.py
    └── utils.py
```

### Package.xml Best Practices

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_robot_bringup</name>
  <version>1.0.0</version>
  <description>Launch files and configurations for my robot</description>

  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <author email="you@example.com">Your Name</author>

  <!-- Build dependencies -->
  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>ament_python</buildtool_depend>

  <!-- Runtime dependencies -->
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher</exec_depend>
  <exec_depend>rviz2</exec_depend>

  <!-- Package-specific dependencies -->
  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>

  <!-- Testing dependencies -->
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <test_depend>ament_cmake_pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

### Setup.py Configuration

```python
from setuptools import setup
from glob import glob
import os

package_name = 'my_robot_bringup'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        # Include config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
        # Include URDF files
        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*.xacro') + glob('urdf/*.urdf')),
        # Include RViz configs
        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Launch files and configurations for my robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Add executable scripts here if needed
        ],
    },
)
```

## 7. Complete Robot Bringup Example

### Master Launch File

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Complete robot bringup launch file."""

    # Declare arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    simulation = LaunchConfiguration('simulation')
    robot_name = LaunchConfiguration('robot_name')
    use_rviz = LaunchConfiguration('use_rviz')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    declare_simulation = DeclareLaunchArgument(
        'simulation',
        default_value='false',
        description='Run in simulation mode'
    )

    declare_robot_name = DeclareLaunchArgument(
        'robot_name',
        default_value='robot',
        description='Robot namespace'
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz for visualization'
    )

    # Package paths
    pkg_bringup = FindPackageShare('my_robot_bringup')
    pkg_description = FindPackageShare('my_robot_description')

    # Parameter files
    robot_params = PathJoinSubstitution([
        pkg_bringup, 'config', 'robot_params.yaml'
    ])

    # Robot description
    robot_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                pkg_description, 'launch', 'robot_description.launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Sensors (real hardware)
    sensors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                pkg_bringup, 'launch', 'sensors.launch.py'
            ])
        ]),
        condition=UnlessCondition(simulation)
    )

    # Simulation
    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                pkg_bringup, 'launch', 'simulation.launch.py'
            ])
        ]),
        condition=IfCondition(simulation)
    )

    # Controllers
    controller_node = Node(
        package='my_robot_control',
        executable='controller_node',
        name='controller',
        namespace=robot_name,
        parameters=[robot_params],
        output='screen'
    )

    # RViz
    rviz_config = PathJoinSubstitution([
        pkg_bringup, 'rviz', 'robot_view.rviz'
    ])

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz),
        output='screen'
    )

    return LaunchDescription([
        # Arguments
        declare_use_sim_time,
        declare_simulation,
        declare_robot_name,
        declare_use_rviz,

        # Launches
        robot_description_launch,
        sensors_launch,
        simulation_launch,

        # Nodes
        controller_node,
        rviz_node,
    ])
```

## 8. Testing and Validation

### Launch File Testing

```bash
# Dry run to check syntax
ros2 launch my_robot_bringup robot.launch.py --show-args

# Launch with specific configuration
ros2 launch my_robot_bringup robot.launch.py \
    simulation:=true \
    use_rviz:=true \
    robot_name:=test_robot

# Monitor launched nodes
ros2 node list
ros2 topic list
ros2 param list
```

### Parameter Validation

```python
# In your node
from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange

# Declare parameter with validation
self.declare_parameter(
    'max_velocity',
    1.0,
    ParameterDescriptor(
        description='Maximum velocity (m/s)',
        floating_point_range=[
            FloatingPointRange(
                from_value=0.0,
                to_value=5.0,
                step=0.1
            )
        ]
    )
)
```

## Summary

This week covered essential tools for managing complex ROS 2 systems:

1. **Launch Files**: Python-based system configuration
2. **Parameters**: Runtime configuration management
3. **Composable Nodes**: Efficient multi-node execution
4. **Package Organization**: Best practices for maintainable code

These tools enable you to build scalable, configurable, and maintainable robot applications.

## Practical Exercise

Create a complete robot bringup package:

1. Package structure with config, launch, and rviz directories
2. Parameter YAML files for different subsystems
3. Launch files for sensors, controllers, and visualization
4. Master launch file with arguments and conditional logic
5. Test with both simulation and hardware configurations

## Additional Resources

- [ROS 2 Launch Documentation](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html)
- [ROS 2 Parameters](https://docs.ros.org/en/humble/Concepts/Basic/About-Parameters.html)
- [Composable Nodes Tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/Composition.html)
- [Package Best Practices](https://docs.ros.org/en/humble/The-ROS2-Project/Contributing/Developer-Guide.html)
