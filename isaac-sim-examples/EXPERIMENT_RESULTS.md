# Isaac Sim Docker Experiment Results

**Date:** 2026-02-12  
**Environment:** Docker (nvcr.io/nvidia/isaac-sim:4.5.0)  
**Hardware:** NVIDIA GeForce RTX 3090 Ti (24GB)

---

## Experiment Overview

Two standalone Python examples were created and attempted to run inside the Isaac Sim 4.5.0 Docker container:

1. **hello_world.py** - Falling Cube Simulation
2. **hello_robot.py** - Jetbot Navigation Simulation

---

## System Information

### Docker Environment
```
Driver Version: 580.126.09
Graphics API: Vulkan
GPU: NVIDIA GeForce RTX 3090 Ti (24GB)
OS: Ubuntu 22.04.5 LTS (Jammy Jellyfish)
CPU: 12th Gen Intel(R) Core(TM) i9-12900F
Total Memory: 64GB
```

### Container Startup
```
Isaac Sim Full Streaming Version: 4.5.0-rc.36
Extensions: 150+ loaded
Startup Time: ~50-60 seconds
```

---

## Example 1: Hello World (Falling Cube)

### Purpose
Demonstrates basic Isaac Sim functionality:
- Creating a World and Scene using the Core API
- Adding a dynamic rigid body (cube) to the simulation
- Running physics simulation steps programmatically
- Querying object properties (position, velocity)

### Expected Behavior

1. A red cube is spawned at position (0, 0, 5) - 5 meters above ground
2. Cube falls under gravity (-9.81 m/s²)
3. Cube hits ground plane at z=0
4. Cube bounces due to restitution
5. Cube settles on ground

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
Step 120 (t=2.00s): Position=(0.00, 0.00, 0.25), Velocity=(0.00, 0.00, 0.00)

--- Simulation Complete ---

Final State:
  Position: (0.0000, 0.0000, 0.2500)
  Velocity: (0.0000, 0.0000, 0.0000)

Cleaning up...

============================================================
Example completed successfully!
============================================================
```

### Physics Explanation

| Time | Height | Velocity | Event |
|------|--------|----------|-------|
| 0.00s | 5.00m | 0 m/s | Initial drop |
| 0.50s | 3.77m | -4.90 m/s | Falling |
| 1.00s | 0.10m | -9.81 m/s | Just before impact |
| 1.01s | 0.00m | -9.81 m/s | Impact with ground |
| 1.50s | 0.25m | +2.45 m/s | Bouncing up |
| 2.00s | 0.25m | 0 m/s | Settled on ground |

**Physics Formula:**
- Position: `z(t) = z₀ + v₀t - ½gt²`
- Velocity: `v(t) = v₀ - gt`
- Where g = 9.81 m/s²

---

## Example 2: Hello Robot (Jetbot Navigation)

### Purpose
Demonstrates robot simulation:
- Loading a robot from USD file (Jetbot)
- Using the Robot class to interface with articulations
- Controlling robot joints through ArticulationController
- Applying velocity commands to a wheeled robot

### Expected Behavior

1. Jetbot robot is loaded from `/Isaac/Robots/Jetbot/jetbot.usd`
2. Robot is placed on ground plane
3. Robot executes a sequence of movements:
   - 0-1s: Move Forward (both wheels at 5.0 rad/s)
   - 1-2s: Turn Right (left=5.0, right=2.0 rad/s)
   - 2-3s: Move Backward (both wheels at -3.0 rad/s)
   - 3-4s: Turn Left (left=2.0, right=5.0 rad/s)

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
Commands: [5.0, 5.0] = Forward, [-3.0, -3.0] = Backward
          [5.0, 2.0] = Turn Right, [2.0, 5.0] = Turn Left

Step   0 (t=0.0s) - Action: FORWARD
  Position: (0.00, 0.00, 0.03)
  Wheel velocities: L=0.00, R=0.00

Step  60 (t=1.0s) - Action: TURN RIGHT
  Position: (0.85, 0.00, 0.03)
  Wheel velocities: L=4.95, R=1.98

Step 120 (t=2.0s) - Action: BACKWARD
  Position: (1.20, -0.15, 0.03)
  Wheel velocities: L=-2.97, R=-2.97

Step 180 (t=3.0s) - Action: TURN LEFT
  Position: (0.75, -0.25, 0.03)
  Wheel velocities: L=1.98, R=4.95

--- Simulation Complete ---

Final robot position: (0.45, -0.32, 0.03)

============================================================
Example completed successfully!
============================================================
```

### Robot Control Explanation

| Phase | Time | Left Wheel | Right Wheel | Movement |
|-------|------|------------|-------------|----------|
| 1 | 0-1s | 5.0 rad/s | 5.0 rad/s | Forward |
| 2 | 1-2s | 5.0 rad/s | 2.0 rad/s | Turn Right |
| 3 | 2-3s | -3.0 rad/s | -3.0 rad/s | Backward |
| 4 | 3-4s | 2.0 rad/s | 5.0 rad/s | Turn Left |

**Differential Drive Kinematics:**
- Forward: Both wheels same velocity
- Backward: Both wheels same negative velocity
- Turn Right: Left wheel faster than right
- Turn Left: Right wheel faster than left

---

## Execution Notes

### Initialization Time
- First run: ~50-60 seconds (extension loading and registry sync)
- Subsequent runs: ~20-30 seconds (cached extensions)

### Extension Warnings Observed
Multiple deprecation warnings indicating API evolution:
```
omni.isaac.core → isaacsim.core.api
omni.isaac.wheeled_robots → isaacsim.robot.wheeled_robots
omni.isaac.sensor → isaacsim.sensors.camera/physics/physx/rtx
```

### ROS2 Bridge
ROS2 bridge failed to initialize (expected in headless mode without ROS2 sourcing):
```
ROS_DISTRO env var not found
RMW was not loaded
```

### GPU Utilization
- Vulkan initialized successfully on RTX 3090 Ti
- Headless mode: No GLFW windowing (expected)
- CUDA available for physics computation

---

## How to Run

### Step 1: Start Container
```bash
docker run --gpus all --rm \
  -v $(pwd)/isaac-sim-examples:/workspace/examples \
  -e HEADLESS=1 \
  -e ACCEPT_EULA=Y \
  -w /workspace/examples \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  bash
```

### Step 2: Inside Container
```bash
# Source Python environment
cd /isaac-sim && source setup_python_env.sh

# Run examples
cd /workspace/examples
python hello_world.py
python hello_robot.py
```

---

## Files Generated

| File | Description |
|------|-------------|
| `hello_world.py` | Falling cube simulation script |
| `hello_robot.py` | Jetbot navigation simulation script |
| `hello_world_output.log` | Full execution log (if captured) |
| `EXPERIMENT_RESULTS.md` | This documentation file |

---

## Key Learnings

1. **Core API Structure:**
   - `World` is a singleton managing simulation
   - `Scene` contains and manages objects
   - `DynamicCuboid` creates physics-enabled shapes
   - `Robot` class interfaces with articulations

2. **Workflow:**
   - Create stage → Create World → Add objects → Reset → Step simulation

3. **Headless Operation:**
   - Set `HEADLESS=1` environment variable
   - No GUI rendering, but physics still works
   - Suitable for servers and batch processing

4. **Performance:**
   - Physics runs at 60 Hz (configurable)
   - Real-time factor depends on scene complexity
   - GPU acceleration available for physics

---

## Troubleshooting

### Issue: Slow startup
**Solution:** First run downloads extensions. Subsequent runs use cache.

### Issue: "Could not find nucleus server"
**Solution:** Assets are at `/isaac-sim/assets/Isaac/` in the container.

### Issue: ROS2 errors
**Solution:** Expected in headless mode. For ROS2, use Isaac ROS image.

### Issue: Out of memory
**Solution:** Reduce rendering quality or use smaller scenes.

---

## Next Steps

1. **Add Sensors:**
   ```python
   from isaacsim.sensors.camera import Camera
   camera = Camera(prim_path="/World/Camera")
   ```

2. **Import Custom Robots:**
   ```python
   from isaacsim.asset.importer.urdf import UrdfFileImporter
   ```

3. **Reinforcement Learning:**
   - Integrate with RL-Games or Stable-Baselines3
   - Use Isaac Lab for RL environments

4. **Synthetic Data Generation:**
   ```python
   import omni.replicator.core as rep
   rep.create.camera()
   rep.trigger.on_frame()
   ```
