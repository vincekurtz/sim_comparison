#!/usr/bin/env python

##
#
# Compare the speeds of various simulation backends on a set of common examples.
#
##

from mujoco_simulate_mjcf import run_simulation as mujoco_run
from drake_simulate_mjcf import run_simulation as drake_run
from genesis_simulate_mjcf import run_simulation as genesis_run
from mjx_simulate_mjcf import run_simulation as mjx_run
import pandas as pd
import matplotlib.pyplot as plt

# Genesis initialization is weird and needs to be done only once        
import genesis as gs
gs.init(backend=gs.gpu, logging_level="warning")

# Define helper functions that run a simulation for 10 seconds and return real-time rate
def run_drake(mjcf, time_step):
    return drake_run(
        xml_file=mjcf,
        visualize=False,
        sim_time=10.0,
        hydroelastic=False,
        time_step=time_step,
    )[1]

def run_mujoco(mjcf, time_step):
    return mujoco_run(
        mjcf=mjcf,
        visualize=False,
        sim_time=10.0,
        time_step=time_step,
    )[1]

def run_mjx_32(mjcf, time_step):
    return mjx_run(
        mjcf=mjcf,
        num_envs=32,
        sim_time=10.0,
        time_step=time_step,
    )[1]

def run_mjx_4096(mjcf, time_step):
    return mjx_run(
        mjcf=mjcf,
        num_envs=4096,
        sim_time=10.0,
        time_step=time_step,
    )[1]

def run_genesis_32(mjcf, time_step):
    return genesis_run(
        mjcf=mjcf,
        num_envs=32,
        sim_time=10.0,
        time_step=time_step,
        visualize=False,
        init=False,
    )[1]

def run_genesis_4096(mjcf, time_step):
    return genesis_run(
        mjcf=mjcf,
        num_envs=4096,
        sim_time=10.0,
        time_step=time_step,
        visualize=False,
        init=False,
    )[1]

def collect_data(fname="simulation_results.csv"):
    """Collect data for a set of models and time steps, and save to a CSV file."""
    models = {
        "Unitree Go2": "mujoco_menagerie/unitree_go2/scene_mjx.xml",
        # "Unitree Go2 (mesh)": "mujoco_menagerie/unitree_go2/scene.xml",
        # "UR5e": "mujoco_menagerie/universal_robots_ur5e/scene.xml",
        # "UR10e": "mujoco_menagerie/universal_robots_ur10e/scene.xml",
        "Kuka IIWA": "mujoco_menagerie/kuka_iiwa_14/scene.xml",
        "Spheres in a box": "other_models/sphere_box.xml",
        "Bunny meshes in a box": "other_models/bunny_box.xml",
    }
    time_steps = [0.01, 0.005, 0.001]
    simulators = {
        "Drake": run_drake,
        "Mujoco": run_mujoco,
        "MJX (32 envs)": run_mjx_32,
        "Genesis (32 envs)": run_genesis_32,
        "MJX (4096 envs)": run_mjx_4096,
        "Genesis (4096 envs)": run_genesis_4096,
    }

    with open(fname, "w") as f:
        f.write("Simulator,Model,Model File,Time Step,Real-Time Rate\n")

    for model_name, model in models.items():
        for time_step in time_steps:
            for name, func in simulators.items():
                print(f"==> Running {name} on {model_name} with time step {time_step}...")

                if name == "MJX (32 envs)" or name == "MJX (4096 envs)":
                    if model_name == "Bunny meshes in a box":
                        print("Skipping bunny meshes for MJX.")
                        continue
                try:
                    rtr = func(model, time_step)
                    with open(fname, "a") as f:
                        f.write(f"{name},{model_name},{model},{time_step},{rtr}\n")
                except Exception as e:
                    print(e)

def plot_data(fname="simulation_results.csv"):
    """Plot the data collected from the simulations."""
    df = pd.read_csv(fname)

    # Get a list of unique parameters
    simulators = df["Simulator"].unique()
    models = df["Model"].unique()
    time_steps = df["Time Step"].unique()

    # Make subplots for each model and each timestep
    fig, axs = plt.subplots(len(models), len(time_steps), figsize=(10, 15), sharey=True)

    for model in models:
        for time_step in time_steps:
            for simulator in simulators:
                # Select matching data points
                mask = (df["Model"] == model) & (df["Time Step"] == time_step) & (df["Simulator"] == simulator)

                # Get the real-time rate and put it on a bar chart
                if mask.any():
                    # If there are multiple matching data points, take the first one
                    # (there should only be one)
                    rtr = df.loc[mask, "Real-Time Rate"].values[0]
                    axs[models.tolist().index(model), time_steps.tolist().index(time_step)].bar(simulator, rtr)

    # On the top row, set the title to the time step
    for i, time_step in enumerate(time_steps):
        axs[0, i].set_title(f"Time Step: {time_step}")

    # On the first column, set the title to the model name
    for i, model in enumerate(models):
        axs[i, 0].set_ylabel(model)
        axs[i, 0].set_yscale("log")

    plt.suptitle("Simulator Real-Time Rates")
    plt.tight_layout()
    plt.show()


if __name__=="__main__":
    # collect_data()
    plot_data()
