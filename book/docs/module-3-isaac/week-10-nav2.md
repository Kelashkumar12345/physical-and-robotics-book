---
sidebar_position: 3
title: "Week 10: VSLAM & Nav2 Path Planning"
---

# Week 10: VSLAM & Nav2 Path Planning

## Introduction to Mobile Robot Navigation

Autonomous navigation is a fundamental capability for mobile robots. It requires:

1. **Localization**: Determining the robot's position in the environment
2. **Mapping**: Building a representation of the environment
3. **Path Planning**: Finding collision-free paths to goal positions
4. **Obstacle Avoidance**: Dynamically avoiding obstacles
5. **Motion Control**: Executing planned trajectories

In this module, we'll explore Visual SLAM (VSLAM) for localization and mapping, and Nav2 for navigation and path planning.

## Visual SLAM Fundamentals

### What is VSLAM?

Visual SLAM (Simultaneous Localization and Mapping) uses camera data to simultaneously:
- Estimate the robot's pose (position and orientation)
- Build a map of the environment

Unlike traditional SLAM using LiDAR, VSLAM leverages visual features from camera images.

### Types of VSLAM

1. **Monocular VSLAM**: Uses a single camera (scale ambiguity)
2. **Stereo VSLAM**: Uses stereo cameras (provides depth)
3. **RGB-D VSLAM**: Uses RGB-D cameras (direct depth measurement)
4. **Visual-Inertial SLAM**: Combines camera with IMU (improved accuracy)

### Key Concepts

- **Feature Detection**: Identifying distinctive points in images (SIFT, SURF, ORB)
- **Feature Matching**: Matching features across frames
- **Triangulation**: Computing 3D positions from 2D observations
- **Bundle Adjustment**: Optimizing camera poses and 3D points
- **Loop Closure**: Recognizing previously visited locations

## Isaac ROS VSLAM Implementation

### Overview

Isaac ROS provides GPU-accelerated VSLAM packages:

- **isaac_ros_visual_slam**: Real-time VSLAM with stereo or RGB-D cameras
- **isaac_ros_nvblox**: 3D reconstruction for navigation
- **Hardware Acceleration**: Optimized for NVIDIA GPUs

### Installation

```bash
# Clone Isaac ROS VSLAM repository
cd ~/workspaces/isaac_ros-dev/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git

# Install dependencies
cd ~/workspaces/isaac_ros-dev
rosdep install -i -r --from-paths src --rosdistro humble -y

# Build
colcon build --symlink-install --packages-up-to isaac_ros_visual_slam

# Source workspace
source install/setup.bash
```

### Launch Isaac ROS VSLAM

```python
# launch/isaac_vslam.launch.py
"""
Launch file for Isaac ROS Visual SLAM
Supports RealSense, ZED, and other stereo cameras
"""

from launch import LaunchDescription
from launch_ros.actions import Node, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Generate launch description for VSLAM"""

    # Declare arguments
    camera_type_arg = DeclareLaunchArgument(
        'camera_type',
        default_value='realsense',
        description='Camera type (realsense, zed, custom)'
    )

    enable_rectified_pose_arg = DeclareLaunchArgument(
        'enable_rectified_pose',
        default_value='True',
        description='Enable rectified pose estimation'
    )

    enable_debug_mode_arg = DeclareLaunchArgument(
        'enable_debug_mode',
        default_value='False',
        description='Enable debug visualization'
    )

    # Visual SLAM node
    visual_slam_node = ComposableNode(
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        name='visual_slam_node',
        parameters=[{
            'denoise_input_images': False,
            'rectified_images': True,
            'enable_debug_mode': LaunchConfiguration('enable_debug_mode'),
            'debug_dump_path': '/tmp/vslam',
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,
            'map_frame': 'map',
            'odom_frame': 'odom',
            'base_frame': 'base_link',
            'input_left_camera_frame': 'camera_infra1_frame',
            'input_right_camera_frame': 'camera_infra2_frame',
            'enable_localization_n_mapping': True,
            'publish_odom_to_base_tf': True,
            'publish_map_to_odom_tf': True,
        }],
        remappings=[
            ('stereo_camera/left/image', '/camera/infra1/image_rect_raw'),
            ('stereo_camera/left/camera_info', '/camera/infra1/camera_info'),
            ('stereo_camera/right/image', '/camera/infra2/image_rect_raw'),
            ('stereo_camera/right/camera_info', '/camera/infra2/camera_info'),
        ]
    )

    # Container for visual SLAM
    visual_slam_container = ComposableNodeContainer(
        name='visual_slam_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[visual_slam_node],
        output='screen'
    )

    return LaunchDescription([
        camera_type_arg,
        enable_rectified_pose_arg,
        enable_debug_mode_arg,
        visual_slam_container,
    ])
```

### VSLAM with RealSense Camera

```python
# scripts/vslam_realsense.py
"""
Visual SLAM with RealSense Camera
Demonstrates VSLAM integration with Intel RealSense
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker, MarkerArray
import numpy as np
from cv_bridge import CvBridge

class VSLAMMonitor(Node):
    """Monitor and visualize VSLAM output"""

    def __init__(self):
        super().__init__('vslam_monitor')

        # Parameters
        self.declare_parameter('save_trajectory', True)
        self.declare_parameter('trajectory_file', '/tmp/vslam_trajectory.txt')

        self.save_trajectory = self.get_parameter('save_trajectory').value
        self.trajectory_file = self.get_parameter('trajectory_file').value

        # CV Bridge
        self.bridge = CvBridge()

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry,
            'visual_slam/tracking/odometry',
            self.odometry_callback,
            10
        )

        self.pose_sub = self.create_subscription(
            PoseStamped,
            'visual_slam/tracking/vo_pose',
            self.pose_callback,
            10
        )

        self.landmarks_sub = self.create_subscription(
            MarkerArray,
            'visual_slam/vis/landmarks_cloud',
            self.landmarks_callback,
            10
        )

        # Publishers
        self.path_pub = self.create_publisher(
            Path,
            'vslam_path',
            10
        )

        # State
        self.trajectory = []
        self.current_pose = None
        self.path_msg = Path()
        self.path_msg.header.frame_id = 'map'

        # Trajectory file
        if self.save_trajectory:
            self.traj_file = open(self.trajectory_file, 'w')
            self.get_logger().info(f'Saving trajectory to {self.trajectory_file}')

        self.get_logger().info('VSLAM Monitor initialized')

    def odometry_callback(self, msg):
        """Process odometry from VSLAM"""

        self.current_pose = msg.pose.pose

        # Add to trajectory
        pose_stamped = PoseStamped()
        pose_stamped.header = msg.header
        pose_stamped.pose = msg.pose.pose

        self.path_msg.poses.append(pose_stamped)
        self.path_msg.header.stamp = msg.header.stamp

        # Publish path
        self.path_pub.publish(self.path_msg)

        # Save to file
        if self.save_trajectory:
            self.save_pose_to_file(msg.header.stamp, msg.pose.pose)

        # Log statistics
        if len(self.path_msg.poses) % 100 == 0:
            self.get_logger().info(
                f'Tracked {len(self.path_msg.poses)} poses. '
                f'Current position: ({msg.pose.pose.position.x:.2f}, '
                f'{msg.pose.pose.position.y:.2f}, '
                f'{msg.pose.pose.position.z:.2f})'
            )

    def pose_callback(self, msg):
        """Process visual odometry pose"""
        pass  # Already handled in odometry_callback

    def landmarks_callback(self, msg):
        """Process landmark points"""

        num_landmarks = len(msg.markers)
        if num_landmarks > 0:
            self.get_logger().info(
                f'Tracking {num_landmarks} landmarks',
                throttle_duration_sec=5.0
            )

    def save_pose_to_file(self, timestamp, pose):
        """Save pose to trajectory file"""

        time_sec = timestamp.sec + timestamp.nanosec * 1e-9
        self.traj_file.write(
            f'{time_sec} {pose.position.x} {pose.position.y} {pose.position.z} '
            f'{pose.orientation.x} {pose.orientation.y} {pose.orientation.z} '
            f'{pose.orientation.w}\n'
        )
        self.traj_file.flush()

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'traj_file'):
            self.traj_file.close()

def main(args=None):
    rclpy.init(args=args)
    node = VSLAMMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Nav2 Navigation Stack

### Overview

Nav2 (Navigation2) is the next-generation ROS navigation stack. It provides:

- **Multiple path planners**: NavFn, Smac Planner, Theta Star
- **Multiple controllers**: DWB, TEB, Regulated Pure Pursuit
- **Behavior Trees**: Flexible navigation logic
- **Costmap 2D**: Obstacle representation
- **Recovery Behaviors**: Stuck detection and recovery
- **Waypoint Following**: Multi-goal navigation

### Nav2 Architecture

```
┌─────────────────┐
│  Behavior Tree  │ ← High-level navigation logic
└────────┬────────┘
         │
    ┌────┴────┐
    │  Planner Server │ ← Global path planning
    └────┬────┘
         │
    ┌────┴────┐
    │ Controller Server │ ← Local trajectory generation
    └────┬────┘
         │
    ┌────┴────┐
    │ Costmap 2D │ ← Obstacle representation
    └─────────┘
```

### Installation

```bash
# Install Nav2
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# Install additional packages
sudo apt install ros-humble-slam-toolbox ros-humble-turtlebot3*
```

## Nav2 Configuration

### Costmap Configuration

Costmaps represent the environment and obstacles for navigation.

```yaml
# config/nav2_params.yaml
# Nav2 Parameters Configuration

bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odometry/filtered
    bt_loop_duration: 10
    default_server_timeout: 20
    enable_groot_monitoring: True
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_compute_path_through_poses_action_bt_node
    - nav2_smooth_path_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_spin_action_bt_node
    - nav2_wait_action_bt_node
    - nav2_back_up_action_bt_node
    - nav2_drive_on_heading_bt_node
    - nav2_clear_costmap_service_bt_node
    - nav2_is_stuck_condition_bt_node
    - nav2_goal_reached_condition_bt_node
    - nav2_goal_updated_condition_bt_node
    - nav2_globally_updated_goal_condition_bt_node
    - nav2_is_path_valid_condition_bt_node
    - nav2_initial_pose_received_condition_bt_node
    - nav2_reinitialize_global_localization_service_bt_node
    - nav2_rate_controller_bt_node
    - nav2_distance_controller_bt_node
    - nav2_speed_controller_bt_node
    - nav2_truncate_path_action_bt_node
    - nav2_truncate_path_local_action_bt_node
    - nav2_goal_updater_node_bt_node
    - nav2_recovery_node_bt_node
    - nav2_pipeline_sequence_bt_node
    - nav2_round_robin_node_bt_node
    - nav2_transform_available_condition_bt_node
    - nav2_time_expired_condition_bt_node
    - nav2_path_expiring_timer_condition
    - nav2_distance_traveled_condition_bt_node
    - nav2_single_trigger_bt_node
    - nav2_is_battery_low_condition_bt_node
    - nav2_navigate_through_poses_action_bt_node
    - nav2_navigate_to_pose_action_bt_node
    - nav2_remove_passed_goals_action_bt_node
    - nav2_planner_selector_bt_node
    - nav2_controller_selector_bt_node
    - nav2_goal_checker_selector_bt_node
    - nav2_controller_cancel_bt_node
    - nav2_path_longer_on_approach_bt_node
    - nav2_wait_cancel_bt_node
    - nav2_spin_cancel_bt_node
    - nav2_back_up_cancel_bt_node
    - nav2_drive_on_heading_cancel_bt_node

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]

    # Progress checker parameters
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    # Goal checker parameters
    general_goal_checker:
      stateful: True
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25

    # DWB controller parameters
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: True
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.26
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.26
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 5
      vtheta_samples: 20
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: True
      stateful: True
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
      BaseObstacle.scale: 0.02
      PathAlign.scale: 32.0
      PathAlign.forward_point_distance: 0.1
      GoalAlign.scale: 24.0
      GoalAlign.forward_point_distance: 0.1
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      RotateToGoal.scale: 32.0
      RotateToGoal.slowing_factor: 5.0
      RotateToGoal.lookahead_time: -1.0

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      robot_radius: 0.22
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      always_send_full_costmap: True

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      robot_radius: 0.22
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      always_send_full_costmap: True

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

smoother_server:
  ros__parameters:
    use_sim_time: True
    smoother_plugins: ["simple_smoother"]
    simple_smoother:
      plugin: "nav2_smoother::SimpleSmoother"
      tolerance: 1.0e-10
      max_its: 1000
      do_refinement: True

behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "drive_on_heading", "wait"]
    spin:
      plugin: "nav2_behaviors::Spin"
    backup:
      plugin: "nav2_behaviors::BackUp"
    drive_on_heading:
      plugin: "nav2_behaviors::DriveOnHeading"
    wait:
      plugin: "nav2_behaviors::Wait"
    global_frame: odom
    robot_base_frame: base_link
    transform_tolerance: 0.1
    use_sim_time: true
    simulate_ahead_time: 2.0
    max_rotational_vel: 1.0
    min_rotational_vel: 0.4
    rotational_acc_lim: 3.2
```

### Launch Nav2

```python
# launch/nav2_navigation.launch.py
"""
Launch file for Nav2 navigation with VSLAM
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    """Generate launch description for Nav2"""

    # Get package directories
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    # Declare arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart', default='true')
    use_composition = LaunchConfiguration('use_composition', default='True')
    use_respawn = LaunchConfiguration('use_respawn', default='False')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            get_package_share_directory('isaac_navigation'),
            'config',
            'nav2_params.yaml'
        ),
        description='Full path to the ROS2 parameters file'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    # Nav2 bringup launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
            'use_composition': use_composition,
            'use_respawn': use_respawn,
        }.items()
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_params_file_cmd,
        declare_autostart_cmd,
        nav2_bringup_launch,
    ])
```

## Path Planning Algorithms

### NavFn Planner (Dijkstra's Algorithm)

NavFn computes optimal paths using Dijkstra's algorithm.

```python
# scripts/path_planning_client.py
"""
Nav2 Path Planning Client
Send navigation goals to Nav2
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import math

class NavigationClient(Node):
    """Client for sending navigation goals"""

    def __init__(self):
        super().__init__('navigation_client')

        # Action client
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        self.get_logger().info('Navigation Client initialized')

    def send_goal(self, x, y, yaw, frame_id='map'):
        """Send navigation goal to Nav2"""

        # Wait for action server
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        # Create goal message
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose_stamped(x, y, yaw, frame_id)

        self.get_logger().info(
            f'Sending goal: ({x:.2f}, {y:.2f}, {math.degrees(yaw):.1f}°)'
        )

        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def create_pose_stamped(self, x, y, yaw, frame_id):
        """Create PoseStamped message"""

        pose = PoseStamped()
        pose.header.frame_id = frame_id
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        # Convert yaw to quaternion
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose

    def goal_response_callback(self, future):
        """Handle goal response"""

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle navigation feedback"""

        feedback = feedback_msg.feedback
        current_pose = feedback.current_pose.pose
        distance_remaining = feedback.distance_remaining

        self.get_logger().info(
            f'Distance remaining: {distance_remaining:.2f}m, '
            f'Current position: ({current_pose.position.x:.2f}, '
            f'{current_pose.position.y:.2f})',
            throttle_duration_sec=2.0
        )

    def get_result_callback(self, future):
        """Handle navigation result"""

        result = future.result().result
        status = future.result().status

        if status == 4:  # SUCCEEDED
            self.get_logger().info('Goal reached successfully!')
        elif status == 5:  # CANCELED
            self.get_logger().warn('Goal was canceled')
        elif status == 6:  # ABORTED
            self.get_logger().error('Goal was aborted')
        else:
            self.get_logger().error(f'Goal failed with status: {status}')

def main(args=None):
    rclpy.init(args=args)

    nav_client = NavigationClient()

    # Example: Send navigation goal
    nav_client.send_goal(x=2.0, y=1.0, yaw=0.0)

    rclpy.spin(nav_client)

    nav_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Waypoint Following

```python
# scripts/waypoint_follower.py
"""
Waypoint Following
Navigate through multiple waypoints sequentially
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateThroughPoses, FollowWaypoints
from geometry_msgs.msg import PoseStamped
import math

class WaypointFollower(Node):
    """Follow multiple waypoints in sequence"""

    def __init__(self):
        super().__init__('waypoint_follower')

        # Action client
        self._action_client = ActionClient(
            self,
            FollowWaypoints,
            'follow_waypoints'
        )

        self.waypoint_index = 0

        self.get_logger().info('Waypoint Follower initialized')

    def follow_waypoints(self, waypoints):
        """
        Follow a list of waypoints

        Args:
            waypoints: List of tuples (x, y, yaw)
        """

        # Wait for action server
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        # Create goal message
        goal_msg = FollowWaypoints.Goal()

        for i, (x, y, yaw) in enumerate(waypoints):
            pose = self.create_pose_stamped(x, y, yaw, 'map')
            goal_msg.poses.append(pose)
            self.get_logger().info(
                f'Waypoint {i}: ({x:.2f}, {y:.2f}, {math.degrees(yaw):.1f}°)'
            )

        self.get_logger().info(f'Following {len(waypoints)} waypoints')

        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def create_pose_stamped(self, x, y, yaw, frame_id):
        """Create PoseStamped message"""

        pose = PoseStamped()
        pose.header.frame_id = frame_id
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        # Convert yaw to quaternion
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose

    def goal_response_callback(self, future):
        """Handle goal response"""

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Waypoints rejected')
            return

        self.get_logger().info('Waypoints accepted')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle waypoint following feedback"""

        feedback = feedback_msg.feedback
        current_waypoint = feedback.current_waypoint

        if current_waypoint != self.waypoint_index:
            self.waypoint_index = current_waypoint
            self.get_logger().info(
                f'Navigating to waypoint {current_waypoint}'
            )

    def get_result_callback(self, future):
        """Handle waypoint following result"""

        result = future.result().result
        status = future.result().status

        if status == 4:  # SUCCEEDED
            self.get_logger().info(
                f'Successfully completed all waypoints! '
                f'Missed waypoints: {result.missed_waypoints}'
            )
        elif status == 5:  # CANCELED
            self.get_logger().warn('Waypoint following canceled')
        elif status == 6:  # ABORTED
            self.get_logger().error('Waypoint following aborted')
        else:
            self.get_logger().error(
                f'Waypoint following failed with status: {status}'
            )

def main(args=None):
    rclpy.init(args=args)

    waypoint_follower = WaypointFollower()

    # Define waypoints (x, y, yaw)
    waypoints = [
        (1.0, 0.0, 0.0),
        (2.0, 1.0, math.pi/2),
        (1.0, 2.0, math.pi),
        (0.0, 1.0, -math.pi/2),
        (0.0, 0.0, 0.0),
    ]

    waypoint_follower.follow_waypoints(waypoints)

    rclpy.spin(waypoint_follower)

    waypoint_follower.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Advanced Path Planning with Smac Planner

```python
# scripts/smac_planner_example.py
"""
Smac Planner Configuration
State-lattice path planning for non-holonomic robots
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
import math

class SmacPlannerMonitor(Node):
    """Monitor and visualize Smac Planner output"""

    def __init__(self):
        super().__init__('smac_planner_monitor')

        # Subscribers
        self.path_sub = self.create_subscription(
            Path,
            '/plan',
            self.path_callback,
            10
        )

        self.get_logger().info('Smac Planner Monitor initialized')

    def path_callback(self, msg):
        """Process planned path"""

        num_poses = len(msg.poses)
        if num_poses == 0:
            return

        # Calculate path length
        path_length = self.calculate_path_length(msg.poses)

        # Calculate path curvature
        max_curvature = self.calculate_max_curvature(msg.poses)

        self.get_logger().info(
            f'Path: {num_poses} poses, Length: {path_length:.2f}m, '
            f'Max curvature: {max_curvature:.3f}',
            throttle_duration_sec=2.0
        )

    def calculate_path_length(self, poses):
        """Calculate total path length"""

        length = 0.0
        for i in range(1, len(poses)):
            dx = poses[i].pose.position.x - poses[i-1].pose.position.x
            dy = poses[i].pose.position.y - poses[i-1].pose.position.y
            length += math.sqrt(dx**2 + dy**2)

        return length

    def calculate_max_curvature(self, poses):
        """Calculate maximum path curvature"""

        if len(poses) < 3:
            return 0.0

        max_curvature = 0.0

        for i in range(1, len(poses) - 1):
            # Get three consecutive points
            p0 = poses[i-1].pose.position
            p1 = poses[i].pose.position
            p2 = poses[i+1].pose.position

            # Calculate curvature using Menger curvature
            a = math.sqrt((p1.x - p0.x)**2 + (p1.y - p0.y)**2)
            b = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
            c = math.sqrt((p2.x - p0.x)**2 + (p2.y - p0.y)**2)

            # Area of triangle
            s = (a + b + c) / 2
            area = math.sqrt(max(s * (s - a) * (s - b) * (s - c), 0))

            # Curvature
            if a * b * c > 0:
                curvature = 4 * area / (a * b * c)
                max_curvature = max(max_curvature, curvature)

        return max_curvature

def main(args=None):
    rclpy.init(args=args)
    node = SmacPlannerMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Complete Navigation System

### Integration of VSLAM and Nav2

```python
# launch/complete_navigation.launch.py
"""
Complete Navigation System
VSLAM + Nav2 integration
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    """Launch complete navigation system"""

    # RealSense camera
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('realsense2_camera'),
                'launch',
                'rs_launch.py'
            ])
        ]),
        launch_arguments={
            'enable_infra1': 'true',
            'enable_infra2': 'true',
            'enable_depth': 'true',
        }.items()
    )

    # Isaac ROS VSLAM
    vslam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('isaac_navigation'),
                'launch',
                'isaac_vslam.launch.py'
            ])
        ])
    )

    # Nav2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('isaac_navigation'),
                'launch',
                'nav2_navigation.launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': 'false',
        }.items()
    )

    # RViz visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('isaac_navigation'),
            'rviz',
            'navigation.rviz'
        ])]
    )

    return LaunchDescription([
        realsense_launch,
        vslam_launch,
        nav2_launch,
        rviz_node,
    ])
```

## Exercises

### Exercise 1: VSLAM Mapping
Use Isaac ROS VSLAM to create a map of your environment. Save the trajectory and visualize in RViz.

### Exercise 2: Nav2 Configuration
Tune Nav2 parameters for your robot. Experiment with different planners and controllers.

### Exercise 3: Waypoint Navigation
Create a waypoint following system that navigates through a predefined path.

### Exercise 4: Dynamic Obstacle Avoidance
Test Nav2's obstacle avoidance capabilities by introducing dynamic obstacles in the environment.

### Exercise 5: Complete Autonomous System
Integrate VSLAM, Nav2, and perception from Week 9 to create a complete autonomous navigation system.

## Additional Resources

- [Nav2 Documentation](https://navigation.ros.org/)
- [Isaac ROS VSLAM](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam)
- [Nav2 Tutorials](https://navigation.ros.org/tutorials/index.html)
- [Behavior Trees in Nav2](https://navigation.ros.org/behavior_trees/index.html)
- [Costmap 2D Documentation](https://navigation.ros.org/configuration/packages/configuring-costmaps.html)

## Summary

In this module, you learned:
- Visual SLAM fundamentals and Isaac ROS VSLAM implementation
- Nav2 navigation stack architecture and configuration
- Path planning algorithms (NavFn, Smac Planner)
- Waypoint following and multi-goal navigation
- Integration of VSLAM and Nav2 for autonomous navigation

This completes Module 3 on NVIDIA Isaac. You now have the skills to build complete robotic systems with simulation, perception, and autonomous navigation capabilities.
