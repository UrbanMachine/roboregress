import faulthandler
from time import sleep
from typing import List

import open3d as o3d
from open3d.visualization import gui, rendering


class Visualizer:
    def __init__(self) -> None:
        faulthandler.enable(all_threads=True)

        self.app: gui.Application = gui.Application.instance
        self.app.initialize()

        self.window: gui.PyWindow = self.app.create_window("Simulation Viewer")
        self._widget3d = gui.SceneWidget()
        self.scene = rendering.Open3DScene(self.window.renderer)

        self._widget3d.scene = self.scene
        self._widget3d.set_view_controls(gui.SceneWidget.Controls.ROTATE_CAMERA)
        self._widget3d.frame = gui.Rect(
            500, self.window.content_rect.y, 900, self.window.content_rect.height
        )

        self.default_material = rendering.MaterialRecord()
        self.default_material.point_size = 5 * self.window.scaling

        # Create widgets
        self._step_button = gui.Button("Step")
        self._step_button.set_on_clicked(self._on_step_clicked)
        self._pause_play_btn = gui.Button("Pause/Play")
        self._pause_play_btn.set_on_clicked(self._on_pause_play_clicked)
        self._timestamp_label = gui.Label("")  # Filled in .draw()

        em = self.window.theme.font_size
        self.gui_layout = gui.Vert(0, gui.Margins(0.5 * em, 0.5 * em, 0.5 * em, 0.5 * em))
        self.gui_layout.add_child(self._timestamp_label)
        self.gui_layout.add_child(self._step_button)
        self.gui_layout.add_child(self._pause_play_btn)

        self.window.set_on_layout(self._on_layout)
        self.window.add_child(self._widget3d)
        self.window.add_child(self.gui_layout)

        self._is_first_render = True
        self._step_clicked = False
        self._continuous_playing = False

    def _on_layout(self, layout_context: gui.LayoutContext) -> None:
        # The on_layout callback should set the frame (position + size) of every
        # child correctly. After the callback is done the window will layout
        # the grandchildren.
        r = self.window.content_rect
        self._widget3d.frame = r
        width = 17 * layout_context.theme.font_size
        height = min(
            r.height,
            self.gui_layout.calc_preferred_size(layout_context, gui.Widget.Constraints()).height,
        )
        self.gui_layout.frame = gui.Rect(r.get_right() - width, r.y, width, height)

    def draw(self, geometries: List[o3d.geometry.Geometry], time: float) -> None:
        self._timestamp_label.text = f"Timestamp: {int(round(time))}"
        self.scene.clear_geometry()

        for i, geometry in enumerate(geometries):
            self.scene.add_geometry(
                name=str(i),
                geometry=geometry,
                material=self.default_material,
                add_downsampled_copy_for_fast_rendering=False,
            )

        # Set up the camera on the first render
        if self._is_first_render:
            bbox = self._widget3d.scene.bounding_box
            self._widget3d.setup_camera(60.0, bbox, bbox.get_center())
            self._is_first_render = False

        self._step_clicked = False

        # Without this, `run_one_tick` will halt until mouse movement or keyboard press
        self.window.post_redraw()
        self.app.run_one_tick()
        while not self._step_clicked and self._continuous_playing:
            self.app.run_one_tick()
        sleep(0.03)

    def _on_step_clicked(self) -> None:
        self._step_clicked = True
        self._continuous_playing = True

    def _on_pause_play_clicked(self) -> None:
        self._continuous_playing = not self._continuous_playing
