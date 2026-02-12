# Isaac Sim Quick Start Guide

## 📁 Files in This Directory

| File | Purpose |
|------|---------|
| `hello_world.py` | Basic physics simulation - falling cube |
| `hello_robot.py` | Robot control simulation - Jetbot navigation |
| `EXPERIMENT_RESULTS.md` | Detailed documentation of expected outputs |
| `QUICK_START.md` | This file - quick reference |

---

## 🚀 Quick Run (Copy & Paste)

### Terminal 1 - Start Container
```bash
cd /home/ubuntu2204/kimi_prj/isaac-sim-examples

docker run --gpus all --rm \
  -v /home/ubuntu2204/kimi_prj/isaac-sim-examples:/workspace/examples \
  -e HEADLESS=1 \
  -e ACCEPT_EULA=Y \
  -w /workspace/examples \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  bash
```

### Terminal 2 - Inside Container
```bash
# Setup environment
cd /isaac-sim && source setup_python_env.sh

# Run examples
cd /workspace/examples

# Example 1: Falling Cube (2 seconds simulation)
python hello_world.py

# Example 2: Jetbot Navigation (4 seconds simulation)
python hello_robot.py
```

---

## 📊 What Each Example Does

### hello_world.py
```
Spawns a red cube at 5m height
↓
Cube falls under gravity (-9.81 m/s²)
↓
Hits ground → bounces → settles
↓
Prints position & velocity every 0.5s
```

### hello_robot.py
```
Loads Jetbot robot from Isaac assets
↓
Executes movement sequence:
  • Forward (1s) → Turn Right (1s)
  → Backward (1s) → Turn Left (1s)
↓
Prints robot position & wheel velocities
```

---

## 🔑 Key Code Patterns

### 1. Create World (Always First)
```python
from isaacsim.core.api import World

world = World(
    physics_dt=1.0/60.0,     # 60 Hz physics
    rendering_dt=1.0/60.0,   # 60 Hz rendering
    device="cuda:0"          # GPU device
)
```

### 2. Add Ground Plane
```python
world.scene.add_default_ground_plane()
```

### 3. Add Object
```python
from isaacsim.core.api.objects import DynamicCuboid
import numpy as np

cube = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Cube",
        name="my_cube",
        position=np.array([0, 0, 5.0]),
        scale=np.array([0.5, 0.5, 0.5]),
        color=np.array([1.0, 0.0, 0.0])  # Red
    )
)
```

### 4. Reset & Run
```python
world.reset()  # Initialize physics

for i in range(120):  # 2 seconds at 60Hz
    world.step(render=True)
    
    # Get object state
    position = cube.get_world_pose()[0]
    velocity = cube.get_linear_velocity()
```

### 5. Add Robot
```python
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage

# Load robot from USD file
add_reference_to_stage(
    usd_path="/isaac-sim/assets/Isaac/Robots/Jetbot/jetbot.usd",
    prim_path="/World/Robot"
)

robot = world.scene.add(
    Robot(prim_path="/World/Robot", name="robot")
)
```

### 6. Control Robot
```python
from isaacsim.core.utils.types import ArticulationAction

# Get controller
controller = robot.get_articulation_controller()

# Apply wheel velocities
action = ArticulationAction(
    joint_velocities=np.array([5.0, 5.0])  # Left, Right
)
controller.apply_action(action)
```

---

## ⚙️ Common Parameters

### World Settings
| Parameter | Description | Default |
|-----------|-------------|---------|
| `physics_dt` | Physics timestep | 1/60 s |
| `rendering_dt` | Rendering timestep | 1/60 s |
| `stage_units_in_meters` | Unit scale | 1.0 |
| `device` | Compute device | "cuda:0" |

### Rigid Body Properties
| Property | Description | Example |
|----------|-------------|---------|
| `mass` | Mass in kg | 1.0 |
| `position` | [x, y, z] in meters | [0, 0, 5] |
| `scale` | [x, y, z] dimensions | [0.5, 0.5, 0.5] |
| `color` | RGB values [0-1] | [1, 0, 0] |
| `linear_velocity` | Initial velocity | [0, 0, 0] |

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Slow startup | Wait for extension download (~1-2 min first run) |
| "Could not find nucleus" | Use `/isaac-sim/assets/` path |
| No GUI | Set `HEADLESS=1` (expected) |
| ROS2 errors | Ignore (not needed for basic sim) |
| Out of memory | Reduce scene complexity |

---

## 📚 API Migration Notes

Old API → New API (Isaac Sim 4.5):
- `omni.isaac.core` → `isaacsim.core.api`
- `omni.isaac.wheeled_robots` → `isaacsim.robot.wheeled_robots`
- `omni.isaac.sensor` → `isaacsim.sensors.*`

---

## 🔗 Useful Paths in Container

| Path | Contents |
|------|----------|
| `/isaac-sim/` | Isaac Sim installation |
| `/isaac-sim/assets/Isaac/` | Robots, environments, sensors |
| `/isaac-sim/exts/` | Extensions |
| `/isaac-sim/python.sh` | Python launcher |
| `/workspace/examples/` | Your mounted scripts |

---

## 💡 Next Steps

1. **Add Camera Sensor:**
   ```python
   from isaacsim.sensors.camera import Camera
   camera = Camera(prim_path="/World/Camera")
   camera.initialize()
   image = camera.get_rgba()
   ```

2. **Import URDF Robot:**
   ```python
   from isaacsim.asset.importer.urdf import UrdfFileImporter
   importer = UrdfFileImporter()
   importer.import_file("/path/to/robot.urdf")
   ```

3. **Synthetic Data:**
   ```python
   import omni.replicator.core as rep
   rep.create.camera(position=(0, 0, 10))
   rep.trigger.on_frame(rt_subframes=16)
   ```

4. **Reinforcement Learning:**
   - Install Isaac Lab: `pip install isaaclab`
   - Use `isaaclab.envs` for RL environments

---

## 📞 Getting Help

- **Isaac Sim Docs:** https://docs.isaacsim.omniverse.nvidia.com/
- **Isaac Lab Docs:** https://isaac-sim.github.io/IsaacLab/
- **NGC Container:** https://catalog.ngc.nvidia.com/orgs/nvidia/containers/isaac-sim

---

**Happy Simulating! 🤖🎮**
