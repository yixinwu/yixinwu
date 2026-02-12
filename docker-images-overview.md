# Docker Images Overview

This document provides an overview of the Docker images available in the current system, including their purpose and key features.

**Last Updated:** 2026-02-12

---

## Summary Table

| Image | Size | Primary Function |
|-------|------|------------------|
| `nvcr.io/nvidia/isaac-sim:4.5.0` | ~15 GB | Robotics simulation and synthetic data generation |
| `easylab/lab:isaac-lab2.0-desktop-v2` | ~17.6 GB | Robot learning framework (Isaac Lab 2.0) |
| `ccr.ccs.tencentyun.com/easylab/lab:isaac-lab2.0-desktop-v1` | ~17 GB | Tencent Cloud mirror of Isaac Lab 2.0 |
| `kjaebye/mujoco200:stable` | ~7.73 GB | Physics simulation engine |
| `isaac-ros:humble-custom` | ~6.4 GB | ROS 2 Humble with Isaac ROS integration |
| `cuda:11.8.0-runtime` | ~2.65 GB | NVIDIA CUDA runtime environment |

---

## Detailed Information

### 1. NVIDIA Isaac Sim 4.5.0

**Image:** `nvcr.io/nvidia/isaac-sim:4.5.0`

**Function:**
NVIDIA Omniverse™ Isaac Sim is a scalable robotics simulation application and synthetic data generation tool built on the NVIDIA Omniverse™ platform. It provides a high-fidelity simulation environment for developing and testing AI-powered robots.

**Key Features:**
- High-fidelity physics simulation
- Photorealistic rendering with ray tracing
- Synthetic data generation for training AI models
- ROS/ROS2 integration for robot development
- Support for Isaac Gym reinforcement learning workflows
- USD (Universal Scene Description) based asset pipeline

**Use Cases:**
- Robot perception algorithm development
- Motion planning and control testing
- Synthetic dataset generation for machine learning
- Multi-robot simulation scenarios

**Reference:** [NVIDIA Isaac Sim Documentation](https://docs.isaacsim.omniverse.nvidia.com/)

---

### 2. Isaac Lab 2.0 Desktop (v2)

**Image:** `easylab/lab:isaac-lab2.0-desktop-v2`

**Function:**
Isaac Lab is a unified and modular GPU-accelerated framework for robot learning built on top of NVIDIA Isaac Sim. It simplifies common workflows in robotics research, including reinforcement learning and imitation learning.

**Key Features:**
- Built on Isaac Sim 4.x
- GPU-accelerated training environments
- Integration with popular RL frameworks (RL-Games, Stable-Baselines3, etc.)
- Modular design for environment creation
- Support for various robot types (manipulators, legged robots, mobile robots)
- Built-in teleoperation and data collection tools

**Use Cases:**
- Reinforcement learning research for robotics
- Imitation learning and behavior cloning
- Robot skill learning
- Sim-to-real transfer experiments

**Reference:** [Isaac Lab Documentation](https://isaac-sim.github.io/IsaacLab/)

---

### 3. Isaac Lab 2.0 Desktop (Tencent Cloud Mirror)

**Image:** `ccr.ccs.tencentyun.com/easylab/lab:isaac-lab2.0-desktop-v1`

**Function:**
This is a Tencent Cloud Container Registry (CCR) mirror of the EasyLab Isaac Lab 2.0 image, optimized for users in China or those using Tencent Cloud infrastructure.

**Key Features:**
- Same functionality as the standard Isaac Lab 2.0 image
- Hosted on Tencent Cloud for faster access in China
- Includes VNC/desktop environment for GUI access
- Pre-configured Isaac Sim dependencies

**Use Cases:**
- Alternative to the main registry for better download speeds in Asia
- Tencent Cloud deployment scenarios

**Reference:** [Tencent Cloud Isaac Sim Deployment Guide](https://cloud.tencent.com/developer/article/2613158)

---

### 4. MuJoCo 2.0.0 (Stable)

**Image:** `kjaebye/mujoco200:stable`

**Function:**
MuJoCo (Multi-Joint dynamics with Contact) is a free and open-source physics engine designed for detailed, efficient rigid body simulations with contacts. It is widely used in robotics, biomechanics, graphics, and machine learning research.

**Key Features:**
- High-quality physics simulation with accurate contact dynamics
- Fast and stable simulation performance
- Support for complex multi-joint robotic systems
- XML-based model definition format (MJCF)
- Python bindings (mujoco-py) for easy integration
- Reinforcement learning benchmark environments

**Use Cases:**
- Robotics control research
- Reinforcement learning algorithm benchmarking
- Biomechanical simulations
- Locomotion research
- Model predictive control testing

**Reference:** [MuJoCo Official Website](https://mujoco.org/)

---

### 5. Isaac ROS (Humble Custom)

**Image:** `isaac-ros:humble-custom`

**Function:**
A custom-built Docker image combining NVIDIA Isaac ROS packages with ROS 2 Humble Hawksbill. Isaac ROS provides GPU-accelerated compute capabilities for ROS 2 applications, optimized for NVIDIA hardware.

**Key Features:**
- ROS 2 Humble Hawksbill LTS distribution
- NVIDIA Isaac ROS packages for AI perception
- CUDA-accelerated image processing
- AprilTag detection
- Stereo depth estimation
- Object detection and tracking
- Integration with Isaac Sim for sim-to-real workflows

**Use Cases:**
- AI-powered robot perception
- Autonomous navigation
- Visual SLAM
- Object manipulation
- Real-time computer vision for robotics

**Reference:** [NVIDIA Isaac ROS Documentation](https://nvidia-isaac-ros.github.io/)

---

### 6. CUDA 11.8.0 Runtime

**Image:** `cuda:11.8.0-runtime`

**Function:**
The NVIDIA CUDA runtime image provides the CUDA toolkit runtime libraries required to run CUDA applications. This specific version includes CUDA 11.8.0 runtime components.

**Key Features:**
- CUDA 11.8.0 runtime libraries
- NVIDIA driver compatibility
- Base layer for GPU-accelerated applications
- Includes necessary CUDA toolkit components (without compiler)
- Support for cuBLAS, cuDNN, cuFFT, and other CUDA libraries

**Use Cases:**
- Base image for GPU-accelerated applications
- Running pre-compiled CUDA binaries
- Deep learning inference deployment
- Scientific computing workloads

**Reference:** [NVIDIA CUDA Docker Hub](https://hub.docker.com/r/nvidia/cuda)

---

## System Requirements

Most of these images require:

- **NVIDIA GPU:** With compute capability 7.0+ (Turing or newer recommended)
- **NVIDIA Driver:** Version 470.57.02 or later
- **NVIDIA Container Toolkit:** Installed and configured
- **Docker:** Version 20.10 or higher
- **Memory:** At least 16 GB RAM (32 GB+ recommended)
- **Storage:** Each image requires significant disk space (see size column)

---

## Quick Reference: Running Containers

### Isaac Sim
```bash
docker run --gpus all -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  nvcr.io/nvidia/isaac-sim:4.5.0
```

### Isaac Lab
```bash
docker run --gpus all -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  easylab/lab:isaac-lab2.0-desktop-v2
```

### MuJoCo
```bash
docker run --gpus all -it --rm \
  kjaebye/mujoco200:stable
```

### Isaac ROS
```bash
docker run --gpus all -it --rm \
  isaac-ros:humble-custom
```

---

## Notes

- The `easylab/lab` images include desktop environments accessible via VNC
- All NVIDIA-based images require the NVIDIA Container Runtime
- Some images may require authentication to pull from private registries
- Consider using `docker system prune` to clean up unused images if disk space is limited
