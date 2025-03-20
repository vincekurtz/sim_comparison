A (somewhat) systematic comparison between MuJoCo, MJX, and Drake.

## Setup

Make a virtual environment and install deps (first time):
```
python -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
```

Install mujoco warp following `https://github.com/google-deepmind/mujoco_warp`

## Usage

Enter the virtual env
```
source .venv/bin/activate
```

Simulate a model with mujoco:
```
./mujoco_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene.xml
```

Simulate a model with mjx:
```
./mjx_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene_mjx.xml --num_envs=3
```

Simulate a model with mujoco warp:
```
./mjwarp_simulate_mjcf.py --mjcf=other_models/humanoid.xml --num_envs=3
```

Run a script with `--help` to see other options.

To run an automatic comparison and make plots, see `compare.py`

## Models

Not all Menagerie models are compatible with Drake. Here are some that work OK.

- `unitree_go2/scene.xml`
    - Starts with feet inside the ground, so Drake yeets it skyward.
- `unitree_go2/scene_mjx.xml`
- `universal_robots_ur5e/scene.xml`
- `universal_robots_ur10e/scene.xml`
    - MuJoCo dynamics are notably more jittery at dt=`0.005`s.
- `kuka_iiwa_14/scene.xml`

Other models that are compatable with all the sims are in the `other_models`
directory.
