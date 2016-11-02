from PyQt5.QtWidgets import QWidget
from PyQt5.QtSql import QSqlQuery

from database import Session


# Helper function to convert SQLAlchemy queries into QSqlQuery objects
def saquery_to_qtquery(sa_query):
    statement = sa_query.statement.compile()
    qtquery = QSqlQuery()
    qtquery.prepare(str(statement))
    for name, value in statement.params.items():
        qtquery.bindValue(':' + name, value)
    return qtquery


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