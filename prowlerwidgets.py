from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSortFilterProxyModel, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QVBoxLayout, QHeaderView, QMenu, QDataWidgetMapper
from PyQt5.QtSql import QSqlTableModel
from delegates import DataMapperDelegate

from database import *
import sqlalchemy.orm


class AlchemyTableModel(QAbstractTableModel):
    """A table model that binds to a SQLAlchemy query object."""

    def __init__(self, parent=None):
        """Initialize the model."""
        super(AlchemyTableModel, self).__init__(parent=parent)

        self._sa_query = None
        self._column_names = []
        self._cache = []
        self._edit_cache = {}
        self._query_count = 0

    @property
    def query(self):
        """Return the SqlAlchemy query object used by the model."""
        return self._sa_query

    @query.setter
    def query(self, value):
        """Set the model's SqlAlchemy query and update the model."""
        assert(isinstance(value, sqlalchemy.orm.query.Query) or isinstance(value, None))
        self.beginResetModel()

        self._sa_query = value
        self._cache = []
        self._edit_cache = {}
        self._column_names = []
        self._query_count = 0

        if value is not None:
            self._column_names = [col['name'] for col in self._sa_query.column_descriptions]
            self._query_count = self._sa_query.count()
            self._cache.extend(self._sa_query[:300])

        self.endResetModel()

    def rowCount(self, parent_idx=QModelIndex()):
        """Return the number of rows currently loaded."""
        return len(self._cache)

    def totalRows(self):
        """Return the total number of rows in the query."""
        return self._query_count

    def columnCount(self, parent_idx=QModelIndex()):
        """Return the number of columns in the query."""
        return len(self._column_names)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return the name for a given column index."""
        if orientation == Qt.Horizontal \
                and role == Qt.DisplayRole \
                and self._column_names:
            return QVariant(self._column_names[section])
        else:
            return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        """Return the data for a given index."""
        if not index.isValid() \
                or role not in (Qt.DisplayRole, Qt.EditRole):
            return QVariant()

        row = index.row()
        col = index.column()

        try:
            return self._edit_cache[row][col]
        except KeyError:
            data = self._cache[row][col]
            return data if data is not None else ''

    def setData(self, index, value, role=Qt.EditRole):
        """Set a given index's data. Currently, edits are cached, but never get written to the database. dataChanged()
        is emitted, though, and subsequent calls to data() will return the edited values, until the model is reset.
        """
        row = index.row()
        col = index.column()

        if self._edit_cache.get(row):
            self._edit_cache[row][col] = value
        else:
            self._edit_cache[row] = {col: value}

        self.dataChanged.emit(index, index, [role])
        return True

    def flags(self, index):
        """Return the flags for a given index."""
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def fieldIndex(self, field):
        """Return the index of the column with the given name."""
        try:
            return self._column_names.index(field)
        except ValueError:
            return -1

    def canFetchMore(self, parent_idx):
        """Return True if more rows can be loaded from the query."""
        return len(self._cache) < self._query_count

    def fetchMore(self, parent_idx):
        """Loads another 100 rows from the query, if possible."""
        cached = len(self._cache)
        extend = min(cached + 100, self._query_count)

        self.beginInsertRows(QModelIndex(), cached, extend - 1)
        self._cache.extend(self._sa_query[cached:extend])
        self.endInsertRows()


class ProwlerSqlWidget(QWidget):
    """Base class for all SQL-dependant widgets. Populates a QSqlTableModel from a given source."""

    def __init__(self, parent=None):
        super(ProwlerSqlWidget, self).__init__(parent=parent)

        self.dbsession = Session()
        self.source = None

        # Set up the main model
        self.model = AlchemyTableModel(self)

    def set_source(self, source):
        """Calls generate_query() with the given source, and populates the model with the resulting query."""
        self.source = source
        self.model.query = self.generate_query(source)

    def generate_query(self, source):
        """Generate a query, based on source, used to populate the main table. Must include an 'id' column for
        selection behaviours to work.
        """

    def reload(self):
        """Repopulates the model."""
        self.set_source(self.source)


class ProwlerTableWidget(ProwlerSqlWidget):
    """Base class for all table-based SQL widgets. Takes care of selection management and context menu."""

    # Notifier for selection changes in the main table. Use the selected_ids property to access the selection.
    selection_changed = pyqtSignal()
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(ProwlerTableWidget, self).__init__(parent=parent)
        self.context_menu_actions = []

        # Set up the model and table
        sort_model = QSortFilterProxyModel(self)
        sort_model.setSourceModel(self.model)

        self.table = QTableView(self)
        self.table.setModel(sort_model)
        self.table.setSortingEnabled(True)

        # Extended row selection by default
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.selectionModel().selectionChanged.connect(self.selection_changed)

        # Editing disabled by default
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Enable custom context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.context_menu)

        # Set default header behaviour
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Add the table to a layout, add the layout to the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.table)
        self.setLayout(layout)

        # Connect the double_clicked signal
        self.table.doubleClicked.connect(self.double_clicked)

    @property
    def selected_ids(self):
        """Return the values in the 'id' column for each selected row."""
        id_idx_list = self.table.selectionModel().selectedRows(self.model.fieldIndex('id'))
        return [idx.data() for idx in id_idx_list]

    def get_selected_id(self):
        """Return the last id in self.selected_ids, or None."""
        return self.selected_ids[-1] if self.selected_ids else None

    def context_menu(self, point):
        """Generate a popup menu from the actions in self.context_menu_actions."""
        menu = QMenu(self)
        menu.addActions(self.context_menu_actions)

        point = self.table.viewport().mapToGlobal(point)
        menu.popup(point)

    def add_context_action(self, action):
        """Add an action to the context menu."""
        self.context_menu_actions.append(action)

    def add_context_actions(self, actions):
        """Adds all actions in an iterable."""
        self.context_menu_actions.extend(actions)

    def remove_context_action(self, action):
        """Remove an action from the context menu."""
        self.context_menu_actions.remove(action)

    def hasFocus(self):
        return self.table.hasFocus()


class ProductDetailsWidget(ProwlerSqlWidget):
    """Base class for the AmzProductDetailsWidget and VndProductDetailsWidget classes. Doesn't have it's own
    UI, but depends on certain UI elements (like self.titleLine) to be available.
    """

    def __init__(self, parent=None):
        super(ProductDetailsWidget, self).__init__(parent=parent)
        self.setupUi(self)

        # Populate the columns
        self.set_source(None)

        # Set up the data widget mapper
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.setItemDelegate(DataMapperDelegate(self))
        self.mapper.currentIndexChanged.connect(self.rewind_lines)

        self.mapper.addMapping(self.titleLine, self.model.fieldIndex('title'))
        self.mapper.addMapping(self.brandLine, self.model.fieldIndex('brand'))
        self.mapper.addMapping(self.modelLine, self.model.fieldIndex('model'))
        self.mapper.addMapping(self.skuLine, self.model.fieldIndex('sku'))
        self.mapper.addMapping(self.upcLine, self.model.fieldIndex('upc'))
        self.mapper.addMapping(self.priceBox, self.model.fieldIndex('price'))
        self.mapper.addMapping(self.quantityBox, self.model.fieldIndex('quantity'))

        self.model.modelReset.connect(self.mapper.toFirst)

    def rewind_lines(self):
        """Reset text lines to home position."""
        self.titleLine.home(False)
        self.brandLine.home(False)
        self.modelLine.home(False)


