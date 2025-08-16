"""
Módulo de configuración de Fondos y Asignación
Maneja la configuración de capital inicial, márgenes, límites de trades y contratos.
"""

from PyQt5 import QtWidgets, QtCore, QtGui

class NumericInputWithLabel(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()
    
    def __init__(self, label_text, default_value, is_required=False, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label con indicador de obligatorio
        label_text_display = f"{label_text} *" if is_required else label_text
        label = QtWidgets.QLabel(label_text_display)
        label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            color: {'#e74c3c' if is_required else '#ecf0f1'};
        """)
        layout.addWidget(label)
        
        # Input más ancho
        self.input = QtWidgets.QLineEdit()
        self.input.setText(str(default_value))
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
                max-width: 200px;
            }
            QLineEdit:hover {
                border-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #1abc9c;
            }
        """)
        self.input.textChanged.connect(self.valueChanged.emit)
        layout.addWidget(self.input)
        
    def value(self):
        return self.input.text()
    
    def setValue(self, value):
        self.input.setText(str(value))

class SlidingToggle(QtWidgets.QWidget):
    """
    Switch deslizante real como los de móviles
    """
    toggled = QtCore.pyqtSignal(bool)
    
    def __init__(self, label_text, default_checked=False, parent=None):
        super().__init__(parent)
        self.is_checked = default_checked
        self.is_enabled = True
        self.label_text = label_text
        
        # Configuraciones del switch
        self.switch_width = 80
        self.switch_height = 40
        self.circle_radius = 14  # ARREGLADO: Radio más pequeño
        self.margin = 4
        
        # ARREGLADO: Inicializar _circle_position ANTES de usarla
        self._circle_position = self._get_initial_position()
        
        # Configurar layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        layout.addWidget(label)
        
        # Widget del switch
        self.switch_widget = QtWidgets.QWidget()
        self.switch_widget.setFixedSize(self.switch_width, self.switch_height)
        self.switch_widget.paintEvent = self.paint_switch
        self.switch_widget.mousePressEvent = self.mouse_press_event
        layout.addWidget(self.switch_widget)
        
        # Animación
        self.animation = QtCore.QPropertyAnimation(self, b"circle_position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.animation.finished.connect(self.switch_widget.update)
    
    def _get_initial_position(self):
        """ARREGLADO: Posiciones que mantienen el círculo DENTRO del óvalo"""
        if self.is_checked:
            # Posición ON - Círculo en el lado derecho DENTRO del óvalo
            return self.switch_width - self.circle_radius - 8
        else:
            # Posición OFF - Círculo en el lado izquierdo DENTRO del óvalo
            return self.circle_radius + 4
    
    def get_circle_position(self):
        """ARREGLADO: Posiciones que mantienen el círculo DENTRO del óvalo"""
        if self.is_checked:
            # ON: Círculo pegado al borde derecho INTERNO
            return self.switch_width - self.circle_radius - 8
        else:
            # OFF: Círculo pegado al borde izquierdo INTERNO
            return self.circle_radius + 4
    
    def paint_switch(self, event):
        """Dibujar el switch con círculo perfectamente contenido"""
        painter = QtGui.QPainter(self.switch_widget)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Colores según estado
        if not self.is_enabled:
            bg_color = QtGui.QColor("#7f8c8d")
            circle_color = QtGui.QColor("#bdc3c7")
            text_color = QtGui.QColor("#95a5a6")
        elif self.is_checked:
            bg_color = QtGui.QColor("#27ae60")
            circle_color = QtGui.QColor("#ecf0f1")
            text_color = QtGui.QColor("#ffffff")
        else:
            bg_color = QtGui.QColor("#e74c3c")
            circle_color = QtGui.QColor("#ecf0f1")
            text_color = QtGui.QColor("#ffffff")
        
        # ARREGLADO: Fondo del switch con padding adecuado
        rect = QtCore.QRect(3, 3, self.switch_width - 6, self.switch_height - 6)
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, rect.height() // 2, rect.height() // 2)
        
        # Asegurar que _circle_position existe
        if not hasattr(self, '_circle_position'):
            self._circle_position = self._get_initial_position()
        
        # ARREGLADO: Círculo más pequeño para quedar DENTRO
        circle_radius = self.circle_radius - 3  # Reducir más el radio
        circle_center = QtCore.QPoint(int(self._circle_position), self.switch_height // 2)
        painter.setBrush(circle_color)
        painter.drawEllipse(circle_center, circle_radius, circle_radius)
        
        # Texto ON/OFF
        painter.setPen(text_color)
        font = painter.font()
        font.setPointSize(8)  # Texto más pequeño
        font.setBold(True)
        painter.setFont(font)
        
        if self.is_checked:
            # Texto ON a la izquierda
            text_rect = QtCore.QRect(8, 0, self.switch_width // 2 - 8, self.switch_height)
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, "ON")
        else:
            # Texto OFF a la derecha
            text_rect = QtCore.QRect(self.switch_width // 2 + 8, 0, self.switch_width // 2 - 8, self.switch_height)
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, "OFF")
    
    def mouse_press_event(self, event):
        """Manejar clic del mouse"""
        if self.is_enabled and event.button() == QtCore.Qt.LeftButton:
            self.toggle()
    
    def toggle(self):
        """Alternar estado con animación"""
        if not self.is_enabled:
            return
            
        self.is_checked = not self.is_checked
        
        # ARREGLADO: Asegurar que _circle_position existe antes de animar
        if not hasattr(self, '_circle_position'):
            self._circle_position = self._get_initial_position()
        
        # Animar movimiento del círculo
        start_pos = self._circle_position
        end_pos = self.get_circle_position()
        
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
        
        self.toggled.emit(self.is_checked)
    
    def setChecked(self, checked):
        """Establecer estado sin animación"""
        self.is_checked = checked
        self._circle_position = self.get_circle_position()
        self.switch_widget.update()
    
    def setEnabled(self, enabled):
        """Habilitar/deshabilitar switch"""
        self.is_enabled = enabled
        self.switch_widget.update()
    
    def isChecked(self):
        """Obtener estado actual"""
        return self.is_checked
    
    # ARREGLADO: Propiedades para la animación
    def get_circle_position_property(self):
        """Getter para la propiedad de animación"""
        if not hasattr(self, '_circle_position'):
            self._circle_position = self._get_initial_position()
        return self._circle_position
    
    def set_circle_position_property(self, position):
        """Setter para la propiedad de animación"""
        self._circle_position = position
        self.switch_widget.update()
    
    # ARREGLADO: Usar nombres diferentes para evitar conflictos
    circle_position = QtCore.pyqtProperty(float, get_circle_position_property, set_circle_position_property)

class FundsPage(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Título
        title = QtWidgets.QLabel("💰 Configuración de Fondos")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Primera fila - Campos obligatorios
        row1 = QtWidgets.QHBoxLayout()
        row1.addStretch(1)
        
        # Starting Funds (obligatorio) - IGUAL QUE STRATEGY: Sin pasar config al constructor
        self.starting_funds = NumericInputWithLabel(
            "Starting Funds ($)", 
            "100000",  # Valor por defecto directo
            is_required=True
        )
        self.starting_funds.valueChanged.connect(self.changed.emit)
        row1.addWidget(self.starting_funds)
        
        row1.addSpacing(30)
        
        # Margin Allocation (obligatorio) - IGUAL QUE STRATEGY
        self.margin_allocation = NumericInputWithLabel(
            "Margin Allocation (%)", 
            "10",  # Valor por defecto directo
            is_required=True
        )
        self.margin_allocation.valueChanged.connect(self.changed.emit)
        row1.addWidget(self.margin_allocation)
        
        row1.addSpacing(30)
        
        # Max Contracts (obligatorio) - IGUAL QUE STRATEGY
        self.max_contracts = NumericInputWithLabel(
            "Max Contracts/Trade", 
            "1",  # Valor por defecto directo
            is_required=True
        )
        self.max_contracts.valueChanged.connect(self.changed.emit)
        row1.addWidget(self.max_contracts)
        
        row1.addStretch(1)
        layout.addLayout(row1)
        
        # Segunda fila - 4 componentes opcionales
        row2 = QtWidgets.QHBoxLayout()
        row2.addStretch(1)
        
        # Max Open Trades (opcional) - IGUAL QUE STRATEGY: Sin config
        self.max_open_trades = NumericInputWithLabel(
            "Max Open Trades", 
            ""  # Vacío por defecto
        )
        self.max_open_trades.valueChanged.connect(self.changed.emit)
        self.max_open_trades.valueChanged.connect(self.on_max_trades_changed)
        row2.addWidget(self.max_open_trades)
        
        row2.addSpacing(25)
        
        # Prune Oldest Trades - IGUAL QUE STRATEGY: Sin config
        self.prune_oldest = SlidingToggle(
            "Prune Oldest Trades",
            False  # Por defecto OFF
        )
        self.prune_oldest.toggled.connect(lambda checked: self.changed.emit())
        row2.addWidget(self.prune_oldest)
        
        row2.addSpacing(25)
        
        # Max Allocation Amount (opcional) - IGUAL QUE STRATEGY
        self.max_allocation = NumericInputWithLabel(
            "Max Allocation ($)", 
            ""  # Vacío por defecto
        )
        self.max_allocation.valueChanged.connect(self.changed.emit)
        row2.addWidget(self.max_allocation)
        
        row2.addSpacing(25)
        
        # Ignore Margin Requirements - IGUAL QUE STRATEGY: Sin config
        self.ignore_margin = SlidingToggle(
            "Ignore Margin Requirements",
            True  # Por defecto ON (como en strategy con qty=1)
        )
        self.ignore_margin.toggled.connect(lambda checked: self.changed.emit())
        row2.addWidget(self.ignore_margin)
        
        row2.addStretch(1)
        layout.addLayout(row2)
        
        layout.addStretch()
        
        # IGUAL QUE STRATEGY: Cargar config DESPUÉS de crear widgets
        if config:
            self.set_config(config)
        
        # Configurar estados iniciales
        self.on_max_trades_changed()
    
    def on_max_trades_changed(self):
        """
        Habilitar/deshabilitar Prune Oldest según si Max Open Trades tiene valor
        """
        try:
            max_trades_value = self.max_open_trades.value().strip()
            has_value = bool(max_trades_value)
            
            # Si no hay valor en Max Open Trades, deshabilitar Prune
            if not has_value:
                self.prune_oldest.setChecked(False)
                self.prune_oldest.setEnabled(False)
            else:
                # Habilitar Prune si hay valor
                self.prune_oldest.setEnabled(True)
                
        except Exception as e:
            print(f"Error en on_max_trades_changed: {e}")
    
    def get_config(self):
        """
        Obtener configuración actual de fondos
        
        Returns:
            dict: Configuración de fondos y asignación
        """
        config = {
            "starting_funds": self.starting_funds.value(),
            "margin_allocation_percent": self.margin_allocation.value(),
            "max_contracts_per_trade": self.max_contracts.value(),
            "max_open_trades": self.max_open_trades.value(),
            "max_allocation_amount": self.max_allocation.value(),
            "prune_oldest_trades": self.prune_oldest.isChecked(),
            "ignore_margin_requirements": self.ignore_margin.isChecked()
        }
        
        return config
    
    def set_config(self, config):
        """
        IGUAL QUE STRATEGY: Cargar config solo si existe en el dict
        """
        try:
            # IGUAL QUE STRATEGY: Solo establecer si existe la clave
            if "starting_funds" in config:
                self.starting_funds.setValue(config["starting_funds"])
                
            if "margin_allocation_percent" in config:
                self.margin_allocation.setValue(config["margin_allocation_percent"])
                
            if "max_contracts_per_trade" in config:
                self.max_contracts.setValue(config["max_contracts_per_trade"])
                
            if "max_open_trades" in config:
                self.max_open_trades.setValue(config["max_open_trades"])
                
            if "prune_oldest_trades" in config:
                self.prune_oldest.setChecked(config["prune_oldest_trades"])
                
            if "ignore_margin_requirements" in config:
                self.ignore_margin.setChecked(config["ignore_margin_requirements"])
                
            if "max_allocation_amount" in config:
                self.max_allocation.setValue(config["max_allocation_amount"])
            
            # Actualizar estados dependientes
            self.on_max_trades_changed()

        except Exception as e:
            print(f"❌ Error en FundsPage.set_config(): {e}")