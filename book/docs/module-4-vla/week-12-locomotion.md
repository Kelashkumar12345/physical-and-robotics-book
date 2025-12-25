---
sidebar_position: 2
title: "Week 12: Bipedal Locomotion"
---

# Week 12: Bipedal Locomotion

## Introduction to Bipedal Walking

Bipedal locomotion is one of the most challenging problems in robotics, requiring precise coordination of multiple joints while maintaining dynamic balance. Unlike wheeled robots, bipedal systems must constantly manage their stability during alternating single and double support phases.

### Why Bipedal Locomotion?

- **Versatility**: Navigate stairs, uneven terrain, and human environments
- **Efficiency**: Lower energy consumption than statically stable gaits when optimized
- **Natural interaction**: Move in ways humans understand and predict
- **Research value**: Insights into human biomechanics and neural control

### Key Challenges

1. **Dynamic stability**: Center of mass must be controlled during flight phases
2. **Underactuation**: Cannot directly control all degrees of freedom
3. **Impact forces**: Foot-ground contact creates discontinuous dynamics
4. **Energy efficiency**: Minimizing power consumption during continuous operation

## Gait Fundamentals

### Gait Cycle Components

```python
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

class GaitPhase(Enum):
    """Phases of bipedal walking gait"""
    DOUBLE_SUPPORT_L = 1  # Both feet on ground, preparing to lift left
    SINGLE_SUPPORT_R = 2  # Right foot only (left swinging)
    DOUBLE_SUPPORT_R = 3  # Both feet on ground, preparing to lift right
    SINGLE_SUPPORT_L = 4  # Left foot only (right swinging)

class GaitCycle:
    """Represents one complete gait cycle"""

    def __init__(self, stride_length=0.4, step_height=0.05, cycle_time=1.2):
        self.stride_length = stride_length  # Total distance per cycle (m)
        self.step_height = step_height      # Maximum foot lift (m)
        self.cycle_time = cycle_time        # Time for one complete cycle (s)

        # Phase durations (as fraction of cycle_time)
        self.phase_durations = {
            GaitPhase.DOUBLE_SUPPORT_L: 0.1,
            GaitPhase.SINGLE_SUPPORT_R: 0.4,
            GaitPhase.DOUBLE_SUPPORT_R: 0.1,
            GaitPhase.SINGLE_SUPPORT_L: 0.4
        }

    def get_phase(self, t):
        """
        Determine gait phase at time t

        Args:
            t: Time in current cycle [0, cycle_time]

        Returns:
            Current GaitPhase
        """
        # Normalize time to [0, 1]
        t_normalized = (t % self.cycle_time) / self.cycle_time

        cumulative = 0
        for phase, duration in self.phase_durations.items():
            cumulative += duration
            if t_normalized < cumulative:
                return phase

        return GaitPhase.SINGLE_SUPPORT_L

    def get_phase_progress(self, t):
        """Get progress within current phase [0, 1]"""
        phase = self.get_phase(t)
        t_normalized = (t % self.cycle_time) / self.cycle_time

        # Find phase start time
        phase_start = 0
        for p, duration in self.phase_durations.items():
            if p == phase:
                break
            phase_start += duration

        phase_duration = self.phase_durations[phase]
        progress = (t_normalized - phase_start) / phase_duration

        return np.clip(progress, 0, 1)

# Example usage
gait = GaitCycle(stride_length=0.4, cycle_time=1.2)

times = np.linspace(0, 2.4, 100)  # Two complete cycles
phases = [gait.get_phase(t) for t in times]

print("Gait cycle analysis:")
print(f"  Stride length: {gait.stride_length}m")
print(f"  Cycle time: {gait.cycle_time}s")
print(f"  Walking speed: {gait.stride_length/gait.cycle_time:.2f}m/s")
```

### Foot Trajectory Generation

```python
class FootTrajectory:
    """Generate smooth foot trajectories during swing phase"""

    @staticmethod
    def bezier_curve(t, control_points):
        """
        Evaluate cubic Bezier curve

        Args:
            t: Parameter [0, 1]
            control_points: List of 4 control points

        Returns:
            Point on curve
        """
        p0, p1, p2, p3 = control_points
        return (1-t)**3 * p0 + 3*(1-t)**2*t * p1 + 3*(1-t)*t**2 * p2 + t**3 * p3

    @staticmethod
    def swing_trajectory(t, start_pos, end_pos, step_height):
        """
        Generate swing phase foot trajectory

        Args:
            t: Normalized time [0, 1] within swing phase
            start_pos: Starting foot position [x, y, z]
            end_pos: Ending foot position [x, y, z]
            step_height: Maximum height during swing

        Returns:
            Current foot position [x, y, z]
        """
        start = np.array(start_pos)
        end = np.array(end_pos)

        # Control points for Bezier curve
        # P0: start position
        # P1: 1/3 along path, slight lift
        # P2: 2/3 along path, max height
        # P3: end position

        p0 = start
        p1 = start + (end - start) * 0.3 + np.array([0, 0, step_height * 0.5])
        p2 = start + (end - start) * 0.7 + np.array([0, 0, step_height])
        p3 = end

        position = FootTrajectory.bezier_curve(t, [p0, p1, p2, p3])

        return position

    @staticmethod
    def stance_trajectory(t, stance_pos):
        """
        Stance phase: foot remains stationary on ground

        Args:
            t: Normalized time [0, 1] within stance phase
            stance_pos: Fixed foot position

        Returns:
            Foot position (unchanged)
        """
        return np.array(stance_pos)

# Example: Generate complete step trajectory
start_foot_pos = [0.0, 0.1, 0.0]  # Left foot
end_foot_pos = [0.4, 0.1, 0.0]    # After one step
step_height = 0.05

# Swing phase trajectory
swing_times = np.linspace(0, 1, 50)
swing_positions = [FootTrajectory.swing_trajectory(t, start_foot_pos, end_foot_pos, step_height)
                  for t in swing_times]

# Visualize
swing_positions = np.array(swing_positions)
print(f"\nSwing trajectory:")
print(f"  Start: {start_foot_pos}")
print(f"  End: {end_foot_pos}")
print(f"  Max height: {swing_positions[:, 2].max():.3f}m")
print(f"  Forward distance: {swing_positions[-1, 0] - swing_positions[0, 0]:.3f}m")
```

## Zero-Moment Point (ZMP) and Stability

The Zero-Moment Point (ZMP) is a crucial concept for bipedal stability. The robot is stable if the ZMP remains within the support polygon (the convex hull of all ground contact points).

### ZMP Theory

```python
class ZMPCalculator:
    """Calculate and analyze Zero-Moment Point for stability"""

    def __init__(self, robot_mass=50.0, gravity=9.81):
        self.mass = robot_mass  # Total robot mass (kg)
        self.g = gravity        # Gravitational acceleration (m/s^2)

    def compute_zmp(self, com_position, com_acceleration, com_height):
        """
        Compute ZMP location based on center of mass dynamics

        Simplified ZMP formula (assuming flat ground):
        ZMP_x = COM_x - (COM_z / g) * COM_acc_x
        ZMP_y = COM_y - (COM_z / g) * COM_acc_y

        Args:
            com_position: Center of mass position [x, y, z]
            com_acceleration: COM acceleration [ax, ay, az]
            com_height: Height of COM above ground

        Returns:
            ZMP position [zmp_x, zmp_y]
        """
        com_x, com_y, com_z = com_position
        acc_x, acc_y, acc_z = com_acceleration

        # ZMP calculation
        zmp_x = com_x - (com_z / (self.g + acc_z)) * acc_x
        zmp_y = com_y - (com_z / (self.g + acc_z)) * acc_y

        return np.array([zmp_x, zmp_y])

    def check_stability(self, zmp, support_polygon):
        """
        Check if ZMP is within support polygon

        Args:
            zmp: ZMP position [x, y]
            support_polygon: List of foot corner points [[x1,y1], [x2,y2], ...]

        Returns:
            True if stable, False otherwise
        """
        # Use cross product to check if point is inside convex polygon
        polygon = np.array(support_polygon)
        n = len(polygon)

        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]

            # Edge vector
            edge = p2 - p1
            # Vector to ZMP
            to_zmp = zmp - p1

            # Cross product (2D)
            cross = edge[0] * to_zmp[1] - edge[1] * to_zmp[0]

            # If ZMP is on the wrong side of any edge, it's outside
            if cross < 0:
                return False

        return True

    def compute_stability_margin(self, zmp, support_polygon):
        """
        Compute minimum distance from ZMP to polygon edges

        Args:
            zmp: ZMP position [x, y]
            support_polygon: List of foot corner points

        Returns:
            Minimum distance to boundary (positive = stable)
        """
        polygon = np.array(support_polygon)
        n = len(polygon)
        min_distance = float('inf')

        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]

            # Distance from point to line segment
            edge = p2 - p1
            edge_length = np.linalg.norm(edge)

            if edge_length == 0:
                continue

            # Project ZMP onto edge
            t = np.dot(zmp - p1, edge) / (edge_length ** 2)
            t = np.clip(t, 0, 1)  # Clamp to segment

            closest_point = p1 + t * edge
            distance = np.linalg.norm(zmp - closest_point)

            min_distance = min(min_distance, distance)

        return min_distance

# Example: ZMP analysis during walking
zmp_calc = ZMPCalculator(robot_mass=60.0)

# Single support phase (right foot only)
right_foot_corners = [
    [-0.1, -0.05],  # Heel left
    [-0.1,  0.05],  # Heel right
    [ 0.1,  0.05],  # Toe right
    [ 0.1, -0.05]   # Toe left
]

# Simulate COM motion
com_pos = [0.05, 0.0, 0.8]  # Slightly forward, centered, 80cm high
com_acc = [0.2, 0.0, 0.0]   # Accelerating forward

zmp = zmp_calc.compute_zmp(com_pos, com_acc, com_pos[2])
is_stable = zmp_calc.check_stability(zmp, right_foot_corners)
margin = zmp_calc.compute_stability_margin(zmp, right_foot_corners)

print(f"\nZMP Analysis:")
print(f"  COM position: {com_pos}")
print(f"  COM acceleration: {com_acc}")
print(f"  ZMP location: [{zmp[0]:.3f}, {zmp[1]:.3f}]")
print(f"  Stable: {is_stable}")
print(f"  Stability margin: {margin:.3f}m")
```

### ZMP-Based Gait Generation

```python
class ZMPGaitGenerator:
    """Generate walking patterns that maintain ZMP stability"""

    def __init__(self, robot_mass, com_height):
        self.mass = robot_mass
        self.com_height = com_height
        self.zmp_calc = ZMPCalculator(robot_mass)

    def generate_com_trajectory(self, zmp_reference, duration, dt=0.01):
        """
        Generate COM trajectory from desired ZMP trajectory

        Uses simplified Linear Inverted Pendulum Model (LIPM):
        COM_acc = (g/z) * (COM - ZMP)

        Args:
            zmp_reference: Desired ZMP trajectory [(x, y), ...]
            duration: Total trajectory duration
            dt: Time step

        Returns:
            COM positions and velocities over time
        """
        n_steps = int(duration / dt)
        times = np.linspace(0, duration, n_steps)

        # Initial state
        com_pos = np.array([0.0, 0.0])
        com_vel = np.array([0.0, 0.0])

        com_trajectory = [com_pos.copy()]
        vel_trajectory = [com_vel.copy()]

        omega = np.sqrt(self.zmp_calc.g / self.com_height)  # Natural frequency

        for i in range(1, n_steps):
            # Get ZMP reference for this timestep
            zmp_idx = min(i, len(zmp_reference) - 1)
            zmp_ref = np.array(zmp_reference[zmp_idx])

            # LIPM dynamics: acc = omega^2 * (com - zmp)
            com_acc = omega**2 * (com_pos - zmp_ref)

            # Integrate
            com_vel += com_acc * dt
            com_pos += com_vel * dt

            com_trajectory.append(com_pos.copy())
            vel_trajectory.append(com_vel.copy())

        return {
            'time': times,
            'com_position': np.array(com_trajectory),
            'com_velocity': np.array(vel_trajectory)
        }

    def preview_control(self, zmp_reference, preview_steps=10):
        """
        Advanced: Preview control for smoother COM tracking

        Args:
            zmp_reference: Desired ZMP trajectory
            preview_steps: Number of future steps to consider

        Returns:
            Optimized COM trajectory
        """
        # Simplified implementation - full version requires optimal control
        # This is a placeholder showing the concept
        print(f"Preview control with {preview_steps} step lookahead")
        return self.generate_com_trajectory(zmp_reference, len(zmp_reference) * 0.01)

# Example: Generate walking pattern
gait_gen = ZMPGaitGenerator(robot_mass=60.0, com_height=0.8)

# Define ZMP reference trajectory (simplified: straight line)
step_length = 0.3
n_steps = 4
zmp_reference = []

for step in range(n_steps):
    # Double support: ZMP between feet
    for _ in range(20):
        zmp_reference.append([step * step_length, 0.0])

    # Single support: ZMP under stance foot
    for _ in range(40):
        zmp_reference.append([step * step_length + step_length/2, 0.0])

# Generate COM trajectory
com_traj = gait_gen.generate_com_trajectory(zmp_reference, duration=len(zmp_reference) * 0.01)

print(f"\nGait generation:")
print(f"  Steps: {n_steps}")
print(f"  Step length: {step_length}m")
print(f"  Total distance: {com_traj['com_position'][-1, 0]:.2f}m")
print(f"  Final velocity: {com_traj['com_velocity'][-1, 0]:.2f}m/s")
```

## Gait Pattern Generation

### Step Pattern Generator

```python
class StepPatternGenerator:
    """Generate foot placement patterns for walking"""

    def __init__(self, step_length=0.3, step_width=0.2, step_height=0.05):
        self.step_length = step_length  # Forward distance per step
        self.step_width = step_width    # Lateral distance between feet
        self.step_height = step_height  # Foot clearance during swing

    def generate_foot_steps(self, n_steps, initial_left_pos=[0, 0.1, 0],
                           initial_right_pos=[0, -0.1, 0]):
        """
        Generate sequence of foot placements

        Args:
            n_steps: Number of steps to generate
            initial_left_pos: Starting position of left foot
            initial_right_pos: Starting position of right foot

        Returns:
            Dictionary with left and right foot positions for each step
        """
        left_positions = [np.array(initial_left_pos)]
        right_positions = [np.array(initial_right_pos)]

        current_left = np.array(initial_left_pos)
        current_right = np.array(initial_right_pos)

        for step in range(n_steps):
            if step % 2 == 0:
                # Move left foot forward
                current_left = current_left + np.array([self.step_length, 0, 0])
                left_positions.append(current_left.copy())
                right_positions.append(current_right.copy())
            else:
                # Move right foot forward
                current_right = current_right + np.array([self.step_length, 0, 0])
                left_positions.append(current_left.copy())
                right_positions.append(current_right.copy())

        return {
            'left_foot': np.array(left_positions),
            'right_foot': np.array(right_positions),
            'n_steps': n_steps
        }

    def generate_continuous_trajectory(self, foot_steps, cycle_time=1.2):
        """
        Convert discrete foot steps into continuous trajectories

        Args:
            foot_steps: Output from generate_foot_steps
            cycle_time: Time per step

        Returns:
            Time-parameterized foot trajectories
        """
        n_steps = foot_steps['n_steps']
        dt = 0.01
        total_time = n_steps * cycle_time
        times = np.arange(0, total_time, dt)

        left_trajectory = []
        right_trajectory = []

        for t in times:
            step_index = int(t / cycle_time)
            phase_progress = (t % cycle_time) / cycle_time

            if step_index >= n_steps:
                step_index = n_steps - 1

            # Determine which foot is swinging
            if step_index % 2 == 0:
                # Left foot swinging
                if step_index < n_steps - 1:
                    left_pos = FootTrajectory.swing_trajectory(
                        phase_progress,
                        foot_steps['left_foot'][step_index],
                        foot_steps['left_foot'][step_index + 1],
                        self.step_height
                    )
                else:
                    left_pos = foot_steps['left_foot'][step_index]

                right_pos = foot_steps['right_foot'][step_index]

            else:
                # Right foot swinging
                left_pos = foot_steps['left_foot'][step_index]

                if step_index < n_steps - 1:
                    right_pos = FootTrajectory.swing_trajectory(
                        phase_progress,
                        foot_steps['right_foot'][step_index],
                        foot_steps['right_foot'][step_index + 1],
                        self.step_height
                    )
                else:
                    right_pos = foot_steps['right_foot'][step_index]

            left_trajectory.append(left_pos)
            right_trajectory.append(right_pos)

        return {
            'time': times,
            'left_foot': np.array(left_trajectory),
            'right_foot': np.array(right_trajectory)
        }

# Example: Generate walking pattern
pattern_gen = StepPatternGenerator(step_length=0.3, step_width=0.2)
foot_steps = pattern_gen.generate_foot_steps(n_steps=6)

print(f"\nStep pattern generation:")
print(f"  Number of steps: {foot_steps['n_steps']}")
print(f"  Final left foot: {foot_steps['left_foot'][-1]}")
print(f"  Final right foot: {foot_steps['right_foot'][-1]}")

# Generate continuous trajectory
continuous = pattern_gen.generate_continuous_trajectory(foot_steps, cycle_time=1.0)
print(f"  Trajectory duration: {continuous['time'][-1]:.2f}s")
print(f"  Trajectory points: {len(continuous['time'])}")
```

### Adaptive Step Planning

```python
class AdaptiveStepPlanner:
    """Adjust step patterns based on terrain and objectives"""

    def __init__(self, base_generator):
        self.base_gen = base_generator

    def plan_terrain_adaptive_steps(self, n_steps, terrain_heights):
        """
        Adjust foot placement heights based on terrain

        Args:
            n_steps: Number of steps
            terrain_heights: Function(x, y) -> z height at position

        Returns:
            Adjusted foot step positions
        """
        # Start with nominal pattern
        foot_steps = self.base_gen.generate_foot_steps(n_steps)

        # Adjust z-coordinate based on terrain
        for i in range(len(foot_steps['left_foot'])):
            x, y, z = foot_steps['left_foot'][i]
            terrain_z = terrain_heights(x, y)
            foot_steps['left_foot'][i][2] = terrain_z

        for i in range(len(foot_steps['right_foot'])):
            x, y, z = foot_steps['right_foot'][i]
            terrain_z = terrain_heights(x, y)
            foot_steps['right_foot'][i][2] = terrain_z

        return foot_steps

    def plan_obstacle_avoidance_steps(self, n_steps, obstacle_positions):
        """
        Adjust step pattern to avoid obstacles

        Args:
            n_steps: Number of steps
            obstacle_positions: List of [x, y, radius] for obstacles

        Returns:
            Modified foot step pattern
        """
        foot_steps = self.base_gen.generate_foot_steps(n_steps)

        # Simple strategy: if step would land in obstacle, shift laterally
        for i in range(len(foot_steps['left_foot'])):
            pos = foot_steps['left_foot'][i][:2]  # x, y

            for obs_x, obs_y, obs_r in obstacle_positions:
                dist = np.linalg.norm(pos - np.array([obs_x, obs_y]))
                if dist < obs_r + 0.1:  # Collision
                    # Shift foot laterally (to the left for left foot)
                    foot_steps['left_foot'][i][1] += obs_r + 0.1 - dist

        # Similar for right foot
        for i in range(len(foot_steps['right_foot'])):
            pos = foot_steps['right_foot'][i][:2]

            for obs_x, obs_y, obs_r in obstacle_positions:
                dist = np.linalg.norm(pos - np.array([obs_x, obs_y]))
                if dist < obs_r + 0.1:
                    # Shift foot laterally (to the right for right foot)
                    foot_steps['right_foot'][i][1] -= obs_r + 0.1 - dist

        return foot_steps

# Example: Terrain-adaptive stepping
def sample_terrain(x, y):
    """Sample terrain height (e.g., stairs)"""
    # Stairs with 10cm rise every 30cm
    stair_height = 0.1
    stair_depth = 0.3
    stair_num = int(x / stair_depth)
    return stair_num * stair_height

pattern_gen = StepPatternGenerator()
adaptive_planner = AdaptiveStepPlanner(pattern_gen)

terrain_steps = adaptive_planner.plan_terrain_adaptive_steps(6, sample_terrain)
print(f"\nTerrain-adaptive steps:")
for i in range(len(terrain_steps['left_foot'])):
    print(f"  Step {i}: Left={terrain_steps['left_foot'][i]}, Right={terrain_steps['right_foot'][i]}")
```

## Balance Control and Recovery

### Push Recovery Controller

```python
class BalanceController:
    """Controller for maintaining balance and recovering from disturbances"""

    def __init__(self, robot_mass, com_height):
        self.mass = robot_mass
        self.com_height = com_height
        self.zmp_calc = ZMPCalculator(robot_mass)

    def compute_ankle_torque(self, com_error, com_velocity, kp=500.0, kd=50.0):
        """
        Ankle strategy for small disturbances

        Args:
            com_error: Difference between desired and actual COM position
            com_velocity: Current COM velocity
            kp, kd: PD control gains

        Returns:
            Required ankle torque
        """
        # PD control
        torque = kp * com_error + kd * com_velocity
        return torque

    def compute_step_adjustment(self, com_position, com_velocity, support_polygon):
        """
        Stepping strategy for large disturbances

        If COM velocity would carry it outside support polygon, take a step

        Args:
            com_position: Current COM position [x, y]
            com_velocity: Current COM velocity [vx, vy]
            support_polygon: Current support region

        Returns:
            Recommended foot placement for recovery step (or None)
        """
        # Predict where COM will be in 0.3 seconds (typical step time)
        prediction_time = 0.3
        predicted_com = com_position + com_velocity * prediction_time

        # Check if prediction is outside support
        is_stable = self.zmp_calc.check_stability(predicted_com, support_polygon)

        if not is_stable:
            # Need to step in direction of velocity
            step_direction = com_velocity / (np.linalg.norm(com_velocity) + 1e-6)
            step_distance = 0.3  # meters

            recovery_foot_pos = com_position + step_direction * step_distance
            return recovery_foot_pos

        return None

    def compute_hip_strategy(self, com_error, kp=300.0):
        """
        Hip strategy for medium disturbances

        Args:
            com_error: COM position error
            kp: Proportional gain

        Returns:
            Hip torque to generate counter-rotation
        """
        # Simplified: proportional control
        hip_torque = kp * com_error
        return hip_torque

# Example: Balance recovery simulation
balance_ctrl = BalanceController(robot_mass=60.0, com_height=0.8)

# Simulate push disturbance
com_pos = np.array([0.05, 0.0])    # Slightly forward
com_vel = np.array([0.5, 0.0])     # Pushed forward
support = [[-0.1, -0.05], [-0.1, 0.05], [0.1, 0.05], [0.1, -0.05]]

print(f"\nBalance recovery:")
print(f"  COM position: {com_pos}")
print(f"  COM velocity: {com_vel}m/s")

# Try ankle strategy
com_error = 0.05  # 5cm forward of desired
ankle_torque = balance_ctrl.compute_ankle_torque(com_error, com_vel[0])
print(f"  Ankle torque: {ankle_torque:.1f}Nm")

# Check if stepping is needed
recovery_step = balance_ctrl.compute_step_adjustment(com_pos, com_vel, support)
if recovery_step is not None:
    print(f"  Recovery step needed at: {recovery_step}")
else:
    print(f"  No step needed, ankle/hip strategy sufficient")
```

### Capture Point Control

```python
class CapturePointController:
    """
    Control based on Capture Point (CP) - the point where robot must step
    to come to a stop
    """

    def __init__(self, com_height, gravity=9.81):
        self.com_height = com_height
        self.g = gravity
        self.omega = np.sqrt(gravity / com_height)  # Natural frequency

    def compute_capture_point(self, com_position, com_velocity):
        """
        Calculate instantaneous capture point

        CP = COM + (1/omega) * COM_velocity

        Args:
            com_position: Current COM position [x, y]
            com_velocity: Current COM velocity [vx, vy]

        Returns:
            Capture point position [x, y]
        """
        cp = com_position + (1.0 / self.omega) * com_velocity
        return cp

    def plan_foot_placement(self, com_position, com_velocity, desired_velocity):
        """
        Determine where to place next foot based on capture point

        Args:
            com_position: Current COM position
            com_velocity: Current COM velocity
            desired_velocity: Target velocity after step

        Returns:
            Recommended foot placement
        """
        # Current capture point
        current_cp = self.compute_capture_point(com_position, com_velocity)

        # Desired capture point (based on target velocity)
        desired_cp = com_position + (1.0 / self.omega) * desired_velocity

        # Foot should be placed at desired capture point
        foot_placement = desired_cp

        return foot_placement, current_cp

    def compute_stepping_urgency(self, com_position, com_velocity, support_polygon):
        """
        Determine how urgently a step is needed

        Args:
            com_position, com_velocity: COM state
            support_polygon: Current support region

        Returns:
            Urgency score [0, 1], 1 = immediate step needed
        """
        cp = self.compute_capture_point(com_position, com_velocity)

        # Calculate distance from CP to support polygon boundary
        zmp_calc = ZMPCalculator()
        margin = zmp_calc.compute_stability_margin(cp, support_polygon)

        # If CP is outside support, urgency = 1
        # If CP is at center, urgency = 0
        max_margin = 0.1  # meters
        urgency = 1.0 - np.clip(margin / max_margin, 0, 1)

        return urgency

# Example: Capture point planning
cp_controller = CapturePointController(com_height=0.8)

# Robot state
com_pos = np.array([0.0, 0.0])
com_vel = np.array([0.4, 0.0])  # Walking forward
desired_vel = np.array([0.5, 0.0])  # Want to walk faster

foot_placement, current_cp = cp_controller.plan_foot_placement(com_pos, com_vel, desired_vel)

print(f"\nCapture point control:")
print(f"  COM position: {com_pos}")
print(f"  COM velocity: {com_vel}m/s")
print(f"  Current capture point: {current_cp}")
print(f"  Desired velocity: {desired_vel}m/s")
print(f"  Recommended foot placement: {foot_placement}")

# Check urgency
support = [[-0.1, -0.05], [-0.1, 0.05], [0.1, 0.05], [0.1, -0.05]]
urgency = cp_controller.compute_stepping_urgency(com_pos, com_vel, support)
print(f"  Stepping urgency: {urgency:.2f}")
```

## Complete Walking Controller

```python
class BipedalWalkingController:
    """Integrated walking controller combining all strategies"""

    def __init__(self, robot_mass=60.0, com_height=0.8, step_length=0.3):
        self.mass = robot_mass
        self.com_height = com_height

        # Sub-controllers
        self.zmp_calc = ZMPCalculator(robot_mass)
        self.gait_gen = ZMPGaitGenerator(robot_mass, com_height)
        self.balance_ctrl = BalanceController(robot_mass, com_height)
        self.cp_ctrl = CapturePointController(com_height)
        self.step_gen = StepPatternGenerator(step_length=step_length)

        # State
        self.current_com_pos = np.array([0.0, 0.0, com_height])
        self.current_com_vel = np.array([0.0, 0.0, 0.0])
        self.desired_velocity = 0.5  # m/s

    def update(self, dt, disturbance_force=None):
        """
        Main control loop update

        Args:
            dt: Time step
            disturbance_force: External force applied to COM [fx, fy, fz]

        Returns:
            Control outputs: foot positions, joint torques, etc.
        """
        # Apply disturbance
        if disturbance_force is not None:
            disturbance_acc = np.array(disturbance_force) / self.mass
            self.current_com_vel[:2] += disturbance_acc[:2] * dt

        # Compute capture point
        cp = self.cp_ctrl.compute_capture_point(
            self.current_com_pos[:2],
            self.current_com_vel[:2]
        )

        # Determine if step is needed
        # (Simplified: always step at regular intervals)

        # Generate ZMP reference
        # ...

        # Compute required ankle/hip torques for balance
        com_error = self.current_com_pos[0]  # Error in x
        ankle_torque = self.balance_ctrl.compute_ankle_torque(
            com_error,
            self.current_com_vel[0]
        )

        # Update COM state (simplified dynamics)
        # In reality, this comes from full-body dynamics simulation
        self.current_com_pos[:2] += self.current_com_vel[:2] * dt

        return {
            'com_position': self.current_com_pos,
            'capture_point': cp,
            'ankle_torque': ankle_torque
        }

    def walk(self, target_distance, dt=0.01):
        """
        Execute walking to cover target distance

        Args:
            target_distance: Distance to walk (meters)
            dt: Simulation time step

        Returns:
            Trajectory history
        """
        n_steps = int(target_distance / self.step_gen.step_length)
        trajectory = {
            'time': [],
            'com_position': [],
            'zmp': [],
            'capture_point': []
        }

        t = 0
        while self.current_com_pos[0] < target_distance:
            outputs = self.update(dt)

            # Log
            trajectory['time'].append(t)
            trajectory['com_position'].append(outputs['com_position'].copy())
            trajectory['capture_point'].append(outputs['capture_point'].copy())

            t += dt

        return trajectory

# Example: Simulate walking
print(f"\n{'='*50}")
print("Complete Walking Simulation")
print(f"{'='*50}")

walker = BipedalWalkingController(robot_mass=60.0, com_height=0.8, step_length=0.3)

# Walk 2 meters
trajectory = walker.walk(target_distance=2.0)

print(f"\nWalking completed:")
print(f"  Distance traveled: {trajectory['com_position'][-1][0]:.2f}m")
print(f"  Time elapsed: {trajectory['time'][-1]:.2f}s")
print(f"  Average speed: {trajectory['com_position'][-1][0] / trajectory['time'][-1]:.2f}m/s")
print(f"  Trajectory points: {len(trajectory['time'])}")
```

## Exercises

### Exercise 1: Gait Optimization
Implement a cost function that minimizes energy consumption (sum of squared torques) while maintaining stability. Optimize step length and step time.

### Exercise 2: Terrain Adaptation
Create a controller that automatically adjusts step height and length when detecting stairs or slopes using terrain height measurements.

### Exercise 3: Push Recovery
Simulate a push disturbance at different magnitudes and directions. Implement a controller that selects the appropriate strategy (ankle, hip, or stepping) based on disturbance magnitude.

### Exercise 4: ZMP Visualization
Create a visualization showing:
- Support polygon (shaded)
- ZMP trajectory (line)
- COM trajectory (line)
- Foot positions
Animate over a complete gait cycle.

## Summary

This module covered:

- **Gait fundamentals**: phases, timing, and foot trajectories
- **Zero-Moment Point (ZMP)**: stability criterion and computation
- **Gait generation**: ZMP-based pattern generation and LIPM
- **Balance control**: ankle, hip, and stepping strategies
- **Capture Point**: predictive step placement for stability
- **Integrated walking**: combining all components into a complete controller

These techniques form the foundation for bipedal robot control and are used in humanoid robots like Atlas, ASIMO, and Cassie.

## Additional Resources

- **Books**:
  - "Biped Locomotion: Principles, Optimization and Control" by Shuuji Kajita
  - "Humanoid Robots: Modeling and Control" by Dragomir Nenchev
- **Papers**:
  - "Biped Walking Pattern Generation by using Preview Control of Zero-Moment Point" (Kajita et al.)
  - "Capture Point: A Step toward Humanoid Push Recovery" (Pratt et al.)
- **Software**:
  - Drake for bipedal simulation
  - Webots humanoid models
  - PyBullet for physics testing

## Next Week

Week 13 concludes the course with a **Capstone Project**: Building a voice-controlled humanoid robot using Vision-Language-Action models. You'll integrate:
- Speech recognition (Whisper)
- Language understanding (LLMs)
- Motion planning (this module)
- Robot control (ROS)
