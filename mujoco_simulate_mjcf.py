#!/usr/bin/env python

##
#
# Simulate a user-provide model in mujoco xml format using mujoco.
#
##

import argparse
import mujoco
import mujoco.viewer
import time

# Get system arguments for what we should do
parser = argparse.ArgumentParser(description='Simulate a mujoco model.')
parser.add_argument(
    "--mjcf",
    type=str,
    help="Path to the xml file defining the model to simulate.",
    required=True,
)
parser.add_argument(
    "--visualize",
    action="store_true",
    help="Whether to visualize the simulation (try for real-time if true).",
    default=False,
    required=False,
)
parser.add_argument(
    "--sim_time",
    type=float,
    help="How long to simulate the model for (in seconds).",
    default=10.0,
    required=False,
)
parser.add_argument(
    "--time_step",
    type=float,
    help="Simulator step size dt (in seconds).",
    default=0.005,
    required=False,
)
args = parser.parse_args()

# Load the model
model = mujoco.MjModel.from_xml_path(args.mjcf)
model.opt.timestep = args.time_step
model.opt.disableactuator = 1   # disable actuators so the robot falls freely
data = mujoco.MjData(model)
    
# Print some statistics
print(f"Simulating a {model.nq} DoF model for {args.sim_time} seconds with dt={args.time_step}...")

if args.visualize:
    # Set up real-time-ish sim with the interactive visualizer
    start_time = time.time()

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while data.time < args.sim_time and viewer.is_running():
            st = time.time()

            # Step the simulation
            mujoco.mj_step(model, data)

            # Update the viewer
            viewer.sync()

            # Try to run in roguhly real-time
            step_time = time.time() - st
            if step_time < model.opt.timestep:
                time.sleep(model.opt.timestep - step_time)

    wall_time = time.time() - start_time

else:
    # Simulate headless and as fast as possible
    start_time = time.time()
    while data.time < args.sim_time:
        mujoco.mj_step(model, data)
    wall_time = time.time() - start_time

# Print some statistics
print(f"Wall time: {wall_time:.4f} seconds")
print(f"Real-time rate: {args.sim_time/wall_time:.4f}x")
print(f"FPS: {(args.sim_time/args.time_step)/wall_time:.4f}")
