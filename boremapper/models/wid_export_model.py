from PySide6.QtCore import Signal

from boremapper.models.model import Model


class WidExportModel(Model):

    changed = Signal()

    def __init__(self, parent: 'DocumentModel'):
        super().__init__(parent)

        self.__dict__['_data'] = {
            'length_type': 'mm',
            'bore_origin': 0,
        }

    def __getattr__(self, name):
        try:
            return self.__dict__['_data'][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self.set_many({ name: value })

    def set_many(self, values: dict):
        if values:
            for name, value in values.items():
                if name not in self.__dict__['_data']:
                    raise AttributeError(name)
                self.__dict__['_data'][name] = value
            self.on_change()

    def on_change(self):
        self.changed.emit()