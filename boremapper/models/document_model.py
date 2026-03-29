from xml.etree import ElementTree as ET
from PySide6.QtCore import Signal

from boremapper import const, exceptions
from boremapper.utils import xml_build_float, xml_find_mandatory, xml_parse_float, length_units
from boremapper.models.model import Model
from boremapper.models.bore_model import BoreModel, BorePointModel
from boremapper.models.wid_export_model import WidExportModel


class DocumentModel(Model):

    file_changed = Signal(str)

    def __init__(self, app: 'App'):
        # Note that the model's parent is initially the app, but the parent should be changed
        # to document window once the model is linked with it.
        super().__init__(app)

        self.app = app
        self.bore = BoreModel(self, app)
        self.wid_export = WidExportModel(self)
        self._file = None

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = file
        self.file_changed.emit(file)

    def to_xml(self) -> ET.Element:
        e_root = ET.Element('boremapper-document')
        e_root.set('version', const.DOCUMENT_XML_VERSION)

        e_bore = ET.SubElement(e_root, 'bore')

        e_points = ET.SubElement(e_bore, 'points')
        for point in self.bore.points:
            e_point = ET.SubElement(e_points, 'point')
            e_point.set('position', xml_build_float(point.position))
            e_point.set('custom-diameter', xml_build_float(point.custom_diameter))
            for p in const.BORE_PARTS:
                e_point.set(p + '-groove-width', xml_build_float(getattr(point, p + '_groove_width')))
                e_point.set(p + '-groove-height', xml_build_float(getattr(point, p + '_groove_height')))
                e_point.set(p + '-cutter-width', xml_build_float(getattr(point, p + '_cutter_width')))
                e_point.set(p + '-cutter-height', xml_build_float(getattr(point, p + '_cutter_height')))
                
        e_wid_export = ET.SubElement(e_root, 'wid-export')
        e_wid_export.set('length-type', self.wid_export.length_type)
        e_wid_export.set('bore-origin', xml_build_float(self.wid_export.bore_origin))

        return e_root

    def wid_incomplete_positions(self) -> list:
        incomplete_positions = []
        for point in self.bore.points:
            if point.diameter is None:
                incomplete_positions.append(point.position)
        return incomplete_positions

    def to_wid_bore_points(self, length_type: str, bore_origin: float):
        length_type_units = length_units(length_type)
        
        out_elements = []
        
        for point in self.bore.points:
            if point.diameter is not None:
                position = length_type_units.from_mm(bore_origin + point.position)
                diameter = length_type_units.from_mm(point.diameter)
                e_point = ET.Element('borePoint')
                e_position = ET.SubElement(e_point, 'borePosition')
                e_position.text = xml_build_float(position)
                e_diameter = ET.SubElement(e_point, 'boreDiameter')
                e_diameter.text = xml_build_float(diameter)
                out_elements.append(e_point)

        return out_elements

    @staticmethod
    def from_defaults(app: 'App') -> 'DocumentModel':
        doc = DocumentModel(app)
        doc.wid_export.length_type = app.settings.load('general', 'length_units')
        return doc

    @staticmethod
    def from_xml(app: 'App', e_root: ET.Element) -> 'DocumentModel':
        doc = DocumentModel(app)

        if e_root.tag != 'boremapper-document':
            raise exceptions.XmlException('Invalid root element. Most likely unsupported XML format.')

        e_bore = xml_find_mandatory(e_root, 'bore')

        # Load bore points

        e_points = xml_find_mandatory(e_bore, 'points')
        for e_point in e_points.iter('point'):
            point = BorePointModel(
                doc.bore.points,
                position=xml_parse_float(e_point.attrib['position']),
                custom_diameter=xml_parse_float(e_point.attrib['custom-diameter']) if 'custom-diameter' in e_point.attrib else None,
            )
            for p in const.BORE_PARTS:
                setattr(point, p + '_groove_width', xml_parse_float(e_point.attrib[p + '-groove-width']))
                setattr(point, p + '_groove_height', xml_parse_float(e_point.attrib[p + '-groove-height']))
                setattr(point, p + '_cutter_width',
                    xml_parse_float(e_point.attrib[p + '-cutter-width']) \
                    if p + '-cutter-width' in e_point.attrib else None)
                setattr(point, p + '_cutter_height',
                    xml_parse_float(e_point.attrib[p + '-cutter-height']) \
                    if p + '-cutter-height' in e_point.attrib else None)

            doc.bore.points.add(point)
            
        # Load WID export properties

        e_wid_export = xml_find_mandatory(e_root, 'wid-export')
        doc.wid_export.length_type = str(e_wid_export.attrib['length-type']).lower()
        doc.wid_export.bore_origin = xml_parse_float(e_wid_export.attrib['bore-origin'])

        return doc

    @staticmethod
    def from_file(app: 'App', file: str) -> 'DocumentModel':
        with open(file, 'r') as f:
            xml_data = f.read()
            e_root = ET.fromstring(xml_data)

        doc = DocumentModel.from_xml(app, e_root)
        doc.file = file
        return doc