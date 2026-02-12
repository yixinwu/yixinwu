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
