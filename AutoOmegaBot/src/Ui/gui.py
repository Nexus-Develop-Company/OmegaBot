"""
Módulo principal de la interfaz gráfica de OmegaBot.

Este módulo contiene la implementación completa de la interfaz de usuario principal
para el sistema de análisis de backtesting de opciones financieras OmegaBot.

Classes:
    StatusWidget: Widget personalizado para mostrar métricas del sistema
    ActionButton: Botón personalizado con estilos y efectos visuales
    LogWidget: Widget de logs con formato avanzado y colores
    FileUploadButton: Botón especializado para selección de archivos
    ErrorDialog: Diálogo personalizado para mostrar errores
    MainWindow: Ventana principal de la aplicación

Author: Nexus Corp
Version: 1.0
Date: 2025
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from Ui.Settings_Ui.setting_gui import ConfigWindow
from Utiles.utils import (
    load_config,              
    get_connection_status,     
    validate_system_ready,     
    save_logs,                
    get_file_info,            
    get_validation_status,    
    get_debug_lines_for_ui,   
    get_current_timestamp,    
    format_execution_summary, 
    get_debug_info_complete,   
)
from Utiles.assets import *
import datetime
import os

class StatusWidget(QtWidgets.QWidget):
    """
    Widget personalizado para mostrar métricas del sistema en tiempo real.
    
    Muestra información como estado del bot, tiempo activo, enlaces analizados, etc.
    con un diseño visual atractivo y colores dinámicos.
    
    Args:
        title (str): Título del widget que se muestra en la parte superior
        value (str): Valor inicial que se muestra con tipografía grande
        color (str): Color de fondo del widget en formato hexadecimal
        icon_svg (str, optional): SVG del icono a mostrar (no implementado)
        parent (QWidget, optional): Widget padre
        
    Attributes:
        value_label (QLabel): Label que contiene el valor principal del widget
    TODO: Implementar soporte para iconos SVG en el layout
    TODO: Agregar animaciones de transición al cambiar valores
    TODO: Implementar tooltips informativos para cada métrica
    """
    def __init__(self, title, value, color="#2980b9", icon_svg=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)  
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  
        layout.setSpacing(15)
        
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 5, 0, 5)
        text_layout.setSpacing(8)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: normal; opacity: 0.9; color: white;")
        title_label.setMinimumHeight(20)  
        
        self.value_label = QtWidgets.QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        self.value_label.setMinimumHeight(35)  
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        text_layout.addStretch()
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def update_value(self, value):
        """
        Actualiza el valor mostrado en el widget.
        
        Args:
            value (str): Nuevo valor a mostrar    
        TODO: Agregar validación de tipo de dato
        TODO: Implementar animación de cambio de valor
        """
        self.value_label.setText(str(value))
    
    def update_color(self, color):
        """
        Actualiza el color de fondo del widget manteniendo el texto blanco.
        
        Args:
            color (str): Nuevo color de fondo en formato hexadecimal            
        TODO: Agregar validación de formato de color
        TODO: Implementar transición suave de colores
        """
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)

class ActionButton(QtWidgets.QPushButton):
    """
    Botón personalizado con estilos avanzados y efectos visuales.
    
    Proporciona un diseño moderno con efectos hover, pressed y disabled,
    además de soporte opcional para iconos SVG.
    
    Args:
        text (str): Texto a mostrar en el botón
        icon_svg (str, optional): Código SVG del icono (no implementado completamente)
        color (str): Color de fondo del botón en formato hexadecimal
        parent (QWidget, optional): Widget padre
    TODO: Completar implementación de iconos SVG
    TODO: Agregar soporte para diferentes tamaños de botón
    TODO: Implementar efectos de animación al hacer clic
    """
    def __init__(self, text, icon_svg=None, color="#3498db", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 0.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.2)};
            }}
            QPushButton:disabled {{
                background-color: #7f8c8d;
                color: #bdc3c7;
            }}
        """)
        
        if icon_svg:
            icon = QtGui.QIcon()
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(icon_svg.encode(), "SVG")
            white_pixmap = QtGui.QPixmap(pixmap.size())
            white_pixmap.fill(QtCore.Qt.white)
            white_pixmap.setMask(pixmap.createMaskFromColor(QtCore.Qt.transparent))
            icon.addPixmap(white_pixmap)
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(20, 20))
    
    def darken_color(self, color, factor):
        """
        Oscurece un color por un factor dado para efectos hover/pressed.
        
        Args:
            color (str): Color en formato hexadecimal (#RRGGBB)
            factor (float): Factor de oscurecimiento (0.0 - 1.0)
            
        Returns:
            str: Color oscurecido en formato hexadecimal
        TODO: Agregar validación de formato de color de entrada
        TODO: Implementar función brightening para efectos contrarios
        """
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

class LogWidget(QtWidgets.QTextEdit):
    """
    Widget especializado para mostrar logs del sistema con formato avanzado.
    
    Proporciona logs con colores, timestamps, niveles de severidad y
    capacidad de guardar en formato plano para exportación.
    
    Attributes:
        plain_logs (list): Lista de logs en formato plano para exportación
    TODO: Implementar filtrado de logs por nivel de severidad
    TODO: Agregar búsqueda en tiempo real dentro de los logs
    TODO: Implementar exportación directa a archivo desde el widget
    TODO: Agregar límite máximo de logs para evitar uso excesivo de memoria
    """
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(700)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2c3e50;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5dade2;
            }
        """)
        
        self.plain_logs = []

    def add_log(self, message, level="INFO"):
        """
        Agrega un nuevo log al widget con formato y color según el nivel.
        
        Args:
            message (str): Mensaje del log
            level (str): Nivel del log (INFO, SUCCESS, ERROR, WARNING)
        TODO: Agregar más niveles de log (DEBUG, CRITICAL)
        TODO: Implementar configuración de formato de timestamp
        TODO: Agregar numeración automática de logs
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        plain_message = f"[{timestamp}] {level}: {message}"
        self.plain_logs.append(plain_message)
        
        if level == "SUCCESS":
            color = "#27ae60"
            icon = "✓"
        elif level == "ERROR":
            color = "#e74c3c"
            icon = "✗"
        elif level == "WARNING":
            color = "#f39c12"
            icon = "⚠"
        else:
            color = "#3498db"
            icon = "ℹ"
        
        formatted_message = f'<span style="color: {color};">[{timestamp}] {icon} {message}</span>'
        
        self.append(formatted_message)
        self.moveCursor(QtGui.QTextCursor.End)

    def get_plain_logs(self):
        """
        Obtiene todos los logs en formato texto plano para exportación.
        
        Returns:
            str: Todos los logs concatenados con saltos de línea
        TODO: Agregar opción de filtrar logs por rango de tiempo
        TODO: Implementar compresión de logs para archivos grandes
        """
        return "\n".join(self.plain_logs)

class FileUploadButton(QtWidgets.QPushButton):
    """
    Botón especializado para selección y carga de archivos.
    
    Maneja la selección de archivos CSV/Excel y emite señales cuando
    se selecciona un archivo válido. Actualiza su texto para mostrar
    el archivo seleccionado.
    
    Signals:
        file_selected (str): Emitida cuando se selecciona un archivo válido
        
    Attributes:
        selected_file (str): Ruta del archivo actualmente seleccionado
        
    TODO: Agregar validación de formato de archivo antes de seleccionar
    TODO: Implementar preview del contenido del archivo
    TODO: Agregar soporte para drag & drop de archivos
    TODO: Mostrar información adicional del archivo (tamaño, fecha)
    """
    file_selected = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Subir Archivo", parent)
        self.selected_file = None
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                text-align: left;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.clicked.connect(self.select_file)
    
    def select_file(self):
        """
        Abre el diálogo de selección de archivos y procesa la selección.
        
        Formatos soportados: CSV, XLSX, XLS
        Actualiza el texto del botón con el nombre del archivo seleccionado.
        
        TODO: Agregar validación de contenido del archivo
        TODO: Implementar historial de archivos recientes
        TODO: Agregar opción de limpiar selección actual
        """
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Seleccionar archivo con enlaces",
            "",
            "Formatos permitidos (*.csv *.xlsx *.xls)"
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            self.setText(f"{filename}")
            self.selected_file = file_path
            self.file_selected.emit(file_path)
    
    def get_selected_file(self):
        """
        Obtiene la ruta del archivo actualmente seleccionado.
        
        Returns:
            str: Ruta del archivo seleccionado o None si no hay selección
            
        TODO: Agregar validación de existencia del archivo
        """
        return self.selected_file

class ErrorDialog(QtWidgets.QDialog):
    """
    Diálogo personalizado para mostrar errores con diseño consistente.
    
    Proporciona un diálogo modal con estilo dark theme que muestra
    mensajes de error con icono y formateo apropiado.
    
    Args:
        parent (QWidget): Widget padre del diálogo
        title (str): Título de la ventana del diálogo
        message (str): Mensaje de error a mostrar
        
    TODO: Agregar diferentes tipos de diálogo (Warning, Info, Question)
    TODO: Implementar botones personalizables (Yes/No, Retry/Cancel)
    TODO: Agregar soporte para mensajes HTML con formato avanzado
    TODO: Implementar sonidos de notificación según el tipo de error
    """
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        
        icon_label = QtWidgets.QLabel("⚠")
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        
        msg_label = QtWidgets.QLabel(message)
        msg_label.setAlignment(QtCore.Qt.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; color: #ecf0f1;")
        
        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        
        layout.addWidget(icon_label)
        layout.addWidget(msg_label)
        layout.addWidget(ok_button)

class MainWindow(QtWidgets.QMainWindow):
    """
    Ventana principal de la aplicación OmegaBot.
    
    Contiene toda la interfaz principal incluyendo paneles de estado,
    controles de bot, logs del sistema y menús de navegación.
    Coordina todas las operaciones de análisis y configuración.
    
    Attributes:
        bot_running (bool): Estado actual del bot (ejecutándose/detenido)
        config (dict): Configuración actual cargada del sistema
        selected_file (str): Archivo actualmente seleccionado para análisis
        last_system_status (dict): Último estado del sistema para detectar cambios
        start_time (datetime): Tiempo de inicio de la ejecución actual
        analysis_count (int): Contador de análisis completados
        
    TODO: Implementar sistema de plugins para extensibilidad
    TODO: Agregar soporte para múltiples archivos simultáneos
    TODO: Implementar sistema de notificaciones push
    TODO: Agregar métricas avanzadas de rendimiento
    TODO: Implementar backup automático de configuraciones
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmegaBot - Options Backtest Analysis")
        self.setMinimumSize(1000, 700)
        
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(OMEGABOT_LOGO_SVG.encode(), "SVG")
        icon.addPixmap(pixmap)
        self.setWindowIcon(icon)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: white;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                border-bottom: 1px solid #34495e;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: #ecf0f1;
                border-top: 1px solid #34495e;
                padding: 5px;
            }
        """)
        
        self.bot_running = False
        self.config = load_config()  
        self.selected_file = None
        self.last_system_status = None
        self.start_time = None
        self.analysis_count = 0
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        self.connection_timer = QtCore.QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(5000)
        
        self.status_timer = QtCore.QTimer()
        self.status_timer.timeout.connect(self.check_system_status_changes)
        self.status_timer.start(5000)
        
        self.uptime_timer = QtCore.QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime_display)
        
        QtCore.QTimer.singleShot(1000, self.initial_system_check)

    def setup_ui(self):
        """
        Configura todos los elementos de la interfaz de usuario principal.
        
        Incluye header con logo, panel de métricas, controles de archivo,
        botones de control del bot y área de logs del sistema.
        
        TODO: Hacer el layout responsivo para diferentes tamaños de pantalla
        TODO: Agregar tema claro/oscuro configurable
        TODO: Implementar personalización de posición de paneles
        TODO: Agregar soporte para múltiples monitores
        """
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(20)  

        header_layout = QtWidgets.QHBoxLayout()
        
        logo_label = QtWidgets.QLabel()
        logo_pixmap = QtGui.QPixmap()
        logo_pixmap.loadFromData(OMEGABOT_LOGO_SVG.encode(), "SVG")
        scaled_logo = logo_pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_logo)
        
        title_widget = QtWidgets.QWidget()
        title_layout = QtWidgets.QVBoxLayout(title_widget)
        title_layout.setContentsMargins(10, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title = QtWidgets.QLabel("OmegaBot")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db; margin: 0;")
        
        subtitle = QtWidgets.QLabel("Options Backtest Analysis System")
        subtitle.setStyleSheet("font-size: 13px; color: #95a5a6; margin: 0;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_widget)
        header_layout.addStretch()
        
        config_btn = ActionButton("Ajustes", GEAR_SVG, "#9b59b6")
        config_btn.clicked.connect(self.open_config)
        config_btn.setFixedWidth(140)
        header_layout.addWidget(config_btn)
        
        main_layout.addLayout(header_layout)

        stats_layout = QtWidgets.QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.status_widget = StatusWidget("Estado", "Detenido", "#e74c3c")
        self.uptime_widget = StatusWidget("Tiempo Activo", "00:00:00", "#9b59b6")
        self.analyzed_widget = StatusWidget("Enlaces Analizados", "0", "#27ae60")
        self.total_enlaces_widget = StatusWidget("Total de Enlaces", "0", "#27ae60")
        
        stats_layout.addWidget(self.status_widget)
        stats_layout.addWidget(self.uptime_widget)
        stats_layout.addWidget(self.analyzed_widget)
        stats_layout.addWidget(self.total_enlaces_widget)
        
        main_layout.addLayout(stats_layout)

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addStretch()
        
        self.file_upload_btn = FileUploadButton()
        self.file_upload_btn.file_selected.connect(self.on_file_selected)
        
        file_layout.addWidget(self.file_upload_btn)
        file_layout.addStretch()
        
        main_layout.addLayout(file_layout)

        control_layout = QtWidgets.QHBoxLayout()
        control_layout.addStretch()
        
        self.start_btn = ActionButton("Iniciar Test", PLAY_SVG, "#27ae60")
        self.start_btn.clicked.connect(self.toggle_bot)
        self.start_btn.setFixedWidth(150)
        
        self.stop_btn = ActionButton("Detener Test", STOP_SVG, "#e74c3c")
        self.stop_btn.clicked.connect(self.toggle_bot)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedWidth(150)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)

        logs_container = QtWidgets.QWidget()
        logs_layout = QtWidgets.QVBoxLayout(logs_container)
        logs_layout.setContentsMargins(0, 0, 0, 0)  
        logs_layout.setSpacing(0)  
        
        log_label = QtWidgets.QLabel("📊 Logs del Sistema")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ecf0f1; margin: 0px;")
        
        self.log_widget = LogWidget()
        self.log_widget.setMinimumHeight(200)
        self.log_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 18px;
                line-height: 2;
                font-weight: 800;
                margin-top: 0px;  
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2c3e50;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5dade2;
            }
        """)
        
        logs_layout.addWidget(log_label)
        logs_layout.addWidget(self.log_widget)
        
        main_layout.addWidget(logs_container)

    def setup_menu(self):
        """
        Configura la barra de menús principal con todas las opciones.
        
        Incluye menús de Archivo, Análisis y Ayuda con sus respectivos
        atajos de teclado y funcionalidades asociadas.
        
        TODO: Agregar menú de Ver para opciones de visualización
        TODO: Implementar menú de Herramientas para utilidades adicionales
        TODO: Agregar historial de archivos recientes en menú Archivo
        TODO: Implementar personalización de atajos de teclado
        """
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Archivo')
        
        upload_action = QtWidgets.QAction('Subir Archivo', self)
        upload_action.setShortcut('Ctrl+O')
        upload_action.triggered.connect(self.file_upload_btn.select_file)
        file_menu.addAction(upload_action)
        
        config_action = QtWidgets.QAction('Configuración', self)
        config_action.setShortcut('Ctrl+P')
        config_action.triggered.connect(self.open_config)
        file_menu.addAction(config_action)
        
        file_menu.addSeparator()
        
        exit_action = QtWidgets.QAction('Salir', self)
        exit_action.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        analysis_menu = menubar.addMenu('Análisis')
        
        start_action = QtWidgets.QAction('Iniciar', self)
        start_action.setShortcut('F5')
        start_action.triggered.connect(self.toggle_bot)
        analysis_menu.addAction(start_action)
        
        stop_action = QtWidgets.QAction('Detener', self)
        stop_action.setShortcut('F6')
        stop_action.triggered.connect(self.toggle_bot)
        analysis_menu.addAction(stop_action)
        
        help_menu = menubar.addMenu('Ayuda')
        
        about_action = QtWidgets.QAction('Acerca de', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """
        Configura la barra de estado inferior con información del sistema.
        
        Incluye indicador de conexión a internet y mensajes de estado
        general del sistema y operaciones actuales.
        
        TODO: Agregar más indicadores de estado (CPU, memoria, disco)
        TODO: Implementar indicador de progreso para operaciones largas
        TODO: Agregar reloj/timestamp en tiempo real
        """
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sistema listo - Cargar archivo y configurar estrategia antes de iniciar")
        
        self.connection_label = QtWidgets.QLabel()
        self.connection_label.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: bold;
                margin-right: 5px;
            }
        """)
        self.connection_label.setText("🟢 Sin conexión")
        
        self.status_bar.addPermanentWidget(self.connection_label)
        self.check_connection()

    def check_connection(self):
        """
        Verifica el estado de conexión a internet y actualiza la UI.
        
        Utiliza las funciones de utilidad para verificar conectividad
        y actualiza el indicador visual en la barra de estado.
        
        Returns:
            bool: True si hay conexión, False en caso contrario
            
        TODO: Implementar verificación de conexión a APIs específicas
        TODO: Agregar reintentos automáticos en caso de falla
        TODO: Mostrar velocidad de conexión cuando sea posible
        """
        is_connected, status_text = get_connection_status()
        
        if is_connected:
            self.connection_label.setStyleSheet("""
                QLabel {
                    background-color: #27ae60;
                    color: white;
                    border-radius: 10px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-right: 5px;
                }
            """)
            self.connection_label.setText("🟢 Conectado")
        else:
            self.connection_label.setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 10px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-right: 5px;
                }
            """)
            self.connection_label.setText("🟢 Sin conexión")
        
        if not self.bot_running:
            self.update_start_button_state()
        
        return is_connected

    def update_start_button_state(self):
        """
        Actualiza el estado del botón de inicio basado en validaciones del sistema.
        
        Verifica todos los requisitos necesarios para ejecutar el bot
        y habilita/deshabilita el botón de inicio apropiadamente.
        
        TODO: Mostrar lista detallada de requisitos faltantes en tooltip
        TODO: Implementar validación en tiempo real mientras se edita configuración
        """
        is_valid, error_message = validate_system_ready(self.config, self.selected_file)
        
        self.start_btn.setEnabled(is_valid)
        self.start_btn.setToolTip(error_message if not is_valid else "")

    def initial_system_check(self):
        """
        Realiza verificación inicial completa del sistema al iniciar la aplicación.
        
        Verifica estado de todos los componentes y muestra información
        detallada en los logs para orientar al usuario.
        
        TODO: Implementar verificación de actualizaciones al inicio
        TODO: Validar integridad de archivos de configuración
        TODO: Verificar permisos de escritura en directorios necesarios
        """
        self.log_widget.add_log("Iniciando OmegaBot - Verificando sistema...", "INFO")
        
        initial_status = get_validation_status(self.config, self.selected_file)
        self.show_complete_debug_in_logs()
        
        self.last_system_status = {
            'internet': initial_status['internet'],
            'file_valid': initial_status['file_valid'],
            'dates_valid': initial_status['dates_valid'],
            'overall_valid': initial_status['overall_valid']
        }
        
        self.update_start_button_state()

    def show_complete_debug_in_logs(self):
        """
        Muestra información completa de debug del sistema en los logs.
        
        Presenta un resumen detallado y visualmente atractivo del estado
        de todos los componentes del sistema con emojis y formato colorido.
        
        TODO: Agregar opción para exportar debug info a archivo
        TODO: Implementar diferentes niveles de detalle configurable
        TODO: Agregar timestamp de última verificación de cada componente
        """
        try:
            debug_info = get_debug_info_complete(self.config, self.selected_file)
            status = debug_info['status']
            
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            self.log_widget.add_log("🤖 OMEGABOT - ESTADO COMPLETO DEL SISTEMA 🤖", "INFO")
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            
            if status['internet']:
                self.log_widget.add_log(f"🌐 Internet: ✅ CONECTADO - {debug_info['connection_info']}", "SUCCESS")
            else:
                self.log_widget.add_log(f"🌐 Internet: ❌ DESCONECTADO - {debug_info['connection_info']}", "ERROR")
            
            if status['file_valid']:
                self.log_widget.add_log(f"📄 Archivo: ✅ VÁLIDO{debug_info['file_info']}", "SUCCESS")
            else:
                self.log_widget.add_log("📄 Archivo: ❌ NO SELECCIONADO - ¡Sube tu archivo primero! 📁", "ERROR")
            
            if status['dates_valid']:
                self.log_widget.add_log(f"📅 Fechas: ✅ CONFIGURADAS{debug_info['dates_info']}", "SUCCESS")
            else:
                self.log_widget.add_log("📅 Fechas: ⚠️ NO CONFIGURADAS - ¡Ve a configuración! ⚙️", "WARNING")
            
            self.log_widget.add_log(f"⚙️ Estrategia: ℹ️ INFORMATIVA{debug_info['strategy_info']}", "INFO")
            self.log_widget.add_log(f"⚙️ Fondos y Asignación: ℹ️ INFORMATIVA{debug_info['funds_info']}", "INFO")
            
            self.log_widget.add_log("🎯" + "-"*30 + " CARPETAS " + "-"*30, "INFO")
            
            if debug_info['general_info']:
                self.log_widget.add_log(f"📊 Salida Excel: ✅ CONFIGURABLE{debug_info['general_info']}", "SUCCESS")
            
            self.log_widget.add_log(f"⚙️ Configuración: 🔒 FIJO - {debug_info['config_path']}", "INFO")
            self.log_widget.add_log(f"📋 Logs: 🔒 FIJO - {debug_info['logs_path']}", "INFO")
            
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            
            if status['overall_valid']:
                self.log_widget.add_log("🚀 ESTADO GENERAL: ✅ ¡LISTO PARA DESPEGAR! 🎉", "SUCCESS")
                self.log_widget.add_log("💪 ¡Todo perfecto! El bot está listo para analizar 📈", "SUCCESS")
                self.log_widget.add_log("🎯 ¡Dale click a 'Iniciar Test' y vamos a hacer magia! ✨", "SUCCESS")
            else:
                self.log_widget.add_log("🛑 ESTADO GENERAL: ❌ NO LISTO - ¡Faltan cositas! 😅", "ERROR")
                self.log_widget.add_log("🔧 Revisa los elementos marcados con ❌ o ⚠️", "ERROR")
                self.log_widget.add_log("😊 ¡Tranquilo! Solo faltan unos ajustes y estaremos listos 💪", "WARNING")
            
            if not status['overall_valid'] and status['errors']:
                self.log_widget.add_log("🎯" + "="*50, "INFO")
                self.log_widget.add_log("🔍 DETALLES DE LO QUE FALTA (¡No te preocupes, es fácil!):", "WARNING")
                for i, error in enumerate(status['errors'], 1):
                    emoji = ["🔸", "🔹", "🔶", "🔷"][i % 4]
                    self.log_widget.add_log(f"  {emoji} {error} - ¡Vamos a arreglarlo! 💪", "ERROR")
            
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            self.log_widget.add_log(f"🕐 Verificación completada: {datetime.datetime.now().strftime('%H:%M:%S')}", "INFO")
            self.log_widget.add_log("🤖 OmegaBot está aquí para ayudarte - ¡Let's go! 🚀", "INFO")
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            
        except Exception as e:
            self.log_widget.add_log(f"💥 Error mostrando debug completo: {str(e)}", "ERROR")
            self.log_widget.add_log("😅 ¡Ups! Algo falló, pero seguimos adelante 💪", "WARNING")

    def check_system_status_changes(self):
        """
        Monitorea cambios en el estado del sistema y los reporta en logs.
        
        Compara el estado actual con el último estado conocido y
        reporta solo cuando hay cambios significativos para evitar spam.
        
        TODO: Implementar throttling para evitar demasiadas verificaciones
        TODO: Agregar métricas de frecuencia de cambios de estado
        TODO: Notificar cambios críticos con mayor prominencia
        """
        current_status = get_validation_status(self.config, self.selected_file)
        
        current_status_hash = {
            'internet': current_status['internet'],
            'file_valid': current_status['file_valid'],
            'dates_valid': current_status['dates_valid'],
            'overall_valid': current_status['overall_valid']
        }
        
        if self.last_system_status != current_status_hash:
            self.last_system_status = current_status_hash
            
            self.log_widget.add_log("🔄 CAMBIO DETECTADO EN EL SISTEMA", "INFO")
            debug_lines = get_debug_lines_for_ui(current_status)
            self.log_debug_lines(debug_lines)

    def log_debug_lines(self, debug_lines):
        """
        Procesa y muestra líneas de debug con formato apropiado.
        
        Args:
            debug_lines (list): Lista de líneas de debug a mostrar
            
        Determina automáticamente el nivel de log basado en el contenido
        de cada línea para aplicar colores y formato apropiados.
        
        TODO: Implementar parser más sofisticado para detección de niveles
        TODO: Agregar soporte para formato markdown en logs
        """
        try:
            for line in debug_lines:
                if line.strip():  
                    if "✓" in line:
                        level = "SUCCESS"
                    elif "✗" in line:
                        level = "ERROR" if "Internet" in line or "Archivo" in line else "WARNING"
                    elif "🎯" in line:
                        level = "SUCCESS" if "LISTO" in line else "ERROR"
                    else:
                        level = "INFO"
                    
                    self.log_widget.add_log(line, level)
                else:
                    self.log_widget.add_log("", "INFO")
                    
        except Exception as e:
            self.log_widget.add_log(f"Error procesando líneas de debug: {str(e)}", "ERROR")

    def update_uptime_display(self):
        """
        Actualiza la visualización del tiempo de ejecución cada segundo.
        
        Calcula y formatea el tiempo transcurrido desde que se inició
        el bot y actualiza el widget correspondiente en tiempo real.
        
        TODO: Agregar opción de mostrar tiempo en diferentes formatos
        TODO: Implementar histórico de tiempos de ejecución por sesión
        TODO: Mostrar tiempo promedio de análisis por elemento
        """
        try:
            if self.start_time and self.bot_running:
                current_time = get_current_timestamp()
                duration = current_time - self.start_time
                
                total_seconds = int(duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.uptime_widget.update_value(time_str)
                
        except Exception as e:
            print(f"Error actualizando tiempo de ejecución: {e}")

    def open_config(self):
        """
        Abre la ventana de configuración modal.
        
        Crea y muestra la ventana de configuración, conectando
        las señales apropiadas para manejar cambios de configuración.
        
        TODO: Implementar configuración no modal para edición en tiempo real
        TODO: Agregar validación de configuración antes de cerrar ventana
        TODO: Implementar backup de configuración antes de cambios
        """
        try:
            config_window = ConfigWindow(self.config, self)
            config_window.config_saved.connect(self.on_config_saved)
            config_window.exec_()
        except Exception as e:
            self.log_widget.add_log(f"Error abriendo configuración: {str(e)}", "ERROR")

    def on_file_selected(self, file_path):
        """
        Maneja la selección de un nuevo archivo para análisis.
        
        Args:
            file_path (str): Ruta del archivo seleccionado
            
        Procesa la selección de archivo, actualiza la UI con información
        del archivo y ejecuta verificaciones completas del sistema.
        
        TODO: Implementar validación de contenido del archivo seleccionado
        TODO: Mostrar preview de los primeros registros del archivo
        TODO: Detectar automáticamente formato y estructura del archivo
        """
        self.selected_file = file_path
        
        file_info = get_file_info(file_path)
        if file_info:
            self.log_widget.add_log(
                f"📁 Archivo seleccionado: {file_info['name']} ({file_info['size']})", 
                "SUCCESS"
            )
            self.status_bar.showMessage(
                f"Archivo: {file_info['name']} - {file_info['size']}"
            )
        else:
            self.log_widget.add_log(f"📁 Archivo seleccionado: {os.path.basename(file_path)}", "SUCCESS")
            self.status_bar.showMessage(f"Archivo cargado: {os.path.basename(file_path)}")
        
        self.show_complete_debug_in_logs()
        self.update_start_button_state()

    def on_config_saved(self, new_config):
        """
        Maneja el guardado de nueva configuración.
        
        Args:
            new_config (dict): Nueva configuración guardada
            
        Actualiza la configuración local, reporta el cambio en logs
        y ejecuta verificaciones completas del sistema.
        
        TODO: Implementar validación de configuración antes de aplicar
        TODO: Mantener histórico de configuraciones para rollback
        TODO: Notificar qué elementos específicos de configuración cambiaron
        """
        self.config = new_config
        self.log_widget.add_log("⚙️ Configuración guardada exitosamente", "SUCCESS")
        self.status_bar.showMessage("Configuración actualizada")
        
        self.show_complete_debug_in_logs()
        self.update_start_button_state()

    def toggle_bot(self):
        """
        Alterna entre iniciar y detener el bot de análisis.
        
        Función principal que coordina el inicio o detención del bot
        basado en su estado actual, manejando errores apropiadamente.
        
        TODO: Agregar confirmación antes de detener bot en proceso
        TODO: Implementar pausa/resume además de start/stop
        TODO: Guardar estado de ejecución para recuperación en caso de falla
        """
        try:
            if not self.bot_running:
                self.start_bot()
            else:
                self.stop_bot()
        except Exception as e:
            self.log_widget.add_log(f"Error alternando estado del bot: {str(e)}", "ERROR")

    def start_bot(self):
        """
        Inicia el proceso de análisis del bot.
        
        Valida todos los requisitos, inicializa contadores y timers,
        actualiza la UI y comienza el proceso de análisis de datos.
        
        TODO: Implementar checkpoint/resume para análisis largos
        TODO: Agregar estimación de tiempo de finalización
        TODO: Implementar procesamiento en background thread
        TODO: Agregar opción de análisis incremental
        """
        try:
            is_valid, error_message = validate_system_ready(self.config, self.selected_file)
            
            if not is_valid:
                self.show_error("No se puede iniciar", error_message)
                return
            
            self.start_time = get_current_timestamp()
            self.analysis_count = 0
            self.bot_running = True
            
            self.status_widget.update_value("Ejecutándose")
            self.status_widget.update_color("#27ae60")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            self.uptime_timer.start(1000)
            
            self.log_widget.add_log("🚀 BOT INICIADO - Comenzando análisis...", "SUCCESS")
            self.log_widget.add_log(f"📊 Archivo: {os.path.basename(self.selected_file)}", "INFO")
            self.log_widget.add_log(f"⚙️ Estrategia: {self.config.get('strategy', 'N/A')}", "INFO")
            
            start_date = self.config.get('start_date', 'N/A')
            end_date = self.config.get('end_date', 'N/A')
            
            from Utiles.utils import get_funds_config_summary
            funds_summary = get_funds_config_summary(self.config)
            self.log_widget.add_log(f"💰 Fondos: {funds_summary}", "INFO")
            self.log_widget.add_log(f"📅 Período: {start_date} a {end_date}", "INFO")
            
            self.status_bar.showMessage("Bot ejecutándose - Analizando enlaces...")
            QtCore.QTimer.singleShot(2000, self.simulate_analysis)
            
        except Exception as e:
            self.log_widget.add_log(f"Error iniciando bot: {str(e)}", "ERROR")
            self.bot_running = False
            
    def stop_bot(self):
        """
        Detiene el proceso de análisis del bot.
        
        Finaliza el análisis actual, calcula métricas finales,
        actualiza la UI y genera resumen de la ejecución.
        
        TODO: Implementar guardado de progreso parcial al detener
        TODO: Agregar opción de generar reporte parcial
        TODO: Permitir cancelación suave vs. cancelación forzada
        """
        try:
            if self.bot_running:
                end_time = get_current_timestamp()
                
                if self.start_time:
                    summary = format_execution_summary(self.start_time, end_time, self.analysis_count)
                    self.log_widget.add_log(summary, "INFO")
                
                self.bot_running = False
                self.uptime_timer.stop()
                
                self.status_widget.update_value("Detenido")
                self.status_widget.update_color("#e74c3c")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                
                self.uptime_widget.update_value("00:00:00")
                
                self.log_widget.add_log("⏹️ BOT DETENIDO por el usuario", "WARNING")
                self.status_bar.showMessage("Bot detenido - Listo para nueva ejecución")
                
        except Exception as e:
            self.log_widget.add_log(f"Error deteniendo bot: {str(e)}", "ERROR")

    def simulate_analysis(self):
        """
        Simula el proceso de análisis para demostración.
        
        NOTA: Esta es una función temporal para demostración.
        En producción debe ser reemplazada por la lógica real de análisis.
        
        TODO: REEMPLAZAR con lógica real de análisis de opciones
        TODO: Implementar procesamiento de datos reales del archivo
        TODO: Agregar cálculo de métricas financieras reales
        TODO: Integrar con APIs de datos financieros
        """
        if self.bot_running:
            self.analysis_count += 1
            self.analyzed_widget.update_value(str(self.analysis_count))
            
            if self.analysis_count % 5 == 0:
                self.log_widget.add_log(f"📈 Procesados {self.analysis_count} enlaces", "SUCCESS")
            
            if self.analysis_count < 20:  
                QtCore.QTimer.singleShot(1500, self.simulate_analysis)
            else:
                self.bot_completed()

    def bot_completed(self):
        """
        Maneja la finalización exitosa del análisis automático.
        
        Se ejecuta cuando el bot completa todos los análisis programados,
        genera reportes finales y actualiza la UI con el estado final.
        
        TODO: Generar archivo Excel con resultados reales
        TODO: Implementar envío de notificaciones de finalización
        TODO: Agregar validación de integridad de resultados
        TODO: Implementar backup automático de resultados
        """
        try:
            if self.bot_running:
                end_time = get_current_timestamp()
                
                if self.start_time:
                    summary = format_execution_summary(self.start_time, end_time, self.analysis_count)
                    self.log_widget.add_log(summary, "SUCCESS")
                
                self.bot_running = False
                self.uptime_timer.stop()
                
                self.status_widget.update_value("Completado")
                self.status_widget.update_color("#3498db")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                
                self.log_widget.add_log("✅ ANÁLISIS COMPLETADO EXITOSAMENTE", "SUCCESS")
                self.log_widget.add_log(f"🎯 Total procesado: {self.analysis_count} enlaces", "SUCCESS")
                self.status_bar.showMessage("Análisis completado - Revise los resultados")
                
        except Exception as e:
            self.log_widget.add_log(f"Error finalizando bot: {str(e)}", "ERROR")

    def show_error(self, title, message):
        """
        Muestra un diálogo de error personalizado.
        
        Args:
            title (str): Título del diálogo de error
            message (str): Mensaje de error a mostrar
            
        Crea y muestra un diálogo de error con el estilo de la aplicación,
        con fallback a logs si el diálogo falla.
        
        TODO: Implementar diferentes tipos de diálogos (warning, info, question)
        TODO: Agregar logging automático de errores mostrados
        TODO: Implementar sistema de reportes de errores
        """
        try:
            error_dialog = ErrorDialog(self, title, message)
            error_dialog.exec_()
        except Exception as e:
            self.log_widget.add_log(f"ERROR - {title}: {message}", "ERROR")

    def show_about(self):
        """
        Muestra el diálogo "Acerca de" con información de la aplicación.
        
        Presenta información sobre la versión, desarrollador y
        derechos de autor de OmegaBot con estilo consistente.
        
        TODO: Agregar información de versión dinámica desde archivo
        TODO: Incluir enlaces a documentación y soporte
        TODO: Mostrar información de librerías y dependencias utilizadas
        TODO: Agregar checking de actualizaciones disponibles
        """
        try:
            about_dialog = QtWidgets.QMessageBox(self)
            about_dialog.setWindowTitle("Acerca de OmegaBot")
            about_dialog.setText("OmegaBot v1.0")
            about_dialog.setInformativeText(
                "Sistema de análisis de backtesting para opciones financieras.\n\n"
                "Desarrollado por Nexus Corp\n"
                "© 2025 Todos los derechos reservados"
            )
            about_dialog.setIcon(QtWidgets.QMessageBox.Information)
            about_dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #2c3e50;
                    color: white;
                }
                QMessageBox QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            about_dialog.exec_()
        except Exception as e:
            self.log_widget.add_log(f"Error mostrando diálogo 'Acerca de': {str(e)}", "ERROR")

    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la aplicación.
        
        Args:
            event (QCloseEvent): Evento de cierre de Qt
            
        Realiza limpieza necesaria al cerrar, incluyendo detener el bot
        si está ejecutándose y guardar logs de la sesión.
        
        TODO: Implementar confirmación antes de cerrar si hay análisis en curso
        TODO: Guardar estado de la aplicación para restaurar en próximo inicio
        TODO: Implementar limpieza de archivos temporales
        TODO: Agregar backup automático de configuración al cerrar
        """
        try:
            if self.bot_running:
                self.stop_bot()
            
            log_content = self.log_widget.get_plain_logs()
            success, result = save_logs(log_content)
            
            if success:
                print(f"Logs guardados en: {result}")
            else:
                print(f"Error guardando logs: {result}")
            
            event.accept()
            
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
            event.accept()