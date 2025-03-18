from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

class VMSelectionModel(QAbstractListModel):
    # Define roles for id and vm_name
    ID_ROLE = Qt.UserRole + 1
    VM_NAME_ROLE = Qt.UserRole + 2

    def __init__(self, items=None):
        super().__init__()
        self._items = items or []

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._items):
            return None

        item = self._items[index.row()]

        if role == VMSelectionModel.ID_ROLE:
            return item.get('id', None)
        elif role == VMSelectionModel.VM_NAME_ROLE:
            return item.get('vm_name', '')
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def roleNames(self):
        return {
            VMSelectionModel.ID_ROLE: b'id',
            VMSelectionModel.VM_NAME_ROLE: b'vm_name',
        }

    def setData(self, data_list):
        self.beginResetModel()
        self._items = data_list
        self.endResetModel()
