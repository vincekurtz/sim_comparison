#!/usr/bin/env python

##
#
# Simulate a user-provided model in mujoco xml format using mujoco (CPU).
#
##

import argparse
import mujoco
import mujoco.viewer
import time


def run_simulation(mjcf, visualize, sim_time, time_step):
    # Load the model
    model = mujoco.MjModel.from_xml_path(mjcf)
    model.opt.timestep = time_step
    model.opt.disableactuator = (
        1  # disable actuators so the robot falls freely
    )
    data = mujoco.MjData(model)

    # Print some statistics
    print(
        f"Simulating a {model.nq} DoF model for {sim_time} seconds with dt={time_step}..."
    )

    if visualize:
        # Set up real-time-ish sim with the interactive visualizer
        start_time = time.time()

        times = []
        solver_iters = []
        with mujoco.viewer.launch_passive(model, data) as viewer:
            while data.time < sim_time and viewer.is_running():
                st = time.time()

                # Step the simulation
                mujoco.mj_step(model, data)

                # Log the number of solver iterations
                times.append(data.time)
                solver_iters.append(sum(data.solver_niter))

                # Update the viewer
                viewer.sync()

                # Try to run in roughly real-time
                step_time = time.time() - st
                if step_time < model.opt.timestep:
                    time.sleep(model.opt.timestep - step_time)

        wall_time = time.time() - start_time

    else:
        # Simulate headless and as fast as possible
        start_time = time.time()
        while data.time < sim_time:
            mujoco.mj_step(model, data)
        wall_time = time.time() - start_time

    # Calculate statistics
    real_time_rate = sim_time / wall_time
    fps = (sim_time / time_step) / wall_time

    print(f"Wall time: {wall_time:.4f} seconds")
    print(f"Real-time rate: {real_time_rate:.4f}x")
    print(f"FPS: {fps:.4f}")

    return wall_time, real_time_rate, fps


if __name__ == "__main__":
    # Get system arguments for what we should do
    parser = argparse.ArgumentParser(description="Simulate a mujoco model.")
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

    # Run the simulation
    wall_time, real_time_rate, fps = run_simulation(
        args.mjcf, args.visualize, args.sim_time, args.time_step
    )
