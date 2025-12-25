---
sidebar_position: 1
---

# Hardware Requirements

This course requires both a development workstation and an edge computing platform for deploying AI models on physical robots. Below are the detailed hardware and software requirements.

## Development Workstation

Your primary development machine where you'll write code, train models, and run simulations.

### Operating System
- **Required**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **Installation**: Native installation or dual-boot strongly recommended
- **Not Recommended**: WSL2 or virtual machines may have issues with GPU access and ROS 2 networking

### Minimum Specifications
- **CPU**: Intel Core i5 (8th gen) or AMD Ryzen 5 (3000 series) or better
- **RAM**: 16 GB DDR4
- **Storage**: 256 GB SSD (at least 100 GB free space)
- **GPU**: Integrated graphics (limited AI capabilities)

### Recommended Specifications
- **CPU**: Intel Core i7/i9 (10th gen+) or AMD Ryzen 7/9 (5000 series+)
- **RAM**: 32 GB DDR4/DDR5
- **Storage**: 512 GB NVMe SSD (at least 200 GB free space)
- **GPU**: NVIDIA RTX 3060 or better (12+ GB VRAM)

### GPU Recommendations

For AI model training and inference, an NVIDIA GPU is highly recommended:

- **Entry Level**: NVIDIA RTX 3060 (12 GB VRAM) - sufficient for inference and small model training
- **Mid-Range**: NVIDIA RTX 3080/4070 (12-16 GB VRAM) - good for most training tasks
- **High-End**: NVIDIA RTX 4080/4090 (16-24 GB VRAM) - optimal for large model training and experimentation

**CUDA Requirements**: CUDA 11.8+ or 12.x with compatible drivers (525.x or newer)

## Edge Computing Kit

The edge platform runs on your physical robot or embedded system for real-time AI inference.

### NVIDIA Jetson Orin Platform

**Recommended**: NVIDIA Jetson Orin Nano Developer Kit or better

#### Jetson Orin Nano (Entry Level)
- **GPU**: 1024-core NVIDIA Ampere GPU
- **CPU**: 6-core Arm Cortex-A78AE
- **RAM**: 8 GB LPDDR5
- **AI Performance**: 40 TOPS (INT8)
- **Power**: 7W - 15W
- **Price**: ~$499

#### Jetson Orin NX (Mid-Range)
- **GPU**: 1024-core NVIDIA Ampere GPU
- **CPU**: 8-core Arm Cortex-A78AE
- **RAM**: 8 GB / 16 GB LPDDR5
- **AI Performance**: 70 TOPS / 100 TOPS (INT8)
- **Power**: 10W - 25W
- **Price**: ~$599 - $799

#### Jetson AGX Orin (High-End)
- **GPU**: 2048-core NVIDIA Ampere GPU
- **CPU**: 12-core Arm Cortex-A78AE
- **RAM**: 32 GB / 64 GB LPDDR5
- **AI Performance**: 275 TOPS (INT8)
- **Power**: 15W - 60W
- **Price**: ~$1,999 - $2,499

### Jetson Accessories

- **Storage**: Minimum 128 GB microSD card (UHS-I, U3 or better) or NVMe SSD
- **Power Supply**: Official NVIDIA power adapter or compatible USB-C PD (for Orin Nano)
- **Cooling**: Heatsink and fan (included with dev kits, essential for sustained AI workloads)
- **Camera**: USB webcam or CSI camera module for vision tasks

## Optional Hardware

### ROS 2 Compatible Robots

For hands-on manipulation and navigation experiments:

- **TurtleBot4**: Affordable mobile robot platform (~$1,500 - $2,500)
- **Universal Robots UR3e/UR5e**: Collaborative robot arms (~$20,000 - $35,000)
- **Franka Emika Panda**: Research-grade manipulator (~$25,000)
- **Custom Builds**: DIY robots using off-the-shelf components

### Sensors

- **RGB-D Camera**: Intel RealSense D435/D455 (~$300 - $400)
- **LiDAR**: RPLidar A1/A2 or Velodyne VLP-16 (~$100 - $8,000)
- **IMU**: Inertial measurement units for odometry and localization
- **Force/Torque Sensors**: For contact-rich manipulation tasks

## Software Prerequisites

### Development Workstation Software

Install these on your Ubuntu 22.04 workstation:

- **ROS 2 Humble**: Primary robotics framework
- **Python 3.10+**: Primary programming language
- **Docker**: Containerization for reproducible environments
- **Git**: Version control
- **CUDA Toolkit**: For NVIDIA GPU users (11.8+ or 12.x)
- **cuDNN**: Deep learning GPU acceleration library
- **VSCode or PyCharm**: Recommended IDE

### Edge Platform Software

Pre-configured on NVIDIA Jetson:

- **JetPack 5.1+**: NVIDIA's SDK for Jetson (includes Ubuntu 20.04)
- **ROS 2 Foxy/Humble**: Can be installed on JetPack
- **TensorRT**: Optimized inference engine
- **DeepStream**: Video analytics framework
- **Docker**: For containerized deployments

### Python Libraries (Installed During Course)

- **PyTorch**: Deep learning framework
- **TensorFlow**: Alternative deep learning framework
- **OpenCV**: Computer vision library
- **NumPy/SciPy**: Numerical computing
- **Transformers**: Hugging Face library for foundation models
- **MoveIt 2**: Motion planning framework
- **Gymnasium**: Reinforcement learning environments
- **Isaac Sim**: NVIDIA's robotics simulation platform

## Verification Checklist

Before starting the course, verify:

- [ ] Ubuntu 22.04 LTS installed and updated
- [ ] NVIDIA GPU drivers installed (if applicable): `nvidia-smi` runs successfully
- [ ] CUDA installed (if applicable): `nvcc --version` shows version
- [ ] Python 3.10+ installed: `python3 --version`
- [ ] Git installed: `git --version`
- [ ] At least 100 GB free disk space
- [ ] Stable internet connection for downloading datasets and models
- [ ] NVIDIA Jetson platform (if pursuing edge deployment labs)

## Budget Considerations

### Minimal Setup (~$1,000 - $1,500)
- Existing workstation with Ubuntu 22.04
- NVIDIA RTX 3060 GPU upgrade
- Jetson Orin Nano Dev Kit
- USB webcam

### Recommended Setup (~$2,500 - $3,500)
- Workstation with RTX 4070
- Jetson Orin NX 16GB
- Intel RealSense D435
- Optional: TurtleBot4 Lite

### Professional Setup (~$5,000+)
- High-end workstation with RTX 4090
- Jetson AGX Orin
- Multiple sensors (RealSense, LiDAR)
- TurtleBot4 or robot arm

## Notes

- Simulation-only path available for students without physical hardware (using Gazebo, Isaac Sim)
- Cloud GPU alternatives (AWS, Google Colab) can supplement local compute for training
- Community forums and Discord available for hardware troubleshooting
- Used/refurbished equipment acceptable as long as it meets minimum specifications

For setup assistance, refer to the [Course Introduction](../intro.md) or join the course Discord community.
