A (somewhat) systematic comparison between MuJoCo, MJX, and Drake.

## Setup

Make a virtual environment and install deps (first time):
```
python -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Enter the virtual env
```
source .venv/bin/activate
```

Simulate a model with mujoco:
```
./mujoco_simulate_mjcf.py --mjcf=mujoco_menagerie/unitree_go2/scene.xml
```
