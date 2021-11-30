import moderngl as mgl

import moderngl_window as mglw
from moderngl_window import geometry

import numpy as np

from array import array
from random import random
from math import sin, cos, sqrt, pi


WIDTH, HEIGHT = 1400, 1400
N_AGENTS = 500_000

# agent parameters
SPEED = 1.0
SENSOR_ANGLE = pi / 8.0
SENSOR_SIZE = 3
SENSOR_DISTANCE = 15.0
ROTATION_ANGLE = pi / 6.0
RANDOM_NOISE_STRENGTH = 0.0

# postprocess parameters
DIFFUSION_STRENGTH = 0.4
EVAPORATE_EXPONENTIALLY = True
EVAPORATION_STRENGTH = 0.1
MINIMAL_SENSIBLE_AMOUNT = 0


def uniform_direction():
    angle = random() * 2 * pi

    return cos(angle), sin(angle)


class SlimeMoldSimulation(mglw.WindowConfig):
    title = "He's Moldin'"
    resource_dir = "resources"
    gl_version = 4, 3
    window_size = WIDTH, HEIGHT
    aspect_ratio = WIDTH / HEIGHT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.texture_program = self.load_program("texture.glsl")
        self.quad_fs = geometry.quad_fs()

        # default dtype of textures is 'f1', i.e. uint8 normalized to the range between 0 and 1
        # TODO: currently, texture gets initialized with (0, 0, 0, 0) everywhere --> figure out how to initialize 
        #       the alpha channel as 1. This can also be used to constrain the simulation to certain shapes.
        self.texture = self.ctx.texture((WIDTH, HEIGHT), 4)
        self.texture.filter = mgl.NEAREST, mgl.NEAREST
        self.texture.bind_to_image(0, read=True, write=True)

        # Agent: vec2 pos, vec2 dir
        self.buffer_agent = self.ctx.buffer(array("f", self._gen_initial_data2(N_AGENTS)))
        self.buffer_agent.bind_to_storage_buffer(0)


        self.shader_agent = self.load_compute_shader("slime_mold.glsl")

        try:
            self.shader_agent["width"] = WIDTH
            self.shader_agent["height"] = HEIGHT
            self.shader_agent["n_agents"] = N_AGENTS

            self.shader_agent["speed"] = SPEED
            self.shader_agent["sensorAngle"] = SENSOR_ANGLE
            self.shader_agent["sensorSize"] = SENSOR_SIZE
            self.shader_agent["sensorDistance"] = SENSOR_DISTANCE
            self.shader_agent["rotationAngle"] = ROTATION_ANGLE
            self.shader_agent["randomNoiseStrength"] = RANDOM_NOISE_STRENGTH
        
        except KeyError as e:
            print(e)

        
        self.shader_postprocess = self.load_compute_shader("postprocess.glsl")

        try:
            self.shader_postprocess["width"] = WIDTH
            self.shader_postprocess["height"] = HEIGHT

            self.shader_postprocess["diffusionStrength"] = DIFFUSION_STRENGTH
            self.shader_postprocess["evaporateExponentially"] = EVAPORATE_EXPONENTIALLY
            self.shader_postprocess["evaporationStrength"] = EVAPORATION_STRENGTH
            self.shader_postprocess["minimalSensibleAmount"] = MINIMAL_SENSIBLE_AMOUNT
        
        except KeyError as e:
            print(e)

        
    def update(self, time):
        # agent compute shader
        self.shader_agent.run(
            group_x=N_AGENTS // 512 + 1,
            group_y=1,
            group_z=1
        )

        # postprocessing compute shader
        self.shader_postprocess.run(
            group_x=WIDTH // 16 + 1,
            group_y=HEIGHT // 16 + 1,
            group_z=1
        )

    def render(self, time, frametime):
        self.ctx.clear(0.3, 0.3, 0.3)

        self.update(time)

        # Render texture
        self.texture.use(location=0)
        self.quad_fs.render(self.texture_program)

    def _gen_initial_data(self, n_agents):
        for _ in range(n_agents):
            # position
            yield WIDTH / 2
            yield HEIGHT / 2

            # direction
            dx, dy = uniform_direction()
            #individual_speed = random()
            individual_speed = 1

            yield dx * individual_speed
            yield dy * individual_speed

    def _gen_initial_data2(self, n_agents):
        for _ in range(n_agents):
            # position: uniformly within a centered disk of radius R
            R = 512

            r = R * sqrt(random())
            theta = random() * 2 * pi

            x =  WIDTH / 2 + r * cos(theta)
            y =  HEIGHT / 2 + r * sin(theta)

            yield x
            yield y

            # direction: facing towards the center
            dx = WIDTH / 2 - x
            dy = HEIGHT / 2 - y
            length = sqrt(dx ** 2 + dy ** 2)

            yield dx / length
            yield dy / length


if __name__ == "__main__":
    mglw.run_window_config(SlimeMoldSimulation)