from PyQt5.QtWidgets import QWidget

from database import Session


class AbstractView(QWidget):

    def __init__(self, parent=None):
        super(AbstractView, self).__init__(parent=parent)

        self.tool_buttons = []
        self._dbsession = None

    @property
    def dbsession(self):
        if self._dbsession is None:
            self._dbsession = Session()
        return self._dbsession