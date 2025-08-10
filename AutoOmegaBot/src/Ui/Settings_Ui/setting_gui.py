from PyQt5 import QtWidgets, QtCore, QtGui
from Ui.Settings_Ui.option_list_ui import OptionListUi
from Ui.Settings_Ui.General.general import GeneralPage
from Ui.Settings_Ui.Fecha.fecha import DatePage
from Ui.Settings_Ui.Estrategia.estrategia import StrategyPage
from Ui.Settings_Ui.status_widget import SystemStatusWidget
from Utiles.utils import load_config, save_config, validate_date_range

class ConfigWindow(QtWidgets.QDialog):
    config_saved = QtCore.pyqtSignal(dict)
    
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración")
        self.setModal(True)
        self.setStyleSheet("""
            QWidget { background-color: #181a1b; color: #fff; }
            QLabel { color: #fff; }
        """)
        
        # Tamaño del modal
        if parent:
            parent_size = parent.size()
            self.resize(int(parent_size.width() * 0.85), int(parent_size.height() * 0.85))
        else:
            self.resize(900, 650)
            
        self.setMinimumSize(700, 500)
        
        self.changes_made = False
        self.config = config or load_config()
        # NUEVO: Para compartir archivo seleccionado con widget de estado
        self.selected_file = getattr(parent, 'selected_file', None) if parent else None

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Menú lateral
        self.menu_list = OptionListUi(self)
        self.menu_list.setMinimumWidth(140)
        self.set_menu_width()
        self.menu_list.addItem("General")
        self.menu_list.addItem("Fecha")
        self.menu_list.addItem("Estrategia")
        self.menu_list.setCurrentRow(0)
        main_layout.addWidget(self.menu_list)

        # Contenedor derecho
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # NUEVO: Widget de estado del sistema
        self.status_widget = SystemStatusWidget()
        self.status_widget.set_config_data(self.config, self.selected_file)
        self.status_widget.setMaximumHeight(300)
        right_layout.addWidget(self.status_widget)
        
        # Stack de páginas
        self.stack = QtWidgets.QStackedWidget()
        right_layout.addWidget(self.stack)

        # Páginas
        self.general_page = GeneralPage(self.config, self)
        self.fecha_page = DatePage(self.config, self)
        self.estrategia_page = StrategyPage(self.config, self)
        self.stack.addWidget(self.general_page)
        self.stack.addWidget(self.fecha_page)
        self.stack.addWidget(self.estrategia_page)

        # Botones
        self.save_button = QtWidgets.QPushButton("Guardar", self)
        self.save_button.setStyleSheet("""
            background-color: #27ae60; color: #fff; border-radius: 8px; padding: 8px 24px;
            margin-bottom: 10px; margin-right: 10px; font-size: 14px;
        """)
        self.close_button = QtWidgets.QPushButton("Cerrar", self)
        self.close_button.setStyleSheet("""
            background-color: #e67e22; color: #fff; border-radius: 8px; padding: 8px 24px;
            margin-bottom: 10px; margin-right: 10px; font-size: 14px;
        """)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_button)
        btn_layout.addSpacing(5)
        btn_layout.addWidget(self.save_button)
        
        right_layout.addLayout(btn_layout)
        main_layout.addWidget(right_widget)

        # Señales
        self.save_button.clicked.connect(self.save_and_close)
        self.close_button.clicked.connect(self.reject)
        self.menu_list.currentRowChanged.connect(self.stack.setCurrentIndex)

        # Detectar cambios y actualizar estado
        for page in [self.general_page, self.fecha_page, self.estrategia_page]:
            page.changed.connect(self.on_config_changed)

        # Centrar respecto al parent
        if parent:
            geo = parent.geometry()
            self.move(geo.center() - self.rect().center())

    def on_config_changed(self):
        """
        NUEVO: Callback cuando cambia la configuración
        Actualiza el widget de estado en tiempo real
        """
        self.changes_made = True
        
        # Obtener configuración actual de todas las páginas
        current_config = self.get_config()
        
        # NUEVO: Actualizar widget de estado con nueva configuración
        self.status_widget.set_config_data(current_config, self.selected_file)

    def set_menu_width(self):
        width = self.width()
        if width < 900:
            self.menu_list.setFixedWidth(int(width * 0.18))
        else:
            self.menu_list.setFixedWidth(int(width * 0.15))

    def resizeEvent(self, event):
        self.set_menu_width()
        super().resizeEvent(event)

    def closeEvent(self, event):
        """Maneja el cierre del modal"""
        if self.changes_made:
            reply = QtWidgets.QMessageBox.question(
                self, "Cambios no guardados",
                "Hay cambios realizados, ¿está seguro de salir sin guardar?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.No:
                event.ignore()
                return
        event.accept()

    def save_and_close(self):
        """
        CORRIGIENDO: Usar validate_date_range en lugar de validate_dates
        UTILS: validate_date_range() - validación de fechas desde utils.py
        """
        config = self.get_config()
        
        # UTILS: Usar función correcta de utils.py
        valid, msg = validate_date_range(config.get("start_date", ""), config.get("end_date", ""))
        if not valid:
            QtWidgets.QMessageBox.critical(self, "Error de Validación", msg)
            return

        # UTILS: Guardar configuración usando utils.py
        if save_config(config):
            self.changes_made = False
            
            # NUEVO: Forzar actualización del widget de estado antes de cerrar
            self.status_widget.set_config_data(config, self.selected_file)
            
            self.config_saved.emit(config)
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")

    def get_config(self):
        config = {}
        config.update(self.general_page.get_config())
        config.update(self.fecha_page.get_config())
        config.update(self.estrategia_page.get_config())
        return config

    def save_config(self):
        """
        MODIFICADO: Validar estructura de carpetas antes de guardar
        """
        try:
            # Obtener configuración de todas las páginas
            config = {}
            
            # General
            general_config = self.general_page.get_config()
            config.update(general_config)
            
            # AGREGADO: Validar output_path antes de guardar
            if 'output_path' in config and config['output_path']:
                from Utiles.utils import validate_and_create_output_path
                validated_path = validate_and_create_output_path(config['output_path'])
                config['output_path'] = validated_path
                
                # Actualizar la página general con la ruta validada
                self.general_page.set_config({"output_path": validated_path})
            
            # Estrategia
            strategy_config = self.strategy_page.get_config()
            config["strategy"] = strategy_config
            
            # Fechas
            dates_config = self.dates_page.get_config()
            config.update(dates_config)
            
            # Guardar usando utils
            from Utiles.utils import save_config
            if save_config(config):
                self.show_success("Configuración guardada exitosamente")
                self.config_saved.emit(config)
                
                # AGREGADO: Mostrar información de estructura creada
                if 'output_path' in config and config['output_path']:
                    self.show_info(
                        "Estructura de carpetas",
                        f"Se creó la estructura completa:\n\n"
                        f"📁 Salida: {config['output_path']}\n"
                        f"📁 Config: {config['output_path'].replace('Output', 'Config')}\n"
                        f"📁 Logs: {config['output_path'].replace('Output', 'Logs')}"
                    )
            else:
                self.show_error("Error", "No se pudo guardar la configuración")
                
        except Exception as e:
            self.show_error("Error", f"Error guardando configuración: {str(e)}")

    def show_info(self, title, message):
        """
        NUEVO: Mostrar diálogo informativo
        """
        try:
            info_dialog = QtWidgets.QMessageBox(self)
            info_dialog.setWindowTitle(title)
            info_dialog.setText(message)
            info_dialog.setIcon(QtWidgets.QMessageBox.Information)
            info_dialog.setStyleSheet("""
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
            info_dialog.exec_()
        except Exception as e:
            print(f"Error mostrando diálogo info: {e}")
