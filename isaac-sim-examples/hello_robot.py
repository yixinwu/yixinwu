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
    print("Commands: [5.0, 5.0] = Forward, [-3.0, -3.0] = Backward")
    print("          [5.0, 2.0] = Turn Right, [2.0, 5.0] = Turn Left")
    
    num_steps = 240  # 4 seconds at 60Hz
    
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
