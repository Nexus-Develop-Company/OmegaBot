from PyQt5 import QtWidgets, QtCore, QtGui
from Utiles.utils import get_system_status_summary

class SystemStatusWidget(QtWidgets.QWidget):
    """
    Widget que muestra el estado del sistema en tiempo real
    Utilizada por: setting_gui.py
    Propósito: Mostrar qué falta para que el sistema esté listo
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {}
        self.selected_file = None
        self.last_status = None  # Para detectar cambios
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Frame contenedor
        self.frame = QtWidgets.QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(52, 152, 219, 0.1);
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        frame_layout = QtWidgets.QVBoxLayout(self.frame)
        frame_layout.setSpacing(8)
        
        # Título
        title = QtWidgets.QLabel("Estado del Sistema")
        title.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #3498db;
            margin-bottom: 5px;
        """)
        frame_layout.addWidget(title)
        
        # Mensaje principal
        self.main_status = QtWidgets.QLabel("Verificando estado...")
        self.main_status.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
        """)
        frame_layout.addWidget(self.main_status)
        
        # Lista de elementos
        self.status_list = QtWidgets.QLabel()
        self.status_list.setStyleSheet("""
            font-size: 11px;
            color: #ecf0f1;
            line-height: 18px;
        """)
        self.status_list.setWordWrap(True)
        frame_layout.addWidget(self.status_list)
        
        layout.addWidget(self.frame)
    
    def set_config_data(self, config, selected_file):
        """Actualizar datos de configuración y verificar cambios"""
        self.config = config
        self.selected_file = selected_file
        self.check_and_update()
    
    def check_and_update(self):
        """Verificar cambios y actualizar solo si es necesario"""
        if not self.config:
            return
        
        # UTILS: Obtener resumen del estado actual
        current_summary = get_system_status_summary(self.config, self.selected_file)
        
        # MODIFICADO: Crear hash del estado para comparar (solo elementos obligatorios)
        current_status_hash = {
            'ready': current_summary['ready'],
            'missing_count': current_summary['missing_count'],
            'items': tuple(current_summary['items'])  # Solo elementos obligatorios ahora
        }
        
        # Solo actualizar si hay cambios
        if self.last_status != current_status_hash:
            self.last_status = current_status_hash
            self.update_status(current_summary)
    
    def update_status(self, summary):
        """Actualizar estado visual con el resumen proporcionado"""
        # Actualizar mensaje principal (sin iconos)
        main_message = summary["main_message"]
        # Quitar iconos del mensaje principal
        clean_message = main_message.replace("🎯 ", "").replace("⚠️ ", "")
        
        self.main_status.setText(clean_message)
        self.main_status.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
            background-color: {summary["status_color"]};
            color: white;
        """)
        
        # Actualizar lista de elementos (sin iconos)
        clean_items = []
        for item in summary["items"]:
            # Quitar iconos de cada elemento
            clean_item = item.replace("✅ ", "").replace("❌ ", "")
            clean_items.append(clean_item)
        
        items_text = "\n".join(clean_items)
        self.status_list.setText(items_text)
        
        # Cambiar color del borde según el estado
        if summary["ready"]:
            border_color = "#27ae60"
        else:
            border_color = "#e74c3c"
        
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(52, 152, 219, 0.1);
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)