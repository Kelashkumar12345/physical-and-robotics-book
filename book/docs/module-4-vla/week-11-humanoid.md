---
sidebar_position: 1
title: "Week 11: Humanoid Kinematics"
---

# Week 11: Humanoid Kinematics

## Introduction to Humanoid Robotics

Humanoid robots are designed to mimic the human body structure, typically featuring a torso, head, arms, and legs. Understanding humanoid kinematics is fundamental to controlling these complex systems and enabling human-like motion.

### Why Humanoid Robots?

- **Human-Centric Environments**: Operate in spaces designed for humans (stairs, doorways, furniture)
- **Natural Interaction**: Intuitive communication and collaboration with people
- **Versatility**: Adaptable to various tasks using the same platform
- **Research Platform**: Study human biomechanics and motor control

### Key Challenges

1. **High Degree of Freedom (DOF)**: Humanoids typically have 20-50+ joints
2. **Redundancy**: Multiple joint configurations can achieve the same end-effector pose
3. **Stability**: Maintaining balance during dynamic movements
4. **Energy Efficiency**: Optimizing power consumption during locomotion

## Kinematic Fundamentals

### Joint Types in Humanoid Robots

```python
import numpy as np
from enum import Enum

class JointType(Enum):
    REVOLUTE = 1  # Rotational joint (most common)
    PRISMATIC = 2  # Linear joint (rare in humanoids)
    SPHERICAL = 3  # Ball-and-socket joint (hip, shoulder)

class HumanoidJoint:
    """Represents a single joint in a humanoid robot"""

    def __init__(self, name, joint_type, axis, limits, home_position=0.0):
        self.name = name
        self.joint_type = joint_type
        self.axis = np.array(axis)  # Rotation/translation axis
        self.limits = limits  # (min, max) in radians or meters
        self.home_position = home_position
        self.current_position = home_position

    def set_position(self, position):
        """Set joint position with limit checking"""
        if self.limits[0] <= position <= self.limits[1]:
            self.current_position = position
            return True
        else:
            print(f"Warning: Position {position} exceeds limits {self.limits}")
            return False

    def get_position(self):
        return self.current_position

# Example: Define a simple humanoid arm
def create_simple_arm():
    """Create a 3-DOF humanoid arm"""
    joints = [
        HumanoidJoint("shoulder_pitch", JointType.REVOLUTE,
                     [0, 1, 0], (-np.pi/2, np.pi/2)),
        HumanoidJoint("shoulder_roll", JointType.REVOLUTE,
                     [1, 0, 0], (-np.pi/3, np.pi/3)),
        HumanoidJoint("elbow", JointType.REVOLUTE,
                     [0, 1, 0], (0, np.pi))
    ]
    return joints

arm_joints = create_simple_arm()
for joint in arm_joints:
    print(f"{joint.name}: limits {joint.limits}")
```

### Denavit-Hartenberg (DH) Parameters

The DH convention is a standard method for describing robot kinematics using four parameters per joint:

- **a** (link length): Distance along x-axis
- **α** (link twist): Rotation around x-axis
- **d** (link offset): Distance along z-axis
- **θ** (joint angle): Rotation around z-axis

```python
class DHParameter:
    """Denavit-Hartenberg parameters for a joint"""

    def __init__(self, a, alpha, d, theta, is_revolute=True):
        self.a = a          # Link length
        self.alpha = alpha  # Link twist
        self.d = d          # Link offset
        self.theta = theta  # Joint angle
        self.is_revolute = is_revolute

    def get_transform_matrix(self, joint_value=0):
        """
        Compute 4x4 homogeneous transformation matrix

        Args:
            joint_value: Joint angle (revolute) or offset (prismatic)
        """
        if self.is_revolute:
            theta = self.theta + joint_value
            d = self.d
        else:
            theta = self.theta
            d = self.d + joint_value

        # DH transformation matrix
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(self.alpha)
        sa = np.sin(self.alpha)

        T = np.array([
            [ct, -st*ca,  st*sa, self.a*ct],
            [st,  ct*ca, -ct*sa, self.a*st],
            [0,   sa,     ca,     d],
            [0,   0,      0,      1]
        ])

        return T

# Example: Simple 2-link planar arm
dh_params_2link = [
    DHParameter(a=0.3, alpha=0, d=0, theta=0),  # Link 1: 30cm
    DHParameter(a=0.25, alpha=0, d=0, theta=0)  # Link 2: 25cm
]

# Compute forward kinematics
def forward_kinematics_dh(dh_params, joint_angles):
    """Compute end-effector pose from joint angles"""
    T = np.eye(4)
    for param, angle in zip(dh_params, joint_angles):
        T = T @ param.get_transform_matrix(angle)
    return T

# Test with specific joint angles
joint_angles = [np.pi/4, np.pi/6]
T_end = forward_kinematics_dh(dh_params_2link, joint_angles)
print("End-effector position:", T_end[:3, 3])
print("End-effector orientation:\n", T_end[:3, :3])
```

## Forward Kinematics

Forward kinematics computes the position and orientation of the end-effector (hand, foot) given joint angles.

### 3D Humanoid Arm Example

```python
class HumanoidArm:
    """Complete 6-DOF humanoid arm with shoulder, elbow, and wrist"""

    def __init__(self):
        # Link lengths (in meters)
        self.upper_arm_length = 0.28
        self.forearm_length = 0.25

        # DH parameters for 6-DOF arm
        self.dh_params = [
            DHParameter(0, -np.pi/2, 0, 0),           # Shoulder yaw
            DHParameter(0, np.pi/2, 0, -np.pi/2),     # Shoulder pitch
            DHParameter(0, np.pi/2, 0, np.pi/2),      # Shoulder roll
            DHParameter(self.upper_arm_length, 0, 0, 0),  # Elbow pitch
            DHParameter(0, -np.pi/2, 0, 0),           # Wrist yaw
            DHParameter(0, np.pi/2, self.forearm_length, 0)  # Wrist pitch
        ]

        # Joint limits (rad)
        self.joint_limits = [
            (-np.pi, np.pi),       # Shoulder yaw
            (-np.pi/2, np.pi/2),   # Shoulder pitch
            (-np.pi/6, np.pi/2),   # Shoulder roll
            (0, 2.5),              # Elbow pitch
            (-np.pi/2, np.pi/2),   # Wrist yaw
            (-np.pi/2, np.pi/2)    # Wrist pitch
        ]

    def forward_kinematics(self, joint_angles):
        """
        Compute end-effector pose

        Args:
            joint_angles: List of 6 joint angles [rad]

        Returns:
            4x4 homogeneous transformation matrix
        """
        if len(joint_angles) != 6:
            raise ValueError("Expected 6 joint angles")

        # Check joint limits
        for i, (angle, limits) in enumerate(zip(joint_angles, self.joint_limits)):
            if not (limits[0] <= angle <= limits[1]):
                print(f"Warning: Joint {i} angle {angle} exceeds limits {limits}")

        # Compute cumulative transformation
        T = np.eye(4)
        for param, angle in zip(self.dh_params, joint_angles):
            T = T @ param.get_transform_matrix(angle)

        return T

    def get_end_effector_position(self, joint_angles):
        """Extract position vector from transformation matrix"""
        T = self.forward_kinematics(joint_angles)
        return T[:3, 3]

    def get_end_effector_orientation(self, joint_angles):
        """Extract rotation matrix from transformation matrix"""
        T = self.forward_kinematics(joint_angles)
        return T[:3, :3]

# Example usage
arm = HumanoidArm()

# Home position (all joints at 0)
home_angles = [0, 0, 0, 0, 0, 0]
print("Home position:", arm.get_end_effector_position(home_angles))

# Reach forward
reach_angles = [0, np.pi/6, 0, np.pi/4, 0, 0]
print("Reach position:", arm.get_end_effector_position(reach_angles))

# Reach to the side
side_angles = [np.pi/2, 0, np.pi/4, np.pi/3, 0, 0]
print("Side position:", arm.get_end_effector_position(side_angles))
```

## Inverse Kinematics

Inverse kinematics (IK) computes the joint angles required to achieve a desired end-effector pose. This is more challenging than forward kinematics and often has multiple solutions.

### Analytical IK for 2-Link Planar Arm

```python
def inverse_kinematics_2link(target_x, target_y, L1, L2):
    """
    Analytical IK solution for 2-link planar arm

    Args:
        target_x, target_y: Desired end-effector position
        L1, L2: Link lengths

    Returns:
        List of solutions [(theta1, theta2), ...] or empty if unreachable
    """
    # Distance to target
    distance = np.sqrt(target_x**2 + target_y**2)

    # Check if target is reachable
    if distance > L1 + L2 or distance < abs(L1 - L2):
        print(f"Target ({target_x}, {target_y}) is unreachable")
        return []

    # Law of cosines for theta2
    cos_theta2 = (target_x**2 + target_y**2 - L1**2 - L2**2) / (2 * L1 * L2)

    # Two solutions for theta2 (elbow up and elbow down)
    solutions = []

    for sign in [1, -1]:
        theta2 = sign * np.arccos(np.clip(cos_theta2, -1, 1))

        # Solve for theta1
        k1 = L1 + L2 * np.cos(theta2)
        k2 = L2 * np.sin(theta2)
        theta1 = np.arctan2(target_y, target_x) - np.arctan2(k2, k1)

        solutions.append((theta1, theta2))

    return solutions

# Test IK
L1, L2 = 0.3, 0.25
target = (0.4, 0.2)

solutions = inverse_kinematics_2link(target[0], target[1], L1, L2)
print(f"\nIK solutions for target {target}:")
for i, (theta1, theta2) in enumerate(solutions):
    print(f"Solution {i+1}: theta1={np.degrees(theta1):.2f}°, theta2={np.degrees(theta2):.2f}°")

    # Verify with FK
    T = forward_kinematics_dh(dh_params_2link, [theta1, theta2])
    actual_pos = T[:2, 3]
    error = np.linalg.norm(actual_pos - np.array(target))
    print(f"  FK verification: position={actual_pos}, error={error:.6f}m")
```

### Numerical IK using Jacobian (Iterative)

For complex manipulators, numerical methods are more practical:

```python
class NumericalIK:
    """Numerical inverse kinematics solver using Jacobian transpose method"""

    def __init__(self, arm_model, max_iterations=100, tolerance=1e-4):
        self.arm = arm_model
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def compute_jacobian(self, joint_angles, delta=1e-6):
        """
        Numerical computation of Jacobian matrix

        Args:
            joint_angles: Current joint configuration
            delta: Small perturbation for numerical differentiation

        Returns:
            6x6 Jacobian matrix (3 position + 3 orientation)
        """
        n_joints = len(joint_angles)
        jacobian = np.zeros((6, n_joints))

        # Current end-effector pose
        T0 = self.arm.forward_kinematics(joint_angles)
        pos0 = T0[:3, 3]

        # Numerical differentiation
        for i in range(n_joints):
            # Perturb joint i
            q_delta = joint_angles.copy()
            q_delta[i] += delta

            # Compute new pose
            T_delta = self.arm.forward_kinematics(q_delta)
            pos_delta = T_delta[:3, 3]

            # Position Jacobian (first 3 rows)
            jacobian[:3, i] = (pos_delta - pos0) / delta

            # Orientation Jacobian (simplified: using position only for now)
            # Full implementation would use rotation difference

        return jacobian[:3, :]  # Return only position Jacobian

    def solve(self, target_position, initial_guess=None, alpha=0.5):
        """
        Solve IK using Jacobian transpose method

        Args:
            target_position: Desired 3D position [x, y, z]
            initial_guess: Starting joint configuration
            alpha: Step size for gradient descent

        Returns:
            Joint angles that reach target (or best attempt)
        """
        if initial_guess is None:
            joint_angles = np.zeros(6)
        else:
            joint_angles = np.array(initial_guess)

        target = np.array(target_position)

        for iteration in range(self.max_iterations):
            # Current position
            current_pos = self.arm.get_end_effector_position(joint_angles)

            # Position error
            error = target - current_pos
            error_magnitude = np.linalg.norm(error)

            # Check convergence
            if error_magnitude < self.tolerance:
                print(f"Converged in {iteration} iterations, error={error_magnitude:.6f}m")
                return joint_angles

            # Compute Jacobian
            J = self.compute_jacobian(joint_angles)

            # Jacobian transpose method: Δq = α * J^T * error
            delta_q = alpha * J.T @ error

            # Update joint angles
            joint_angles += delta_q

            # Enforce joint limits
            for i, limits in enumerate(self.arm.joint_limits):
                joint_angles[i] = np.clip(joint_angles[i], limits[0], limits[1])

        print(f"Max iterations reached. Final error: {error_magnitude:.6f}m")
        return joint_angles

# Example usage
arm = HumanoidArm()
ik_solver = NumericalIK(arm)

# Solve for a target position
target_pos = [0.4, 0.1, 0.3]
solution = ik_solver.solve(target_pos)

print(f"\nIK Solution:")
print(f"Joint angles (deg): {np.degrees(solution)}")
print(f"Achieved position: {arm.get_end_effector_position(solution)}")
print(f"Target position:   {target_pos}")
```

## Joint Configurations and Workspace

### Workspace Analysis

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class WorkspaceAnalyzer:
    """Analyze and visualize robot workspace"""

    def __init__(self, arm_model):
        self.arm = arm_model

    def sample_workspace(self, n_samples=10000):
        """
        Sample random joint configurations and compute reachable positions

        Args:
            n_samples: Number of random samples

        Returns:
            Array of reachable positions (n_samples x 3)
        """
        positions = []

        for _ in range(n_samples):
            # Random joint angles within limits
            joint_angles = []
            for limits in self.arm.joint_limits:
                angle = np.random.uniform(limits[0], limits[1])
                joint_angles.append(angle)

            # Compute position
            pos = self.arm.get_end_effector_position(joint_angles)
            positions.append(pos)

        return np.array(positions)

    def plot_workspace_3d(self, positions, title="Arm Workspace"):
        """Visualize workspace in 3D"""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                  c=positions[:, 2], cmap='viridis', alpha=0.1, s=1)

        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(title)

        # Equal aspect ratio
        max_range = np.array([positions[:, 0].max() - positions[:, 0].min(),
                             positions[:, 1].max() - positions[:, 1].min(),
                             positions[:, 2].max() - positions[:, 2].min()]).max() / 2.0

        mid_x = (positions[:, 0].max() + positions[:, 0].min()) * 0.5
        mid_y = (positions[:, 1].max() + positions[:, 1].min()) * 0.5
        mid_z = (positions[:, 2].max() + positions[:, 2].min()) * 0.5

        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

        plt.tight_layout()
        return fig

# Analyze workspace
analyzer = WorkspaceAnalyzer(arm)
workspace_points = analyzer.sample_workspace(5000)

print(f"Workspace statistics:")
print(f"  X range: [{workspace_points[:, 0].min():.3f}, {workspace_points[:, 0].max():.3f}]m")
print(f"  Y range: [{workspace_points[:, 1].min():.3f}, {workspace_points[:, 1].max():.3f}]m")
print(f"  Z range: [{workspace_points[:, 2].min():.3f}, {workspace_points[:, 2].max():.3f}]m")

# Uncomment to visualize (requires display)
# fig = analyzer.plot_workspace_3d(workspace_points)
# plt.show()
```

### Singularity Detection

```python
def detect_singularity(jacobian, threshold=1e-3):
    """
    Detect kinematic singularities by examining Jacobian condition

    Args:
        jacobian: Jacobian matrix
        threshold: Condition number threshold for singularity

    Returns:
        True if singular, False otherwise
    """
    # Compute singular values
    singular_values = np.linalg.svd(jacobian, compute_uv=False)

    # Check condition number
    if singular_values[-1] < threshold:
        return True, singular_values

    return False, singular_values

# Test singularity
arm = HumanoidArm()
ik_solver = NumericalIK(arm)

# Fully extended arm (often singular)
extended_config = [0, 0, 0, 2.0, 0, 0]
J = ik_solver.compute_jacobian(extended_config)
is_singular, sv = detect_singularity(J)

print(f"\nSingularity check for extended arm:")
print(f"  Singular values: {sv}")
print(f"  Is singular: {is_singular}")
print(f"  Condition number: {sv[0]/sv[-1] if sv[-1] > 0 else 'inf'}")
```

## Motion Planning for Humanoids

### Joint Space Trajectory Planning

```python
class TrajectoryPlanner:
    """Plan smooth trajectories in joint space"""

    @staticmethod
    def quintic_polynomial(t, t_total, q_start, q_end):
        """
        Fifth-order polynomial trajectory (smooth position, velocity, acceleration)

        Args:
            t: Current time
            t_total: Total trajectory duration
            q_start: Starting position
            q_end: Ending position

        Returns:
            (position, velocity, acceleration) at time t
        """
        # Normalize time to [0, 1]
        s = t / t_total

        # Quintic coefficients (boundary conditions: zero vel/acc at start/end)
        h = q_end - q_start
        position = q_start + h * (10*s**3 - 15*s**4 + 6*s**5)
        velocity = h * (30*s**2 - 60*s**3 + 30*s**4) / t_total
        acceleration = h * (60*s - 180*s**2 + 120*s**3) / (t_total**2)

        return position, velocity, acceleration

    @staticmethod
    def plan_multi_joint_trajectory(q_start, q_end, duration, dt=0.01):
        """
        Plan synchronized trajectory for multiple joints

        Args:
            q_start: Starting joint configuration
            q_end: Ending joint configuration
            duration: Trajectory duration (seconds)
            dt: Time step

        Returns:
            Dictionary with time, positions, velocities, accelerations
        """
        n_joints = len(q_start)
        n_steps = int(duration / dt) + 1
        times = np.linspace(0, duration, n_steps)

        positions = np.zeros((n_steps, n_joints))
        velocities = np.zeros((n_steps, n_joints))
        accelerations = np.zeros((n_steps, n_joints))

        for i, t in enumerate(times):
            for j in range(n_joints):
                pos, vel, acc = TrajectoryPlanner.quintic_polynomial(
                    t, duration, q_start[j], q_end[j]
                )
                positions[i, j] = pos
                velocities[i, j] = vel
                accelerations[i, j] = acc

        return {
            'time': times,
            'position': positions,
            'velocity': velocities,
            'acceleration': accelerations
        }

# Example: Plan arm reaching motion
start_config = np.array([0, 0, 0, 0, 0, 0])
end_config = np.array([np.pi/4, np.pi/6, np.pi/8, np.pi/3, 0, 0])

trajectory = TrajectoryPlanner.plan_multi_joint_trajectory(
    start_config, end_config, duration=2.0
)

print(f"\nTrajectory planning:")
print(f"  Duration: {trajectory['time'][-1]}s")
print(f"  Steps: {len(trajectory['time'])}")
print(f"  Start config: {np.degrees(start_config)}")
print(f"  End config: {np.degrees(end_config)}")

# Plot first joint trajectory
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(10, 8))
joint_idx = 0

axes[0].plot(trajectory['time'], np.degrees(trajectory['position'][:, joint_idx]))
axes[0].set_ylabel('Position (deg)')
axes[0].set_title(f'Joint {joint_idx} Trajectory')
axes[0].grid(True)

axes[1].plot(trajectory['time'], np.degrees(trajectory['velocity'][:, joint_idx]))
axes[1].set_ylabel('Velocity (deg/s)')
axes[1].grid(True)

axes[2].plot(trajectory['time'], np.degrees(trajectory['acceleration'][:, joint_idx]))
axes[2].set_ylabel('Acceleration (deg/s²)')
axes[2].set_xlabel('Time (s)')
axes[2].grid(True)

plt.tight_layout()
# plt.show()  # Uncomment to display
```

### Cartesian Space Planning

```python
class CartesianPlanner:
    """Plan trajectories in Cartesian (task) space"""

    def __init__(self, arm_model, ik_solver):
        self.arm = arm_model
        self.ik_solver = ik_solver

    def plan_straight_line(self, start_pos, end_pos, duration, dt=0.01):
        """
        Plan straight-line motion in Cartesian space

        Args:
            start_pos: Starting position [x, y, z]
            end_pos: Ending position [x, y, z]
            duration: Motion duration
            dt: Time step

        Returns:
            Trajectory with Cartesian waypoints and joint configurations
        """
        times = np.linspace(0, duration, int(duration/dt) + 1)

        cartesian_waypoints = []
        joint_waypoints = []

        # Get initial joint configuration
        current_joints = self.ik_solver.solve(start_pos)

        for t in times:
            # Linear interpolation in Cartesian space
            s = t / duration
            target_pos = start_pos + s * (np.array(end_pos) - np.array(start_pos))

            # Solve IK for this waypoint
            joint_config = self.ik_solver.solve(target_pos, initial_guess=current_joints)

            cartesian_waypoints.append(target_pos)
            joint_waypoints.append(joint_config)
            current_joints = joint_config

        return {
            'time': times,
            'cartesian': np.array(cartesian_waypoints),
            'joints': np.array(joint_waypoints)
        }

# Example: Plan straight-line reaching
arm = HumanoidArm()
ik_solver = NumericalIK(arm, max_iterations=50)
cartesian_planner = CartesianPlanner(arm, ik_solver)

start_pos = [0.3, 0.0, 0.2]
end_pos = [0.4, 0.2, 0.3]

cart_trajectory = cartesian_planner.plan_straight_line(start_pos, end_pos, duration=1.5)

print(f"\nCartesian trajectory:")
print(f"  Start: {start_pos}")
print(f"  End: {end_pos}")
print(f"  Waypoints: {len(cart_trajectory['time'])}")

# Verify path is straight
path_errors = []
for i, pos in enumerate(cart_trajectory['cartesian']):
    # Check deviation from straight line
    t = cart_trajectory['time'][i] / cart_trajectory['time'][-1]
    ideal_pos = start_pos + t * (np.array(end_pos) - np.array(start_pos))
    error = np.linalg.norm(pos - ideal_pos)
    path_errors.append(error)

print(f"  Max path deviation: {max(path_errors):.6f}m")
```

## Practical Application: Full-Body Configuration

```python
class SimpleHumanoid:
    """Simplified humanoid robot model"""

    def __init__(self):
        # Define body structure
        self.body_parts = {
            'torso': {'height': 0.5},
            'left_arm': HumanoidArm(),
            'right_arm': HumanoidArm(),
            'head': {'pan_range': (-np.pi/2, np.pi/2),
                    'tilt_range': (-np.pi/4, np.pi/4)}
        }

        # Torso-relative arm positions
        self.left_arm_offset = np.array([0, 0.2, 0.4])   # Left shoulder
        self.right_arm_offset = np.array([0, -0.2, 0.4]) # Right shoulder

    def get_left_hand_position(self, left_arm_joints):
        """Get left hand position in world frame"""
        # Position relative to left shoulder
        local_pos = self.body_parts['left_arm'].get_end_effector_position(left_arm_joints)
        # Transform to world frame
        return self.left_arm_offset + local_pos

    def get_right_hand_position(self, right_arm_joints):
        """Get right hand position in world frame"""
        local_pos = self.body_parts['right_arm'].get_end_effector_position(right_arm_joints)
        return self.right_arm_offset + local_pos

    def dual_arm_reaching(self, left_target, right_target):
        """
        Coordinate both arms to reach targets simultaneously

        Args:
            left_target: Target position for left hand
            right_target: Target position for right hand

        Returns:
            Joint configurations for both arms
        """
        # Convert targets to arm-local coordinates
        left_local = np.array(left_target) - self.left_arm_offset
        right_local = np.array(right_target) - self.right_arm_offset

        # Solve IK for each arm
        left_ik = NumericalIK(self.body_parts['left_arm'])
        right_ik = NumericalIK(self.body_parts['right_arm'])

        left_joints = left_ik.solve(left_local)
        right_joints = right_ik.solve(right_local)

        return left_joints, right_joints

# Example: Dual arm manipulation
humanoid = SimpleHumanoid()

# Reach for an object with both hands
object_left = [0.4, 0.3, 0.4]
object_right = [0.4, -0.1, 0.4]

left_config, right_config = humanoid.dual_arm_reaching(object_left, object_right)

print(f"\nDual-arm coordination:")
print(f"  Left arm config: {np.degrees(left_config)}")
print(f"  Left hand position: {humanoid.get_left_hand_position(left_config)}")
print(f"  Right arm config: {np.degrees(right_config)}")
print(f"  Right hand position: {humanoid.get_right_hand_position(right_config)}")
```

## Exercises

### Exercise 1: Custom Manipulator
Design a 4-DOF robotic arm with your own DH parameters. Implement forward kinematics and test with various joint configurations.

### Exercise 2: IK Validation
Implement an IK solver for a 3-link planar arm and validate it by:
1. Generating random target positions
2. Solving IK
3. Verifying with forward kinematics
4. Measuring position errors

### Exercise 3: Obstacle Avoidance
Extend the trajectory planner to avoid a spherical obstacle:
- Input: Start, end positions, obstacle center and radius
- Output: Joint trajectory that maintains safe distance from obstacle

### Exercise 4: Workspace Visualization
Create a 2D cross-section of the arm workspace at different heights (z-planes). Visualize reachable regions and singularities.

## Summary

In this module, we covered:

- **Humanoid structure** and joint types
- **Denavit-Hartenberg parameters** for systematic kinematic modeling
- **Forward kinematics** for computing end-effector pose
- **Inverse kinematics** using analytical and numerical methods
- **Workspace analysis** and singularity detection
- **Motion planning** in joint and Cartesian space
- **Multi-arm coordination** for humanoid tasks

These fundamentals are essential for controlling humanoid robots and will be built upon in the next modules covering locomotion and balance control.

## Additional Resources

- **Books**:
  - "Introduction to Robotics: Mechanics and Control" by John J. Craig
  - "Modern Robotics" by Kevin Lynch and Frank Park
- **Software**:
  - PyBullet for physics simulation
  - MoveIt for motion planning
  - Pinocchio for efficient kinematics/dynamics
- **Papers**: Search for "humanoid kinematics" and "redundant manipulator control"

## Next Week

Week 12 will focus on **Bipedal Locomotion**, where we'll explore:
- Walking pattern generation
- Zero-Moment Point (ZMP) stability
- Balance control and recovery
- Dynamic walking strategies
