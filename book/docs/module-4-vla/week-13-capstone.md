---
sidebar_position: 3
title: "Week 13: Capstone Project"
description: "Build a complete voice-controlled humanoid robot integrating all course concepts"
---

# Week 13: Capstone Project - Voice-Controlled Humanoid

This capstone integrates everything you've learned: ROS 2, simulation, perception, navigation, and voice-to-action pipelines into a complete humanoid robot system.

## Learning Objectives

By the end of this week, you will:
- Design a complete humanoid robot control system
- Implement voice-to-action using Whisper + LLM
- Deploy from simulation to edge hardware
- Present a working demonstration

## Project Overview

### The Challenge

Build a humanoid robot that:
1. Accepts voice commands via microphone
2. Interprets intent using LLM
3. Plans and executes actions in simulation
4. Demonstrates sim-to-real transfer concepts

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Whisper   │────►│   LLM       │────►│  ROS 2      │
│   (STT)     │     │  (Intent)   │     │  Actions    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┤
                    │                          │
                    ▼                          ▼
             ┌─────────────┐           ┌─────────────┐
             │  Isaac Sim  │           │   Gazebo    │
             │  (Train)    │           │   (Test)    │
             └─────────────┘           └─────────────┘
```

## Part 1: Voice Input Pipeline

### Setting Up Whisper

```python
import whisper
import sounddevice as sd
import numpy as np

class VoiceCapture:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)
        self.sample_rate = 16000

    def record_audio(self, duration: float = 5.0) -> np.ndarray:
        """Record audio from microphone."""
        print("Listening...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()
        return audio.flatten()

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio to text."""
        result = self.model.transcribe(audio)
        return result["text"].strip()
```

### ROS 2 Voice Node

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command_node')
        self.publisher = self.create_publisher(String, 'voice_commands', 10)
        self.voice_capture = VoiceCapture()
        self.timer = self.create_timer(0.1, self.listen_callback)
        self.is_listening = False

    def listen_callback(self):
        if not self.is_listening:
            self.is_listening = True
            audio = self.voice_capture.record_audio(duration=3.0)
            text = self.voice_capture.transcribe(audio)

            if text:
                msg = String()
                msg.data = text
                self.publisher.publish(msg)
                self.get_logger().info(f'Command: {text}')

            self.is_listening = False
```

## Part 2: LLM Intent Parsing

### Intent Classification with OpenAI

```python
from openai import OpenAI

class IntentParser:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """You are a robot command parser.
        Given a voice command, extract:
        - action: walk, wave, pick_up, look_at, stop
        - target: object or direction if applicable
        - parameters: speed, distance, etc.

        Respond in JSON format only."""

    def parse(self, command: str) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": command}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
```

### Example Parsing

```python
parser = IntentParser()

# Input: "Walk forward three steps"
result = parser.parse("Walk forward three steps")
# Output: {"action": "walk", "target": "forward", "parameters": {"steps": 3}}

# Input: "Wave hello to the person on the left"
result = parser.parse("Wave hello to the person on the left")
# Output: {"action": "wave", "target": "left", "parameters": {"gesture": "hello"}}
```

## Part 3: Action Execution

### ROS 2 Action Client

```python
from rclpy.action import ActionClient
from humanoid_interfaces.action import ExecuteMotion

class MotionExecutor(Node):
    def __init__(self):
        super().__init__('motion_executor')
        self._action_client = ActionClient(
            self,
            ExecuteMotion,
            'execute_motion'
        )
        self.subscription = self.create_subscription(
            String,
            'parsed_intents',
            self.intent_callback,
            10
        )

    def intent_callback(self, msg):
        intent = json.loads(msg.data)
        self.execute_motion(intent)

    def execute_motion(self, intent: dict):
        goal = ExecuteMotion.Goal()
        goal.action = intent['action']
        goal.target = intent.get('target', '')
        goal.parameters = json.dumps(intent.get('parameters', {}))

        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if goal_handle.accepted:
            self.get_logger().info('Motion accepted')
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Motion complete: {result.success}')
```

## Part 4: Simulation Integration

### Isaac Sim Setup

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.robots import Robot

class HumanoidSimulation:
    def __init__(self, usd_path: str):
        self.world = World()
        self.robot = self.world.scene.add(
            Robot(
                prim_path="/World/Humanoid",
                usd_path=usd_path,
                name="humanoid"
            )
        )
        self.world.reset()

    def step(self, joint_positions: list):
        """Execute one simulation step with joint targets."""
        self.robot.set_joint_positions(joint_positions)
        self.world.step(render=True)

    def execute_walk(self, steps: int, speed: float = 1.0):
        """Execute walking motion."""
        for step in range(steps):
            # Load walking trajectory
            trajectory = self.load_walk_trajectory(speed)
            for joint_pos in trajectory:
                self.step(joint_pos)
```

### Gazebo Bridge

```python
from ros_gz_bridge.bridge import Bridge

class GazeboBridge:
    def __init__(self):
        self.bridge = Bridge()
        self.bridge.add_topic(
            ros_topic='/joint_states',
            gz_topic='/model/humanoid/joint_state',
            direction='gz_to_ros'
        )
        self.bridge.add_topic(
            ros_topic='/joint_commands',
            gz_topic='/model/humanoid/joint_cmd',
            direction='ros_to_gz'
        )
```

## Part 5: Complete Pipeline

### Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='humanoid_voice',
            executable='voice_command_node',
            name='voice_input'
        ),
        Node(
            package='humanoid_brain',
            executable='intent_parser_node',
            name='intent_parser'
        ),
        Node(
            package='humanoid_motion',
            executable='motion_executor_node',
            name='motion_executor'
        ),
        Node(
            package='humanoid_sim',
            executable='simulation_bridge_node',
            name='sim_bridge'
        ),
    ])
```

### Running the Demo

```bash
# Terminal 1: Launch simulation
ros2 launch humanoid_sim simulation.launch.py

# Terminal 2: Launch voice pipeline
ros2 launch humanoid_voice voice_pipeline.launch.py

# Terminal 3: Monitor topics
ros2 topic echo /voice_commands
ros2 topic echo /parsed_intents
ros2 topic echo /motion_status
```

## Capstone Requirements

### Minimum Viable Demo

| Requirement | Description |
|-------------|-------------|
| Voice input | Capture and transcribe 3+ commands |
| Intent parsing | Correctly interpret walk, wave, stop |
| Simulation | Execute motions in Gazebo or Isaac |
| Feedback | Visual confirmation of command execution |

### Stretch Goals

- Multi-step command sequences ("Walk to the door and wave")
- Object detection integration (pick up red ball)
- Emotion/gesture recognition
- Edge deployment on Jetson

## Evaluation Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| Functionality | 40% | Does it work end-to-end? |
| Code Quality | 20% | Clean, documented, follows ROS 2 conventions |
| Integration | 20% | Proper use of course concepts |
| Presentation | 20% | Clear demo, explains design decisions |

## Resources

### Code Templates

- [Starter Repository](https://github.com/physical-ai-book/capstone-starter)
- [Humanoid URDF Models](https://github.com/physical-ai-book/humanoid-models)
- [Motion Trajectories](https://github.com/physical-ai-book/motion-library)

### Documentation

- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [ROS 2 Actions Tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/Writing-an-Action-Server-Client.html)
- [Isaac Sim Python API](https://docs.omniverse.nvidia.com/isaacsim/latest/core_api.html)

## Summary

Congratulations on completing the Physical AI & Humanoid Robotics course! You've learned:

1. **ROS 2 Fundamentals** - Nodes, topics, services, actions
2. **Simulation** - Gazebo, Unity, Isaac Sim
3. **Perception** - VSLAM, depth cameras, LiDAR
4. **Navigation** - Nav2, path planning
5. **Humanoid Control** - Kinematics, locomotion
6. **Voice-to-Action** - Whisper, LLMs, intent parsing

The capstone brings it all together into a working system. Good luck!

## Next Steps

After completing this course:
- Explore [ROS 2 Iron](https://docs.ros.org/en/iron/) for latest features
- Join the [Physical AI Community](https://discord.gg/physical-ai)
- Contribute to open-source humanoid projects
- Consider [NVIDIA Jetson Developer Certification](https://developer.nvidia.com/embedded/learn/jetson-ai-certification-programs)
