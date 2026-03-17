"""
Guideline for models in this project:

- __init__() - sets all properties to bring the instance into its *empty*, but already usable state.
  It should not change anything outside its scope.
- from_* - static methods that create an instance using some source data (file, default settings, etc.)
  E.g.
  DocumentModel.from_file()
  DocumentModel.from_defaults()
"""

from PySide6.QtCore import QObject


class Model(QObject):

    def __init__(self, parent: QObject|None):
        super().__init__(parent)