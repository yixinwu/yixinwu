# Isaac Sim Standalone Python Example Guide

This guide provides practical examples of using NVIDIA Isaac Sim 4.5.0 in standalone Python mode within a Docker container.

**Last Updated:** 2026-02-12

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Example 1: Hello World (Falling Cube)](#example-1-hello-world-falling-cube)
4. [Example 2: Hello Robot (Jetbot Navigation)](#example-2-hello-robot-jetbot-navigation)
5. [Running Examples in Docker](#running-examples-in-docker)
6. [Understanding the Core API](#understanding-the-core-api)

---

## Overview

Isaac Sim provides three main workflows for Python scripting:

| Workflow | Description | Use Case |
|----------|-------------|----------|
| **Extension Workflow** | Python code runs inside the Isaac Sim GUI | Interactive development, visualization |
| **Standalone Python** | Python script runs independently without GUI | Headless simulation, batch processing, CI/CD |
| **Jupyter Notebook** | Interactive Python in a notebook environment | Research, experimentation |

This guide focuses on the **Standalone Python** workflow, which is ideal for Docker containers and headless servers.

---

## Prerequisites

### System Requirements
- NVIDIA GPU with compute capability 7.0+
- NVIDIA Driver 470.57.02 or later
- NVIDIA Container Toolkit installed
- Docker 20.10 or higher

### Docker Run Command

```bash
# Run Isaac Sim container with GPU support
docker run --gpus all -it --rm \
  -v $(pwd)/examples:/workspace/examples \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  bash
```

For headless mode (no GUI):
```bash
docker run --gpus all -it --rm \
  -v $(pwd)/examples:/workspace/examples \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  bash
```

---

## Example 1: Hello World (Falling Cube)

### Purpose

This example demonstrates the fundamental concepts of Isaac Sim:
- Creating a **World** and **Scene** using the Core API
- Adding a rigid body (cube) to the simulation
- Running physics simulation steps programmatically
- Querying object properties (position, velocity)

### Code: `hello_world.py`

```python
#!/usr/bin/env python3
"""
Isaac Sim Hello World - Falling Cube Example

This script demonstrates basic Isaac Sim functionality:
- Creating a World and Scene
- Adding a dynamic rigid body (cube)
- Running physics simulation
- Querying object state

Run with: python hello_world.py
"""

import os
import sys
import numpy as np

# Import Isaac Sim Core API
from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.utils.stage import create_new_stage

# For headless operation
os.environ["HEADLESS"] = "1"  # Set to "0" for GUI mode


def main():
    """Main function to run the falling cube simulation."""
    
    print("=" * 60)
    print("Isaac Sim Hello World - Falling Cube Example")
    print("=" * 60)
    
    # Create a new stage (empty scene)
    print("\n[1/5] Creating new stage...")
    create_new_stage()
    
    # Create the World (singleton that manages simulation)
    print("[2/5] Initializing World...")
    world = World(
        stage_units_in_meters=1.0,  # Use meters as unit
        physics_dt=1.0 / 60.0,     # Physics timestep (60 Hz)
        rendering_dt=1.0 / 60.0,   # Rendering timestep (60 Hz)
        device="cuda:0"             # Use GPU for computation
    )
    
    # Add a default ground plane
    print("[3/5] Adding ground plane...")
    world.scene.add_default_ground_plane(z_position=0.0)
    
    # Create a dynamic cube (rigid body that responds to physics)
    print("[4/5] Adding dynamic cube...")
    cube = world.scene.add(
        DynamicCuboid(
            prim_path="/World/Cube",
            name="falling_cube",
            position=np.array([0.0, 0.0, 5.0]),      # Start 5 meters high
            scale=np.array([0.5, 0.5, 0.5]),         # 0.5m x 0.5m x 0.5m
            color=np.array([1.0, 0.0, 0.0]),         # Red color (RGB)
            mass=1.0,                                # 1 kg mass
            linear_velocity=np.array([0.0, 0.0, 0.0]) # Initial velocity
        )
    )
    
    # Reset the world to initialize physics
    print("[5/5] Resetting world (initializing physics)...")
    world.reset()
    
    # Run simulation for 2 seconds (120 steps at 60Hz)
    print("\n--- Starting Simulation ---")
    num_steps = 120
    
    for step in range(num_steps):
        # Step the physics simulation
        world.step(render=True)
        
        # Get cube state every 30 steps (0.5 seconds)
        if step % 30 == 0:
            position = cube.get_world_pose()[0]  # [x, y, z]
            velocity = cube.get_linear_velocity()  # [vx, vy, vz]
            
            print(f"Step {step:3d} (t={step/60:.2f}s): "
                  f"Position=({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}), "
                  f"Velocity=({velocity[0]:.2f}, {velocity[1]:.2f}, {velocity[2]:.2f})")
    
    print("\n--- Simulation Complete ---")
    
    # Final state
    final_position = cube.get_world_pose()[0]
    final_velocity = cube.get_linear_velocity()
    print(f"\nFinal State:")
    print(f"  Position: ({final_position[0]:.4f}, {final_position[1]:.4f}, {final_position[2]:.4f})")
    print(f"  Velocity: ({final_velocity[0]:.4f}, {final_velocity[1]:.4f}, {final_velocity[2]:.4f})")
    
    # Cleanup
    print("\nCleaning up...")
    world.stop()
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

### Function Breakdown

| Component | Function |
|-----------|----------|
| `World` | Singleton class that manages the simulation loop, physics stepping, and scene management |
| `DynamicCuboid` | Creates a cube-shaped rigid body with physics properties (mass, velocity) |
| `add_default_ground_plane()` | Adds an infinite ground plane with collision detection |
| `world.reset()` | Initializes physics handles and resets all objects to initial state |
| `world.step()` | Advances the simulation by one timestep |
| `get_world_pose()` | Returns the object's position and orientation in world coordinates |
| `get_linear_velocity()` | Returns the object's linear velocity vector |

### Expected Output

```
============================================================
Isaac Sim Hello World - Falling Cube Example
============================================================

[1/5] Creating new stage...
[2/5] Initializing World...
[3/5] Adding ground plane...
[4/5] Adding dynamic cube...
[5/5] Resetting world (initializing physics)...

--- Starting Simulation ---
Step   0 (t=0.00s): Position=(0.00, 0.00, 5.00), Velocity=(0.00, 0.00, 0.00)
Step  30 (t=0.50s): Position=(0.00, 0.00, 3.77), Velocity=(0.00, 0.00, -4.90)
Step  60 (t=1.00s): Position=(0.00, 0.00, 0.10), Velocity=(0.00, 0.00, -9.81)
Step  90 (t=1.50s): Position=(0.00, 0.00, 0.25), Velocity=(0.00, 0.00, 2.45)
...

--- Simulation Complete ---

Final State:
  Position: (0.0000, 0.0000, 0.2500)
  Velocity: (0.0000, 0.0000, 0.0000)
```

> **Note:** The cube bounces slightly after hitting the ground due to the default restitution (bounciness) property.

---

## Example 2: Hello Robot (Jetbot Navigation)

### Purpose

This example demonstrates:
- Loading a robot from a USD file
- Using the Robot class to interface with articulations
- Controlling robot joints through the ArticulationController
- Applying velocity commands to a wheeled robot

### Code: `hello_robot.py`

```python
#!/usr/bin/env python3
"""
Isaac Sim Hello Robot - Jetbot Navigation Example

This script demonstrates robot simulation:
- Loading a robot from USD file
- Controlling robot articulations
- Applying velocity commands
- Running closed-loop simulation

Run with: python hello_robot.py
"""

import os
import numpy as np

from isaacsim.core.api import World
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.utils.stage import create_new_stage, add_reference_to_stage
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.types import ArticulationAction
import carb

# For headless operation
os.environ["HEADLESS"] = "1"


def main():
    """Main function to run the Jetbot navigation simulation."""
    
    print("=" * 60)
    print("Isaac Sim Hello Robot - Jetbot Navigation Example")
    print("=" * 60)
    
    # Create new stage
    print("\n[1/6] Creating new stage...")
    create_new_stage()
    
    # Initialize World
    print("[2/6] Initializing World...")
    world = World(
        stage_units_in_meters=1.0,
        physics_dt=1.0 / 60.0,
        rendering_dt=1.0 / 60.0,
        device="cuda:0"
    )
    
    # Add ground plane
    print("[3/6] Adding ground plane...")
    world.scene.add_default_ground_plane()
    
    # Load Jetbot robot
    print("[4/6] Loading Jetbot robot...")
    
    # Get path to Isaac assets
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac assets. Using default path.")
        assets_root_path = "/isaac-sim/assets"
    
    # Path to Jetbot USD file
    jetbot_usd_path = f"{assets_root_path}/Isaac/Robots/Jetbot/jetbot.usd"
    print(f"    Loading from: {jetbot_usd_path}")
    
    # Add robot reference to stage
    add_reference_to_stage(
        usd_path=jetbot_usd_path,
        prim_path="/World/Jetbot"
    )
    
    # Create Robot object to interface with the articulation
    jetbot = world.scene.add(
        Robot(prim_path="/World/Jetbot", name="my_jetbot")
    )
    
    # Reset world to initialize physics
    print("[5/6] Resetting world...")
    world.reset()
    
    # Get articulation controller for the robot
    print("[6/6] Getting articulation controller...")
    articulation_controller = jetbot.get_articulation_controller()
    
    # Print robot information
    print("\n--- Robot Information ---")
    print(f"Robot name: {jetbot.name}")
    print(f"Number of degrees of freedom (DOF): {jetbot.num_dof}")
    print(f"Joint names: {jetbot.dof_names}")
    print(f"Initial joint positions: {jetbot.get_joint_positions()}")
    
    # Run simulation with robot movement
    print("\n--- Starting Navigation Simulation ---")
    print("Commands: [1.0, 1.0] = Forward, [-1.0, -1.0] = Backward")
    print("          [2.0, 0.5] = Turn Right, [0.5, 2.0] = Turn Left")
    
    num_steps = 300  # 5 seconds at 60Hz
    
    for step in range(num_steps):
        # Change command every 60 steps (1 second)
        command_phase = (step // 60) % 4
        
        if command_phase == 0:
            # Move forward
            left_velocity = 5.0
            right_velocity = 5.0
            action_name = "FORWARD"
        elif command_phase == 1:
            # Turn right
            left_velocity = 5.0
            right_velocity = 2.0
            action_name = "TURN RIGHT"
        elif command_phase == 2:
            # Move backward
            left_velocity = -3.0
            right_velocity = -3.0
            action_name = "BACKWARD"
        else:
            # Turn left
            left_velocity = 2.0
            right_velocity = 5.0
            action_name = "TURN LEFT"
        
        # Apply velocity command to wheels
        # ArticulationAction takes joint_positions, joint_efforts, joint_velocities
        # None means "do not control this aspect"
        action = ArticulationAction(
            joint_positions=None,
            joint_efforts=None,
            joint_velocities=np.array([left_velocity, right_velocity])
        )
        articulation_controller.apply_action(action)
        
        # Step simulation
        world.step(render=True)
        
        # Print status every 60 steps
        if step % 60 == 0:
            position = jetbot.get_world_pose()[0]
            orientation = jetbot.get_world_pose()[1]  # Quaternion
            joint_vels = jetbot.get_joint_velocities()
            
            print(f"\nStep {step:3d} (t={step/60:.1f}s) - Action: {action_name}")
            print(f"  Position: ({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f})")
            print(f"  Wheel velocities: L={joint_vels[0]:.2f}, R={joint_vels[1]:.2f}")
    
    print("\n--- Simulation Complete ---")
    
    # Final position
    final_position = jetbot.get_world_pose()[0]
    print(f"\nFinal robot position: ({final_position[0]:.2f}, {final_position[1]:.2f}, {final_position[2]:.2f})")
    
    # Cleanup
    world.stop()
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

### Function Breakdown

| Component | Function |
|-----------|----------|
| `get_assets_root_path()` | Returns the path to Isaac Sim assets (robots, environments) |
| `add_reference_to_stage()` | References a USD file into the scene at a specific prim path |
| `Robot` | High-level class for interfacing with articulated robots |
| `get_articulation_controller()` | Returns a controller for managing joint positions/velocities/efforts |
| `ArticulationAction` | Data structure for specifying joint commands |
| `apply_action()` | Sends commands to the robot's joints |
| `get_joint_positions()` / `get_joint_velocities()` | Query current joint states |

### Expected Output

```
============================================================
Isaac Sim Hello Robot - Jetbot Navigation Example
============================================================

[1/6] Creating new stage...
[2/6] Initializing World...
[3/6] Adding ground plane...
[4/6] Loading Jetbot robot...
    Loading from: /isaac-sim/assets/Isaac/Robots/Jetbot/jetbot.usd
[5/6] Resetting world...
[6/6] Getting articulation controller...

--- Robot Information ---
Robot name: my_jetbot
Number of degrees of freedom (DOF): 2
Joint names: ['left_wheel_joint', 'right_wheel_joint']
Initial joint positions: [0. 0.]

--- Starting Navigation Simulation ---
Commands: [1.0, 1.0] = Forward, [-1.0, -1.0] = Backward
          [2.0, 0.5] = Turn Right, [0.5, 2.0] = Turn Left

Step   0 (t=0.0s) - Action: FORWARD
  Position: (0.00, 0.00, 0.03)
  Wheel velocities: L=0.00, R=0.00

Step  60 (t=1.0s) - Action: TURN RIGHT
  Position: (0.85, 0.00, 0.03)
  Wheel velocities: L=4.95, R=1.98
...

--- Simulation Complete ---

Final robot position: (0.45, -0.32, 0.03)

============================================================
Example completed successfully!
============================================================
```

---

## Running Examples in Docker

### Step 1: Create Example Directory

```bash
mkdir -p ~/isaac-sim-examples
cd ~/isaac-sim-examples
```

### Step 2: Save the Python Scripts

Save the example code above to:
- `~/isaac-sim-examples/hello_world.py`
- `~/isaac-sim-examples/hello_robot.py`

### Step 3: Run the Container

**Headless Mode (recommended for servers):**
```bash
docker run --gpus all -it --rm \
  -v ~/isaac-sim-examples:/workspace/examples \
  -e HEADLESS=1 \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  bash
```

**With GUI (requires X11 forwarding):**
```bash
xhost +local:docker

docker run --gpus all -it --rm \
  -v ~/isaac-sim-examples:/workspace/examples \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  bash
```

### Step 4: Run the Examples

Inside the container:

```bash
cd /workspace/examples

# Run Hello World (Falling Cube)
python hello_world.py

# Run Hello Robot (Jetbot Navigation)
python hello_robot.py
```

### Common Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `HEADLESS` | Run without GUI | `1` or `true` |
| `OMNI_KIT_ACCEPT_EULA` | Accept EULA automatically | `YES` |
| `CUDA_VISIBLE_DEVICES` | Select specific GPU | `0` |
| `NVIDIA_VISIBLE_DEVICES` | Docker GPU visibility | `all` |

---

## Understanding the Core API

### World Class

The `World` class is a **singleton** that manages the simulation:

```python
from isaacsim.core.api import World

# Create or get existing world
world = World(
    physics_dt=1.0/60.0,    # Physics timestep
    rendering_dt=1.0/60.0,  # Rendering timestep
    stage_units_in_meters=1.0
)

# Key methods
world.reset()           # Initialize physics, reset all objects
world.step(render=True) # Advance simulation by one step
world.stop()            # Stop simulation, cleanup
world.play()            # Start simulation loop
world.pause()           # Pause simulation
```

### Scene Management

```python
# Add objects to the scene
cube = world.scene.add(DynamicCuboid(...))
robot = world.scene.add(Robot(...))

# Retrieve objects by name
obj = world.scene.get_object("object_name")

# Access all objects
objects = world.scene.objects
```

### Physics Callbacks

```python
def my_callback(step_size):
    """Called every physics step."""
    print(f"Physics step with dt={step_size}")

# Add callback
world.add_physics_callback("my_callback_name", my_callback)

# Remove callback
world.remove_physics_callback("my_callback_name")
```

### Object Types

| Object Class | Description |
|--------------|-------------|
| `DynamicCuboid` | Rigid body cube with physics |
| `FixedCuboid` | Static cube (no physics) |
| `DynamicSphere` | Rigid body sphere |
| `DynamicCapsule` | Rigid body capsule |
| `DynamicCone` | Rigid body cone |
| `DynamicCylinder` | Rigid body cylinder |

---

## Troubleshooting

### Issue: "Could not find nucleus server"

**Solution:** The assets path might be different. Try:
```python
assets_root_path = "/isaac-sim/assets"  # Local path in container
# OR
assets_root_path = get_assets_root_path()  # Auto-detect
```

### Issue: "Physics not initialized"

**Solution:** Always call `world.reset()` after adding objects:
```python
world.scene.add(robot)
world.reset()  # Required!
```

### Issue: "No CUDA capable device"

**Solution:** Check GPU availability:
```bash
docker run --gpus all --rm nvcr.io/nvidia/isaac-sim:4.5.0 nvidia-smi
```

### Issue: Display/GLFW errors

**Solution:** Ensure `HEADLESS=1` is set:
```python
import os
os.environ["HEADLESS"] = "1"
```

---

## Further Resources

- [Isaac Sim Core API Documentation](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/core_api_tutorials/index.html)
- [Isaac Sim Python Scripting Guide](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/python_scripting/index.html)
- [Isaac Lab Documentation](https://isaac-sim.github.io/IsaacLab/)
- [NVIDIA NGC Isaac Sim](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/isaac-sim)

---

## Next Steps

1. **Add Sensors:** Try adding a camera or LiDAR to the robot
2. **Custom Environments:** Create your own USD scenes
3. **Reinforcement Learning:** Integrate with RL libraries (Stable-Baselines3, RL-Games)
4. **Sim-to-Real:** Export trained policies to real robots
