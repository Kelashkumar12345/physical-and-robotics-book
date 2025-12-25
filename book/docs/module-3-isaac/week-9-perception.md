---
sidebar_position: 2
title: "Week 9: AI Perception & Manipulation"
---

# Week 9: AI Perception & Manipulation

## Introduction to AI-Powered Perception

Perception is the ability of a robot to understand its environment through sensors. AI-powered perception leverages deep learning models to extract meaningful information from sensory data. In this module, we'll explore:

- Object detection and recognition
- Semantic and instance segmentation
- 6D pose estimation
- Depth estimation
- Grasp pose prediction

### Why Isaac ROS for Perception?

Isaac ROS provides GPU-accelerated perception packages optimized for NVIDIA hardware:

1. **Hardware Acceleration**: Up to 20x faster than CPU-based implementations
2. **Pre-trained Models**: Ready-to-use models for common perception tasks
3. **ROS 2 Integration**: Seamless integration with the ROS ecosystem
4. **DNN Inference**: Optimized inference using TensorRT
5. **Sensor Support**: Works with RealSense, ZED, and other cameras

## Isaac ROS Perception Packages

### Overview of Isaac ROS GEMs

Isaac ROS GEMs (GPU-Enabled Modules) are hardware-accelerated ROS 2 packages:

- **isaac_ros_dnn_inference**: TensorRT-accelerated DNN inference
- **isaac_ros_object_detection**: Object detection (DetectNet, YOLO)
- **isaac_ros_image_segmentation**: Semantic and instance segmentation
- **isaac_ros_pose_estimation**: 6D pose estimation (DOPE, FoundationPose)
- **isaac_ros_depth_estimation**: Monocular and stereo depth estimation
- **isaac_ros_apriltag**: AprilTag detection and localization

### Installation

```bash
# Install Isaac ROS common dependencies
sudo apt-get install -y ros-humble-isaac-ros-common

# Create workspace
mkdir -p ~/workspaces/isaac_ros-dev/src
cd ~/workspaces/isaac_ros-dev/src

# Clone Isaac ROS repositories
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation.git

# Build workspace
cd ~/workspaces/isaac_ros-dev
colcon build --symlink-install

# Source workspace
source install/setup.bash
```

### Docker Development Environment (Recommended)

```bash
# Use Isaac ROS development container
cd ~/workspaces/isaac_ros-dev/src/isaac_ros_common
./scripts/run_dev.sh

# Inside container, build workspace
cd /workspaces/isaac_ros-dev
colcon build --symlink-install
source install/setup.bash
```

## Object Detection and Recognition

### DetectNet with Isaac ROS

DetectNet is a real-time object detection network optimized for NVIDIA GPUs.

```python
# scripts/isaac_object_detection.py
"""
Object Detection using Isaac ROS DetectNet
Real-time object detection with TensorRT acceleration
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D
from cv_bridge import CvBridge
import cv2
import numpy as np

class ObjectDetectionNode(Node):
    """Object detection node using Isaac ROS"""

    def __init__(self):
        super().__init__('object_detection_node')

        # Parameters
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('enable_visualization', True)

        self.confidence_threshold = self.get_parameter(
            'confidence_threshold'
        ).value
        self.enable_viz = self.get_parameter(
            'enable_visualization'
        ).value

        # CV Bridge
        self.bridge = CvBridge()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            'image_raw',
            self.image_callback,
            10
        )

        self.detections_sub = self.create_subscription(
            Detection2DArray,
            'detections',
            self.detections_callback,
            10
        )

        # Publisher for annotated images
        self.annotated_pub = self.create_publisher(
            Image,
            'annotated_image',
            10
        )

        self.current_image = None
        self.latest_detections = None

        self.get_logger().info('Object Detection Node initialized')

    def image_callback(self, msg):
        """Store latest image"""
        self.current_image = msg

    def detections_callback(self, msg):
        """Process detections"""
        self.latest_detections = msg

        if self.enable_viz and self.current_image is not None:
            self.visualize_detections(self.current_image, msg)

    def visualize_detections(self, image_msg, detections_msg):
        """Draw bounding boxes on image"""

        # Convert ROS Image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(image_msg, 'bgr8')

        # Draw each detection
        for detection in detections_msg.detections:
            # Get bounding box
            bbox = detection.bbox
            center_x = bbox.center.position.x
            center_y = bbox.center.position.y
            size_x = bbox.size_x
            size_y = bbox.size_y

            # Calculate corners
            x1 = int(center_x - size_x / 2)
            y1 = int(center_y - size_y / 2)
            x2 = int(center_x + size_x / 2)
            y2 = int(center_y + size_y / 2)

            # Get class and confidence
            if detection.results:
                result = detection.results[0]
                class_id = result.hypothesis.class_id
                score = result.hypothesis.score

                if score >= self.confidence_threshold:
                    # Draw bounding box
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Draw label
                    label = f"{class_id}: {score:.2f}"
                    cv2.putText(
                        cv_image,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

        # Publish annotated image
        annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
        annotated_msg.header = image_msg.header
        self.annotated_pub.publish(annotated_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Launch File for Object Detection

```python
# launch/object_detection.launch.py
"""
Launch file for Isaac ROS object detection
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """Generate launch description for object detection"""

    # Declare arguments
    model_name_arg = DeclareLaunchArgument(
        'model_name',
        default_value='peoplenet',
        description='Model name (peoplenet, trafficcamnet, etc.)'
    )

    model_repository_paths_arg = DeclareLaunchArgument(
        'model_repository_paths',
        default_value='["/tmp/models"]',
        description='Model repository paths'
    )

    # DNN Image Encoder Node
    dnn_image_encoder_node = Node(
        package='isaac_ros_dnn_image_encoder',
        executable='dnn_image_encoder',
        name='dnn_image_encoder',
        parameters=[{
            'network_image_width': 960,
            'network_image_height': 544,
            'image_mean': [0.5, 0.5, 0.5],
            'image_stddev': [0.5, 0.5, 0.5],
        }],
        remappings=[
            ('image', 'image_raw'),
            ('encoded_tensor', 'tensor_pub'),
        ]
    )

    # Triton Node for DNN Inference
    triton_node = Node(
        package='isaac_ros_triton',
        executable='isaac_ros_triton',
        name='triton_node',
        parameters=[{
            'model_name': LaunchConfiguration('model_name'),
            'model_repository_paths': LaunchConfiguration('model_repository_paths'),
            'input_tensor_names': ['input_tensor'],
            'input_binding_names': ['input_1'],
            'output_tensor_names': ['output_cov', 'output_bbox'],
            'output_binding_names': ['output_cov/Sigmoid', 'output_bbox/BiasAdd'],
            'max_batch_size': 1,
        }]
    )

    # DetectNet Decoder Node
    detectnet_decoder_node = Node(
        package='isaac_ros_detectnet',
        executable='isaac_ros_detectnet',
        name='detectnet_decoder',
        parameters=[{
            'confidence_threshold': 0.5,
            'coverage_threshold': 0.5,
        }],
        remappings=[
            ('detections', 'detections_output'),
        ]
    )

    # Visualization Node
    visualization_node = Node(
        package='isaac_perception',
        executable='object_detection_node.py',
        name='detection_visualizer',
        parameters=[{
            'confidence_threshold': 0.5,
            'enable_visualization': True,
        }],
        remappings=[
            ('detections', 'detections_output'),
        ]
    )

    return LaunchDescription([
        model_name_arg,
        model_repository_paths_arg,
        dnn_image_encoder_node,
        triton_node,
        detectnet_decoder_node,
        visualization_node,
    ])
```

## Image Segmentation

### Semantic Segmentation with U-Net

Semantic segmentation assigns a class label to each pixel in an image.

```python
# scripts/semantic_segmentation.py
"""
Semantic Segmentation using Isaac ROS U-Net
Pixel-wise classification for scene understanding
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class SemanticSegmentationNode(Node):
    """Semantic segmentation node"""

    def __init__(self):
        super().__init__('semantic_segmentation_node')

        # Parameters
        self.declare_parameter('num_classes', 21)  # PASCAL VOC
        self.declare_parameter('color_map', 'pascal')

        self.num_classes = self.get_parameter('num_classes').value
        self.color_map_type = self.get_parameter('color_map').value

        # CV Bridge
        self.bridge = CvBridge()

        # Color map for visualization
        self.color_map = self.create_color_map()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            'image_raw',
            self.image_callback,
            10
        )

        self.segmentation_sub = self.create_subscription(
            Image,
            'segmentation',
            self.segmentation_callback,
            10
        )

        # Publishers
        self.colored_seg_pub = self.create_publisher(
            Image,
            'colored_segmentation',
            10
        )

        self.overlay_pub = self.create_publisher(
            Image,
            'segmentation_overlay',
            10
        )

        self.current_image = None

        self.get_logger().info('Semantic Segmentation Node initialized')

    def create_color_map(self):
        """Create color map for visualization"""

        if self.color_map_type == 'pascal':
            # PASCAL VOC color map
            color_map = np.zeros((256, 3), dtype=np.uint8)
            color_map[0] = [0, 0, 0]  # Background
            color_map[1] = [128, 0, 0]  # Aeroplane
            color_map[2] = [0, 128, 0]  # Bicycle
            color_map[3] = [128, 128, 0]  # Bird
            color_map[4] = [0, 0, 128]  # Boat
            color_map[5] = [128, 0, 128]  # Bottle
            color_map[6] = [0, 128, 128]  # Bus
            color_map[7] = [128, 128, 128]  # Car
            color_map[8] = [64, 0, 0]  # Cat
            color_map[9] = [192, 0, 0]  # Chair
            color_map[10] = [64, 128, 0]  # Cow
            # ... add more classes
        else:
            # Random color map
            color_map = np.random.randint(
                0, 255,
                size=(self.num_classes, 3),
                dtype=np.uint8
            )
            color_map[0] = [0, 0, 0]  # Background

        return color_map

    def image_callback(self, msg):
        """Store latest RGB image"""
        self.current_image = msg

    def segmentation_callback(self, msg):
        """Process segmentation mask"""

        # Convert segmentation mask to CV image
        seg_mask = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')

        # Create colored segmentation
        colored_seg = self.colorize_segmentation(seg_mask)

        # Publish colored segmentation
        colored_msg = self.bridge.cv2_to_imgmsg(colored_seg, 'bgr8')
        colored_msg.header = msg.header
        self.colored_seg_pub.publish(colored_msg)

        # Create overlay if RGB image available
        if self.current_image is not None:
            overlay = self.create_overlay(self.current_image, colored_seg)
            overlay_msg = self.bridge.cv2_to_imgmsg(overlay, 'bgr8')
            overlay_msg.header = msg.header
            self.overlay_pub.publish(overlay_msg)

    def colorize_segmentation(self, seg_mask):
        """Apply color map to segmentation mask"""

        h, w = seg_mask.shape
        colored = np.zeros((h, w, 3), dtype=np.uint8)

        for class_id in range(self.num_classes):
            mask = seg_mask == class_id
            colored[mask] = self.color_map[class_id]

        return colored

    def create_overlay(self, rgb_msg, colored_seg):
        """Create overlay of RGB image and segmentation"""

        # Convert RGB message to CV image
        rgb_image = self.bridge.imgmsg_to_cv2(rgb_msg, 'bgr8')

        # Resize segmentation if necessary
        if rgb_image.shape[:2] != colored_seg.shape[:2]:
            colored_seg = cv2.resize(
                colored_seg,
                (rgb_image.shape[1], rgb_image.shape[0])
            )

        # Blend images
        alpha = 0.6
        overlay = cv2.addWeighted(rgb_image, alpha, colored_seg, 1 - alpha, 0)

        return overlay

def main(args=None):
    rclpy.init(args=args)
    node = SemanticSegmentationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 6D Pose Estimation for Manipulation

### DOPE (Deep Object Pose Estimation)

DOPE estimates the 6D pose (3D position and 3D orientation) of known objects.

```python
# scripts/pose_estimation_dope.py
"""
6D Pose Estimation using Isaac ROS DOPE
Estimate object pose for robotic manipulation
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseArray, Pose
from vision_msgs.msg import Detection3DArray
from cv_bridge import CvBridge
import cv2
import numpy as np
import tf2_ros
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class PoseEstimationNode(Node):
    """6D pose estimation node using DOPE"""

    def __init__(self):
        super().__init__('pose_estimation_node')

        # Parameters
        self.declare_parameter('object_name', 'soup_can')
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('camera_frame', 'camera_color_optical_frame')

        self.object_name = self.get_parameter('object_name').value
        self.publish_tf = self.get_parameter('publish_tf').value
        self.camera_frame = self.get_parameter('camera_frame').value

        # CV Bridge
        self.bridge = CvBridge()

        # TF Broadcaster
        if self.publish_tf:
            self.tf_broadcaster = TransformBroadcaster(self)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            'image_raw',
            self.image_callback,
            10
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            'camera_info',
            self.camera_info_callback,
            10
        )

        self.detections_sub = self.create_subscription(
            Detection3DArray,
            'dope/detections',
            self.detections_callback,
            10
        )

        # Publishers
        self.pose_pub = self.create_publisher(
            PoseArray,
            'object_poses',
            10
        )

        self.annotated_pub = self.create_publisher(
            Image,
            'pose_annotated_image',
            10
        )

        self.current_image = None
        self.camera_info = None

        self.get_logger().info(f'Pose Estimation Node initialized for {self.object_name}')

    def image_callback(self, msg):
        """Store latest image"""
        self.current_image = msg

    def camera_info_callback(self, msg):
        """Store camera calibration info"""
        self.camera_info = msg

    def detections_callback(self, msg):
        """Process 6D pose detections"""

        if len(msg.detections) == 0:
            return

        pose_array = PoseArray()
        pose_array.header = msg.header

        for idx, detection in enumerate(msg.detections):
            pose = detection.results[0].pose.pose
            pose_array.poses.append(pose)

            # Publish TF
            if self.publish_tf:
                self.publish_object_tf(pose, msg.header, idx)

            # Log pose
            self.get_logger().info(
                f'Object {idx}: Position ({pose.position.x:.3f}, '
                f'{pose.position.y:.3f}, {pose.position.z:.3f}), '
                f'Orientation ({pose.orientation.x:.3f}, '
                f'{pose.orientation.y:.3f}, {pose.orientation.z:.3f}, '
                f'{pose.orientation.w:.3f})'
            )

        # Publish pose array
        self.pose_pub.publish(pose_array)

        # Visualize
        if self.current_image is not None:
            self.visualize_poses(self.current_image, msg)

    def publish_object_tf(self, pose, header, idx):
        """Publish TF transform for object"""

        t = TransformStamped()
        t.header = header
        t.child_frame_id = f'{self.object_name}_{idx}'

        t.transform.translation.x = pose.position.x
        t.transform.translation.y = pose.position.y
        t.transform.translation.z = pose.position.z

        t.transform.rotation = pose.orientation

        self.tf_broadcaster.sendTransform(t)

    def visualize_poses(self, image_msg, detections_msg):
        """Draw 3D bounding box on image"""

        cv_image = self.bridge.imgmsg_to_cv2(image_msg, 'bgr8')

        if self.camera_info is None:
            return

        # Get camera intrinsics
        K = np.array(self.camera_info.k).reshape(3, 3)

        for detection in detections_msg.detections:
            pose = detection.results[0].pose.pose

            # Get object dimensions (example: soup can)
            # Replace with actual object dimensions
            dimensions = np.array([0.067, 0.067, 0.103])  # [width, height, depth]

            # Draw 3D bounding box
            self.draw_3d_bbox(cv_image, pose, dimensions, K)

        # Publish annotated image
        annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
        annotated_msg.header = image_msg.header
        self.annotated_pub.publish(annotated_msg)

    def draw_3d_bbox(self, image, pose, dimensions, K):
        """Draw 3D bounding box on image"""

        # Define 3D bounding box corners
        w, h, d = dimensions
        corners_3d = np.array([
            [-w/2, -h/2, -d/2],
            [w/2, -h/2, -d/2],
            [w/2, h/2, -d/2],
            [-w/2, h/2, -d/2],
            [-w/2, -h/2, d/2],
            [w/2, -h/2, d/2],
            [w/2, h/2, d/2],
            [-w/2, h/2, d/2],
        ])

        # Convert quaternion to rotation matrix
        q = pose.orientation
        R = self.quaternion_to_rotation_matrix(q)

        # Transform corners to camera frame
        t = np.array([pose.position.x, pose.position.y, pose.position.z])
        corners_cam = (R @ corners_3d.T).T + t

        # Project to image plane
        corners_2d = (K @ corners_cam.T).T
        corners_2d = corners_2d[:, :2] / corners_2d[:, 2:]

        # Draw edges
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
            (0, 4), (1, 5), (2, 6), (3, 7),  # Vertical edges
        ]

        for edge in edges:
            pt1 = tuple(corners_2d[edge[0]].astype(int))
            pt2 = tuple(corners_2d[edge[1]].astype(int))
            cv2.line(image, pt1, pt2, (0, 255, 0), 2)

    @staticmethod
    def quaternion_to_rotation_matrix(q):
        """Convert quaternion to rotation matrix"""

        qx, qy, qz, qw = q.x, q.y, q.z, q.w

        R = np.array([
            [1 - 2*(qy**2 + qz**2), 2*(qx*qy - qw*qz), 2*(qx*qz + qw*qy)],
            [2*(qx*qy + qw*qz), 1 - 2*(qx**2 + qz**2), 2*(qy*qz - qw*qx)],
            [2*(qx*qz - qw*qy), 2*(qy*qz + qw*qx), 1 - 2*(qx**2 + qy**2)],
        ])

        return R

def main(args=None):
    rclpy.init(args=args)
    node = PoseEstimationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Grasping and Manipulation Planning

### Grasp Pose Generation

```python
# scripts/grasp_planning.py
"""
Grasp Planning for Robotic Manipulation
Generate grasp poses based on object pose and geometry
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose, PoseStamped
from moveit_msgs.msg import Grasp, GripperTranslation
from std_msgs.msg import Header
import numpy as np
from scipy.spatial.transform import Rotation

class GraspPlanningNode(Node):
    """Generate grasp poses for manipulation"""

    def __init__(self):
        super().__init__('grasp_planning_node')

        # Parameters
        self.declare_parameter('gripper_width', 0.08)
        self.declare_parameter('approach_distance', 0.15)
        self.declare_parameter('retreat_distance', 0.15)
        self.declare_parameter('num_grasps_per_object', 8)

        self.gripper_width = self.get_parameter('gripper_width').value
        self.approach_dist = self.get_parameter('approach_distance').value
        self.retreat_dist = self.get_parameter('retreat_distance').value
        self.num_grasps = self.get_parameter('num_grasps_per_object').value

        # Subscribers
        self.object_pose_sub = self.create_subscription(
            PoseArray,
            'object_poses',
            self.object_pose_callback,
            10
        )

        # Publishers
        self.grasp_poses_pub = self.create_publisher(
            PoseArray,
            'grasp_poses',
            10
        )

        self.get_logger().info('Grasp Planning Node initialized')

    def object_pose_callback(self, msg):
        """Generate grasp poses for detected objects"""

        all_grasp_poses = PoseArray()
        all_grasp_poses.header = msg.header

        for object_pose in msg.poses:
            grasp_poses = self.generate_grasp_poses(object_pose)
            all_grasp_poses.poses.extend(grasp_poses)

        # Publish all grasp poses
        self.grasp_poses_pub.publish(all_grasp_poses)

        self.get_logger().info(
            f'Generated {len(all_grasp_poses.poses)} grasp poses for '
            f'{len(msg.poses)} objects'
        )

    def generate_grasp_poses(self, object_pose):
        """Generate multiple grasp poses for an object"""

        grasp_poses = []

        # Extract object position and orientation
        obj_pos = np.array([
            object_pose.position.x,
            object_pose.position.y,
            object_pose.position.z
        ])

        obj_quat = np.array([
            object_pose.orientation.x,
            object_pose.orientation.y,
            object_pose.orientation.z,
            object_pose.orientation.w
        ])

        obj_rot = Rotation.from_quat(obj_quat)

        # Generate grasps around the object
        for i in range(self.num_grasps):
            angle = 2 * np.pi * i / self.num_grasps

            # Grasp approach direction (around z-axis of object)
            approach_dir = np.array([np.cos(angle), np.sin(angle), 0])

            # Rotate approach direction by object orientation
            approach_dir_world = obj_rot.apply(approach_dir)

            # Grasp position (offset from object center)
            grasp_offset = 0.05  # 5cm from center
            grasp_pos = obj_pos + approach_dir_world * grasp_offset

            # Grasp orientation
            # Gripper approaches from the side
            z_axis = -approach_dir_world  # Approach direction
            x_axis = np.array([0, 0, 1])  # Gripper opening direction
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            x_axis = np.cross(y_axis, z_axis)

            # Create rotation matrix
            rot_matrix = np.column_stack([x_axis, y_axis, z_axis])
            grasp_rot = Rotation.from_matrix(rot_matrix)
            grasp_quat = grasp_rot.as_quat()

            # Create grasp pose
            grasp_pose = Pose()
            grasp_pose.position.x = grasp_pos[0]
            grasp_pose.position.y = grasp_pos[1]
            grasp_pose.position.z = grasp_pos[2]
            grasp_pose.orientation.x = grasp_quat[0]
            grasp_pose.orientation.y = grasp_quat[1]
            grasp_pose.orientation.z = grasp_quat[2]
            grasp_pose.orientation.w = grasp_quat[3]

            grasp_poses.append(grasp_pose)

        return grasp_poses

    def create_moveit_grasp(self, grasp_pose, object_name):
        """Create MoveIt Grasp message"""

        grasp = Grasp()
        grasp.id = f"grasp_{object_name}"

        # Grasp pose
        grasp.grasp_pose = PoseStamped()
        grasp.grasp_pose.header.frame_id = "base_link"
        grasp.grasp_pose.pose = grasp_pose

        # Pre-grasp approach
        grasp.pre_grasp_approach = GripperTranslation()
        grasp.pre_grasp_approach.direction.header.frame_id = "base_link"
        grasp.pre_grasp_approach.direction.vector.z = -1.0
        grasp.pre_grasp_approach.min_distance = 0.05
        grasp.pre_grasp_approach.desired_distance = self.approach_dist

        # Post-grasp retreat
        grasp.post_grasp_retreat = GripperTranslation()
        grasp.post_grasp_retreat.direction.header.frame_id = "base_link"
        grasp.post_grasp_retreat.direction.vector.z = 1.0
        grasp.post_grasp_retreat.min_distance = 0.05
        grasp.post_grasp_retreat.desired_distance = self.retreat_dist

        # Gripper posture
        # Open gripper before grasp
        grasp.pre_grasp_posture.joint_names = ["panda_finger_joint1", "panda_finger_joint2"]
        grasp.pre_grasp_posture.points = [type('', (), {'positions': [0.04, 0.04]})]

        # Close gripper during grasp
        grasp.grasp_posture.joint_names = ["panda_finger_joint1", "panda_finger_joint2"]
        grasp.grasp_posture.points = [type('', (), {'positions': [0.02, 0.02]})]

        return grasp

def main(args=None):
    rclpy.init(args=args)
    node = GraspPlanningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Complete Perception Pipeline

```python
# scripts/perception_pipeline.py
"""
Complete Perception Pipeline
Integrates detection, segmentation, and pose estimation
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from vision_msgs.msg import Detection2DArray, Detection3DArray
from geometry_msgs.msg import PoseArray
from cv_bridge import CvBridge
import cv2
import numpy as np

class PerceptionPipeline(Node):
    """Unified perception pipeline for manipulation"""

    def __init__(self):
        super().__init__('perception_pipeline')

        # Parameters
        self.declare_parameter('enable_detection', True)
        self.declare_parameter('enable_segmentation', True)
        self.declare_parameter('enable_pose_estimation', True)
        self.declare_parameter('target_objects', ['bottle', 'can', 'box'])

        self.enable_detection = self.get_parameter('enable_detection').value
        self.enable_segmentation = self.get_parameter('enable_segmentation').value
        self.enable_pose = self.get_parameter('enable_pose_estimation').value
        self.target_objects = self.get_parameter('target_objects').value

        # CV Bridge
        self.bridge = CvBridge()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10
        )

        if self.enable_detection:
            self.detection_sub = self.create_subscription(
                Detection2DArray, 'detections', self.detection_callback, 10
            )

        if self.enable_segmentation:
            self.segmentation_sub = self.create_subscription(
                Image, 'segmentation', self.segmentation_callback, 10
            )

        if self.enable_pose:
            self.pose_sub = self.create_subscription(
                Detection3DArray, 'pose_detections', self.pose_callback, 10
            )

        # Publishers
        self.scene_understanding_pub = self.create_publisher(
            Image, 'scene_understanding', 10
        )

        self.target_poses_pub = self.create_publisher(
            PoseArray, 'target_object_poses', 10
        )

        # State
        self.current_image = None
        self.current_detections = None
        self.current_segmentation = None
        self.current_poses = None

        self.get_logger().info('Perception Pipeline initialized')

    def image_callback(self, msg):
        """Process incoming image"""
        self.current_image = msg
        self.process_scene()

    def detection_callback(self, msg):
        """Store detections"""
        self.current_detections = msg

    def segmentation_callback(self, msg):
        """Store segmentation"""
        self.current_segmentation = msg

    def pose_callback(self, msg):
        """Store pose estimates"""
        self.current_poses = msg
        self.filter_target_objects()

    def filter_target_objects(self):
        """Filter poses for target objects only"""

        if self.current_poses is None:
            return

        target_pose_array = PoseArray()
        target_pose_array.header = self.current_poses.header

        for detection in self.current_poses.detections:
            if detection.results:
                class_id = detection.results[0].hypothesis.class_id
                if class_id in self.target_objects:
                    pose = detection.results[0].pose.pose
                    target_pose_array.poses.append(pose)

        self.target_poses_pub.publish(target_pose_array)

    def process_scene(self):
        """Create unified scene understanding visualization"""

        if self.current_image is None:
            return

        cv_image = self.bridge.imgmsg_to_cv2(self.current_image, 'bgr8')
        scene_viz = cv_image.copy()

        # Overlay segmentation
        if self.current_segmentation is not None:
            seg_mask = self.bridge.imgmsg_to_cv2(
                self.current_segmentation, 'mono8'
            )
            colored_seg = self.colorize_segmentation(seg_mask)
            scene_viz = cv2.addWeighted(scene_viz, 0.6, colored_seg, 0.4, 0)

        # Draw detections
        if self.current_detections is not None:
            scene_viz = self.draw_detections(scene_viz, self.current_detections)

        # Draw pose estimates
        if self.current_poses is not None:
            scene_viz = self.draw_poses(scene_viz, self.current_poses)

        # Publish scene understanding
        scene_msg = self.bridge.cv2_to_imgmsg(scene_viz, 'bgr8')
        scene_msg.header = self.current_image.header
        self.scene_understanding_pub.publish(scene_msg)

    def colorize_segmentation(self, seg_mask):
        """Apply color map to segmentation"""
        # Simplified color map
        color_map = np.random.randint(0, 255, size=(256, 3), dtype=np.uint8)
        color_map[0] = [0, 0, 0]
        return color_map[seg_mask]

    def draw_detections(self, image, detections):
        """Draw 2D bounding boxes"""
        for det in detections.detections:
            bbox = det.bbox
            x1 = int(bbox.center.position.x - bbox.size_x / 2)
            y1 = int(bbox.center.position.y - bbox.size_y / 2)
            x2 = int(bbox.center.position.x + bbox.size_x / 2)
            y2 = int(bbox.center.position.y + bbox.size_y / 2)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return image

    def draw_poses(self, image, poses):
        """Draw 3D pose indicators"""
        for detection in poses.detections:
            pose = detection.results[0].pose.pose
            # Draw center point
            x = int(pose.position.x * 100 + image.shape[1] / 2)
            y = int(pose.position.y * 100 + image.shape[0] / 2)
            cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
        return image

def main(args=None):
    rclpy.init(args=args)
    node = PerceptionPipeline()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Exercises

### Exercise 1: Object Detection Pipeline
Setup an object detection pipeline using Isaac ROS DetectNet. Test with different confidence thresholds and measure accuracy.

### Exercise 2: Semantic Segmentation
Train a semantic segmentation model on synthetic data from Isaac Sim and deploy it using Isaac ROS.

### Exercise 3: 6D Pose Estimation
Implement a complete pose estimation pipeline for manipulation. Generate grasp poses based on detected object poses.

### Exercise 4: Complete Manipulation
Integrate perception with MoveIt2 to execute pick-and-place tasks based on detected objects.

## Additional Resources

- [Isaac ROS Documentation](https://nvidia-isaac-ros.github.io/index.html)
- [DOPE Paper](https://arxiv.org/abs/1809.10790)
- [Isaac ROS GitHub](https://github.com/NVIDIA-ISAAC-ROS)
- [TensorRT Documentation](https://docs.nvidia.com/deeplearning/tensorrt/)

## Next Steps

In Week 10, we'll explore Visual SLAM (VSLAM) and Nav2 path planning for autonomous navigation, building on the perception capabilities developed this week.
