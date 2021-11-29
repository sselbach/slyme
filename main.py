import moderngl as mgl

import moderngl_window as mglw
from moderngl_window import geometry

import numpy as np

from array import array
from random import random
from math import sin, cos, pi


WIDTH, HEIGHT = 1920, 1080
N_AGENTS = 100


def uniform_direction():
    angle = random() * 2 * pi

    return cos(angle), sin(angle)


class ComputeRenderToTexture(mglw.WindowConfig):
    title = "He's Moldin'"
    resource_dir = "resources"
    gl_version = 4, 3
    window_size = 1920, 1080

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.compute_shader = self.load_compute_shader("slime_mold.glsl")
        self.compute_shader["trailMap"] = 0

        try:
            self.compute_shader["width"] = WIDTH
            self.compute_shader["height"] = HEIGHT
            self.compute_shader["speed"] = 2
        
        except KeyError as e:
            print("Warning: Tried setting a uniform that does not exist or is not active within the shader.")
            print(e)

        self.texture_program = self.load_program("texture.glsl")
        self.quad_fs = geometry.quad_fs()

        # default dtype of textures is 'f1', i.e. uint8 normalized to the range between 0 and 1
        self.texture = self.ctx.texture((WIDTH, HEIGHT), 4)
        self.texture.filter = mgl.LINEAR, mgl.LINEAR

        # Agent: vec2 pos, vec2 dir
        self.buffer_agent = self.ctx.buffer(array("f", self._gen_initial_data(N_AGENTS)))

        
    def render(self, time, frame_time):
        self.ctx.clear(0.3, 0.3, 0.3)

        nx, ny, nz = N_AGENTS // 512 + 1, 1, 1

        # Automatically binds as a GL_R32F / r32f (read from the texture)
        self.texture.bind_to_image(0, read=True, write=True)

        # bind Agent buffer to the shader
        self.buffer_agent.bind_to_storage_buffer(0)

        self.compute_shader.run(nx, ny, nz)

        # Render texture
        self.texture.use(location=0)
        self.quad_fs.render(self.texture_program)

    def _gen_initial_data(self, n_agents):
        for _ in range(n_agents):
            # position
            yield WIDTH / 2
            yield HEIGHT / 2

            # direction
            x, y = uniform_direction()
            individual_speed = random()

            yield x * individual_speed
            yield y * individual_speed


if __name__ == "__main__":
    mglw.run_window_config(ComputeRenderToTexture)