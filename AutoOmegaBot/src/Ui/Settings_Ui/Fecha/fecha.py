from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime, timedelta
from Utiles.assets import CALENDAR_SVG
from Utiles.utils import validate_date_format

class DateInputWithCalendar(QtWidgets.QWidget):
    dateChanged = QtCore.pyqtSignal(str)  # CAMBIADO: Emite MM/DD/YYYY directamente
    
    def __init__(self, placeholder, default_date, parent=None):
        super().__init__(parent)
        self.setup_ui(placeholder, default_date)
                
    def setup_ui(self, placeholder, default_date):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.date_input = QtWidgets.QLineEdit()
        self.date_input.setPlaceholderText(placeholder)  # Ahora será "MM/DD/AAAA"
        
        if default_date:
            self.date_input.setText(default_date)
        
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: bold;
                min-height: 18px;
                min-width: 120px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QLineEdit:hover {
                border-color: #5d6d7e;
            }
        """)
        
        self.date_input.textChanged.connect(self.on_text_changed)
        
        # Botón de calendario con icono SVG
        self.calendar_btn = QtWidgets.QPushButton()
        self.calendar_btn.setFixedSize(40, 40)
        
        # Usar icono SVG blanco
        icon_pixmap = QtGui.QPixmap()
        white_svg = CALENDAR_SVG.replace('fill="currentColor"', 'fill="white"')
        white_svg = white_svg.replace('stroke="currentColor"', 'stroke="white"')
        icon_pixmap.loadFromData(white_svg.encode(), "SVG")
        scaled_icon = icon_pixmap.scaled(20, 20, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        self.calendar_btn.setIcon(QtGui.QIcon(scaled_icon))
        self.calendar_btn.setToolTip("Abrir calendario")
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: none;
                border-radius: 6px;
                padding: 8px;
                min-width: 36px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        self.calendar_btn.clicked.connect(self.show_native_calendar)
        
        layout.addWidget(self.date_input)
        layout.addWidget(self.calendar_btn)

    def on_text_changed(self, text):
        """
        SIMPLIFICADO: Solo validar y emitir MM/DD/YYYY
        """
        from Utiles.utils import validate_date_format
        
        if validate_date_format(text):
            # SIMPLIFICADO: Emitir directamente en MM/DD/YYYY
            self.dateChanged.emit(text)
        else:
            self.dateChanged.emit("")

    def set_date(self, date_string):
        """
        SIMPLIFICADO: Recibir MM/DD/YYYY directamente
        """
        if date_string:
            # NO CONVERTIR - ya viene en MM/DD/YYYY
            self.date_input.setText(date_string)
        else:
            self.date_input.clear()

    def get_date(self):
        """
        SIMPLIFICADO: Retornar MM/DD/YYYY directamente
        """
        from Utiles.utils import validate_date_format
        
        text = self.date_input.text()
        if validate_date_format(text):
            return text  # RETORNAR MM/DD/YYYY directamente
        return ""

    def show_native_calendar(self):
        """
        MODIFICADO: Convertir solo para mostrar en calendario
        """
        current_text = self.date_input.text()
        if current_text:
            try:
                # TEMPORAL: Convertir MM/DD/YYYY a objeto date para calendario
                date_obj = datetime.strptime(current_text, "%m/%d/%Y")
                initial_date = QtCore.QDate(date_obj.year, date_obj.month, date_obj.day)
            except:
                initial_date = QtCore.QDate.currentDate()
        else:
            initial_date = QtCore.QDate.currentDate()
        
        # Crear diálogo de fecha nativo
        date_dialog = QtWidgets.QDialog(self)
        date_dialog.setWindowTitle("Seleccionar Fecha")
        date_dialog.setModal(True)
        date_dialog.setFixedSize(450, 350)
        
        layout = QtWidgets.QVBoxLayout(date_dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        calendar = QtWidgets.QCalendarWidget()
        calendar.setSelectedDate(initial_date)
        calendar.setGridVisible(True)
        
        # ARREGLADO: Estilo corregido para que se vean todos los días y headers
        calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
            }
            
            QCalendarWidget QTableView {
                background-color: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #5d6d7e;
                outline: none;
                border: none;
            }
            
            QCalendarWidget QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: 1px solid #2980b9;
                font-weight: bold;
                font-size: 12px;
            }
            
            QCalendarWidget QTableView::item {
                color: #ecf0f1;
                background-color: #34495e;
                padding: 5px;
                border: 1px solid #5d6d7e;
            }
            
            QCalendarWidget QTableView::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            
            QCalendarWidget QTableView::item:hover {
                background-color: #5d6d7e;
                color: white;
            }
            
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #3498db;
                border-radius: 6px;
                margin: 3px;
            }
            
            QCalendarWidget QToolButton {
                color: white;
                background-color: #3498db;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            
            QCalendarWidget QToolButton:hover {
                background-color: #2980b9;
            }
            
            QCalendarWidget QSpinBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #5d6d7e;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
                margin: 2px;
            }
            
            QCalendarWidget QSpinBox:focus {
                border-color: #1abc9c;
                background-color: #34495e;
            }
        """)
        
        layout.addWidget(calendar)
        
        # Botones
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QtWidgets.QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { 
                background-color: #c0392b; 
            }
        """)
        cancel_btn.clicked.connect(date_dialog.reject)
        
        ok_btn = QtWidgets.QPushButton("Seleccionar")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { 
                background-color: #229954; 
            }
        """)
        ok_btn.clicked.connect(date_dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        date_dialog.show()
        QtCore.QTimer.singleShot(50, lambda: self.force_calendar_style(calendar))
        
        # SIMPLIFICADO: Emitir MM/DD/YYYY directamente
        if date_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_date = calendar.selectedDate()
            # CONVERTIR: De QDate a MM/DD/YYYY
            display_date = selected_date.toString("MM/dd/yyyy")
            self.date_input.setText(display_date)
            self.dateChanged.emit(display_date)  # EMITIR MM/DD/YYYY

    def force_calendar_style(self, calendar):
        """
        Forzar el estilo en los headers después de que se rendericen
        """
        try:
            for header in calendar.findChildren(QtWidgets.QHeaderView):
                header.setStyleSheet("""
                    QHeaderView {
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                        border: none;
                    }
                    QHeaderView::section {
                        background-color: #3498db;
                        color: white;
                        padding: 8px;
                        border: 1px solid #2980b9;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """)
            
            for table in calendar.findChildren(QtWidgets.QTableView):
                table.setStyleSheet("""
                    QTableView {
                        background-color: #34495e;
                        color: #ecf0f1;
                        selection-background-color: #3498db;
                        selection-color: white;
                        gridline-color: #5d6d7e;
                        outline: none;
                        border: none;
                    }
                    QTableView::item {
                        color: #ecf0f1;
                        background-color: #34495e;
                        padding: 5px;
                        border: 1px solid #5d6d7e;
                    }
                    QTableView::item:selected {
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                    }
                    QTableView::item:hover {
                        background-color: #5d6d7e;
                        color: white;
                    }
                """)
                
            calendar.update()
            calendar.repaint()
            
        except Exception as e:
            print(f"Error aplicando estilo: {e}")

class DatePage(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        # Layout principal sin fondo especial
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(40)
        
        # Título
        title = QtWidgets.QLabel("Configuración de Fechas")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Contenedor de fechas
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(30)
        
        # Fecha de inicio
        start_container = QtWidgets.QWidget()
        start_layout = QtWidgets.QVBoxLayout(start_container)
        start_layout.setSpacing(10)
        
        start_label = QtWidgets.QLabel("Fecha de Inicio")
        start_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ecf0f1;
            margin-bottom: 8px;
        """)
        start_layout.addWidget(start_label)
        
        self.start_date = DateInputWithCalendar("DD/MM/YYYY", default_date=config.get("start_date"))
        self.start_date.dateChanged.connect(self.changed.emit)
        start_layout.addWidget(self.start_date)
        
        content_layout.addWidget(start_container)
        
        # Separador
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #5d6d7e;
                border: none;
                height: 2px;
                margin: 10px 20px;
            }
        """)
        content_layout.addWidget(separator)
        
        # Fecha de fin
        end_container = QtWidgets.QWidget()
        end_layout = QtWidgets.QVBoxLayout(end_container)
        end_layout.setSpacing(10)
        
        end_label = QtWidgets.QLabel("Fecha de Fin")
        end_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ecf0f1;
            margin-bottom: 8px;
        """)
        end_layout.addWidget(end_label)
        
        self.end_date = DateInputWithCalendar("DD/MM/YYYY", default_date=config.get("end_date"))
        self.end_date.dateChanged.connect(self.changed.emit)
        end_layout.addWidget(self.end_date)
        
        content_layout.addWidget(end_container)
        
        main_layout.addLayout(content_layout)
        main_layout.addStretch()
    
    def get_config(self):
        return {
            "start_date": self.start_date.get_date(),
            "end_date": self.end_date.get_date()
        }
    
    def set_config(self, config):
        if "start_date" in config:
            self.start_date.set_date(config["start_date"])
        if "end_date" in config:
            self.end_date.set_date(config["end_date"])