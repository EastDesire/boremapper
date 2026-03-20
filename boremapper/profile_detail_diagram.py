from PySide6.QtWidgets import QWidget

from boremapper.bunch import Bunch
from boremapper.diagram import Diagram


class ProfileDetailDiagram(Diagram):

    margin_x = 8
    margin_y = 8

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent, app)
        # TODO: use?
        self.data = Bunch()
    
    def get_content_geometry(self):
        return (
            self.margin_x,
            self.margin_y,
            self.width() - 2 * self.margin_x,
            self.height() - 2 * self.margin_y,
        )

    # TODO: use?
    def set_data(self, **kwargs):
        self.data.__dict__.update(kwargs)