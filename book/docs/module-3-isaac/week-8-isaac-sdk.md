---
sidebar_position: 1
title: "Week 8: Isaac SDK & Isaac Sim"
---

# Week 8: Isaac SDK & Isaac Sim

## Introduction to NVIDIA Isaac Platform

The NVIDIA Isaac platform is a comprehensive robotics development toolkit that provides tools for simulation, perception, manipulation, and navigation. It consists of several key components:

- **Isaac Sim**: A photorealistic robot simulator built on NVIDIA Omniverse
- **Isaac SDK**: A collection of GPU-accelerated libraries for robotics applications
- **Isaac ROS**: ROS 2 packages optimized for NVIDIA hardware
- **Isaac Gym**: A high-performance physics simulation environment for reinforcement learning

### Why Isaac Platform?

The Isaac platform offers several advantages for robotics development:

1. **Photorealistic Simulation**: Isaac Sim provides physically accurate and visually realistic environments
2. **GPU Acceleration**: Leverages NVIDIA GPUs for high-performance computation
3. **Synthetic Data Generation**: Create large-scale training datasets without manual labeling
4. **Hardware Acceleration**: Optimized for NVIDIA Jetson and other NVIDIA platforms
5. **Seamless Integration**: Works with ROS 2, PyTorch, and other popular frameworks

## Isaac Sim for Photorealistic Simulation

### Overview

Isaac Sim is built on the NVIDIA Omniverse platform and uses the Universal Scene Description (USD) format for 3D scenes. It provides:

- Ray-traced rendering for photorealistic visuals
- PhysX for accurate physics simulation
- Support for importing CAD models and URDF robot descriptions
- Synthetic data generation with ground truth annotations
- Multi-robot and multi-camera simulations

### Key Features

1. **RTX Rendering**: Real-time ray tracing for realistic lighting and shadows
2. **Physics Simulation**: Accurate contact dynamics, friction, and collision detection
3. **Sensor Simulation**: RGB cameras, depth cameras, LiDAR, IMU, and more
4. **Domain Randomization**: Automatic variation of scene parameters for robust training
5. **ROS 2 Bridge**: Bidirectional communication between Isaac Sim and ROS 2

### System Requirements

```bash
# Minimum Requirements
- NVIDIA RTX GPU (RTX 2070 or higher recommended)
- Ubuntu 20.04 or 22.04
- 32 GB RAM (64 GB recommended)
- 50 GB disk space

# Software Dependencies
- NVIDIA Driver 525.60.11 or later
- Docker (optional but recommended)
- ROS 2 Humble or later
```

### Installation

```bash
# Install Omniverse Launcher
wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage
chmod +x omniverse-launcher-linux.AppImage
./omniverse-launcher-linux.AppImage

# Through Omniverse Launcher, install:
# 1. Isaac Sim (latest version)
# 2. Nucleus (for asset storage)

# Or use Docker (recommended for development)
docker pull nvcr.io/nvidia/isaac-sim:2023.1.1

# Run Isaac Sim with Docker
docker run --name isaac-sim --entrypoint bash -it --gpus all \
  -e "ACCEPT_EULA=Y" --rm --network=host \
  -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
  -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
  -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
  -v ~/docker/isaac-sim/cache/glcache:/root/.cache/nvidia/GLCache:rw \
  -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
  -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
  -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
  nvcr.io/nvidia/isaac-sim:2023.1.1
```

## Setting Up Isaac Sim with ROS 2

### ROS 2 Bridge Configuration

Isaac Sim provides a ROS 2 bridge for seamless integration with the ROS ecosystem.

```python
# scripts/isaac_ros2_bridge.py
"""
Isaac Sim ROS 2 Bridge Setup
Demonstrates how to establish communication between Isaac Sim and ROS 2
"""

import omni
from omni.isaac.kit import SimulationApp

# Launch Isaac Sim
simulation_app = SimulationApp({"headless": False})

import carb
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage
import omni.graph.core as og

class IsaacROS2Bridge:
    """Setup ROS 2 bridge in Isaac Sim"""

    def __init__(self):
        self.world = World(stage_units_in_meters=1.0)
        self.setup_ros2_bridge()

    def setup_ros2_bridge(self):
        """Configure ROS 2 bridge with action graph"""

        # Create ROS 2 context
        try:
            og.Controller.edit(
                {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("ROS2Context", "omni.isaac.ros2_bridge.ROS2Context"),
                        ("ROS2CameraHelper", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
                        ("ROS2PublishClock", "omni.isaac.ros2_bridge.ROS2PublishClock"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("OnPlaybackTick.outputs:tick", "ROS2PublishClock.inputs:execIn"),
                        ("ROS2Context.outputs:context", "ROS2PublishClock.inputs:context"),
                    ],
                    og.Controller.Keys.SET_VALUES: [
                        ("ROS2Context.inputs:useDomainIDEnvVar", True),
                    ],
                },
            )
            print("ROS 2 bridge configured successfully")
        except Exception as e:
            carb.log_error(f"Failed to create ROS 2 bridge: {e}")

    def add_camera_publisher(self, camera_path: str, topic_name: str):
        """Add ROS 2 camera publisher"""

        try:
            og.Controller.edit(
                {"graph_path": "/ActionGraph"},
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("ROS2PubImage", "omni.isaac.ros2_bridge.ROS2PublishImage"),
                        ("ROS2PubCameraInfo", "omni.isaac.ros2_bridge.ROS2PublishCameraInfo"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("OnPlaybackTick.outputs:tick", "ROS2PubImage.inputs:execIn"),
                        ("ROS2Context.outputs:context", "ROS2PubImage.inputs:context"),
                        ("ROS2Context.outputs:context", "ROS2PubCameraInfo.inputs:context"),
                    ],
                    og.Controller.Keys.SET_VALUES: [
                        ("ROS2PubImage.inputs:topicName", topic_name),
                        ("ROS2PubImage.inputs:renderProductPath", camera_path),
                        ("ROS2PubCameraInfo.inputs:topicName", f"{topic_name}/camera_info"),
                    ],
                },
            )
            print(f"Camera publisher added for {topic_name}")
        except Exception as e:
            carb.log_error(f"Failed to add camera publisher: {e}")

    def add_tf_publisher(self):
        """Add TF publisher for robot transforms"""

        try:
            og.Controller.edit(
                {"graph_path": "/ActionGraph"},
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("ROS2PubTF", "omni.isaac.ros2_bridge.ROS2PublishTransformTree"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("OnPlaybackTick.outputs:tick", "ROS2PubTF.inputs:execIn"),
                        ("ROS2Context.outputs:context", "ROS2PubTF.inputs:context"),
                    ],
                },
            )
            print("TF publisher configured")
        except Exception as e:
            carb.log_error(f"Failed to add TF publisher: {e}")

    def run_simulation(self):
        """Run the simulation loop"""

        self.world.reset()

        # Simulation loop
        while simulation_app.is_running():
            self.world.step(render=True)

        simulation_app.close()

# Example usage
if __name__ == "__main__":
    bridge = IsaacROS2Bridge()
    bridge.add_camera_publisher("/Camera", "camera/image_raw")
    bridge.add_tf_publisher()
    bridge.run_simulation()
```

### Loading and Controlling Robots

```python
# scripts/robot_control.py
"""
Robot Loading and Control in Isaac Sim
Demonstrates how to load and control robots
"""

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.articulations import ArticulationView
import numpy as np

class RobotSimulation:
    """Setup and control robot in Isaac Sim"""

    def __init__(self):
        self.world = World(stage_units_in_meters=1.0)
        self.robot = None

    def load_robot_from_usd(self, usd_path: str, robot_path: str = "/World/Robot"):
        """Load robot from USD file"""

        add_reference_to_stage(usd_path=usd_path, prim_path=robot_path)
        self.robot = self.world.scene.add(Robot(prim_path=robot_path, name="robot"))

        print(f"Robot loaded at {robot_path}")
        print(f"Number of DOFs: {self.robot.num_dof}")

    def load_franka_robot(self):
        """Load Franka Emika Panda robot from Isaac assets"""

        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            print("Could not find Isaac Sim assets folder")
            return

        asset_path = assets_root_path + "/Isaac/Robots/Franka/franka_alt_fingers.usd"
        self.load_robot_from_usd(asset_path, "/World/Franka")

    def set_joint_positions(self, positions: list):
        """Set robot joint positions"""

        if self.robot is None:
            print("No robot loaded")
            return

        self.robot.set_joint_positions(positions)
        print(f"Joint positions set to: {positions}")

    def get_joint_positions(self):
        """Get current joint positions"""

        if self.robot is None:
            return None

        return self.robot.get_joint_positions()

    def apply_joint_efforts(self, efforts: list):
        """Apply efforts (torques) to joints"""

        if self.robot is None:
            print("No robot loaded")
            return

        self.robot.set_joint_efforts(efforts)

    def run_position_control(self):
        """Example: Run position control"""

        self.world.reset()

        # Define target positions
        target_positions = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
        step_count = 0

        while simulation_app.is_running():
            self.world.step(render=True)

            if step_count % 100 == 0:
                current_pos = self.get_joint_positions()
                print(f"Current joint positions: {current_pos}")

            # Set target position every 500 steps
            if step_count == 500:
                self.set_joint_positions(target_positions)

            step_count += 1

        simulation_app.close()

# Example usage
if __name__ == "__main__":
    sim = RobotSimulation()
    sim.load_franka_robot()
    sim.run_position_control()
```

## Synthetic Data Generation for Training

### Overview

Isaac Sim can generate large-scale synthetic datasets with perfect ground truth labels for training perception models. This includes:

- RGB images
- Depth maps
- Semantic segmentation
- Instance segmentation
- 2D/3D bounding boxes
- Keypoint annotations

### Domain Randomization

Domain randomization is a technique to improve model generalization by varying scene parameters.

```python
# scripts/synthetic_data_generation.py
"""
Synthetic Data Generation with Domain Randomization
Generate training data with automatic labeling
"""

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

import omni.replicator.core as rep
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
import numpy as np
import random

class SyntheticDataGenerator:
    """Generate synthetic training data with domain randomization"""

    def __init__(self, output_dir: str = "~/isaac_data"):
        self.world = World(stage_units_in_meters=1.0)
        self.output_dir = output_dir

    def setup_scene(self):
        """Setup basic scene with objects"""

        # Add ground plane
        self.world.scene.add_default_ground_plane()

        # Add objects to detect (example: cubes)
        self.objects = []
        for i in range(5):
            cube_path = f"/World/Cube_{i}"
            cube = rep.create.cube(
                semantics=[("class", "cube")],
                position=(random.uniform(-1, 1), random.uniform(-1, 1), 0.5),
                scale=random.uniform(0.1, 0.3)
            )
            self.objects.append(cube)

        print("Scene setup complete")

    def setup_camera(self):
        """Setup camera with replicator"""

        # Create camera
        self.camera = rep.create.camera(
            position=(2, 2, 1.5),
            look_at=(0, 0, 0)
        )

        # Attach to render product
        render_product = rep.create.render_product(
            self.camera,
            resolution=(1024, 1024)
        )

        return render_product

    def configure_domain_randomization(self):
        """Configure domain randomization parameters"""

        with rep.new_layer():
            # Randomize object positions
            def randomize_objects():
                for obj in self.objects:
                    with obj:
                        rep.modify.pose(
                            position=rep.distribution.uniform(
                                (-1, -1, 0.1), (1, 1, 1)
                            ),
                            rotation=rep.distribution.uniform(
                                (0, 0, 0), (360, 360, 360)
                            ),
                        )

            # Randomize lighting
            def randomize_lighting():
                lights = rep.create.light(
                    light_type="Sphere",
                    intensity=rep.distribution.uniform(1000, 5000),
                    position=rep.distribution.uniform(
                        (-5, -5, 3), (5, 5, 8)
                    ),
                    scale=rep.distribution.uniform(0.5, 2),
                    count=3
                )
                return lights.node

            # Randomize textures
            def randomize_textures():
                for obj in self.objects:
                    with obj:
                        rep.randomizer.color(
                            colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
                        )

            # Register randomizers
            rep.randomizer.register(randomize_objects)
            rep.randomizer.register(randomize_lighting)
            rep.randomizer.register(randomize_textures)

    def setup_writers(self, render_product):
        """Configure data writers for annotations"""

        # RGB writer
        rgb_writer = rep.WriterRegistry.get("BasicWriter")
        rgb_writer.initialize(
            output_dir=f"{self.output_dir}/rgb",
            rgb=True
        )
        rgb_writer.attach([render_product])

        # Semantic segmentation writer
        seg_writer = rep.WriterRegistry.get("BasicWriter")
        seg_writer.initialize(
            output_dir=f"{self.output_dir}/semantic_segmentation",
            semantic_segmentation=True,
            colorize_semantic_segmentation=True
        )
        seg_writer.attach([render_product])

        # Bounding box writer
        bbox_writer = rep.WriterRegistry.get("BasicWriter")
        bbox_writer.initialize(
            output_dir=f"{self.output_dir}/bounding_boxes",
            bounding_box_2d_tight=True,
            bounding_box_3d=True
        )
        bbox_writer.attach([render_product])

        # Depth writer
        depth_writer = rep.WriterRegistry.get("BasicWriter")
        depth_writer.initialize(
            output_dir=f"{self.output_dir}/depth",
            distance_to_camera=True
        )
        depth_writer.attach([render_product])

        print(f"Writers configured. Output directory: {self.output_dir}")

    def generate_data(self, num_frames: int = 1000):
        """Generate synthetic dataset"""

        # Setup scene and camera
        self.setup_scene()
        render_product = self.setup_camera()

        # Configure randomization
        self.configure_domain_randomization()

        # Setup writers
        self.setup_writers(render_product)

        # Run data generation
        rep.orchestrator.run_until_complete(num_frames=num_frames)

        print(f"Generated {num_frames} frames of synthetic data")

# Example usage
if __name__ == "__main__":
    generator = SyntheticDataGenerator(output_dir="~/synthetic_dataset")
    generator.generate_data(num_frames=1000)
    simulation_app.close()
```

### Advanced Synthetic Data Pipeline

```python
# scripts/advanced_data_pipeline.py
"""
Advanced Synthetic Data Pipeline
Includes pose estimation keypoints and instance segmentation
"""

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

import omni.replicator.core as rep
from omni.isaac.core import World
import omni.isaac.core.utils.numpy.rotations as rot_utils
import numpy as np

class AdvancedDataPipeline:
    """Generate advanced synthetic data for perception tasks"""

    def __init__(self, output_dir: str = "~/advanced_dataset"):
        self.world = World(stage_units_in_meters=1.0)
        self.output_dir = output_dir

    def create_labeled_objects(self):
        """Create objects with semantic labels and keypoints"""

        # Create cube with keypoints for pose estimation
        cube = rep.create.cube(
            semantics=[("class", "target_object")],
            position=(0, 0, 0.5),
            scale=0.2
        )

        # Add keypoints for 6D pose estimation
        # Corners of the cube
        keypoints = [
            (-0.1, -0.1, 0.4),  # Bottom corners
            (0.1, -0.1, 0.4),
            (0.1, 0.1, 0.4),
            (-0.1, 0.1, 0.4),
            (-0.1, -0.1, 0.6),  # Top corners
            (0.1, -0.1, 0.6),
            (0.1, 0.1, 0.6),
            (-0.1, 0.1, 0.6),
        ]

        return cube, keypoints

    def setup_multi_camera_rig(self):
        """Setup multiple cameras for different viewpoints"""

        cameras = []
        render_products = []

        # Camera positions around the object
        camera_positions = [
            (2, 0, 1),
            (1.5, 1.5, 1),
            (0, 2, 1),
            (-1.5, 1.5, 1),
        ]

        for idx, pos in enumerate(camera_positions):
            camera = rep.create.camera(
                position=pos,
                look_at=(0, 0, 0.5),
                name=f"Camera_{idx}"
            )

            render_product = rep.create.render_product(
                camera,
                resolution=(640, 480)
            )

            cameras.append(camera)
            render_products.append(render_product)

        return cameras, render_products

    def configure_advanced_randomization(self, target_object):
        """Advanced domain randomization"""

        with rep.new_layer():
            # Randomize object pose
            def randomize_pose():
                with target_object:
                    rep.modify.pose(
                        position=rep.distribution.uniform(
                            (-0.5, -0.5, 0.3), (0.5, 0.5, 0.8)
                        ),
                        rotation=rep.distribution.uniform(
                            (0, 0, 0), (360, 360, 360)
                        ),
                    )

            # Randomize lighting conditions
            def randomize_advanced_lighting():
                # Dome light for ambient lighting
                dome_light = rep.create.light(
                    light_type="Dome",
                    intensity=rep.distribution.uniform(500, 2000)
                )

                # Directional lights
                for i in range(2):
                    rep.create.light(
                        light_type="Distant",
                        intensity=rep.distribution.uniform(1000, 3000),
                        rotation=rep.distribution.uniform(
                            (0, 0, 0), (360, 360, 360)
                        )
                    )

                return dome_light.node

            # Randomize materials and textures
            def randomize_materials():
                with target_object:
                    rep.randomizer.materials(
                        materials=rep.distribution.choice([
                            "OmniPBR",
                            "OmniGlass",
                        ])
                    )
                    rep.randomizer.color(
                        colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
                    )

            # Randomize camera parameters
            def randomize_camera_params():
                cameras = rep.get.prims(path_pattern=".*Camera.*")
                with cameras:
                    rep.modify.attribute(
                        "focalLength",
                        rep.distribution.uniform(18, 35)
                    )

            # Register randomizers
            rep.randomizer.register(randomize_pose)
            rep.randomizer.register(randomize_advanced_lighting)
            rep.randomizer.register(randomize_materials)
            rep.randomizer.register(randomize_camera_params)

    def generate_dataset(self, num_frames: int = 1000):
        """Generate complete dataset"""

        # Create scene
        self.world.scene.add_default_ground_plane()
        target_object, keypoints = self.create_labeled_objects()

        # Setup cameras
        cameras, render_products = self.setup_multi_camera_rig()

        # Configure randomization
        self.configure_advanced_randomization(target_object)

        # Setup comprehensive writers
        for idx, rp in enumerate(render_products):
            writer = rep.WriterRegistry.get("BasicWriter")
            writer.initialize(
                output_dir=f"{self.output_dir}/camera_{idx}",
                rgb=True,
                semantic_segmentation=True,
                instance_segmentation=True,
                distance_to_camera=True,
                bounding_box_2d_tight=True,
                bounding_box_2d_loose=True,
                bounding_box_3d=True,
                occlusion=True,
            )
            writer.attach([rp])

        # Run generation
        print(f"Starting data generation for {num_frames} frames...")
        rep.orchestrator.run_until_complete(num_frames=num_frames)
        print(f"Dataset generation complete. Saved to {self.output_dir}")

# Example usage
if __name__ == "__main__":
    pipeline = AdvancedDataPipeline(output_dir="~/advanced_perception_data")
    pipeline.generate_dataset(num_frames=1000)
    simulation_app.close()
```

## Isaac Sim Python API Reference

### Core Concepts

```python
# Key Isaac Sim imports and concepts

# Simulation Application
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})  # GUI mode
# simulation_app = SimulationApp({"headless": True})  # Headless mode

# Core World and Scene Management
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage

# Robot and Articulation Control
from omni.isaac.core.robots import Robot
from omni.isaac.core.articulations import Articulation, ArticulationView

# Utilities
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim, get_prim_at_path

# Replicator for Synthetic Data
import omni.replicator.core as rep

# Action Graphs for ROS 2
import omni.graph.core as og
```

### Common Patterns

```python
# Pattern 1: Basic simulation setup
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
world.reset()

while simulation_app.is_running():
    world.step(render=True)

# Pattern 2: Loading assets
assets_root = get_assets_root_path()
asset_path = assets_root + "/Isaac/Robots/Franka/franka.usd"
add_reference_to_stage(usd_path=asset_path, prim_path="/World/Franka")

# Pattern 3: Robot control
robot = world.scene.add(Robot(prim_path="/World/Robot", name="my_robot"))
robot.set_joint_positions([0.0, 0.0, 0.0])
current_pos = robot.get_joint_positions()
```

## Exercises

### Exercise 1: Basic Scene Setup
Create a scene with a robot, camera, and multiple objects. Configure ROS 2 bridge to publish camera images.

### Exercise 2: Position Control
Implement a position controller that moves a robot through a series of waypoints.

### Exercise 3: Synthetic Data Collection
Generate a dataset of 500 images with semantic segmentation and bounding boxes for training an object detector.

### Exercise 4: Multi-Robot Simulation
Setup a scene with multiple robots and demonstrate coordinated movement.

## Additional Resources

- [Isaac Sim Documentation](https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/overview.html)
- [Isaac Sim Python API](https://docs.omniverse.nvidia.com/py/isaacsim/index.html)
- [Replicator Documentation](https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_replicator.html)
- [ROS 2 Bridge Tutorial](https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/tutorial_ros2_manipulation.html)

## Next Steps

In Week 9, we'll explore AI-powered perception using Isaac ROS packages, including object detection, segmentation, and pose estimation for robotic manipulation tasks.
