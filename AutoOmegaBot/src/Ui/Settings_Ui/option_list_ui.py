from PyQt5 import QtWidgets, QtCore, QtGui

class OptionListUi(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232629, stop:1 #1a1c1e);
                color: #fff;
                border: none;
                border-top-left-radius: 18px;
                border-bottom-left-radius: 18px;
                font-size: 18px;
                padding-top: 30px;
                padding-bottom: 30px;
                border-right: 3px solid #2980b9;
            }
            QListWidget::item {
                padding: 18px 12px;
                margin: 8px 0;
                border-radius: 10px;
                border: none;
                outline: none;
                font-weight: 500;
                transition: background 0.2s;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2980b9, stop:1 #6dd5fa);
                color: #fff;
                font-weight: bold;
                border: none;
                outline: none;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setSpacing(2)