from PySide6.QtCore import Signal

from boremapper import const
from boremapper.calculations import circle_radius_from_area, groove_crosssectional_area
from boremapper.models.model import Model


class BoreModel(Model):

    def __init__(self, parent: 'DocumentModel'):
        super().__init__(parent)

        self.corrections = BoreCorrectionsModel(self)
        self.points = BorePointsModel(self)

        # Bore points use corrections in their cached parameters, so changing the corrections must invalidate the cache
        self.corrections.updated.connect(self.points.invalidate_all)


class BoreCorrectionsModel(Model):

    updated = Signal()

    def __init__(self, parent: 'BoreModel'):
        super().__init__(parent)

        self.__dict__['_data'] = {}

        for p in const.BORE_PARTS:
            self.__dict__['_data'][p + '_groove_width'] = 0
            self.__dict__['_data'][p + '_groove_height'] = 0

    # TODO test
    def __getattr__(self, name):
        try:
            return self.__dict__['_data'][name]
        except KeyError:
            raise AttributeError(name)

    # TODO test
    def __setattr__(self, name, value):
        self.set_many({ name: value })

    def set_many(self, values: dict):
        if values:
            for name, value in values.items():
                try:
                    self.__dict__['_data'][name] = value
                except KeyError:
                    raise AttributeError(name)
            self.on_updated()

    def on_updated(self):
        self.updated.emit()


class BorePointsModel(Model):

    updated = Signal()

    def __init__(self, parent: 'BoreModel'):
        super().__init__(parent)
        self._points = []

    def __len__(self):
        return len(self._points)

    def __iter__(self):
        return iter(self._points)

    def __getitem__(self, index: int) -> 'BorePointModel':
        return self._points[index]

    def __setitem__(self, index: int, point: 'BorePointModel'):
        self._points[index] = point
        self.on_points_updated()

    def __delitem__(self, index):
        # TODO: also need destroy()?
        del self._points[index]
        self.on_points_updated()

    def _add_point(self, point: 'BorePointModel') -> int:
        insert_at = None
        for i, p in enumerate(self._points):
            if point.position < p.position:
                insert_at = i
                break
        if insert_at is None:
            insert_at = len(self._points)

        self._points.insert(insert_at, point)
        return insert_at

    # TODO: test
    def add(self, mixed: 'BorePointModel|list|tuple') -> list:
        """
        :param mixed: Bore point or multiple bore points
        :return: List of inserted indexes
        """
        points = mixed if type(mixed) in (list, tuple) else (mixed,)
        inserted_indexes = []

        # We need to insert the points sorted by position to ensure the indexes will be also inserted from the lowest to the highest.
        # Without sorting, some of the returned indexes might already contain different elements than we inserted.
        for point in sorted(points, key=lambda p: p.position):
            if self.find_position(point.position) is None:
                index = self._add_point(point)
                inserted_indexes.append(index)

        if inserted_indexes:
            self.on_points_updated()

        return inserted_indexes

    # TODO: test
    def delete(self, mixed: int|list|tuple):
        """
        :param mixed: Index or indexes to be deleted
        """
        indexes = mixed if type(mixed) in (list, tuple) else (mixed,)
        if not indexes:
            return

        # We need to go from the last index to the first one, so that we don't shift the index of subsequent items
        for index in sorted(indexes, reverse=True):
            # TODO: also need destroy()?
            del self._points[index]

        self.on_points_updated()

    def find_position(self, position: float) -> int|None:
        """
        Note that rounding to displayed decimal places is used during lookup.
        """
        for idx, point in enumerate(self._points):
            if round(point.position, const.LENGTH_DISPLAY_DECIMALS) == round(position, const.LENGTH_DISPLAY_DECIMALS):
                return idx
        return None

    def on_points_updated(self):
        self.updated.emit()

    def invalidate_all(self):
        for item in self._points:
            item.invalidate()


class BorePointModel(Model):
    """
    To make sure the derived parameters are always up-to-date when accessed from outside, the class automatically
    invalidates its cache upon changing its input parameters.
    However, when changing external parameters used in the calculations (e.g. corrections), it is necessary
    to explicitly invalidate the cache to let the class calculate fresh values.
    """

    def __init__(self, parent: 'BorePointsModel', position: float, **kwargs):
        super().__init__(parent)

        # Cache for derived parameters
        self.__dict__['_cache'] = {}

        # Input parameters
        self.__dict__['_data'] = {
            'position': position,
            'override_diameter': kwargs['override_diameter'] if 'override_diameter' in kwargs else None,
        }

        for p in const.BORE_PARTS:
            self.__dict__['_data'][p + '_groove_width'] = kwargs[p + '_groove_width'] if p + '_groove_width' in kwargs else None
            self.__dict__['_data'][p + '_groove_height'] = kwargs[p + '_groove_height'] if p + '_groove_height' in kwargs else None
            self.__dict__['_data'][p + '_cutter_width'] = kwargs[p + '_cutter_width'] if p + '_cutter_width' in kwargs else None
            self.__dict__['_data'][p + '_cutter_height'] = kwargs[p + '_cutter_height'] if p + '_cutter_height' in kwargs else None

    def __getattr__(self, name):
        if name in self.__dict__['_data']:
            return self.__dict__['_data'][name]
        return self._get_derived_param(name)

    def __setattr__(self, name, value):
        if not name in self.__dict__['_data']:
            raise AttributeError(name)
        self.invalidate() # Changing the data -> derived values are no longer valid
        self.__dict__['_data'][name] = value

    def invalidate(self):
        self.__dict__['_cache'].clear()

    def _get_derived_param(self, name):
        if not self.__dict__['_cache']:
            if not self._is_derived_param(name):
                raise AttributeError(name)
            self._build_cache()
        return self.__dict__['_cache'][name]

    def _is_derived_param(self, name):
        if name in (
            'area',
            'equivalent_diameter',
            'diameter',
            'warnings'
        ):
            return True

        if name.startswith(('bottom_', 'top_')):
            part, param = name.split('_', 1)
            if param in (
                'resolved_groove_width',
                'resolved_groove_height',
                'resolved_cutter_width',
                'resolved_cutter_height',
                'area'
            ):
                return True

        return False

    # TODO test
    def _build_cache(self):
        """
        Calculates derived parameters and stores them in cache.
        """

        warnings = []
        corr = self.parent().parent().corrections
        d = self.__dict__['_data']
        c = self.__dict__['_cache'] = {}

        for p in const.BORE_PARTS:
            # Resolve groove width and height
            c[p + '_resolved_groove_width'] = None if d[p + '_groove_width'] is None else d[p + '_groove_width'] + getattr(corr, p + '_groove_width')
            c[p + '_resolved_groove_height'] = None if d[p + '_groove_height'] is None else d[p + '_groove_height'] + getattr(corr, p + '_groove_height')

            # Resolve part's cutter width and height to be used in calculations
            c[p + '_resolved_cutter_width'] = d[p + '_cutter_width'] if d[p + '_cutter_width'] is not None else c[p + '_resolved_groove_width']
            c[p + '_resolved_cutter_height'] = d[p + '_cutter_height'] if d[p + '_cutter_height'] is not None else c[p + '_resolved_groove_height']

            # Calculate cross-sectional area of part's groove
            if None in (
                c[p + '_resolved_groove_width'],
                c[p + '_resolved_groove_height'],
                c[p + '_resolved_cutter_width'],
                c[p + '_resolved_cutter_height'],
            ):
                c[p + '_area'] = None
            else:
                try:
                    c[p + '_area'] = groove_crosssectional_area(
                        c[p + '_resolved_groove_width'],
                        c[p + '_resolved_groove_height'],
                        c[p + '_resolved_cutter_width'],
                        c[p + '_resolved_cutter_height'],
                    )
                except ValueError as e:
                    warnings.append({
                        'part': p,
                        'text': str(e),
                    })
                    c[p + '_area'] = None

        areas = list(c[p + '_area'] for p in const.BORE_PARTS)
        c['area'] = None if None in areas else sum(areas)
        c['equivalent_diameter'] = \
            None if c['area'] is None else \
            2 * circle_radius_from_area(c['area'])

        # Resolve final diameter at given point
        try:
            if d['override_diameter'] is not None:
                if d['override_diameter'] < 0:
                    raise ValueError('Invalid override diameter')
                c['diameter'] = d['override_diameter']
            elif c['equivalent_diameter'] is not None:
                c['diameter'] = c['equivalent_diameter']
            else:
                c['diameter'] = None
                
        except ValueError as e:
            warnings.append({'text': str(e)})
            c['diameter'] = None

        c['warnings'] = warnings

    @staticmethod
    def format_warning(warning: dict) -> str:
        return (
            (warning['part'].capitalize() + ' part: ' if 'part' in warning else '') +
            warning['text']
        )