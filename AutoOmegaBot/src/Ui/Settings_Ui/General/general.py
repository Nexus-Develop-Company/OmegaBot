from PyQt5 import QtWidgets, QtCore, QtGui
from Utiles.assets import FOLDER_SVG
import os
from Utiles.utils import get_output_folder, get_system_documents_folder  # AGREGADO

class FilePathSelector(QtWidgets.QWidget):
    pathChanged = QtCore.pyqtSignal(str)
    
    def __init__(self, title, default_path=None, placeholder=None, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
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
        if placeholder:
            self.path_input.setPlaceholderText(placeholder)
        
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
        
        # Descripción
        # ARREGLADO: Usar ruta por defecto si no hay default_path
        if not default_path:
            default_path = get_output_folder()
        
        if default_path:
            self.path_input.setText(default_path)
        
        description = QtWidgets.QLabel()
        description.setStyleSheet("""
            font-size: 12px;
            color: #95a5a6;
            font-style: italic;
        """)
        description.setWordWrap(True)
        self.description_label = description
        layout.addWidget(description)
        
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
        MODIFICADO: Crear estructura AutoOmega Bot al seleccionar carpeta
        """
        # ARREGLADO: Usar ruta por defecto como punto de partida
        current_path = self.path_input.text() if self.path_input.text() else get_output_folder()
        
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta base (se creará AutoOmega Bot/Output dentro)",
            current_path,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            # AGREGADO: Crear estructura AutoOmega Bot/Output
            try:
                from Utiles.utils import ensure_autobot_structure
                final_output_path = ensure_autobot_structure(folder_path)
                
                # Mostrar la ruta final de Output
                self.path_input.setText(final_output_path)
                self.pathChanged.emit(final_output_path)
                
                # Actualizar descripción
                self.update_description(final_output_path)
                
            except Exception as e:
                # Fallback si hay error
                print(f"Error creando estructura: {e}")
                self.path_input.setText(folder_path)
                self.pathChanged.emit(folder_path)

    def update_description(self, path):
        """
        NUEVO: Actualizar descripción mostrando estructura creada
        """
        try:
            if path and "AutoOmega Bot" in path:
                # Mostrar que se creó la estructura completa
                base_path = path.split("AutoOmega Bot")[0].rstrip(os.sep)
                self.description_label.setText(
                    f"✅ Estructura creada en: {base_path}\n"
                    f"📁 Archivos Excel: {path}\n"
                    f"📁 Configuración: {os.path.join(os.path.dirname(path), 'Config')}\n"
                    f"📁 Logs: {os.path.join(os.path.dirname(path), 'Logs')}"
                )
            else:
                self.description_label.setText(f"Archivos se guardarán en: {path}")
        except Exception:
            self.description_label.setText(f"Archivos se guardarán en: {path}")

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
            default_output_path,
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