from roboregress.robot.surfaces import Surface


class WoodSurface:
    pass


class Wood:
    def __init__(self) -> None:
        self.top = WoodSurface()
        self.right = WoodSurface()
        self.bottom = WoodSurface()
        self.left = WoodSurface()

    def get_surface(self, surface: Surface) -> WoodSurface:
        return {
            Surface.TOP: self.top,
            Surface.RIGHT: self.right,
            Surface.BOTTOM: self.bottom,
            Surface.LEFT: self.left,
        }[surface]
