---
sidebar_position: 2
title: "Week 2: Sensor Systems"
---

# Week 2: Sensor Systems

## Introduction to Robot Perception

For a robot to operate in the physical world, it must first **perceive** its environment. Sensor systems are the eyes, ears, and proprioceptive sense of Physical AI systems. This week, we'll explore the three fundamental sensor modalities used in modern robotics:

1. **LiDAR** - 3D spatial understanding
2. **RGB-D Cameras** - Visual and depth perception
3. **IMUs** - Orientation and motion sensing

## LiDAR: Light Detection and Ranging

### What is LiDAR?

LiDAR sensors emit laser pulses and measure the time it takes for the light to bounce back, calculating distances to objects in the environment. The result is a **point cloud** - a 3D representation of the space.

### How LiDAR Works

```
Sensor → Laser Pulse → Object → Reflection → Sensor
         |_____________ Time of Flight _____________|

Distance = (Speed of Light × Time of Flight) / 2
```

### Types of LiDAR

1. **Mechanical LiDAR**: Rotating sensor (360° coverage)
   - Examples: Velodyne VLP-16, Ouster OS1
   - 16 to 128 laser channels
   - Range: 100-200 meters

2. **Solid-State LiDAR**: No moving parts (limited FOV)
   - Examples: Livox Mid-360
   - More affordable and robust
   - Range: 40-70 meters

3. **Flash LiDAR**: Illuminates entire scene at once
   - Used in indoor/drone applications
   - Shorter range but high frame rate

### Point Cloud Data Structure

A point cloud is a collection of 3D points (x, y, z) with optional additional information:

```
Point = {
    x: float,       # Position in 3D space
    y: float,
    z: float,
    intensity: float,  # Reflectivity (optional)
    ring: int,         # Which laser ring (optional)
    timestamp: float   # When point was captured
}
```

### LiDAR in ROS 2

ROS 2 uses the `sensor_msgs/PointCloud2` message type for point cloud data.

```python
#!/usr/bin/env python3
"""
LiDAR Point Cloud Subscriber and Processor

This node subscribes to LiDAR data, processes the point cloud,
and extracts useful information like obstacle detection.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
import numpy as np


class LiDARProcessor(Node):
    """
    Processes LiDAR point clouds to detect obstacles and measure distances.
    """

    def __init__(self):
        super().__init__('lidar_processor')

        # Subscribe to LiDAR point cloud topic
        # Common topic names: /scan, /velodyne_points, /livox/lidar
        self.subscription = self.create_subscription(
            PointCloud2,
            '/scan',  # Change to your LiDAR topic
            self.lidar_callback,
            10
        )

        # Parameters for obstacle detection
        self.min_distance = 0.5  # meters - ignore points closer than this
        self.max_distance = 10.0  # meters - ignore points farther than this
        self.obstacle_threshold = 2.0  # meters - warn if obstacle within this distance

        self.get_logger().info('LiDAR Processor Node Started')

    def lidar_callback(self, msg):
        """
        Process incoming point cloud data.

        Args:
            msg: PointCloud2 message from LiDAR sensor
        """
        # Convert ROS PointCloud2 message to numpy array
        points = self.pointcloud2_to_array(msg)

        if points.size == 0:
            self.get_logger().warn('Received empty point cloud')
            return

        # Process the point cloud
        self.analyze_point_cloud(points)

    def pointcloud2_to_array(self, cloud_msg):
        """
        Convert PointCloud2 message to numpy array.

        Args:
            cloud_msg: sensor_msgs/PointCloud2 message

        Returns:
            numpy array of shape (N, 3) containing x, y, z coordinates
        """
        # Extract points from PointCloud2 message
        points_list = []

        for point in point_cloud2.read_points(
            cloud_msg,
            field_names=("x", "y", "z"),
            skip_nans=True
        ):
            points_list.append([point[0], point[1], point[2]])

        if not points_list:
            return np.array([])

        return np.array(points_list)

    def analyze_point_cloud(self, points):
        """
        Analyze point cloud for obstacles and spatial information.

        Args:
            points: numpy array of shape (N, 3) with x, y, z coordinates
        """
        # Calculate distances from sensor (assuming sensor is at origin)
        distances = np.linalg.norm(points, axis=1)

        # Filter points by distance range
        valid_mask = (distances >= self.min_distance) & (distances <= self.max_distance)
        valid_points = points[valid_mask]
        valid_distances = distances[valid_mask]

        if len(valid_points) == 0:
            self.get_logger().warn('No valid points in range')
            return

        # Find closest obstacle
        min_distance = np.min(valid_distances)
        min_idx = np.argmin(valid_distances)
        closest_point = valid_points[min_idx]

        # Obstacle detection
        if min_distance < self.obstacle_threshold:
            self.get_logger().warn(
                f'OBSTACLE DETECTED! Distance: {min_distance:.2f}m at '
                f'position ({closest_point[0]:.2f}, {closest_point[1]:.2f}, {closest_point[2]:.2f})'
            )
        else:
            self.get_logger().info(f'Closest obstacle: {min_distance:.2f}m away')

        # Compute point cloud statistics
        self.compute_statistics(valid_points, valid_distances)

    def compute_statistics(self, points, distances):
        """
        Compute and log statistics about the point cloud.

        Args:
            points: numpy array of valid points
            distances: numpy array of distances
        """
        # Calculate statistics
        num_points = len(points)
        mean_distance = np.mean(distances)
        std_distance = np.std(distances)

        # Analyze spatial distribution
        x_range = np.ptp(points[:, 0])  # peak-to-peak (max - min)
        y_range = np.ptp(points[:, 1])
        z_range = np.ptp(points[:, 2])

        # Log statistics (every 10th callback to avoid spam)
        if not hasattr(self, 'callback_count'):
            self.callback_count = 0

        self.callback_count += 1

        if self.callback_count % 10 == 0:
            self.get_logger().info(
                f'Point Cloud Stats: {num_points} points, '
                f'Mean distance: {mean_distance:.2f}m, '
                f'Spatial extent: ({x_range:.2f}, {y_range:.2f}, {z_range:.2f})m'
            )


def main(args=None):
    rclpy.init(args=args)
    node = LiDARProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down LiDAR Processor...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Visualizing Point Clouds

Use RViz2 to visualize point cloud data:

```bash
# Terminal 1: Run your LiDAR node
ros2 run your_package lidar_processor

# Terminal 2: Launch RViz2
rviz2

# In RViz2:
# 1. Add → PointCloud2
# 2. Set topic to /scan (or your LiDAR topic)
# 3. Set Fixed Frame to "laser_frame" or "base_link"
```

## RGB-D Cameras: Depth Sensing

### What is an RGB-D Camera?

RGB-D cameras provide both color images (RGB) and depth information (D), creating a 3D understanding of the scene.

### Popular RGB-D Sensors

1. **Intel RealSense D435/D455**
   - Stereo depth technology
   - Range: 0.3 - 10 meters
   - 1280x720 @ 30fps

2. **Microsoft Azure Kinect**
   - Time-of-Flight (ToF) depth
   - Range: 0.5 - 5.5 meters
   - 1024x1024 depth @ 30fps

3. **Structure Core**
   - Structured light depth
   - Range: 0.35 - 3.5 meters
   - Compact and robust

### How Depth Cameras Work

#### 1. Stereo Vision
Two cameras separated by a baseline, depth calculated via triangulation (like human eyes).

#### 2. Time-of-Flight (ToF)
Emits infrared light, measures time for reflection (like LiDAR but for entire image).

#### 3. Structured Light
Projects a known pattern, depth calculated from pattern distortion.

### RGB-D Data Processing in ROS 2

```python
#!/usr/bin/env python3
"""
RGB-D Camera Data Processor

Processes synchronized RGB and Depth images from an RGB-D camera.
Demonstrates object detection zone analysis using depth information.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np


class RGBDProcessor(Node):
    """
    Processes RGB-D camera data to analyze depth zones and detect objects.
    """

    def __init__(self):
        super().__init__('rgbd_processor')

        # CV Bridge for converting ROS images to OpenCV format
        self.bridge = CvBridge()

        # Subscribe to RGB image
        self.rgb_sub = self.create_subscription(
            Image,
            '/camera/color/image_raw',  # Change to your camera topic
            self.rgb_callback,
            10
        )

        # Subscribe to Depth image
        self.depth_sub = self.create_subscription(
            Image,
            '/camera/depth/image_raw',  # Change to your depth topic
            self.depth_callback,
            10
        )

        # Subscribe to camera info for intrinsic parameters
        self.info_sub = self.create_subscription(
            CameraInfo,
            '/camera/depth/camera_info',
            self.camera_info_callback,
            10
        )

        # Storage for latest images
        self.latest_rgb = None
        self.latest_depth = None
        self.camera_info = None

        # Depth zones (in meters)
        self.zones = {
            'immediate': (0.0, 0.5),    # Very close - danger zone
            'near': (0.5, 1.5),         # Near - caution zone
            'medium': (1.5, 3.0),       # Medium - safe zone
            'far': (3.0, 10.0)          # Far - detection zone
        }

        self.get_logger().info('RGB-D Processor Node Started')

    def camera_info_callback(self, msg):
        """Store camera intrinsic parameters."""
        self.camera_info = msg

    def rgb_callback(self, msg):
        """
        Process RGB image.

        Args:
            msg: sensor_msgs/Image (RGB8 encoding)
        """
        try:
            # Convert ROS Image to OpenCV format
            self.latest_rgb = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Error converting RGB image: {str(e)}')

    def depth_callback(self, msg):
        """
        Process depth image and analyze zones.

        Args:
            msg: sensor_msgs/Image (16UC1 or 32FC1 encoding)
        """
        try:
            # Convert ROS Image to OpenCV format
            # Depth is typically in millimeters (16UC1) or meters (32FC1)
            if msg.encoding == '16UC1':
                depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='16UC1')
                # Convert from millimeters to meters
                depth_image = depth_image.astype(np.float32) / 1000.0
            elif msg.encoding == '32FC1':
                depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
            else:
                self.get_logger().warn(f'Unknown depth encoding: {msg.encoding}')
                return

            self.latest_depth = depth_image

            # Analyze depth zones
            self.analyze_depth_zones(depth_image)

            # If we have both RGB and depth, create a visualization
            if self.latest_rgb is not None:
                self.create_visualization(self.latest_rgb, depth_image)

        except Exception as e:
            self.get_logger().error(f'Error processing depth image: {str(e)}')

    def analyze_depth_zones(self, depth_image):
        """
        Analyze what percentage of the view is in each depth zone.

        Args:
            depth_image: numpy array of depth values in meters
        """
        # Filter out invalid depths (0 or NaN)
        valid_depth = depth_image[np.isfinite(depth_image) & (depth_image > 0)]

        if len(valid_depth) == 0:
            self.get_logger().warn('No valid depth data')
            return

        total_valid_pixels = len(valid_depth)

        # Count pixels in each zone
        zone_stats = {}
        for zone_name, (min_dist, max_dist) in self.zones.items():
            in_zone = np.sum((valid_depth >= min_dist) & (valid_depth < max_dist))
            percentage = (in_zone / total_valid_pixels) * 100
            zone_stats[zone_name] = percentage

        # Calculate minimum distance in center region (for obstacle detection)
        h, w = depth_image.shape
        center_region = depth_image[h//3:2*h//3, w//3:2*w//3]
        valid_center = center_region[np.isfinite(center_region) & (center_region > 0)]

        if len(valid_center) > 0:
            min_center_distance = np.min(valid_center)

            # Log warning if obstacle is close in center
            if min_center_distance < 0.5:
                self.get_logger().warn(
                    f'CLOSE OBSTACLE AHEAD! Distance: {min_center_distance:.2f}m'
                )

        # Log zone statistics periodically
        if not hasattr(self, 'depth_callback_count'):
            self.depth_callback_count = 0

        self.depth_callback_count += 1

        if self.depth_callback_count % 30 == 0:  # Every 30 frames
            self.get_logger().info(
                f'Depth Zones - Immediate: {zone_stats["immediate"]:.1f}%, '
                f'Near: {zone_stats["near"]:.1f}%, '
                f'Medium: {zone_stats["medium"]:.1f}%, '
                f'Far: {zone_stats["far"]:.1f}%'
            )

    def create_visualization(self, rgb_image, depth_image):
        """
        Create a side-by-side visualization of RGB and colorized depth.

        Args:
            rgb_image: numpy array (H, W, 3) in BGR format
            depth_image: numpy array (H, W) in meters
        """
        # Normalize depth for visualization (0-5 meters mapped to 0-255)
        depth_normalized = np.clip(depth_image, 0, 5.0)
        depth_normalized = (depth_normalized / 5.0 * 255).astype(np.uint8)

        # Apply colormap to depth
        depth_colorized = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

        # Handle invalid depths (make them black)
        invalid_mask = (depth_image == 0) | (~np.isfinite(depth_image))
        depth_colorized[invalid_mask] = [0, 0, 0]

        # Resize if necessary to match RGB
        if rgb_image.shape[:2] != depth_colorized.shape[:2]:
            depth_colorized = cv2.resize(
                depth_colorized,
                (rgb_image.shape[1], rgb_image.shape[0])
            )

        # Create side-by-side display
        combined = np.hstack([rgb_image, depth_colorized])

        # Display (optional - comment out if running headless)
        # cv2.imshow('RGB-D Visualization', combined)
        # cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = RGBDProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down RGB-D Processor...')
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Dependencies

Install required Python packages:

```bash
sudo apt install ros-humble-cv-bridge python3-opencv
pip3 install numpy opencv-python
```

## IMU: Inertial Measurement Unit

### What is an IMU?

An IMU measures a body's specific force, angular rate, and sometimes magnetic field. It typically combines:

1. **Accelerometer** - Measures linear acceleration (3 axes)
2. **Gyroscope** - Measures angular velocity (3 axes)
3. **Magnetometer** (optional) - Measures magnetic field (3 axes, for absolute heading)

### Why IMUs are Critical for Robotics

- **Orientation Estimation**: Know which way is "up" and robot's attitude
- **Motion Detection**: Detect movement, vibration, collisions
- **Dead Reckoning**: Track position when GPS/vision unavailable
- **Sensor Fusion**: Combine with other sensors for robust state estimation

### IMU Coordinate Frame

```
      Z (Up)
      |
      |
      |_______ Y (Right)
     /
    /
   X (Forward)

Roll:  Rotation around X-axis
Pitch: Rotation around Y-axis
Yaw:   Rotation around Z-axis
```

### IMU Data Processing in ROS 2

```python
#!/usr/bin/env python3
"""
IMU Data Processor

Processes IMU data to estimate orientation, detect motion events,
and provide state information for Physical AI systems.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
import numpy as np
import math


class IMUProcessor(Node):
    """
    Processes IMU sensor data for orientation and motion detection.
    """

    def __init__(self):
        super().__init__('imu_processor')

        # Subscribe to IMU data
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',  # Common topic names: /imu/data, /imu/data_raw, /imu
            self.imu_callback,
            10
        )

        # Publisher for processed orientation (roll, pitch, yaw in degrees)
        self.orientation_pub = self.create_publisher(
            Vector3,
            '/imu/orientation_degrees',
            10
        )

        # Motion detection parameters
        self.accel_threshold = 2.0  # m/s^2 - threshold for motion detection
        self.gyro_threshold = 0.5   # rad/s - threshold for rotation detection

        # State tracking
        self.previous_orientation = None
        self.is_moving = False
        self.is_rotating = False

        self.get_logger().info('IMU Processor Node Started')

    def imu_callback(self, msg):
        """
        Process IMU data.

        Args:
            msg: sensor_msgs/Imu message containing orientation,
                 angular velocity, and linear acceleration
        """
        # Extract orientation (as quaternion)
        orientation_q = msg.orientation
        roll, pitch, yaw = self.quaternion_to_euler(
            orientation_q.x,
            orientation_q.y,
            orientation_q.z,
            orientation_q.w
        )

        # Convert to degrees for easier interpretation
        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)

        # Publish orientation in degrees
        orientation_msg = Vector3()
        orientation_msg.x = roll_deg
        orientation_msg.y = pitch_deg
        orientation_msg.z = yaw_deg
        self.orientation_pub.publish(orientation_msg)

        # Extract linear acceleration
        accel = msg.linear_acceleration
        accel_magnitude = math.sqrt(
            accel.x**2 + accel.y**2 + accel.z**2
        )

        # Remove gravity (assuming Z is up and robot is level)
        # In practice, you'd use the orientation to rotate gravity vector
        accel_without_gravity = accel_magnitude - 9.81

        # Extract angular velocity (gyroscope)
        gyro = msg.angular_velocity
        gyro_magnitude = math.sqrt(
            gyro.x**2 + gyro.y**2 + gyro.z**2
        )

        # Motion detection
        currently_moving = abs(accel_without_gravity) > self.accel_threshold
        currently_rotating = gyro_magnitude > self.gyro_threshold

        # Log state changes
        if currently_moving and not self.is_moving:
            self.get_logger().info('Motion detected! Linear acceleration spike.')
            self.is_moving = True
        elif not currently_moving and self.is_moving:
            self.get_logger().info('Motion stopped.')
            self.is_moving = False

        if currently_rotating and not self.is_rotating:
            self.get_logger().info('Rotation detected!')
            self.is_rotating = True
        elif not currently_rotating and self.is_rotating:
            self.get_logger().info('Rotation stopped.')
            self.is_rotating = False

        # Periodic status logging
        if not hasattr(self, 'callback_count'):
            self.callback_count = 0

        self.callback_count += 1

        if self.callback_count % 50 == 0:
            self.get_logger().info(
                f'Orientation (R/P/Y): ({roll_deg:.1f}, {pitch_deg:.1f}, {yaw_deg:.1f})° | '
                f'Accel: {accel_magnitude:.2f} m/s² | '
                f'Gyro: {gyro_magnitude:.2f} rad/s'
            )

        # Detect tilt (if pitch or roll exceeds threshold)
        tilt_threshold = 30  # degrees
        if abs(roll_deg) > tilt_threshold or abs(pitch_deg) > tilt_threshold:
            self.get_logger().warn(
                f'TILT DETECTED! Roll: {roll_deg:.1f}°, Pitch: {pitch_deg:.1f}°'
            )

    def quaternion_to_euler(self, x, y, z, w):
        """
        Convert quaternion to Euler angles (roll, pitch, yaw).

        Args:
            x, y, z, w: Quaternion components

        Returns:
            tuple: (roll, pitch, yaw) in radians
        """
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw


def main(args=None):
    rclpy.init(args=args)
    node = IMUProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down IMU Processor...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Sensor Fusion: Combining Multiple Sensors

### Why Sensor Fusion?

No single sensor is perfect:

- **LiDAR**: Excellent 3D geometry, but no color/texture information
- **Cameras**: Rich visual data, but depth ambiguity
- **IMU**: Fast orientation updates, but drifts over time

**Sensor fusion** combines complementary sensor data to create a more accurate, robust understanding of the environment.

### Common Fusion Approaches

#### 1. Kalman Filter
Optimal estimator for linear systems with Gaussian noise. Used for fusing IMU + GPS, IMU + wheel odometry.

#### 2. Extended Kalman Filter (EKF)
Handles non-linear systems. Common in robot localization (combining multiple sensors).

#### 3. Complementary Filter
Simple frequency-domain approach. Combines high-frequency (gyroscope) and low-frequency (accelerometer) data.

#### 4. Particle Filter
Monte Carlo approach. Useful when uncertainties are non-Gaussian.

### Simple Sensor Fusion Example

```python
#!/usr/bin/env python3
"""
Simple Sensor Fusion: LiDAR + IMU

Combines LiDAR obstacle detection with IMU orientation
to create a robust safety system.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, PointCloud2
from std_msgs.msg import String
import numpy as np
import math


class SensorFusionNode(Node):
    """
    Fuses LiDAR and IMU data for enhanced environmental awareness.
    """

    def __init__(self):
        super().__init__('sensor_fusion_node')

        # Subscribe to IMU
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        # Subscribe to LiDAR
        self.lidar_sub = self.create_subscription(
            PointCloud2,
            '/scan',
            self.lidar_callback,
            10
        )

        # Publish fused safety status
        self.status_pub = self.create_publisher(
            String,
            '/safety_status',
            10
        )

        # State variables
        self.current_orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.closest_obstacle_distance = float('inf')
        self.is_tilted = False
        self.obstacle_warning = False

        # Safety thresholds
        self.tilt_threshold = 25.0  # degrees
        self.obstacle_threshold = 1.0  # meters

        # Timer for periodic status updates
        self.create_timer(1.0, self.publish_status)

        self.get_logger().info('Sensor Fusion Node Started')

    def imu_callback(self, msg):
        """Update orientation from IMU."""
        q = msg.orientation
        roll, pitch, yaw = self.quaternion_to_euler(q.x, q.y, q.z, q.w)

        self.current_orientation = {
            'roll': math.degrees(roll),
            'pitch': math.degrees(pitch),
            'yaw': math.degrees(yaw)
        }

        # Check tilt
        self.is_tilted = (
            abs(self.current_orientation['roll']) > self.tilt_threshold or
            abs(self.current_orientation['pitch']) > self.tilt_threshold
        )

    def lidar_callback(self, msg):
        """Update obstacle distance from LiDAR."""
        # Simplified: assume we process the point cloud and get min distance
        # In practice, use the full processing from earlier example
        # For now, simulate with a placeholder
        # self.closest_obstacle_distance = process_point_cloud(msg)
        pass

    def publish_status(self):
        """Publish fused safety status."""
        status = "SAFE"
        details = []

        if self.is_tilted:
            status = "WARNING"
            details.append(
                f"Tilt detected: Roll={self.current_orientation['roll']:.1f}°, "
                f"Pitch={self.current_orientation['pitch']:.1f}°"
            )

        if self.closest_obstacle_distance < self.obstacle_threshold:
            status = "DANGER"
            details.append(
                f"Obstacle at {self.closest_obstacle_distance:.2f}m"
            )

        # Publish status
        msg = String()
        msg.data = f"Status: {status} | {' | '.join(details)}" if details else f"Status: {status}"
        self.status_pub.publish(msg)

    def quaternion_to_euler(self, x, y, z, w):
        """Convert quaternion to Euler angles."""
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = math.asin(np.clip(sinp, -1.0, 1.0))

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw


def main(args=None):
    rclpy.init(args=args)
    node = SensorFusionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Sensor Fusion Node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Key Takeaways

1. **LiDAR** provides accurate 3D spatial data through point clouds
2. **RGB-D cameras** combine visual and depth information for rich scene understanding
3. **IMUs** enable fast orientation tracking and motion detection
4. **Sensor fusion** combines complementary strengths of multiple sensors
5. **ROS 2** provides standard message types and tools for sensor data processing

## Exercises

1. **LiDAR**: Modify the LiDAR processor to segment the point cloud into ground and non-ground points
2. **RGB-D**: Add simple blob detection to identify objects in specific depth zones
3. **IMU**: Implement a complementary filter to fuse accelerometer and gyroscope data for stable orientation
4. **Fusion**: Create a node that uses IMU orientation to transform LiDAR points into a world-fixed coordinate frame

## Next Week

In Week 3, we'll explore **ROS 2 Architecture & Nodes** in depth - learning how to build robust, modular robot systems using the publisher-subscriber pattern, services, and actions.

## Additional Resources

- [ROS 2 Sensor Messages](https://github.com/ros2/common_interfaces/tree/humble/sensor_msgs)
- [Point Cloud Library (PCL)](https://pointclouds.org/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Understanding IMU Data](https://www.vectornav.com/resources/inertial-navigation-primer)
- [Sensor Fusion Algorithms](https://github.com/ros2/robot_localization)
