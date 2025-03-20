#!/usr/bin/env python

##
#
# Simulate a user-provided model in mujoco xml format using mujoco warp (GPU).
#
##

import argparse
import mujoco
import numpy as np
import warp as wp
import mujoco_warp as mjwarp
import time


def run_simulation(mjcf, num_envs, sim_time, time_step):
    # Load the model
    model = mujoco.MjModel.from_xml_path(mjcf)
    model.opt.timestep = time_step
    model.opt.disableactuator = (
        1  # disable actuators so the robot falls freely
    )

    # MJX-style optimizations
    model.opt.iterations = 1
    model.opt.ls_iterations = 6
    model.opt.enableflags = mujoco.mjtDisableBit.mjDSBL_EULERDAMP
    model.opt.cone = mujoco.mjtCone.mjCONE_PYRAMIDAL

    data = mujoco.MjData(model)

    # Hacks from mujoco_warp/contrib/jax_unroll.py to avoid strange linear
    # algebra errors
    data.qvel = np.random.uniform(-0.01, 0.01, model.nv)
    mujoco.mj_step(model, data, 3)
    mujoco.mj_forward(model, data)

    print(
        f"Simulating a {model.nq} DoF model for {sim_time} seconds with dt={time_step}..."
    )

    # Convert to mjwarp
    warp_model = mjwarp.put_model(model)
    warp_data = mjwarp.put_data(model, data, nworld=num_envs)

    # JIT compile
    print("Jitting step function...")
    st = time.time()
    mjwarp.step(warp_model, warp_data)
    mjwarp.step(warp_model, warp_data)

    with wp.ScopedCapture() as capture:
        mjwarp.step(warp_model, warp_data)
    graph = capture.graph
    print(f"Done jitting in {time.time()-st} seconds.")
   
    # Run the sim
    t = 0.0
    start_time = time.time()
    while t < sim_time:
        wp.capture_launch(graph)
        wp.synchronize()
        t += time_step
    wall_time = time.time() - start_time

    # Calculate statistics
    real_time_rate = sim_time / wall_time * num_envs
    fps = (sim_time / time_step) / wall_time * num_envs

    print(f"Wall time: {wall_time:.4f} seconds")
    print(f"Real-time rate: {real_time_rate:.4f}x")
    print(f"FPS: {fps:.4f}")

    return wall_time, real_time_rate, fps


if __name__=="__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simulate an MJX model.")
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
        required=True,
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
    args = parser.parse_args()

    run_simulation(
        args.mjcf,
        args.num_envs,
        args.sim_time,
        args.time_step,
    )
