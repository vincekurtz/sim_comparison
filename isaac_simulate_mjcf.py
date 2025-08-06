#!/usr/bin/env python

# Need to run this before other isaac sim imports
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False}) # we can also run as headless.

# from isaacsim.core.api import World
# import time

# Load a USD simulation that we set up before with the GUI
# import isaacsim.core.utils.stage as stage_utils
# usd_path = "./other_models/bunny.usd"
# stage_utils.open_stage(usd_path)

# S

import time
from isaacsim.core.api import SimulationContext
from isaacsim.core.utils.prims import create_prim
from isaacsim.core.utils.stage import add_reference_to_stage, is_stage_loading

# This loads the model, but it's rotated 90 degrees
# asset_path = "./other_models/bunny.usd"
# robot = add_reference_to_stage(usd_path=asset_path, prim_path="/World")

import isaacsim.core.utils.stage as stage_utils
stage_utils.open_stage("./other_models/bunny.usd")

# Set y-is-up for the stage
from pxr import UsdGeom
stage = stage_utils.get_current_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)



simulation_context = SimulationContext()
create_prim("/DistantLight", "DistantLight")
# wait for things to load
simulation_app.update()
while is_stage_loading():
    simulation_app.update()

# need to initialize physics getting any articulation..etc
simulation_context.initialize_physics()
simulation_context.play()

for i in range(10000):
    simulation_context.step(render=True)
    time.sleep(0.01)

print("Finished simulating for 1000 steps")

simulation_context.stop()
simulation_app.close()





# world = World()
# world.scene.add_default_ground_plane()

# # status, import_config = omni.kit.commands.execute("MJCFCreateImportConfig")
# # import_config.set_fix_base(False)
# # import_config.set_make_default_prim(False)

# # mjcf_path="./other_models/one_bunny.xml"
# # omni.kit.commands.execute(
# #     "MJCFCreateAsset",
# #     mjcf_path=mjcf_path,
# #     import_config=import_config,
# #     prim_path="/bunny1",
# # )


# # Set the timestep
# time_step = 0.01
# world.set_simulation_dt(physics_dt=time_step, rendering_dt=0.01)

# #fancy_cube =  world.scene.add(
# #    DynamicCuboid(
# #        prim_path="/World/random_cube",
# #        name="fancy_cube",
# #        position=np.array([0, 0, 1.0]),
# #        scale=np.array([0.5015, 0.5015, 0.5015]),
# #        color=np.array([0, 0, 1.0]),
# #    ))
# # Resetting the world needs to be called before querying anything related to an articulation specifically.
# # Its recommended to always do a reset after adding your assets, for physics handles to be propagated properly
# world.reset()
# st = time.time()
# for i in range(int(10/time_step)):
#     print(f"Step {i}")

#     # we have control over stepping physics and rendering in this workflow
#     # things run in sync
#     world.step(render=True) # execute one physics step and one rendering step
# wall_time = time.time() - st

# print("Wall time:", wall_time)
# print("RTR:", (10/wall_time))

# #simulation_app.close() # close Isaac Sim
