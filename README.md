# Slyme

A Python and OpenGL compute shader implementation of a slime mold simulation as described in this paper: https://uwe-repository.worktribe.com/output/980579

Heavily inspired by Sebastian Lague's excellent YouTube video: https://www.youtube.com/watch?v=X-iSQQgOd1A

## Requirements

Python 3 is required to run this project (tested with Python 3.9). You will also need a GPU that supports OpenGL 4.3. Most recent GPUs should work, even integrated graphics.

## Installation

1. Clone the repository
2. Ideally create a new virtual Python environment and activate it
3. Run `$ pip install -r requirements.txt`
4. Done!

## Usage

To run a simulation, execute `main.py`, for example like this:

``` 
python main.py 
```

To change the parameter preset, you currently still need to edit `main.py`. Look for the line that reads
```python
CONFIG_PATH = "path/to/config.yaml"
```
and modify it accordingly. This will change in a later version such that no code editing is required.

To edit a preset, just modify the respective `.yaml` file in the `profiles` directory.