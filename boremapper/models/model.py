"""
Guideline for models in this project:

- __init__() - sets all properties to bring the instance into its *empty*, but already usable state.
  It should not change anything outside its scope. (TODO: ensure this can be always met)
- from_* - static methods that create an instance using some source data (file, default settings, etc.)
  E.g.
  DocumentModel.from_file()
  DocumentModel.from_defaults()
"""

from PySide6.QtCore import QObject


class Model(QObject):

    def __init__(self, parent: QObject|None):
        super().__init__(parent)


# TODO: use?
"""
class ListModel(Model):

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._items = []

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __setitem__(self, index, item):
        self._items[index] = item
        self.on_items_updated()

    def __delitem__(self, index):
        del self._items[index]
        self.on_items_updated()

    def append(self, item):
        self._items.append(item)
        self.on_items_updated()

    def extend(self, items: list|tuple):
        if items:
            self._items.extend(items)
            self.on_items_updated()

    def insert(self, index, item):
        self._items.insert(index, item)
        self.on_items_updated()

    # TODO: test
    def insert_many(self, values: dict):
        if values:
            # We need to go from the last index to the first one, so that we don't shift the index of subsequent items
            for index in sorted(values.keys(), reverse=True):
                self._items.insert(index, values[index])
            self.on_items_updated()

    def set_many(self, values: dict):
        if values:
            for index, value in values.items():
                self._items[index] = value
            self.on_items_updated()

    def del_many(self, indexes: list|tuple):
        if indexes:
            # We need to go from the last index to the first one, so that we don't shift the index of subsequent items
            for index in sorted(indexes, reverse=True):
                del self._items[index]
            self.on_items_updated()

    def on_items_updated(self):
        pass
"""


# TODO: use?
"""
class DictModel(Model):

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._items = []

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, item):
        self._items[key] = item
        self.on_items_updated()

    def __delitem__(self, key):
        del self._items[key]
        self.on_items_updated()

    def set_many(self, values: dict):
        if values:
            for key, value in values.items():
                self._items[key] = value
            self.on_items_updated()

    def del_many(self, keys: list|tuple):
        if keys:
            for key in keys:
                del self._items[key]
            self.on_items_updated()

    def on_items_updated(self):
        pass
"""
