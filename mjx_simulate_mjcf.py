#!/usr/bin/env python

##
#
# Simulate a user-provided model in mujoco xml format using mjx (GPU).
#
##

import argparse
import mujoco
from mujoco import mjx
import jax
import time

# Set XLA flags for better performance
# (see https://mujoco.readthedocs.io/en/latest/mjx.html#gpu-performance)
import os
os.environ["XLA_FLAGS"] = "--xla_gpu_triton_gemm_any=true"

def run_simulation(mjcf, num_envs, sim_time, time_step):
    # Load the model
    model = mujoco.MjModel.from_xml_path(mjcf)
    model.opt.timestep = time_step
    model.opt.disableactuator = (
        1  # disable actuators so the robot falls freely
    )
    data = mujoco.MjData(model)
    
    print(
        f"Simulating a {model.nq} DoF model for {sim_time} seconds with dt={time_step}..."
    )

    # Convert to MJX
    mjx_model = mjx.put_model(model)
    mjx_data = mjx.put_data(model, data)

    # Create a batch of environments (all with the same initial state)
    rng = jax.random.key(0)
    rng = jax.random.split(rng, num_envs)
    batch = jax.vmap(
        lambda rng: mjx_data.replace(
            qpos=jax.random.uniform(
                rng, (mjx_model.nq), minval=mjx_data.qpos, maxval=mjx_data.qpos
            )
        )
    )(rng)

    # Define a jitted step function
    jit_step = jax.jit(jax.vmap(mjx.step, in_axes=(None, 0)), donate_argnums=(1,))

    # Do the jit compilation before we take timing stats
    print("Jitting step function...")
    st = time.time()
    batch = jit_step(mjx_model, batch)
    batch = jit_step(mjx_model, batch)  # for some reason the second call is not compiled
    print(f"Done jitting in {time.time() - st:.2f} seconds.")

    t = 0.0
    start_time = time.time()
    while t < sim_time:
        # Step the simulation
        batch = jit_step(mjx_model, batch)
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
