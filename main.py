import moderngl as mgl

import moderngl_window as mglw
from moderngl_window import geometry


WIDTH, HEIGHT = 1920, 1080

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
        
        except KeyError as e:
            print("Warning: Tried setting a uniform that does not exist or is not active within the shader.")
            print(e)

        self.texture_program = self.load_program("texture.glsl")
        self.quad_fs = geometry.quad_fs()

        # default dtype of textures is 'f1', i.e. uint8 normalized to the range between 0 and 1
        self.texture = self.ctx.texture((WIDTH, HEIGHT), 4)
        self.texture.filter = mgl.LINEAR, mgl.LINEAR
        
    def render(self, time, frame_time):
        self.ctx.clear(0.3, 0.3, 0.3)

        w, h = self.texture.size
        gw, gh = 16, 16
        nx, ny, nz = int(w / gw), int(h / gh), 1


        nx, ny, nz = 10, 1, 1

        try:
            self.compute_shader["time"] = time

        except KeyError as e:
            print(e)

        # Automatically binds as a GL_R32F / r32f (read from the texture)
        self.texture.bind_to_image(0, read=False, write=True)
        self.compute_shader.run(nx, ny, nz)

        # Render texture
        self.texture.use(location=0)
        self.quad_fs.render(self.texture_program)


if __name__ == "__main__":
    mglw.run_window_config(ComputeRenderToTexture)