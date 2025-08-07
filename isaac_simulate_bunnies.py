#!/usr/bin/env python

visualize = True

# Need to run this before other isaac sim imports
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": not visualize}) # we can also run as headless.

import time
from isaacsim.core.api import SimulationContext
import isaacsim.core.utils.stage as stage_utils

# Load a scene that we created with the GUI
stage = stage_utils.open_stage("./other_models/bunnies_rotated.usd")

# Set up the simulation
simulation_context = SimulationContext()
simulation_app.update()
while stage_utils.is_stage_loading():
    simulation_app.update()
simulation_context.initialize_physics()
simulation_context.play()

# Set the timestep
time_step = 0.001
simulation_context.set_simulation_dt(physics_dt=time_step, rendering_dt=time_step)

num_steps = int(10/time_step)  # run for 10 seconds
st = time.time()
for i in range(num_steps):
    simulation_context.step(render=visualize)

wall_time = time.time() - st
print("Wall time:", wall_time)
print("RTR:", (10/wall_time))

simulation_context.stop()
simulation_app.close()

