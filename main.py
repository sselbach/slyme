import moderngl as mgl

import moderngl_window as mglw
from moderngl_window import geometry

import numpy as np
import yaml
from PIL import Image

from array import array
from random import random
from math import sin, cos, sqrt, pi

from utils import uniform_direction
import initializers


CONFIG_PATH = "profiles/thick_worms.yaml"

# load configuration file
with open(CONFIG_PATH) as config_file:
    CONFIG = yaml.load(config_file, yaml.Loader)


class SlimeMoldSimulation(mglw.WindowConfig):
    title = "He's Moldin'"
    resource_dir = "resources"
    gl_version = 4, 3
    window_size = CONFIG["width"], CONFIG["height"]
    aspect_ratio = CONFIG["width"] / CONFIG["height"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # initialize and bind the texture that will be the pheromone trail map
        # default dtype of textures is 'f1', i.e. uint8 normalized to the range between 0 and 1
        self.texture = self.ctx.texture((CONFIG["width"], CONFIG["height"]), 4)
        self.texture.filter = mgl.NEAREST, mgl.NEAREST
        self.texture.bind_to_image(0, read=True, write=True)
        self.texture.use(location=0)

        # geometry that the texture will be applied to
        self.quad_fs = geometry.quad_fs()

        # absolutely no idea what this does.. 
        self.texture_program = self.load_program("texture.glsl")

        # get generator for initial agent data by string from the config
        initializer = getattr(initializers, CONFIG["initializer"])

        # initialize agents
        # Agent: vec2 pos, vec2 dir --> 4 floats
        initial_agents = initializer(CONFIG)
        self.buffer_agent = self.ctx.buffer(array("f", initial_agents))
        self.buffer_agent.bind_to_storage_buffer(0)

        # the agent compute shader is dispatched per agent and handles agent movement
        self.shader_agent = self.load_compute_shader("slime_mold.glsl")

        try:
            # TODO: use dict.get to have default values for CONFIG
            self.shader_agent["width"] = CONFIG["width"]
            self.shader_agent["height"] = CONFIG["height"]
            self.shader_agent["n_agents"] = CONFIG["n_agents"]

            self.shader_agent["speed"] = CONFIG["speed"]
            self.shader_agent["sensorAngle"] = CONFIG["sensor_angle"]
            self.shader_agent["sensorSize"] = CONFIG["sensor_size"]
            self.shader_agent["sensorDistance"] = CONFIG["sensor_distance"]
            self.shader_agent["rotationAngle"] = CONFIG["rotation_angle"]
            self.shader_agent["randomNoiseStrength"] = CONFIG["random_noise_strength"]
            self.shader_agent["noiseBias"] = CONFIG["noise_bias"]
            self.shader_agent["n_species"] = CONFIG["n_species"]
            self.shader_agent["interspeciesAversion"] = CONFIG["interspecies_aversion"]
        
        except KeyError as e:
            print(e)

        
        # the postprocessing compute shader is dispatched per texel and handles diffusion and evaporation
        self.shader_postprocess = self.load_compute_shader("postprocess.glsl")

        try:
            # TODO: use dict.get to have default values for CONFIG
            self.shader_postprocess["width"] = CONFIG["width"]
            self.shader_postprocess["height"] = CONFIG["height"]

            self.shader_postprocess["diffusionStrength"] = CONFIG["diffusion_strength"]
            self.shader_postprocess["evaporateExponentially"] = CONFIG["evaporate_exponentially"]
            self.shader_postprocess["evaporationStrength"] = CONFIG["evaporation_strength"]
            self.shader_postprocess["minimalAmount"] = CONFIG["minimal_amount"]
        
        except KeyError as e:
            print(e)

        # set a flag no screenshot has been taken yet
        self.screenshot_done = False

    
    def update(self, time):
        """A single simulation step. Dispatches agent and postprocessing shader."""

        self.shader_agent.run(
            group_x=CONFIG["n_agents"] // 512 + 1,
            group_y=1,
            group_z=1
        )

        self.shader_postprocess.run(
            group_x=CONFIG["width"] // 16 + 1,
            group_y=CONFIG["height"] // 16 + 1,
            group_z=1
        )

    def render(self, time, frametime):
        self.ctx.clear(0.3, 0.3, 0.3)

        self.update(time)

        # check if it's time to take a screenshot
        if time > CONFIG.get("screenshot_after", float("inf")) and not self.screenshot_done:
            im = Image.frombuffer("RGBA", (CONFIG["width"], CONFIG["height"]), self.texture.read(), "raw")
            im.save("screenshot.png", format="png")

            self.screenshot_done = True
        
        # Render texture
        self.quad_fs.render(self.texture_program)


if __name__ == "__main__":
    mglw.run_window_config(SlimeMoldSimulation)