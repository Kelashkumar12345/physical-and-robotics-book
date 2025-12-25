---
sidebar_position: 2
title: "Week 7: URDF/SDF & Unity Visualization"
---

# Week 7: URDF/SDF & Unity Visualization

## Introduction to URDF

URDF (Unified Robot Description Format) is an XML specification used in ROS to describe all elements of a robot. It defines the kinematic and dynamic properties, visual representation, and collision geometry of robots.

### Why URDF?

- **Standard Format**: Universal in ROS ecosystem
- **Modular Design**: Reusable components through macros
- **Simulation Ready**: Works with Gazebo, MoveIt, RViz
- **Visualization**: Automatic rendering in RViz and other tools
- **Physics Integration**: Inertial properties for realistic simulation

### URDF vs SDF

| Feature | URDF | SDF |
|---------|------|-----|
| **Ecosystem** | ROS-centric | Gazebo-native |
| **Complexity** | Single robot only | Multi-robot, complex worlds |
| **Sensors** | Limited | Comprehensive |
| **Plugins** | ROS-specific | Gazebo plugins |
| **Macros** | Xacro support | Limited |
| **Versioning** | Static | Version-tracked |

## URDF Fundamentals

### Basic Structure

A URDF file consists of:
1. **Links**: Rigid bodies with visual, collision, and inertial properties
2. **Joints**: Connections between links defining motion constraints
3. **Sensors**: Optional perception elements
4. **Transmissions**: Actuator interfaces (for ros_control)

### Minimal URDF Example

Create `simple_box.urdf`:

```xml
<?xml version="1.0"?>
<robot name="simple_box">

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.166" ixy="0.0" ixz="0.0"
               iyy="0.166" iyz="0.0" izz="0.166"/>
    </inertial>
  </link>

</robot>
```

**Visualize in RViz:**

```bash
# Install tools
sudo apt install ros-humble-joint-state-publisher-gui
sudo apt install ros-humble-urdf-tutorial

# Launch visualization
ros2 launch urdf_tutorial display.launch.py model:=simple_box.urdf
```

## Creating Robot Models with Links and Joints

### Link Anatomy

A link defines a rigid body:

```xml
<link name="link_name">
  <!-- Visual representation (what you see) -->
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.5 0.5 0.5"/>
      <!-- or <cylinder radius="0.1" length="0.5"/> -->
      <!-- or <sphere radius="0.1"/> -->
      <!-- or <mesh filename="package://pkg/meshes/model.dae"/> -->
    </geometry>
    <material name="material_name">
      <color rgba="1 0 0 1"/>
      <!-- or <texture filename="texture.png"/> -->
    </material>
  </visual>

  <!-- Collision geometry (for physics) -->
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.5 0.5 0.5"/>
    </geometry>
  </collision>

  <!-- Inertial properties (mass and inertia tensor) -->
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="5.0"/>
    <inertia ixx="1.0" ixy="0.0" ixz="0.0"
             iyy="1.0" iyz="0.0" izz="1.0"/>
  </inertial>
</link>
```

### Joint Types

URDF supports six joint types:

1. **Fixed**: No motion (rigid connection)
2. **Revolute**: Rotation with limits
3. **Continuous**: Unlimited rotation
4. **Prismatic**: Linear sliding with limits
5. **Floating**: 6-DOF (rarely used)
6. **Planar**: 2D motion in a plane

### Joint Definition

```xml
<joint name="joint_name" type="revolute">
  <!-- Parent and child links -->
  <parent link="parent_link"/>
  <child link="child_link"/>

  <!-- Joint origin relative to parent -->
  <origin xyz="0 0 1" rpy="0 0 0"/>

  <!-- Axis of rotation/translation -->
  <axis xyz="0 0 1"/>

  <!-- Limits (for revolute/prismatic) -->
  <limit lower="-1.57" upper="1.57"
         effort="100.0" velocity="1.0"/>

  <!-- Dynamics (optional) -->
  <dynamics damping="0.1" friction="0.1"/>
</joint>
```

## Complete Example: Simple Robot Arm

Create `robot_arm.urdf`:

```xml
<?xml version="1.0"?>
<robot name="simple_arm">

  <!-- Materials -->
  <material name="blue">
    <color rgba="0 0 0.8 1"/>
  </material>
  <material name="black">
    <color rgba="0 0 0 1"/>
  </material>
  <material name="orange">
    <color rgba="1 0.5 0 1"/>
  </material>
  <material name="grey">
    <color rgba="0.5 0.5 0.5 1"/>
  </material>

  <!-- Base Link (Fixed to World) -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder radius="0.15" length="0.05"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.15" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.0015" ixy="0.0" ixz="0.0"
               iyy="0.0015" iyz="0.0" izz="0.0028"/>
    </inertial>
  </link>

  <!-- Link 1: Lower Arm -->
  <link name="link_1">
    <visual>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.5"/>
      </geometry>
      <material name="orange"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.0428" ixy="0.0" ixz="0.0"
               iyy="0.0428" iyz="0.0" izz="0.0021"/>
    </inertial>
  </link>

  <!-- Joint 1: Base to Link 1 (Revolute) -->
  <joint name="joint_1" type="revolute">
    <parent link="base_link"/>
    <child link="link_1"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14159" upper="3.14159"
           effort="100.0" velocity="1.0"/>
    <dynamics damping="0.7" friction="0.0"/>
  </joint>

  <!-- Link 2: Upper Arm -->
  <link name="link_2">
    <visual>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <box size="0.06 0.06 0.4"/>
      </geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <box size="0.06 0.06 0.4"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <mass value="1.5"/>
      <inertia ixx="0.0208" ixy="0.0" ixz="0.0"
               iyy="0.0208" iyz="0.0" izz="0.00045"/>
    </inertial>
  </link>

  <!-- Joint 2: Link 1 to Link 2 (Revolute) -->
  <joint name="joint_2" type="revolute">
    <parent link="link_1"/>
    <child link="link_2"/>
    <origin xyz="0 0 0.5" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-1.57" upper="1.57"
           effort="100.0" velocity="1.0"/>
    <dynamics damping="0.7" friction="0.0"/>
  </joint>

  <!-- Link 3: Wrist -->
  <link name="link_3">
    <visual>
      <origin xyz="0 0 0.075" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.15"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.075" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.15"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.075" rpy="0 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.00098" ixy="0.0" ixz="0.0"
               iyy="0.00098" iyz="0.0" izz="0.0004"/>
    </inertial>
  </link>

  <!-- Joint 3: Link 2 to Link 3 (Revolute) -->
  <joint name="joint_3" type="revolute">
    <parent link="link_2"/>
    <child link="link_3"/>
    <origin xyz="0 0 0.4" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-1.57" upper="1.57"
           effort="50.0" velocity="1.0"/>
    <dynamics damping="0.5" friction="0.0"/>
  </joint>

  <!-- End Effector (Gripper Base) -->
  <link name="gripper_base">
    <visual>
      <geometry>
        <box size="0.08 0.05 0.03"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.08 0.05 0.03"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.00003" ixy="0.0" ixz="0.0"
               iyy="0.00003" iyz="0.0" izz="0.00002"/>
    </inertial>
  </link>

  <!-- Joint 4: Wrist to Gripper (Fixed) -->
  <joint name="joint_gripper" type="fixed">
    <parent link="link_3"/>
    <child link="gripper_base"/>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
  </joint>

  <!-- Gripper Finger Left -->
  <link name="gripper_finger_left">
    <visual>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <geometry>
        <box size="0.01 0.02 0.08"/>
      </geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <geometry>
        <box size="0.01 0.02 0.08"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <mass value="0.05"/>
      <inertia ixx="0.00003" ixy="0.0" ixz="0.0"
               iyy="0.00003" iyz="0.0" izz="0.000001"/>
    </inertial>
  </link>

  <!-- Gripper Joint Left -->
  <joint name="gripper_joint_left" type="prismatic">
    <parent link="gripper_base"/>
    <child link="gripper_finger_left"/>
    <origin xyz="0 0.025 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0.0" upper="0.03"
           effort="10.0" velocity="0.5"/>
  </joint>

  <!-- Gripper Finger Right -->
  <link name="gripper_finger_right">
    <visual>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <geometry>
        <box size="0.01 0.02 0.08"/>
      </geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <geometry>
        <box size="0.01 0.02 0.08"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <mass value="0.05"/>
      <inertia ixx="0.00003" ixy="0.0" ixz="0.0"
               iyy="0.00003" iyz="0.0" izz="0.000001"/>
    </inertial>
  </link>

  <!-- Gripper Joint Right -->
  <joint name="gripper_joint_right" type="prismatic">
    <parent link="gripper_base"/>
    <child link="gripper_finger_right"/>
    <origin xyz="0 -0.025 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.03" upper="0.0"
           effort="10.0" velocity="0.5"/>
  </joint>

</robot>
```

**Launch visualization:**

```bash
ros2 launch urdf_tutorial display.launch.py model:=robot_arm.urdf
```

## Sensors in URDF

### Camera Sensor

```xml
<link name="camera_link">
  <visual>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
    <material name="red">
      <color rgba="1 0 0 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.00002" ixy="0" ixz="0"
             iyy="0.00002" iyz="0" izz="0.00002"/>
  </inertial>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="gripper_base"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0" rpy="0 0 0"/>
</joint>

<!-- Gazebo plugin for camera -->
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <update_rate>30.0</update_rate>
    <camera name="head">
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.02</near>
        <far>300</far>
      </clip>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.007</stddev>
      </noise>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>/camera</namespace>
      </ros>
      <camera_name>simple_camera</camera_name>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### LiDAR Sensor

```xml
<link name="lidar_link">
  <visual>
    <geometry>
      <cylinder radius="0.05" length="0.04"/>
    </geometry>
    <material name="black">
      <color rgba="0 0 0 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <cylinder radius="0.05" length="0.04"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.2"/>
    <inertia ixx="0.0001" ixy="0" ixz="0"
             iyy="0.0001" iyz="0" izz="0.0001"/>
  </inertial>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
</joint>

<!-- Gazebo plugin for LiDAR -->
<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>
      </noise>
    </ray>
    <plugin name="gazebo_ros_laser_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>/lidar</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### IMU Sensor

```xml
<link name="imu_link">
  <visual>
    <geometry>
      <box size="0.02 0.02 0.01"/>
    </geometry>
    <material name="green">
      <color rgba="0 1 0 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.02 0.02 0.01"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.01"/>
    <inertia ixx="0.000001" ixy="0" ixz="0"
             iyy="0.000001" iyz="0" izz="0.000001"/>
  </inertial>
</link>

<joint name="imu_joint" type="fixed">
  <parent link="base_link"/>
  <child link="imu_link"/>
  <origin xyz="0 0 0.025" rpy="0 0 0"/>
</joint>

<!-- Gazebo plugin for IMU -->
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
          </noise>
        </z>
      </angular_velocity>
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </noise>
        </z>
      </linear_acceleration>
    </imu>
    <plugin name="gazebo_ros_imu_controller" filename="libgazebo_ros_imu_sensor.so">
      <ros>
        <namespace>/imu</namespace>
        <remapping>~/out:=data</remapping>
      </ros>
      <frame_name>imu_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## SDF Format and Migration from URDF

### Why SDF?

SDF (Simulation Description Format) is more flexible than URDF:
- Supports multiple models in one file
- Better plugin system
- More sensor types
- World descriptions

### Converting URDF to SDF

**Method 1: Using gz command**

```bash
# Install conversion tool
sudo apt install gz-tools

# Convert URDF to SDF
gz sdf -p robot_arm.urdf > robot_arm.sdf
```

**Method 2: Programmatic conversion**

```python
#!/usr/bin/env python3
import sys
from ament_index_python.packages import get_package_share_directory
import xacro

def urdf_to_sdf(urdf_path, sdf_path):
    # Process xacro if needed
    doc = xacro.process_file(urdf_path)
    urdf_content = doc.toxml()

    # Use gz tool
    import subprocess
    result = subprocess.run(
        ['gz', 'sdf', '-p'],
        input=urdf_content.encode(),
        capture_output=True
    )

    with open(sdf_path, 'w') as f:
        f.write(result.stdout.decode())

if __name__ == '__main__':
    urdf_to_sdf('robot_arm.urdf', 'robot_arm.sdf')
```

### SDF Structure Example

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="robot_arm">

    <link name="base_link">
      <pose>0 0 0 0 0 0</pose>
      <inertial>
        <mass>1.0</mass>
        <inertia>
          <ixx>0.0015</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.0015</iyy>
          <iyz>0</iyz>
          <izz>0.0028</izz>
        </inertia>
      </inertial>
      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.15</radius>
            <length>0.05</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>0 0 0.8 1</ambient>
          <diffuse>0 0 0.8 1</diffuse>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.15</radius>
            <length>0.05</length>
          </cylinder>
        </geometry>
      </collision>
    </link>

    <link name="link_1">
      <pose relative_to="joint_1">0 0 0 0 0 0</pose>
      <!-- Similar structure as URDF -->
    </link>

    <joint name="joint_1" type="revolute">
      <parent>base_link</parent>
      <child>link_1</child>
      <pose>0 0 0.05 0 0 0</pose>
      <axis>
        <xyz>0 0 1</xyz>
        <limit>
          <lower>-3.14159</lower>
          <upper>3.14159</upper>
          <effort>100</effort>
          <velocity>1.0</velocity>
        </limit>
        <dynamics>
          <damping>0.7</damping>
          <friction>0.0</friction>
        </dynamics>
      </axis>
    </joint>

    <!-- Sensors in SDF format -->
    <link name="camera_link">
      <pose relative_to="gripper_base">0.05 0 0 0 0 0</pose>
      <sensor name="camera" type="camera">
        <update_rate>30</update_rate>
        <camera>
          <horizontal_fov>1.396</horizontal_fov>
          <image>
            <width>640</width>
            <height>480</height>
          </image>
          <clip>
            <near>0.1</near>
            <far>100</far>
          </clip>
        </camera>
      </sensor>
    </link>

  </model>
</sdf>
```

## Unity for High-Fidelity Visualization

Unity provides photorealistic rendering and advanced physics simulation. The Unity Robotics Hub enables ROS 2 integration.

### Setting Up Unity Robotics

**Step 1: Install Unity**

1. Download Unity Hub: https://unity.com/download
2. Install Unity 2021.3 LTS or newer
3. Create a new 3D project

**Step 2: Install Unity Robotics Packages**

In Unity:
1. Open Window > Package Manager
2. Click "+" > Add package from git URL
3. Add these packages:
   - `https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector`
   - `https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer`
   - `https://github.com/Unity-Technologies/Visualizations.git?path=/com.unity.robotics.visualizations`

**Step 3: Import URDF into Unity**

1. In Unity, go to Assets > Import Robot from URDF
2. Select your `.urdf` file
3. Configure import settings:
   - Choose axis orientations (ROS uses Z-up)
   - Set mesh decomposition for complex geometries
   - Configure materials

**Step 4: ROS 2 Connection**

Install ROS-TCP-Endpoint on your ROS 2 system:

```bash
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint
source install/setup.bash
```

Start the endpoint:

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```

In Unity:
1. Go to Robotics > ROS Settings
2. Set ROS IP Address: `127.0.0.1`
3. Set ROS Port: `10000`

### Unity Visualization Example

Create a C# script `RobotController.cs`:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class RobotController : MonoBehaviour
{
    ROSConnection ros;
    public string topicName = "/joint_states";

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<JointStateMsg>(topicName);
        ros.Subscribe<JointStateMsg>(topicName, UpdateJointStates);
    }

    void UpdateJointStates(JointStateMsg jointState)
    {
        // Update Unity joint positions
        for (int i = 0; i < jointState.name.Length; i++)
        {
            string jointName = jointState.name[i];
            float position = (float)jointState.position[i];

            // Find articulation body by name
            ArticulationBody joint = FindArticulationBody(jointName);
            if (joint != null)
            {
                var drive = joint.xDrive;
                drive.target = position * Mathf.Rad2Deg;
                joint.xDrive = drive;
            }
        }
    }

    ArticulationBody FindArticulationBody(string name)
    {
        ArticulationBody[] bodies = GetComponentsInChildren<ArticulationBody>();
        foreach (var body in bodies)
        {
            if (body.name == name)
                return body;
        }
        return null;
    }
}
```

### Advanced Unity Features

**1. Realistic Materials**

```csharp
using UnityEngine;

public class MaterialEnhancer : MonoBehaviour
{
    void Start()
    {
        // Add physically-based materials
        Renderer renderer = GetComponent<Renderer>();
        Material material = renderer.material;

        material.SetFloat("_Metallic", 0.5f);
        material.SetFloat("_Smoothness", 0.7f);
        material.EnableKeyword("_NORMALMAP");
    }
}
```

**2. Camera Simulation**

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class CameraPublisher : MonoBehaviour
{
    public Camera sensorCamera;
    public string topicName = "/camera/image_raw";
    private ROSConnection ros;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<ImageMsg>(topicName);
        InvokeRepeating("PublishImage", 1f, 0.1f);
    }

    void PublishImage()
    {
        RenderTexture rt = sensorCamera.targetTexture;
        Texture2D texture = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
        RenderTexture.active = rt;
        texture.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        texture.Apply();

        ImageMsg msg = new ImageMsg
        {
            height = (uint)texture.height,
            width = (uint)texture.width,
            encoding = "rgb8",
            data = texture.GetRawTextureData()
        };

        ros.Publish(topicName, msg);
    }
}
```

## Practical Exercises

### Exercise 1: Design a Mobile Robot

Create a URDF for a differential drive robot with:
- Chassis (base_link)
- Two drive wheels (continuous joints)
- Two caster wheels (fixed joints)
- LiDAR sensor
- Camera

### Exercise 2: Inertial Calculations

Write a Python script to calculate inertia tensors for:
- Solid box
- Solid cylinder
- Solid sphere
- Hollow cylinder

### Exercise 3: URDF to SDF Migration

Convert your robot from Exercise 1:
1. Export to SDF format
2. Add Gazebo-specific sensors
3. Test in Gazebo simulation
4. Compare with URDF performance

### Exercise 4: Unity Integration

1. Import your robot URDF into Unity
2. Create a photorealistic environment
3. Set up ROS 2 communication
4. Publish joint states from Gazebo to Unity
5. Record high-quality video

## Best Practices

### URDF Design

1. **Modularity**: Use Xacro macros for repeated elements
2. **Naming**: Consistent naming conventions (e.g., `<part>_link`, `<part>_joint`)
3. **Units**: Stick to SI units (meters, kilograms, seconds)
4. **Inertias**: Calculate accurate inertial properties
5. **Collision**: Keep collision geometry simple for performance
6. **Visual**: Use detailed meshes for visual representation

### Collision vs Visual Geometry

```xml
<!-- Visual: detailed mesh -->
<visual>
  <geometry>
    <mesh filename="package://my_robot/meshes/arm_link.dae" scale="1 1 1"/>
  </geometry>
</visual>

<!-- Collision: simplified geometry -->
<collision>
  <geometry>
    <cylinder radius="0.05" length="0.5"/>
  </geometry>
</collision>
```

### Inertia Calculation Helper

```python
def box_inertia(mass, x, y, z):
    """Calculate inertia tensor for solid box"""
    ixx = (mass / 12.0) * (y**2 + z**2)
    iyy = (mass / 12.0) * (x**2 + z**2)
    izz = (mass / 12.0) * (x**2 + y**2)
    return ixx, iyy, izz

def cylinder_inertia(mass, radius, length):
    """Calculate inertia tensor for solid cylinder (axis along z)"""
    ixx = iyy = (mass / 12.0) * (3 * radius**2 + length**2)
    izz = (mass / 2.0) * radius**2
    return ixx, iyy, izz

def sphere_inertia(mass, radius):
    """Calculate inertia tensor for solid sphere"""
    i = (2.0 / 5.0) * mass * radius**2
    return i, i, i
```

## Common Issues and Solutions

### Issue: Robot falls through floor
**Solution**: Check collision geometries and mass properties

### Issue: Joints don't move in RViz
**Solution**: Publish joint states using `joint_state_publisher`

### Issue: Unity import fails
**Solution**: Verify URDF is valid using `check_urdf`

```bash
check_urdf robot_arm.urdf
```

### Issue: Incorrect inertial properties cause instability
**Solution**: Use calculated inertias or MeshLab for complex geometries

## Resources

- [URDF Tutorials](http://wiki.ros.org/urdf/Tutorials)
- [SDF Format Specification](http://sdformat.org/)
- [Unity Robotics Hub](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
- [Xacro Documentation](http://wiki.ros.org/xacro)
- [MoveIt URDF Setup](https://moveit.picknik.ai/main/doc/examples/setup_assistant/setup_assistant_tutorial.html)

## Next Steps

In Module 3, you will:
- Implement advanced control algorithms
- Use MoveIt for motion planning
- Integrate perception pipelines
- Deploy robots in real-world scenarios
