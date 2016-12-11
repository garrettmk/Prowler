from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QItemDelegate, QStyledItemDelegate, QComboBox, QLineEdit, QDoubleSpinBox, QAbstractSpinBox
from PyQt5.QtGui import QValidator, QDoubleValidator


class ReadOnlyDelegate(QStyledItemDelegate):

    def __init__(self, readonly=True, parent=None):
        super(QStyledItemDelegate, self).__init__(parent=parent)
        self._readonly = True

    @property
    def readonly(self):
        return self._readonly

    @readonly.setter
    def readonly(self, value):
        self._readonly = bool(value)

    def createEditor(self, parent, options, index):
        if self._readonly:
            return None
        else:
            return super(ReadOnlyDelegate, self).createEditor(parent, options, index)


class CategoryDelegate(QStyledItemDelegate):

    def __init__(self, categories=[], parent=None):
        super(CategoryDelegate, self).__init__(parent)
        self._categories = categories

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, values):
        try:
            self._categories = list(values)
        except TypeError:
            raise TypeError('Expected iterable, recieved %s' % str(type(values)))

    def createEditor(self, parent, options, index):
        box = QComboBox(parent)

        for item in self._categories:
            box.addItem(item)

        return box

    def setEditorData(self, editor, index):
        data = index.data(Qt.EditRole)
        try:
            idx = self._categories.index(data)
        except ValueError:
            idx = 0
        else:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)


class BooleanDelegate(QStyledItemDelegate):

    def __init__(self, terms=['False', 'True'], parent=None):
        super(BooleanDelegate, self).__init__(parent)
        self._terms = terms

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, values):
        try:
            self._terms = list(values)
        except TypeError:
            raise TypeError('Expected iterable, received %s' % str(type(values)))

    def displayText(self, value, locale):
        return self.terms[bool(value)]

    def createEditor(self, parent, options, index):
        box = QComboBox(parent)
        box.addItem(self.terms[0])
        box.addItem(self.terms[1])
        return box

    def setEditorData(self, editor, index):
        data = str(index.data(Qt.EditRole))
        if data.isdigit():
            editor.setCurrentIndex(int(data))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex(), Qt.EditRole)


class ValidatorDelegate(QStyledItemDelegate):

    def __init__(self, validator=None, parent=None):
        super(ValidatorDelegate, self).__init__(parent)
        self._validator = validator

    @property
    def validator(self):
        return self._validator

    @validator.setter
    def validator(self, value):
        if isinstance(value, QValidator):
            self._validator = value
        else:
            raise TypeError('%s is not an instance of QValidator.' % type(value))

    def createEditor(self, parent, options, index):
        editor = QLineEdit(parent)
        editor.setValidator(self._validator)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value)


class NumericDelegate(QStyledItemDelegate):

    def __init__(self, precision=2, readonly=False, parent=None):
        super(NumericDelegate, self).__init__(parent)
        self._precision = precision
        self._readonly = readonly
        # self._validator = QDoubleValidator(0-float('inf'), float('inf'), precision, parent)

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        self._precision = int(value)

    @property
    def readonly(self):
        return self._readonly

    @readonly.setter
    def readonly(self, value):
        self._readonly = bool(value)

    def displayText(self, value, locale):
        try:
            fstr = '{:,.%sf}' % self._precision
            return fstr.format(float(value))
        except (ValueError, TypeError):
            return ''

    def createEditor(self, parent, options, index):
        if self.readonly:
            return None

        editor = QDoubleSpinBox(parent)
        editor.setDecimals(self._precision)
        editor.setRange(-float('inf'), +float('inf'))
        return editor

    def setEditorData(self, editor, index):
        try:
            value = float(index.data(Qt.EditRole))
        except ValueError:
            value = 0

        editor.setValue(value)

    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value)


class IntegerDelegate(NumericDelegate):

    def __init__(self, parent=None):
        super(IntegerDelegate, self).__init__(precision=0, parent=parent)


class CurrencyDelegate(NumericDelegate):

    def __init__(self, prefix='$', readonly=False, parent=None):
        super(CurrencyDelegate, self).__init__(precision=2, readonly=readonly, parent=parent)
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    def displayText(self, value, locale):
        return self._prefix + super(CurrencyDelegate, self).displayText(value, locale)


class PercentDelegate(NumericDelegate):

    def __init__(self, precision=2, parent=None):
        super(PercentDelegate, self).__init__(precision=precision, parent=parent)

    def displayText(self, value, locale):
        return '%' + super(PercentDelegate, self).displayText(100 * value, locale)


class DataMapperDelegate(QItemDelegate):

    def setEditorData(self, widget, index):
        data = index.data()

        if isinstance(widget, QAbstractSpinBox):
            if not data:
                widget.setValue(0)
            else:
                widget.setValue(data)
        elif isinstance(widget, QLineEdit):
            widget.setText(str(data))


class UTCtoLocalDelegate(QStyledItemDelegate):
    """Delegate for converting naive time strings from UTC to local time."""

    def __init__(self, parent=None):
        super(UTCtoLocalDelegate, self).__init__(parent=parent)

    def displayText(self, value, locale):
        try:
            dt = QDateTime.fromString(value, Qt.ISODate)
            dt.setTimeSpec(Qt.UTC)
            return dt.toLocalTime().toString(Qt.TextDate)
        except TypeError:
            pass

        try:
            dt = QDateTime.fromTime_t(value.timestamp())
            dt.setTimeSpec(Qt.UTC)
            return dt.toLocalTime().toString(Qt.TextDate)
        except AttributeError:
            raise ValueError('Expected string or datetime, got %s' % type(value))

