A rough throughput comparison between MuJoCo, Drake, MJX, Genesis, and MjWarp.

## Setup

Clone and pull in the mujoco menagerie as a submodule:
```
git clone --recurse-submodules https://github.com/vincekurtz/sim_comparison
cd sim_comparison
```

Make a virtual environment and install deps:
```
python -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
```

Install mujoco warp following the instructions
[here](https://github.com/google-deepmind/mujoco_warp).

## Usage

Enter the virtual env
```
source .venv/bin/activate
```

Run a simulation with something like
```
./[simulator]_simulate_mjcf.py --mjcf=path/to/model.xml
```
Where `[simulator]` is one of the available simulators. See below for details.

### MuJoCo

To simulate as fast as possible and report timing stats:
```
./mujoco_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene.xml
```

To visualize that simulation in (roughly) real-time:
```
./mujoco_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene.xml --visualize
```

Also useful for running an interactive simulation:
```
python -m mujoco.viewer --mjcf=path/to/model.xml
```

### Drake

To simulate as fast as possible and report timing stats:
```
./drake_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene.xml
```

To view that same simulation in meshcat:
```
./drake_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene.xml --visualize
```

### MJX

Simulate as fast as possible across several envs:
```
./mjx_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene_mjx.xml --num_envs=32
```

To visualize a sim with mjx physics:
```
python -m mujoco.mjx.viewer --mjcf=path/to/model.xml
```

### Genesis

Simulate as fast as possible across several envs:
```
./genesis_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene_mjx.xml --num_envs=32
```

Use the `--visualize` flag to show the sim and run in roughly real-time. 

### MuJoCo Warp

Simulate a model with mujoco warp:
```
./mjwarp_simulate_mjcf.py --mjcf=other_models/humanoid.xml --num_envs=32
```

To visualize a sim with mjwarp physics:
```
python -m mujoco_warp.viewer --mjcf=path/to/model.xml
```

## Models

Not all Menagerie models are compatible with Drake. Here are some that work OK:
- `unitree_go2/scene.xml`
- `unitree_go2/scene_mjx.xml`
- `universal_robots_ur5e/scene.xml`
- `universal_robots_ur10e/scene.xml`
- `kuka_iiwa_14/scene.xml`

Other models that are generally compatable across sims are in the `other_models`
directory.
