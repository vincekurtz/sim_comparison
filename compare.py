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
import importlib
import numpy as np

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
    importlib.reload(gs)
    return genesis_run(
        mjcf=mjcf,
        num_envs=32,
        sim_time=10.0,
        time_step=time_step,
        visualize=False,
    )[1]

def run_genesis_4096(mjcf, time_step):
    importlib.reload(gs)
    return genesis_run(
        mjcf=mjcf,
        num_envs=4096,
        sim_time=10.0,
        time_step=time_step,
        visualize=False,
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
        "Complicated scene": "other_models/complicated_scene.xml",
    }
    time_steps = [0.01, 0.001]
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

                # MJX breaks on bunny meshes
                if name == "MJX (32 envs)" or name == "MJX (4096 envs)":
                    if model_name == "Bunny meshes in a box":
                        print("Skipping bunny meshes for MJX.")
                        continue

                # For the complicated scene we only run dt=0.001, and skip MJX
                if model_name == "Complicated scene":
                    if time_step == 0.01:
                        print("Skipping dt=0.01 for complicated scene.")
                        continue
                    if name == "MJX (32 envs)" or name == "MJX (4096 envs)":
                        print("Skipping MJX for complicated scene.")
                        continue

                rtr = func(model, time_step)
                with open(fname, "a") as f:
                    f.write(f"{name},{model_name},{model},{time_step},{rtr}\n")

def plot_data(fname="simulation_results.csv"):
    """Plot the data collected from the simulations."""
    df = pd.read_csv(fname)

    simulators = ["MJX", "Genesis", "MjWarp"]
    num_envs = [256, 512, 1024, 2048, 4096, 8192]

    # Make subplots for each simulator
    fig, ax = plt.subplots(1, len(simulators), sharey=True)
    ax[0].set_yscale("log")

    for sim in simulators:
        for ne in num_envs:
            # Select matching data points
            mask = (df["Simulator"] == sim) & (df["Envs"] == ne)
        
            # Get the realtime rate
            if mask.any():
                rtr = df.loc[mask, "Real-Time Rate"].values[0]
            else:
                rtr = 0.0

            # Make the bar chart
            ax[simulators.index(sim)].bar(num_envs.index(ne), rtr)

    # Set the x-ticks and labels
    for i, sim in enumerate(simulators):
        ax[i].set_xticks(range(len(num_envs)))
        ax[i].set_xticklabels(num_envs)
        ax[i].set_title(sim)
        ax[i].set_xlabel("Number of Envs")
        ax[i].tick_params(axis="x", rotation=45)
        ax[i].yaxis.grid(True, which="both", color="gray", alpha=0.5)

    plt.suptitle("Humanoid Ragdoll")
    ax[0].set_ylabel("Real-Time Rate")

    plt.tight_layout()
    plt.show()        

    ## Get a list of unique parameters
    #simulators = df["Simulator"].unique()
    #models = df["Model"].unique()
    #time_steps = df["Time Step"].unique()

    ## Make subplots for each model and each timestep, + a column for images
    #fig, axs = plt.subplots(len(models), len(time_steps)+1, figsize=(15, 20), width_ratios=[0.5, 1, 1])

    ## First axes are images of the models
    #images = {
    #    "Unitree Go2": "img/go2.png",
    #    "Kuka IIWA": "img/kuka.png",
    #    "Spheres in a box": "img/sphere_box.png",
    #    "Bunny meshes in a box": "img/bunny_box.png",
    #    "Complicated scene": "img/complicated_scene.png",
    #}
    #for (i, model) in enumerate(models):
    #    img = plt.imread(images[model])
    #    axs[i, 0].imshow(img)
    #    axs[i, 0].set_ylabel(model)
    #    axs[i, 0].set_xticks([])
    #    axs[i, 0].set_yticks([])

    ## Read data from the CSV file and plot it
    #for model in models:
    #    for time_step in time_steps:
    #        for simulator in simulators:
    #            # Select matching data points
    #            mask = (df["Model"] == model) & (df["Time Step"] == time_step) & (df["Simulator"] == simulator)

    #            # Get the real-time rate and put it on a bar chart
    #            if mask.any():
    #                rtr = df.loc[mask, "Real-Time Rate"].values[0]
    #            else:
    #                # Missing data (OOM error, or otherwise failed simulation)
    #                rtr = 0.0
    #            
    #            axs[models.tolist().index(model), time_steps.tolist().index(time_step)+1].bar(simulator, rtr)

    ## On the top row, set the title to the time step
    #for i, time_step in enumerate(time_steps):
    #    axs[0, i+1].set_title(f"Time Step: {time_step}")

    ## Iterate over the axes that are not in the first column
    #for i in range(len(models)):
    #    for j in range(1, len(time_steps)+1):
    #        axs[i,j].tick_params(axis="x", rotation=65)
    #        axs[i,j].set_yscale("log")
    #        axs[i,j].yaxis.grid(True, which="both", color="gray", alpha=0.5)
    #        axs[i,j].set_ylabel("Real-Time Rate")

    #        if i == 4:
    #            # Tighter limits on last axis
    #            axs[i,j].set_ylim((1e-1, 1e1))
    #        else:
    #            axs[i,j].set_ylim((1e0, 1e5))

    #plt.tight_layout()
    #plt.show()


if __name__=="__main__":
    # collect_data()
    plot_data()
