from PyQt5 import QtWidgets, QtCore, QtGui
from Utiles.assets import FOLDER_SVG
import os
from Utiles.utils import get_output_folder, get_system_documents_folder  # AGREGADO

class FilePathSelector(QtWidgets.QWidget):
    pathChanged = QtCore.pyqtSignal(str)
    
    def __init__(self, title, description, placeholder_text="Selecciona una carpeta...", parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # AGREGADO: Label de descripción que faltaba
        self.description_label = QtWidgets.QLabel(description)
        self.description_label.setStyleSheet("""
            font-size: 11px;
            color: #95a5a6;
            font-style: italic;
        """)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        
        # Título
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ecf0f1;
            margin-bottom: 5px;
        """)
        layout.addWidget(title_label)
        
        # Contenedor de input y botón
        input_container = QtWidgets.QHBoxLayout()
        input_container.setSpacing(10)
        
        # Input de ruta
        self.path_input = QtWidgets.QLineEdit()
        if placeholder_text:
            self.path_input.setPlaceholderText(placeholder_text)
        
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px 15px;
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
        
        # Conectar cambios
        self.path_input.textChanged.connect(self.on_path_changed)
        
        # Botón de examinar
        browse_btn = QtWidgets.QPushButton("Examinar...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        browse_btn.clicked.connect(self.browse_folder)
        
        input_container.addWidget(self.path_input)
        input_container.addWidget(browse_btn)
        layout.addLayout(input_container)
        
        # ARREGLADO: Definir default_path antes de usarlo
        default_path = get_output_folder()
        
        if default_path:
            self.path_input.setText(default_path)
        
        # Actualizar descripción inicial
        self.update_description(default_path or "")

    def on_path_changed(self, path):
        """
        MODIFICADO: Validar y crear estructura al cambiar ruta
        """
        try:
            from Utiles.utils import validate_and_create_output_path
            
            if path:
                # Validar y crear estructura
                validated_path = validate_and_create_output_path(path)
                if validated_path != path:
                    # Se modificó la ruta, actualizar input
                    self.path_input.setText(validated_path)
                    path = validated_path
                
                self.update_description(path)
            else:
                # Si está vacío, usar ruta por defecto
                default_path = get_output_folder()
                self.description_label.setText(f"Usando ruta por defecto: {default_path}")
            
            self.pathChanged.emit(path)
            
        except Exception as e:
            print(f"Error validando ruta: {e}")
            self.pathChanged.emit(path)

    def browse_folder(self):
        """
        MODIFICADO: Solo crear carpeta Output en la ubicación seleccionada
        """
        current_path = self.path_input.text() if self.path_input.text() else get_output_folder()
        
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta para archivos Excel (se creará carpeta Output)",
            current_path,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            # MODIFICADO: Solo crear carpeta Output
            try:
                from Utiles.utils import ensure_output_structure
                final_output_path = ensure_output_structure(folder_path)
                
                # Mostrar la ruta final de Output
                self.path_input.setText(final_output_path)
                self.pathChanged.emit(final_output_path)
                
                # Actualizar descripción
                self.update_description(final_output_path)
                
            except Exception as e:
                print(f"Error creando carpeta Output: {e}")
                self.path_input.setText(folder_path)
                self.pathChanged.emit(folder_path)

    def update_description(self, path):
        """
        MODIFICADO: Mostrar que Config/Logs están fijos en Documents
        """
        try:
            from Utiles.utils import get_config_folder, get_logs_folder
            
            config_path = get_config_folder()
            logs_path = get_logs_folder()
            
            self.description_label.setText(
                f"📁 Archivos Excel: {path}\n"
                f"📁 Configuración (fijo): {config_path}\n"
                f"📁 Logs (fijo): {logs_path}"
            )
        except Exception:
            self.description_label.setText(f"Archivos Excel se guardarán en: {path}")

    def get_path(self):
        """
        AGREGADO: Devolver ruta actual o por defecto si está vacío
        """
        current_path = self.path_input.text().strip()
        if current_path:
            return current_path
        else:
            # Si está vacío, devolver ruta por defecto
            return get_output_folder()

    def set_path(self, path):
        """
        AGREGADO: Establecer ruta programáticamente
        """
        if path:
            self.path_input.setText(path)
            self.update_description(path)
        else:
            default_path = get_output_folder()
            self.path_input.setText(default_path)
            self.update_description(default_path)

class GeneralPage(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        # Layout principal simple - sin fondo especial, usar el de la ventana
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(40)
        
        # Título sin demasiados colores
        title = QtWidgets.QLabel("Configuración General")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Selector de carpeta de salida - estilo más simple
        # ARREGLADO: Asegurar que se use la ruta por defecto correcta
        default_output_path = config.get("output_path", "") or get_output_folder()
        
        self.output_path_selector = FilePathSelector(
            "Carpeta de Salida para Archivos Excel",
            "Selecciona la carpeta donde se guardarán los archivos Excel generados.",
            "Usar carpeta por defecto o seleccionar carpeta personalizada..."
        )
        self.output_path_selector.pathChanged.connect(self.changed.emit)
        main_layout.addWidget(self.output_path_selector)
        
        main_layout.addStretch()
    
    def get_config(self):
        """
        ARREGLADO: Usar get_path() que ahora existe
        """
        return {
            "output_path": self.output_path_selector.get_path()
        }

    def set_config(self, config):
        """
        ARREGLADO: Usar set_path() para establecer configuración
        """
        if "output_path" in config and config["output_path"]:
            self.output_path_selector.set_path(config["output_path"])
        else:
            # ARREGLADO: Establecer ruta por defecto completa si no hay configuración
            self.output_path_selector.set_path(get_output_folder())