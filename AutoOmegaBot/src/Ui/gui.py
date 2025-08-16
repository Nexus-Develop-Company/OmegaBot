from PyQt5 import QtWidgets, QtCore, QtGui
from Ui.Settings_Ui.setting_gui import ConfigWindow
# CARGA DESDE UTILS: Todas las funciones de lógica de negocio
from Utiles.utils import (
    load_config,              # Cargar configuración persistente
    get_connection_status,     # Estado formateado para UI
    validate_system_ready,     # Validación completa del sistema
    save_logs,                # Guardar logs al cerrar
    get_file_info,            # Info de archivo seleccionado
    get_validation_status,    # Estado detallado para logs
    get_debug_lines_for_ui,   # Líneas formateadas para UI
    get_current_timestamp,    # NUEVO: Timestamp actual
    format_execution_summary, # NUEVO: Resumen de ejecución
    get_debug_info_complete,   # AGREGADO: Debug completo y divertido
    
)
from Utiles.assets import *
import datetime
import os

class StatusWidget(QtWidgets.QWidget):
    def __init__(self, title, value, color="#2980b9", icon_svg=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)  # Más altura para que se vean las letras
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
        layout.setContentsMargins(20, 20, 20, 20)  # Más padding
        layout.setSpacing(15)
        
        
        # Textos con más espacio vertical
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 5, 0, 5)
        text_layout.setSpacing(8)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: normal; opacity: 0.9; color: white;")
        title_label.setMinimumHeight(20)  # Altura mínima para el título
        
        self.value_label = QtWidgets.QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        self.value_label.setMinimumHeight(35)  # Altura mínima para el valor
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        text_layout.addStretch()
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def update_value(self, value):
        self.value_label.setText(str(value))
    
    def update_color(self, color):
        # ARREGLADO: Mantener el color del texto siempre blanco
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
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

class LogWidget(QtWidgets.QTextEdit):
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
        
        # Para tracking de logs planos
        self.plain_logs = []

    def add_log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Guardar en lista plana para logs
        plain_message = f"[{timestamp}] {level}: {message}"
        self.plain_logs.append(plain_message)
        
        # Formatear para display
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
        """Obtener logs como texto plano para guardar en archivo"""
        return "\n".join(self.plain_logs)

class FileUploadButton(QtWidgets.QPushButton):
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
        return self.selected_file

class ErrorDialog(QtWidgets.QDialog):
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmegaBot - Options Backtest Analysis")
        self.setMinimumSize(1000, 700)
        
        # Establecer el logo como icono de la ventana
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
        # UTILS: Cargar configuración desde utils.py
        self.config = load_config()  
        self.selected_file = None
        
        # NUEVO: Para tracking de cambios en logs
        self.last_system_status = None
        
        # NUEVO: Para tracking de tiempo de ejecución
        self.start_time = None
        self.analysis_count = 0
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Timer para conexión
        self.connection_timer = QtCore.QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(5000)
        
        # Timer para logs
        self.status_timer = QtCore.QTimer()
        self.status_timer.timeout.connect(self.check_system_status_changes)
        self.status_timer.start(5000)
        
        # NUEVO: Timer para actualizar tiempo de ejecución cada segundo
        self.uptime_timer = QtCore.QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime_display)
        
        # Revisión inicial
        QtCore.QTimer.singleShot(1000, self.initial_system_check)

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(20)  # Más espacio entre elementos

        # Header
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

        # Panel de estadísticas con más altura
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

        # Botón de archivo simple
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addStretch()
        
        self.file_upload_btn = FileUploadButton()
        self.file_upload_btn.file_selected.connect(self.on_file_selected)
        
        file_layout.addWidget(self.file_upload_btn)
        file_layout.addStretch()
        
        main_layout.addLayout(file_layout)

        # Panel de control
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

        # ALTERNATIVA: Layout específico para logs con spacing controlado
        logs_container = QtWidgets.QWidget()
        logs_layout = QtWidgets.QVBoxLayout(logs_container)
        logs_layout.setContentsMargins(0, 0, 0, 0)  # Sin margen
        logs_layout.setSpacing(0)  # Solo 5px entre label y widget
        
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
                margin-top: 0px;  /* Sin margen superior */
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
        
        # OPCIÓN 2: Mantener Ctrl+Q específico
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
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sistema listo - Cargar archivo y configurar estrategia antes de iniciar")
        
        # Widget de conexión en el status bar (lado derecho)
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
        
        # Agregar al status bar (lado derecho)
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # Actualizar estado inicial
        self.check_connection()

    def check_connection(self):
        """
        OPTIMIZADO: Usar función de utils para verificar conexión
        UTILS: get_connection_status() - obtiene estado formateado
        """
        # UTILS: Obtener estado desde utils.py
        is_connected, status_text = get_connection_status()
        
        # UI: Actualizar indicador visual (se mantiene igual)
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
        
        # OPTIMIZADO: Actualizar botón solo si no está ejecutándose
        if not self.bot_running:
            self.update_start_button_state()
        
        return is_connected

    def update_start_button_state(self):
        """
        OPTIMIZADO: Usar validación completa de utils.py
        UTILS: validate_system_ready() - validación completa del sistema
        """
        # UTILS: Validación completa desde utils.py
        is_valid, error_message = validate_system_ready(self.config, self.selected_file)
        
        # UI: Actualizar estado del botón
        self.start_btn.setEnabled(is_valid)
        self.start_btn.setToolTip(error_message if not is_valid else "")

    def initial_system_check(self):
        """
        MODIFICADO: Mostrar debug completo en logs (no en consola)
        """
        self.log_widget.add_log("Iniciando OmegaBot - Verificando sistema...", "INFO")
        
        # UTILS: Obtener estado inicial del sistema
        initial_status = get_validation_status(self.config, self.selected_file)
        
        # MODIFICADO: Mostrar debug completo en logs en lugar de consola
        self.show_complete_debug_in_logs()
        
        # Establecer estado inicial para tracking
        self.last_system_status = {
            'internet': initial_status['internet'],
            'file_valid': initial_status['file_valid'],
            'dates_valid': initial_status['dates_valid'],
            'overall_valid': initial_status['overall_valid']
        }
        
        # UTILS: Actualizar botón basado en estado inicial
        self.update_start_button_state()

    def show_complete_debug_in_logs(self):
        """
        ARREGLADO: Debug divertido como el original + separación de carpetas
        """
        try:
            # UTILS: Obtener información completa de debug
            debug_info = get_debug_info_complete(self.config, self.selected_file)
            status = debug_info['status']
            
            # Header divertido igual que en consola
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            self.log_widget.add_log("🤖 OMEGABOT - ESTADO COMPLETO DEL SISTEMA 🤖", "INFO")
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            
            # 1. Estado de Internet con info detallada
            if status['internet']:
                self.log_widget.add_log(f"🌐 Internet: ✅ CONECTADO - {debug_info['connection_info']}", "SUCCESS")
            else:
                self.log_widget.add_log(f"🌐 Internet: ❌ DESCONECTADO - {debug_info['connection_info']}", "ERROR")
            
            # 2. Estado del archivo con info detallada
            if status['file_valid']:
                self.log_widget.add_log(f"📄 Archivo: ✅ VÁLIDO{debug_info['file_info']}", "SUCCESS")
            else:
                self.log_widget.add_log("📄 Archivo: ❌ NO SELECCIONADO - ¡Sube tu archivo primero! 📁", "ERROR")
            
            # 3. Estado de fechas con info detallada
            if status['dates_valid']:
                self.log_widget.add_log(f"📅 Fechas: ✅ CONFIGURADAS{debug_info['dates_info']}", "SUCCESS")
            else:
                self.log_widget.add_log("📅 Fechas: ⚠️ NO CONFIGURADAS - ¡Ve a configuración! ⚙️", "WARNING")
            
            # 4. Estrategia como informativa (igual que antes)
            self.log_widget.add_log(f"⚙️ Estrategia: ℹ️ INFORMATIVA{debug_info['strategy_info']}", "INFO")
            
            self.log_widget.add_log(f"⚙️ Fondos y Asignación: ℹ️ INFORMATIVA{debug_info['funds_info']}", "INFO")
            
            # 5. SEPARADOR para carpetas
            self.log_widget.add_log("🎯" + "-"*30 + " CARPETAS " + "-"*30, "INFO")
            
            # 6. Carpeta de salida (configurable)
            if debug_info['general_info']:
                self.log_widget.add_log(f"📊 Salida Excel: ✅ CONFIGURABLE{debug_info['general_info']}", "SUCCESS")
            
            # 7. Carpetas fijas (Config y Logs)
            self.log_widget.add_log(f"⚙️ Configuración: 🔒 FIJO - {debug_info['config_path']}", "INFO")
            self.log_widget.add_log(f"📋 Logs: 🔒 FIJO - {debug_info['logs_path']}", "INFO")
            
            # Separador decorativo
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            
            # Estado general final CON ESTILO DIVERTIDO
            if status['overall_valid']:
                self.log_widget.add_log("🚀 ESTADO GENERAL: ✅ ¡LISTO PARA DESPEGAR! 🎉", "SUCCESS")
                self.log_widget.add_log("💪 ¡Todo perfecto! El bot está listo para analizar 📈", "SUCCESS")
                self.log_widget.add_log("🎯 ¡Dale click a 'Iniciar Test' y vamos a hacer magia! ✨", "SUCCESS")
            else:
                self.log_widget.add_log("🛑 ESTADO GENERAL: ❌ NO LISTO - ¡Faltan cositas! 😅", "ERROR")
                self.log_widget.add_log("🔧 Revisa los elementos marcados con ❌ o ⚠️", "ERROR")
                self.log_widget.add_log("😊 ¡Tranquilo! Solo faltan unos ajustes y estaremos listos 💪", "WARNING")
            
            # Mostrar errores específicos con ESTILO DIVERTIDO
            if not status['overall_valid'] and status['errors']:
                self.log_widget.add_log("🎯" + "="*50, "INFO")
                self.log_widget.add_log("🔍 DETALLES DE LO QUE FALTA (¡No te preocupes, es fácil!):", "WARNING")
                for i, error in enumerate(status['errors'], 1):
                    emoji = ["🔸", "🔹", "🔶", "🔷"][i % 4]
                    self.log_widget.add_log(f"  {emoji} {error} - ¡Vamos a arreglarlo! 💪", "ERROR")
            
            # Footer divertido
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            self.log_widget.add_log(f"🕐 Verificación completada: {datetime.datetime.now().strftime('%H:%M:%S')}", "INFO")
            self.log_widget.add_log("🤖 OmegaBot está aquí para ayudarte - ¡Let's go! 🚀", "INFO")
            self.log_widget.add_log("🎯" + "="*50, "INFO")
            
        except Exception as e:
            self.log_widget.add_log(f"💥 Error mostrando debug completo: {str(e)}", "ERROR")
            self.log_widget.add_log("😅 ¡Ups! Algo falló, pero seguimos adelante 💪", "WARNING")

    def check_system_status_changes(self):
        """
        MODIFICADO: Usar debug simplificado para cambios (no completo)
        """
        # UTILS: Obtener estado actual detallado
        current_status = get_validation_status(self.config, self.selected_file)
        
        # Crear hash del estado para comparar
        current_status_hash = {
            'internet': current_status['internet'],
            'file_valid': current_status['file_valid'],
            'dates_valid': current_status['dates_valid'],
            'overall_valid': current_status['overall_valid']
        }
        
        # Solo loggear si hay cambios
        if self.last_system_status != current_status_hash:
            self.last_system_status = current_status_hash
            
            # MODIFICADO: Mostrar cambio más compacto (no debug completo)
            self.log_widget.add_log("🔄 CAMBIO DETECTADO EN EL SISTEMA", "INFO")
            
            # UTILS: Obtener líneas de debug formateadas usando función de utils
            debug_lines = get_debug_lines_for_ui(current_status)
            
            # Loggear cada línea del debug con formato apropiado
            self.log_debug_lines(debug_lines)

    def log_debug_lines(self, debug_lines):
        """
        Loggear líneas de debug con formato apropiado
        """
        try:
            for line in debug_lines:
                if line.strip():  # Solo loggear líneas no vacías
                    # Determinar tipo de log basado en el contenido
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
                    # Línea vacía para separación
                    self.log_widget.add_log("", "INFO")
                    
        except Exception as e:
            self.log_widget.add_log(f"Error procesando líneas de debug: {str(e)}", "ERROR")

    def update_uptime_display(self):
        """
        Actualizar display de tiempo de ejecución cada segundo
        """
        try:
            if self.start_time and self.bot_running:
                # Calcular tiempo transcurrido
                current_time = get_current_timestamp()
                duration = current_time - self.start_time
                
                # Formatear en HH:MM:SS
                total_seconds = int(duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                # Actualizar widget
                self.uptime_widget.update_value(time_str)
                
        except Exception as e:
            print(f"Error actualizando tiempo de ejecución: {e}")

    def open_config(self):
        """
        NUEVO: Abrir ventana de configuración
        """
        try:
            config_window = ConfigWindow(self.config, self)
            config_window.config_saved.connect(self.on_config_saved)
            config_window.exec_()
        except Exception as e:
            self.log_widget.add_log(f"Error abriendo configuración: {str(e)}", "ERROR")

    def on_file_selected(self, file_path):
        """
        MODIFICADO: Debug completo al seleccionar archivo
        """
        self.selected_file = file_path
        
        # UTILS: Obtener información del archivo
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
        
        # MODIFICADO: Mostrar debug completo después de seleccionar archivo
        self.show_complete_debug_in_logs()
        
        # UTILS: Revalidar usando utils
        self.update_start_button_state()

    def on_config_saved(self, new_config):
        """
        MODIFICADO: Debug completo al guardar configuración
        """
        self.config = new_config
        self.log_widget.add_log("⚙️ Configuración guardada exitosamente", "SUCCESS")
        self.status_bar.showMessage("Configuración actualizada")
        
        # MODIFICADO: Mostrar debug completo después de guardar configuración
        self.show_complete_debug_in_logs()
        
        # UTILS: Revalidar usando utils
        self.update_start_button_state()

    def toggle_bot(self):
        """
        NUEVO: Alternar estado del bot (iniciar/detener)
        """
        try:
            if not self.bot_running:
                # Iniciar bot
                self.start_bot()
            else:
                # Detener bot
                self.stop_bot()
        except Exception as e:
            self.log_widget.add_log(f"Error alternando estado del bot: {str(e)}", "ERROR")

    def start_bot(self):
        """
        SIMPLIFICADO: Las fechas ya están en MM/DD/YYYY
        """
        try:
            # ...existing code hasta logs...
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
            
            # SIMPLIFICADO: Las fechas ya están en MM/DD/YYYY
            start_date = self.config.get('start_date', 'N/A')
            end_date = self.config.get('end_date', 'N/A')
            
            # AGREGADO: Información de fondos
            from Utiles.utils import get_funds_config_summary
            funds_summary = get_funds_config_summary(self.config)
            self.log_widget.add_log(f"💰 Fondos: {funds_summary}", "INFO")
            
            
            # SIN CONVERSIÓN - usar directamente
            self.log_widget.add_log(f"📅 Período: {start_date} a {end_date}", "INFO")
            
            self.status_bar.showMessage("Bot ejecutándose - Analizando enlaces...")
            
            QtCore.QTimer.singleShot(2000, self.simulate_analysis)
            
          
        except Exception as e:
            self.log_widget.add_log(f"Error iniciando bot: {str(e)}", "ERROR")
            self.bot_running = False
            
    def stop_bot(self):
        """
        NUEVO: Detener el bot de análisis
        """
        try:
            if self.bot_running:
                # Calcular tiempo total
                end_time = get_current_timestamp()
                
                # UTILS: Generar resumen de ejecución
                if self.start_time:
                    summary = format_execution_summary(self.start_time, end_time, self.analysis_count)
                    self.log_widget.add_log(summary, "INFO")
                
                # Marcar como detenido
                self.bot_running = False
                self.uptime_timer.stop()
                
                # Actualizar UI
                self.status_widget.update_value("Detenido")
                self.status_widget.update_color("#e74c3c")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                
                # Reset tiempo si se detiene manualmente
                self.uptime_widget.update_value("00:00:00")
                
                # Log de finalización
                self.log_widget.add_log("⏹️ BOT DETENIDO por el usuario", "WARNING")
                self.status_bar.showMessage("Bot detenido - Listo para nueva ejecución")
                
        except Exception as e:
            self.log_widget.add_log(f"Error deteniendo bot: {str(e)}", "ERROR")

    def simulate_analysis(self):
        """
        NUEVO: Simulación de análisis (reemplazar con lógica real)
        """
        if self.bot_running:
            # Simular progreso
            self.analysis_count += 1
            self.analyzed_widget.update_value(str(self.analysis_count))
            
            # Simular logs de análisis
            if self.analysis_count % 5 == 0:
                self.log_widget.add_log(f"📈 Procesados {self.analysis_count} enlaces", "SUCCESS")
            
            # Continuar simulación o terminar
            if self.analysis_count < 20:  # Simular 20 análisis
                QtCore.QTimer.singleShot(1500, self.simulate_analysis)
            else:
                # Terminar automáticamente
                self.bot_completed()

    def bot_completed(self):
        """
        NUEVO: Bot completó su ejecución automáticamente
        """
        try:
            if self.bot_running:
                # Calcular tiempo total
                end_time = get_current_timestamp()
                
                # UTILS: Generar resumen de ejecución
                if self.start_time:
                    summary = format_execution_summary(self.start_time, end_time, self.analysis_count)
                    self.log_widget.add_log(summary, "SUCCESS")
                
                # Marcar como completado
                self.bot_running = False
                self.uptime_timer.stop()
                
                # Actualizar UI
                self.status_widget.update_value("Completado")
                self.status_widget.update_color("#3498db")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                
                # Log de finalización exitosa
                self.log_widget.add_log("✅ ANÁLISIS COMPLETADO EXITOSAMENTE", "SUCCESS")
                self.log_widget.add_log(f"🎯 Total procesado: {self.analysis_count} enlaces", "SUCCESS")
                self.status_bar.showMessage("Análisis completado - Revise los resultados")
                
                # TODO: Aquí se generaría y guardaría el archivo Excel de resultados
                
        except Exception as e:
            self.log_widget.add_log(f"Error finalizando bot: {str(e)}", "ERROR")

    def show_error(self, title, message):
        """
        NUEVO: Mostrar diálogo de error
        """
        try:
            error_dialog = ErrorDialog(self, title, message)
            error_dialog.exec_()
        except Exception as e:
            # Fallback a log si el diálogo falla
            self.log_widget.add_log(f"ERROR - {title}: {message}", "ERROR")

    def show_about(self):
        """
        NUEVO: Mostrar información "Acerca de"
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
        NUEVO: Manejar cierre de la aplicación
        """
        try:
            # Detener bot si está ejecutándose
            if self.bot_running:
                self.stop_bot()
            
            # UTILS: Guardar logs de la sesión
            log_content = self.log_widget.get_plain_logs()
            success, result = save_logs(log_content)
            
            if success:
                print(f"Logs guardados en: {result}")
            else:
                print(f"Error guardando logs: {result}")
            
            # Aceptar cierre
            event.accept()
            
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
            event.accept()