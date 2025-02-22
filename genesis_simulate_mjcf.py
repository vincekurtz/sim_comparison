#!/usr/bin/env python

##
#
# Simulate a user-provided model in mujoco xml format using Genesis (GPU).
#
##

import argparse
import genesis as gs
import time


def run_simulation(mjcf, visualize, num_envs, sim_time, time_step):
    # Simulator setup
    gs.init(backend=gs.gpu, logging_level="warning")
    scene = gs.Scene(
        show_viewer=visualize, sim_options=gs.options.SimOptions(dt=time_step)
    )

    # Add the model
    robot = scene.add_entity(gs.morphs.MJCF(file=mjcf))

    # Make sure the first step is compiled (tbh not sure if Genesis jitting
    # works this way or not, but just to be safe...)
    print("Jitting step function...")
    st = time.time()
    scene.build(n_envs=num_envs, env_spacing=(1.0, 1.0))
    scene.step()
    print(f"Done jitting in {time.time() - st:.2f} seconds.")

    # Run the sm
    t = 0.0
    start_time = time.time()
    while t < sim_time:
        # Step the simulation
        scene.step()
        t += time_step
    wall_time = time.time() - start_time

    # Calculate statistics
    real_time_rate = sim_time / wall_time * num_envs
    fps = (sim_time / time_step) / wall_time * num_envs

    print(f"Wall time: {wall_time:.4f} seconds")
    print(f"Real-time rate: {real_time_rate:.4f}x")
    print(f"FPS: {fps:.4f}")

    return wall_time, real_time_rate, fps


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simulate a Genesis model.")
    parser.add_argument(
        "--mjcf",
        type=str,
        help="Path to the MJCF file.",
        required=True,
    )
    parser.add_argument(
        "--num_envs",
        type=int,
        help="Number of environments to simulate in parallel.",
        default=1,
    )
    parser.add_argument(
        "--sim_time",
        type=float,
        help="Simulation time in seconds.",
        default=10.0,
    )
    parser.add_argument(
        "--time_step",
        type=float,
        help="Simulation time step in seconds.",
        default=0.005,
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Whether to visualize the simulation.",
        default=False,
    )
    args = parser.parse_args()

    run_simulation(
        mjcf=args.mjcf,
        visualize=args.visualize,
        num_envs=args.num_envs,
        sim_time=args.sim_time,
        time_step=args.time_step,
    )
