from PySide6.QtCore import QObject, QSettings, Signal

from boremapper import const
from boremapper.exceptions import NotCachedException
from boremapper.models.model import Model


class SettingsModel(Model):

    changed = Signal(list)

    def __init__(self, parent: QObject, definitions: dict = None):
        super().__init__(parent)

        self._qsettings = QSettings(const.ORGANIZATION_HANDLE, const.APP_HANDLE)
        self._defs = {}
        self._cache = {}

        if definitions is not None:
            self.define(definitions)

    def define(self, definitions: dict):
        """
        Defines details about settings, like a default value and value type.
        """
        for group, defs in definitions.items():
            if not group in self._defs:
                self._defs[group] = {}
            for param, d in defs.items():
                value_type, default_value = d
                self._defs[group][param] = (value_type, default_value)

    def load(self, group: str, param: str):
        """
        Get a value of given setting.
        """
        def cached():
            return self._get_cache(group, param)
        
        try:
            return cached()
        
        except NotCachedException:
            qs = self._qsettings
            qs.beginGroup(group)
            param_def = \
                self._defs[group][param] if (group in self._defs and param in self._defs[group]) else \
                None
            value = qs.value(
                param,
                defaultValue={} if param_def is None else param_def[1],
                type=None if param_def is None else param_def[0],
            )
            qs.endGroup()
            
            self._set_cache(group, param, value)
            return cached()

    def write(self, data: dict):
        """
        Write one or more groups of settings.
        :param data: Settings in format: { group: { parameter: value, ...}, ...}
        """
        qs = self._qsettings
        changes = []
        
        for group, params in data.items():
            if params:
                qs.beginGroup(group)
                for param, value in params.items():
                    self._clear_cache(group, param)
                    qs.setValue(param, value)
                    changes.append(SettingsModelChange(group, param, value))
                qs.endGroup()
                
        if changes:
            self.changed.emit(changes)

    def toggle(self, group: str, param: str):
        """
        Toggle given boolean setting
        """
        self.write({ group: { param: not self.load(group, param) } })

    def _get_cache(self, group: str, param: str):
        try:
            ret = self._cache[group][param]
            return ret
        except KeyError:
            raise NotCachedException
        
    def _set_cache(self, group: str, param: str, value):
        if group not in self._cache:
            self._cache[group] = {}
        self._cache[group][param] = value

    def _clear_cache(self, group: str, param: str):
        try:
            del self._cache[group][param]
        except KeyError:
            pass


class SettingsModelChange:
    
    def __init__(self, group: str, param: str, value):
        self.group = group
        self.param = param
        self.value = value