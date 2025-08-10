from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime, timedelta
from Utiles.assets import CALENDAR_SVG
from Utiles.utils import validate_date_format

class DateInputWithCalendar(QtWidgets.QWidget):
    dateChanged = QtCore.pyqtSignal(str)
    
    def __init__(self, placeholder="DD/MM/YYYY", default_date=None, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Input de fecha editable
        self.date_input = QtWidgets.QLineEdit()
        self.date_input.setPlaceholderText(placeholder)
        if default_date:
            # Convertir formato interno YYYY-MM-DD a DD/MM/YYYY para mostrar
            self.date_input.setText(self.convert_to_display_format(default_date))
        
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
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
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
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
    
    def convert_to_display_format(self, date_str):
        """Convertir YYYY-MM-DD a DD/MM/YYYY"""
        try:
            if '-' in date_str and len(date_str) == 10:  # formato yyyy-mm-dd
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj.strftime("%d/%m/%Y")
            elif '/' in date_str:  # ya está en formato dd/mm/yyyy
                return date_str
            return date_str
        except:
            return date_str
    
    def convert_to_internal_format(self, date_str):
        """Convertir DD/MM/YYYY a YYYY-MM-DD"""
        try:
            if '/' in date_str and len(date_str) == 10:  # formato dd/mm/yyyy
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                return date_obj.strftime("%Y-%m-%d")
            elif '-' in date_str:  # ya está en formato yyyy-mm-dd
                return date_str
            return date_str
        except:
            return date_str
    
    def on_text_changed(self, text):
        # Emitir cambio en formato interno
        if text.strip():
            internal_format = self.convert_to_internal_format(text)
            self.dateChanged.emit(internal_format)
        else:
            self.dateChanged.emit("")
        
        # Restaurar estilo normal siempre
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QLineEdit:hover {
                border-color: #5d6d7e;
            }
        """)
    
    def show_native_calendar(self):
        """ARREGLADO: Usar calendario nativo del sistema operativo"""
        # Obtener fecha actual del input o usar hoy
        current_text = self.date_input.text()
        if current_text:
            try:
                internal_date = self.convert_to_internal_format(current_text)
                date_obj = datetime.strptime(internal_date, "%Y-%m-%d")
                initial_date = QtCore.QDate(date_obj.year, date_obj.month, date_obj.day)
            except:
                initial_date = QtCore.QDate.currentDate()
        else:
            initial_date = QtCore.QDate.currentDate()
        
        # Crear diálogo de fecha nativo
        date_dialog = QtWidgets.QDialog(self)
        date_dialog.setWindowTitle("Seleccionar Fecha")
        date_dialog.setModal(True)
        date_dialog.setFixedSize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(date_dialog)
        
        # Calendario nativo
        calendar = QtWidgets.QCalendarWidget()
        calendar.setSelectedDate(initial_date)
        calendar.setGridVisible(True)
        
        # ARREGLADO: Estilo corregido para que se vean todos los días y headers
        calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
                font-weight: bold;
            }
            
            /* ARREGLADO: Header horizontal (días de la semana) */
            QCalendarWidget QWidget#qt_calendar_calendarview QHeaderView::section {
                background-color: #348db;
                color: white;
                padding: 5px;
                border: 1px solid #2980b9;
                font-weight: bold;
                font-size: 11px;
            }
            
            /* ARREGLADO: Header vertical (números de semana) */
            QCalendarWidget QWidget#qt_calendar_calendarview QHeaderView::section:vertical {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 5px;
                border: 1px solid #5d6d7e;
                font-weight: bold;
                min-width: 30px;
            }
            
            /* ARREGLADO: Celdas de días */
            QCalendarWidget QTableView {
                background-color: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #5d6d7e;
                outline: none;
            }
            
            /* ARREGLADO: Items individuales (días) */
            QCalendarWidget QAbstractItemView:enabled {
                color: #ecf0f1;
                background-color: transparent;
                font-weight: bold;
            }
            
            /* ARREGLADO: Día seleccionado */
            QCalendarWidget QAbstractItemView:selected {
                background-color: #3498db;
                color: white;
                border: 2px solid #1abc9c;
            }
            
            /* ARREGLADO: Día con foco */
            QCalendarWidget QAbstractItemView:focus {
                background-color: #2980b9;
                color: white;
            }
            
            /* ARREGLADO: Días del mes anterior/siguiente */
            QCalendarWidget QAbstractItemView:disabled {
                color: #7f8c8d;
                background-color: transparent;
            }
            
            /* ARREGLADO: Barra de navegación superior */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #3498db;
                border-radius: 6px;
                margin: 2px;
                padding: 2px;
            }
            
            /* ARREGLADO: Botones de navegación */
            QCalendarWidget QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 30px;
            }
            
            QCalendarWidget QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QCalendarWidget QToolButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
            
            /* ARREGLADO: SpinBoxes para mes y año */
            QCalendarWidget QSpinBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #5d6d7e;
                border-radius: 4px;
                padding: 3px;
                font-weight: bold;
                min-width: 60px;
            }
            
            QCalendarWidget QSpinBox:focus {
                border-color: #1abc9c;
            }
            
            QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {
                background-color: #3498db;
                border: none;
                width: 16px;
                border-radius: 2px;
            }
            
            QCalendarWidget QSpinBox::up-button:hover, QCalendarWidget QSpinBox::down-button:hover {
                background-color: #2980b9;
            }
            
            /* ARREGLADO: Forzar visibilidad de headers */
            QCalendarWidget QHeaderView {
                background-color: #3498db;
                color: white;
            }
            
            QCalendarWidget QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
                border: 1px solid #2980b9;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(calendar)
        
        # Botones
        button_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        cancel_btn.clicked.connect(date_dialog.reject)
        
        ok_btn = QtWidgets.QPushButton("Seleccionar")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        ok_btn.clicked.connect(date_dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Mostrar diálogo
        if date_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_date = calendar.selectedDate()
            # Mostrar en formato DD/MM/YYYY
            display_date = selected_date.toString("dd/MM/yyyy")
            self.date_input.setText(display_date)
            # Emitir en formato interno YYYY-MM-DD
            internal_date = selected_date.toString("yyyy-MM-dd")
            self.dateChanged.emit(internal_date)
    
    def get_date(self):
        # Devolver en formato interno
        display_text = self.date_input.text()
        return self.convert_to_internal_format(display_text) if display_text else ""
    
    def set_date(self, date_str):
        # Recibir formato interno y mostrar en formato display
        if date_str:
            display_format = self.convert_to_display_format(date_str)
            self.date_input.setText(display_format)
        else:
            self.date_input.setText("")

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
        
        self.start_date = DateInputWithCalendar("DD/MM/YYYY", config.get("start_date"))
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
        
        self.end_date = DateInputWithCalendar("DD/MM/YYYY", config.get("end_date"))
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