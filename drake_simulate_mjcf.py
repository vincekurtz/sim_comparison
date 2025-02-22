#!/usr/bin/env python

##
#
# Simulate a user-provided model in mujoco xml format using drake.
#
##

import argparse
from pydrake.geometry import StartMeshcat, SceneGraphConfig
from pydrake.multibody.parsing import Parser
from pydrake.multibody.plant import AddMultibodyPlantSceneGraph
from pydrake.systems.analysis import Simulator
from pydrake.systems.framework import DiagramBuilder
from pydrake.visualization import AddDefaultVisualization
import time


def run_simulation(xml_file, visualize, sim_time, hydroelastic, time_step):
    # Start meshcat
    meshcat = StartMeshcat()

    # Set up the system diagram
    builder = DiagramBuilder()

    plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step)
    parser = Parser(plant, scene_graph)
    parser.AddModels(xml_file)
    plant.Finalize()

    if hydroelastic:
        sg_config = SceneGraphConfig()
        sg_config.default_proximity_properties.compliance_type = "compliant"
        sg_config.default_proximity_properties.slab_thickness = 0.1
        scene_graph.set_config(sg_config)

    if visualize:
        AddDefaultVisualization(builder=builder, meshcat=meshcat)

    diagram = builder.Build()

    # Initialize the simulator
    simulator = Simulator(diagram)
    if visualize:
        simulator.set_target_realtime_rate(1.0)
        simulator.set_publish_every_time_step(True)
    simulator.Initialize()

    # Wait for meshcat to be ready
    print(f"Simulating a {plant.num_positions()} DoF model for {sim_time} seconds with dt={time_step}...")
    if visualize:
        input("Press [ENTER] to continue...")

    # Run the simulation
    meshcat.StartRecording()
    start_time = time.time()
    simulator.AdvanceTo(sim_time)
    wall_time = time.time() - start_time
    meshcat.StopRecording()
    meshcat.PublishRecording()

    # Print some statistics
    rtr = sim_time / wall_time
    fps = (sim_time/time_step)/wall_time
    print(f"Wall time: {wall_time:.4f} seconds")
    print(f"Real-time rate: {rtr:.4f}x")
    print(f"FPS: {fps:.4f}")

    # Wait for meshcat to publish the recording
    if visualize:
        input("Press [ENTER] to exit...")

    return wall_time, rtr, fps

if __name__=="__main__":
    # Get system arguments for what we should do
    parser = argparse.ArgumentParser(description="Simulate a drake model.")
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
        "--hydroelastic",
        action="store_true",
        help="Whether to use hydroelastic contact (default is false).",
        default=False,
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
    run_simulation(
        args.mjcf,
        args.visualize,
        args.sim_time,
        args.hydroelastic,
        args.time_step,
    )
