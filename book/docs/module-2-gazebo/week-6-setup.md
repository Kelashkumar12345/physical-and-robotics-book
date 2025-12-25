---
sidebar_position: 1
title: "Week 6: Gazebo Simulation Setup"
---

# Week 6: Gazebo Simulation Setup

## Introduction to Gazebo Simulation

Gazebo is a powerful, open-source 3D robotics simulator that enables you to test algorithms, design robots, and perform regression testing using realistic scenarios. Gazebo offers the ability to accurately and efficiently simulate populations of robots in complex indoor and outdoor environments.

### Why Gazebo?

- **Physics-Based Simulation**: Realistic physics engines (ODE, Bullet, Simbody, DART)
- **High-Quality Graphics**: OpenGL rendering with dynamic lighting and shadows
- **Sensor Simulation**: Camera, laser rangefinder, IMU, contact sensors, and more
- **ROS 2 Integration**: Native support for ROS 2 communication
- **Plugin Architecture**: Extensible through C++ plugins
- **Headless Mode**: Run simulations without GUI for CI/CD pipelines

### Gazebo Versions

- **Gazebo Classic** (versions 1-11): Legacy version, paired with ROS 1
- **Ignition Gazebo** (now called **Gazebo**): Modern architecture, better performance
  - Fortress: Recommended for ROS 2 Humble
  - Garden: Latest LTS release
  - Harmonic: Newest version with advanced features

## Installing Gazebo with ROS 2

### Prerequisites

Ensure you have ROS 2 installed. This guide assumes ROS 2 Humble on Ubuntu 22.04.

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install ROS 2 Humble (if not already installed)
# Follow: https://docs.ros.org/en/humble/Installation.html
```

### Installing Gazebo Fortress

Gazebo Fortress is the recommended version for ROS 2 Humble:

```bash
# Add Gazebo repository
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget https://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -

# Update and install Gazebo Fortress
sudo apt update
sudo apt install ignition-fortress -y

# Install ROS 2 - Gazebo bridge
sudo apt install ros-humble-ros-gz -y
```

### Verifying Installation

```bash
# Test Gazebo launch
ign gazebo

# Check version
ign gazebo --version

# List available worlds
ign gazebo --help
```

### Environment Setup

Add to your `~/.bashrc`:

```bash
# Source ROS 2
source /opt/ros/humble/setup.bash

# Source Gazebo (if needed)
export IGN_GAZEBO_RESOURCE_PATH=/usr/share/ignition/ignition-gazebo6/worlds
```

## Creating Your First Simulation World

### Understanding SDF Format

SDF (Simulation Description Format) is an XML format that describes objects and environments for robot simulators, visualization, and control.

### Basic World Structure

Create a directory for your simulation:

```bash
mkdir -p ~/ros2_ws/src/my_gazebo_tutorials/worlds
cd ~/ros2_ws/src/my_gazebo_tutorials/worlds
```

### Example 1: Empty World

Create `empty_world.sdf`:

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="empty_world">

    <!-- Physics Engine Configuration -->
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Plugin for physics -->
    <plugin
      filename="ignition-gazebo-physics-system"
      name="ignition::gazebo::systems::Physics">
    </plugin>

    <!-- Plugin for user commands -->
    <plugin
      filename="ignition-gazebo-user-commands-system"
      name="ignition::gazebo::systems::UserCommands">
    </plugin>

    <!-- Plugin for scene broadcast -->
    <plugin
      filename="ignition-gazebo-scene-broadcaster-system"
      name="ignition::gazebo::systems::SceneBroadcaster">
    </plugin>

    <!-- Lighting -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground Plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.8 0.8 0.8 1</specular>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

**Launch the world:**

```bash
ign gazebo empty_world.sdf
```

### Example 2: World with Simple Objects

Create `simple_world.sdf`:

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="simple_world">

    <!-- Physics and Plugins (same as above) -->
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <plugin filename="ignition-gazebo-physics-system"
            name="ignition::gazebo::systems::Physics">
    </plugin>
    <plugin filename="ignition-gazebo-user-commands-system"
            name="ignition::gazebo::systems::UserCommands">
    </plugin>
    <plugin filename="ignition-gazebo-scene-broadcaster-system"
            name="ignition::gazebo::systems::SceneBroadcaster">
    </plugin>

    <!-- Sun -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.5 0.5 0.5 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Box Obstacle -->
    <model name="box">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="box_link">
        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.166667</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>0.166667</iyy>
            <iyz>0.0</iyz>
            <izz>0.166667</izz>
          </inertia>
        </inertial>
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
            <specular>1 0 0 1</specular>
          </material>
        </visual>
      </link>
    </model>

    <!-- Cylinder Object -->
    <model name="cylinder">
      <pose>-2 2 0.5 0 0 0</pose>
      <link name="cylinder_link">
        <inertial>
          <mass>2.0</mass>
          <inertia>
            <ixx>0.145833</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>0.145833</iyy>
            <iyz>0.0</iyz>
            <izz>0.125</izz>
          </inertia>
        </inertial>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.5</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.5</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0 0 1 1</ambient>
            <diffuse>0 0 1 1</diffuse>
            <specular>0 0 1 1</specular>
          </material>
        </visual>
      </link>
    </model>

    <!-- Sphere Object -->
    <model name="sphere">
      <pose>0 -3 0.5 0 0 0</pose>
      <link name="sphere_link">
        <inertial>
          <mass>0.5</mass>
          <inertia>
            <ixx>0.05</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>0.05</iyy>
            <iyz>0.0</iyz>
            <izz>0.05</izz>
          </inertia>
        </inertial>
        <collision name="collision">
          <geometry>
            <sphere>
              <radius>0.5</radius>
            </sphere>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <sphere>
              <radius>0.5</radius>
            </sphere>
          </geometry>
          <material>
            <ambient>0 1 0 1</ambient>
            <diffuse>0 1 0 1</diffuse>
            <specular>0 1 0 1</specular>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

## Physics Engines and Simulation Parameters

### Available Physics Engines

Gazebo supports multiple physics engines:

1. **ODE (Open Dynamics Engine)**: Default, good balance of speed and accuracy
2. **Bullet**: Fast, suitable for many objects
3. **DART**: Advanced features, better for manipulation
4. **Simbody**: High accuracy, slower performance

### Configuring Physics Parameters

```xml
<physics name="fast" type="ode">
  <!-- Time step in seconds -->
  <max_step_size>0.001</max_step_size>

  <!-- Real-time factor (1.0 = real-time, >1.0 = faster) -->
  <real_time_factor>1.0</real_time_factor>

  <!-- Solver parameters -->
  <ode>
    <solver>
      <type>quick</type>
      <iters>50</iters>
      <sor>1.0</sor>
    </solver>
    <constraints>
      <cfm>0.0</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Gravity Configuration

```xml
<world name="custom_gravity">
  <!-- Standard Earth gravity -->
  <gravity>0 0 -9.81</gravity>

  <!-- Or custom gravity (e.g., Moon) -->
  <!-- <gravity>0 0 -1.62</gravity> -->

  <!-- Magnetic field -->
  <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
</world>
```

## Spawning Robots and Objects

### Method 1: Include in SDF World File

```xml
<world name="robot_world">
  <!-- Include a pre-built model from Gazebo resources -->
  <include>
    <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Ground Plane</uri>
  </include>

  <include>
    <name>my_robot</name>
    <pose>0 0 0.5 0 0 0</pose>
    <uri>model://my_custom_robot</uri>
  </include>
</world>
```

### Method 2: Spawn via ROS 2 Node

Create `spawn_robot.launch.py`:

```python
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import os

def generate_launch_description():

    # Path to SDF model
    sdf_file = os.path.join(
        os.getcwd(),
        'models',
        'my_robot',
        'model.sdf'
    )

    # Spawn entity
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_robot',
            '-file', sdf_file,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0'
        ],
        output='screen'
    )

    return LaunchDescription([
        spawn_entity
    ])
```

### Method 3: Programmatic Spawning via Service

```bash
# Using Gazebo service
ign service -s /world/simple_world/create \
  --reqtype ignition.msgs.EntityFactory \
  --reptype ignition.msgs.Boolean \
  --timeout 1000 \
  --req 'sdf_filename: "/path/to/model.sdf", name: "my_model"'
```

## Advanced World Example: Indoor Environment

Create `indoor_world.sdf`:

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="indoor_environment">

    <physics name="1ms" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <plugin filename="ignition-gazebo-physics-system"
            name="ignition::gazebo::systems::Physics">
    </plugin>
    <plugin filename="ignition-gazebo-user-commands-system"
            name="ignition::gazebo::systems::UserCommands">
    </plugin>
    <plugin filename="ignition-gazebo-scene-broadcaster-system"
            name="ignition::gazebo::systems::SceneBroadcaster">
    </plugin>

    <!-- Ambient lighting -->
    <light type="directional" name="ceiling_light">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 5 0 0 0</pose>
      <diffuse>0.9 0.9 0.9 1</diffuse>
      <specular>0.3 0.3 0.3 1</specular>
      <direction>0 0 -1</direction>
    </light>

    <!-- Floor -->
    <model name="floor">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>20 20</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.8</mu>
                <mu2>0.8</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>20 20</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Walls -->
    <model name="wall_north">
      <static>true</static>
      <pose>0 10 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="wall_south">
      <static>true</static>
      <pose>0 -10 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="wall_east">
      <static>true</static>
      <pose>10 0 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="wall_west">
      <static>true</static>
      <pose>-10 0 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Obstacle course -->
    <model name="obstacle_1">
      <pose>3 0 0.25 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 2 0.5</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 2 0.5</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.3 0.3 1</ambient>
            <diffuse>0.8 0.3 0.3 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

## Practical Exercises

### Exercise 1: Create a Maze World

Design an SDF world with:
- Multiple walls forming a maze
- Different surface friction zones
- Colored markers for navigation
- Dynamic lighting

### Exercise 2: Physics Experimentation

Create worlds with:
- Different gravity settings
- Various friction coefficients
- Collision testing scenarios
- Stress testing with many objects

### Exercise 3: Launch File Integration

Create a ROS 2 launch file that:
1. Starts Gazebo with your custom world
2. Spawns a robot at a specific pose
3. Launches RViz for visualization
4. Bridges Gazebo and ROS 2 topics

## Best Practices

1. **Organization**: Keep worlds, models, and launch files in separate directories
2. **Modularity**: Use `<include>` for reusable models
3. **Performance**: Use static models for non-moving objects
4. **Naming**: Use descriptive names for models and links
5. **Documentation**: Comment your SDF files
6. **Version Control**: Track SDF files in git
7. **Testing**: Test worlds in headless mode for CI/CD

## Common Issues and Solutions

### Issue: Gazebo crashes on launch
**Solution**: Check GPU drivers and reduce physics complexity

### Issue: Models fall through ground
**Solution**: Ensure proper collision geometry and check gravity settings

### Issue: Slow simulation
**Solution**: Reduce `max_step_size`, disable shadows, use simpler geometry

### Issue: Objects don't collide
**Solution**: Verify collision geometries and contact parameters

## Resources

- [Gazebo Official Documentation](https://gazebosim.org/docs)
- [SDF Format Specification](http://sdformat.org/)
- [Gazebo Fuel Model Library](https://app.gazebosim.org/fuel/models)
- [ROS 2 Gazebo Integration](https://github.com/gazebosim/ros_gz)

## Next Steps

In Week 7, you will learn to:
- Create robot descriptions using URDF
- Convert between URDF and SDF formats
- Add sensors to robot models
- Visualize robots in Unity for high-fidelity rendering
