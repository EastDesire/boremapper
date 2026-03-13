from PySide6.QtGui import QDoubleValidator, QValidator


class OptionalDoubleValidator(QDoubleValidator):

    def validate(self, input, pos):
        if input.strip() == '':
            return QValidator.State.Acceptable
        return super().validate(input, pos)