from PyQt5.QtWidgets import QVBoxLayout
from baseview import BaseView
from amazonview import AmzHistoryStackWidget


class AmzSingleProductView(BaseView):
    """Provides a detail view of a single product."""

    def __init__(self, parent=None):
        """Initialize the view."""
        super(BaseView, self).__init__(parent=parent)

        self._source = None

    def setup_ui(self):
        """Set up the UI elements of the view."""
        # Create a layout for the view
        self.setLayout(QVBoxLayout(self))

        # Create the chart widget
        self.history_stack = AmzHistoryStackWidget(self)

        self.layout().addWidget(self.history_stack)




    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value




