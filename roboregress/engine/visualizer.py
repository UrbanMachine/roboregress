from typing import List

import open3d as o3d
import glfw


class Visualizer:
    def __init__(self):
        self._vis = o3d.visualization.VisualizerWithKeyCallback()
        self._vis.create_window("Simulation Viewer")
        self._vis.register_key_callback(
            glfw.KEY_SPACE, self._on_stop_rendering_key_pressed
        )
        self._is_first_render = True
        self._user_requested_continue = False

    def draw(self, geometries: List[o3d.geometry.Geometry]):
        self._vis.clear_geometries()
        for geometry in geometries:
            self._vis.add_geometry(geometry, reset_bounding_box=self._is_first_render)

        print("Press 'Space' to continue to the next time step")
        self._user_requested_continue = False
        self._is_first_render = False
        self._vis.update_renderer()

        while not self._user_requested_continue:
            self._vis.poll_events()

    def _on_stop_rendering_key_pressed(self, _):
        self._user_requested_continue = True

    def __del__(self):
        self._vis.close()
