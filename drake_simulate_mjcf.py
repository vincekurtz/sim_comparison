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

# Start meshcat
meshcat = StartMeshcat()

# Set up the system diagram
builder = DiagramBuilder()

plant, scene_graph = AddMultibodyPlantSceneGraph(builder, args.time_step)
parser = Parser(plant, scene_graph)
parser.AddModels(args.mjcf)
plant.Finalize()

if args.hydroelastic:
    sg_config = SceneGraphConfig()
    sg_config.default_proximity_properties.compliance_type = "compliant"
    sg_config.default_proximity_properties.slab_thickness = 0.1
    scene_graph.set_config(sg_config)

if args.visualize:
    AddDefaultVisualization(builder=builder, meshcat=meshcat)

diagram = builder.Build()

# Initialize the simulator
simulator = Simulator(diagram)
if args.visualize:
    simulator.set_target_realtime_rate(1.0)
    simulator.set_publish_every_time_step(True)
simulator.Initialize()

# Wait for meshcat to be ready
print(f"Simulating a {plant.num_positions()} DoF model for {args.sim_time} seconds with dt={args.time_step}...")
if args.visualize:
    input("Press [ENTER] to continue...")

# Run the simulation
meshcat.StartRecording()
start_time = time.time()
simulator.AdvanceTo(args.sim_time)
wall_time = time.time() - start_time
meshcat.StopRecording()
meshcat.PublishRecording()

# Print some statistics
print(f"Wall time: {wall_time:.4f} seconds")
print(f"Real-time rate: {args.sim_time/wall_time:.4f}x")
print(f"FPS: {(args.sim_time/args.time_step)/wall_time:.4f}")

# Wait for meshcat to publish the recording
if args.visualize:
    input("Press [ENTER] to exit...")
