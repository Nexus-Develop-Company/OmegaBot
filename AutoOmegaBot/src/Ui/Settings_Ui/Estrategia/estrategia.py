from PyQt5 import QtWidgets, QtCore, QtGui
from Utiles.assets import INFO_SVG
# CARGA DESDE UTILS: Funciones para obtener opciones de estrategias
from Utiles.utils import (
    get_available_strategies,  # Lista de estrategias disponibles
    get_pct_types,            # Tipos de porcentaje (Delta, Percentage, Strike)
    get_buy_sell_options,     # Opciones Buy/Sell
    get_call_put_options,     # Opciones Call/Put
    get_yes_no_options        # Opciones Yes/No
)

class ToggleButton(QtWidgets.QWidget):
    toggled = QtCore.pyqtSignal()
    
    def __init__(self, left_label, right_label, default, parent=None):
        super().__init__(parent)
        self.left_label = left_label
        self.right_label = right_label
        self.value_ = default if default in [left_label, right_label] else left_label
        self.is_right_selected = (self.value_ == right_label)
        
        self.setFixedHeight(40)
        self.setMinimumWidth(160)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Estilo base del widget
        self.setStyleSheet("""
            ToggleButton {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 20px;
            }
            ToggleButton:hover {
                border-color: #3498db;
            }
        """)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        # Fondo del toggle
        bg_color = QtGui.QColor("#2c3e50")
        border_color = QtGui.QColor("#34495e")
        
        if self.underMouse():
            border_color = QtGui.QColor("#3498db")
        
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.setPen(QtGui.QPen(border_color, 2))
        painter.drawRoundedRect(rect, 20, 20)
        
        # Posición del switch
        switch_width = rect.width() // 2
        switch_height = rect.height() - 6
        switch_y = 3
        
        if self.is_right_selected:
            switch_x = rect.width() // 2
            switch_color = QtGui.QColor("#27ae60")  # Verde para Buy (derecha)
        else:
            switch_x = 3
            switch_color = QtGui.QColor("#e74c3c")  # Rojo para Sell (izquierda)
        
        # Dibujar el switch activo
        painter.setBrush(QtGui.QBrush(switch_color))
        painter.setPen(QtGui.QPen(switch_color.darker(120), 1))
        switch_rect = QtCore.QRect(switch_x, switch_y, switch_width - 3, switch_height)
        painter.drawRoundedRect(switch_rect, 17, 17)
        
        # Textos
        painter.setPen(QtGui.QPen(QtGui.QColor("#ecf0f1"), 1))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        
        # Texto izquierdo (Sell)
        left_rect = QtCore.QRect(5, 0, switch_width - 10, rect.height())
        if not self.is_right_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff"), 1))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor("#95a5a6"), 1))
        painter.drawText(left_rect, QtCore.Qt.AlignCenter, self.left_label)
        
        # Texto derecho (Buy)
        right_rect = QtCore.QRect(switch_width + 5, 0, switch_width - 10, rect.height())
        if self.is_right_selected:
            painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff"), 1))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor("#95a5a6"), 1))
        painter.drawText(right_rect, QtCore.Qt.AlignCenter, self.right_label)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.toggle()

    def toggle(self):
        self.is_right_selected = not self.is_right_selected
        self.value_ = self.right_label if self.is_right_selected else self.left_label
        self.update()  # Forzar repintado
        self.toggled.emit()

    def value(self):
        return self.value_

    def setValue(self, value):
        if value in [self.left_label, self.right_label]:
            self.is_right_selected = (value == self.right_label)
            self.value_ = value
            self.update()

class CustomSelect(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()
    def __init__(self, options, default, parent=None, block_first_reselect=False):
        super().__init__(parent)
        self.options = options
        self.block_first_reselect = block_first_reselect
        self.selected = default if default in options else options[0]
        self.button = QtWidgets.QPushButton(self.selected, self)
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
                min-width: 180px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
            QPushButton::menu-indicator { 
                image: none; 
            }
        """)
        
        self.menu = QtWidgets.QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::item:disabled {
                color: #7f8c8d;
                background-color: #34495e;
            }
        """)
        
        self.actions = []
        for i, opt in enumerate(options):
            action = self.menu.addAction(opt)
            if i == 0 and block_first_reselect:
                action.setEnabled(False)
            action.triggered.connect(lambda checked, o=opt: self.set_selected(o))
            self.actions.append(action)
        self.button.setMenu(self.menu)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.button)

    def set_selected(self, value):
        if self.block_first_reselect and value == self.options[0]:
            return
        self.selected = value
        self.button.setText(value)
        if self.block_first_reselect:
            self.actions[0].setEnabled(False)
        self.changed.emit()

    def currentText(self):
        return self.selected

    def setCurrentText(self, value):
        self.set_selected(value)

class SwitchButton(QtWidgets.QWidget):
    toggled = QtCore.pyqtSignal(bool)
    
    def __init__(self, label_text, default=False, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.is_on = default
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Label
        self.label = QtWidgets.QLabel(label_text)
        self.label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        layout.addWidget(self.label)
        
        # Switch widget
        self.switch_widget = QtWidgets.QWidget()
        self.switch_widget.setFixedSize(50, 25)
        self.switch_widget.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.switch_widget)
        
        layout.addStretch()
    
    def paintEvent(self, event):
        # Solo pintar el switch widget
        if not hasattr(self, 'switch_widget'):
            return
            
        painter = QtGui.QPainter(self.switch_widget)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.switch_widget.rect()
        
        # Fondo del switch
        bg_color = QtGui.QColor("#27ae60" if self.is_on else "#e74c3c")
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.setPen(QtGui.QPen(bg_color.darker(120), 1))
        painter.drawRoundedRect(rect, 12, 12)
        
        # Círculo del switch
        circle_size = 18
        circle_x = rect.width() - circle_size - 4 if self.is_on else 4
        circle_y = (rect.height() - circle_size) // 2
        
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.setPen(QtGui.QPen(QtGui.QColor("#bdc3c7"), 1))
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.toggle()
    
    def toggle(self):
        self.is_on = not self.is_on
        self.update()
        self.toggled.emit(self.is_on)
    
    def setValue(self, value):
        self.is_on = bool(value)
        self.update()
    
    def value(self):
        return self.is_on

class NumericInputWithLabel(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(int)
    
    def __init__(self, label_text, default_value=0, min_val=0, max_val=999, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)
        self.spinbox.setValue(default_value)
        self.spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
                font-weight: bold;
                min-width: 50px;
                max-width: 80px;
            }
            QSpinBox:hover {
                border-color: #3498db;
            }
            QSpinBox:focus {
                border-color: #1abc9c;
            }
        """)
        self.spinbox.valueChanged.connect(self.valueChanged.emit)
        
        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        
        layout.addWidget(self.spinbox)
        layout.addWidget(label)
    
    def value(self):
        return self.spinbox.value()
    
    def setValue(self, value):
        self.spinbox.setValue(value)

class StrategyPage(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()
    def __init__(self, config, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        # Fila de tres componentes principales
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        
        # Ticker
        ticker_widget = QtWidgets.QWidget()
        ticker_layout = QtWidgets.QVBoxLayout(ticker_widget)
        ticker_layout.setContentsMargins(0, 0, 0, 0)
        ticker_layout.setSpacing(8)
        ticker_label = QtWidgets.QLabel("Ticker")
        ticker_label.setStyleSheet("""
            font-size: 15px; 
            font-weight: bold; 
            color: #ecf0f1;
            margin-bottom: 5px;
        """)
        ticker_layout.addWidget(ticker_label)
        self.ticker_select = CustomSelect(["SPX", "SPY", "IWM", "QQQ", "AAPL", "TSLA"], default=config["ticker"] if config and "ticker" in config else "SPY")
        self.ticker_select.button.clicked.connect(self.changed.emit)
        ticker_layout.addWidget(self.ticker_select)
        row.addWidget(ticker_widget)

        row.addSpacing(25)

        # Strategy
        strat_widget = QtWidgets.QWidget()
        strat_layout = QtWidgets.QVBoxLayout(strat_widget)
        strat_layout.setContentsMargins(0, 0, 0, 0)
        strat_layout.setSpacing(8)
        strat_label = QtWidgets.QLabel("Strategy")
        strat_label.setStyleSheet("""
            font-size: 15px; 
            font-weight: bold; 
            color: #ecf0f1;
            margin-bottom: 5px;
        """)
        strat_layout.addWidget(strat_label)
        self.strat_select = CustomSelect(
            ["Select strategy", "Butterfly", "Calendar", "Double Calendar", "Double Diagonal", "Iron Condor", "Iron Fly",
             "Long Call", "Long Call Spread", "Long Put", "Long Put Spread", "Ratio Spread",
             "Short Call", "Short Call Spread", "Short Put", "Short Put Spread",
             "Short Straddle", "Short Strangle"],
            default=config["strategy"] if config and "strategy" in config else "Select strategy",
            block_first_reselect=True
        )
        self.strat_select.changed.connect(self.changed.emit)
        strat_layout.addWidget(self.strat_select)
        row.addWidget(strat_widget)

        row.addSpacing(25)

        # Percentage
        pct_widget = QtWidgets.QWidget()
        pct_layout = QtWidgets.QVBoxLayout(pct_widget)
        pct_layout.setContentsMargins(0, 0, 0, 0)
        pct_layout.setSpacing(8)
        pct_label = QtWidgets.QLabel("Percentage type")
        pct_label.setStyleSheet("""
            font-size: 15px; 
            font-weight: bold; 
            color: #ecf0f1;
            margin-bottom: 5px;
        """)
        pct_layout.addWidget(pct_label)
        self.pct_select = CustomSelect(["Delta", "OTM", "Fixed Premium", "Strike Offset"], default=config["pct_type"] if config and "pct_type" in config else "Delta")
        self.pct_select.button.clicked.connect(self.changed.emit)
        pct_layout.addWidget(self.pct_select)
        row.addWidget(pct_widget)

        row.addStretch(1)
        layout.addLayout(row)

        # Segunda fila: Toggle buttons y campos numéricos
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(25)
        
        # AGREGADO: Stretch inicial para centrar
        row2.addStretch(1)
        
        # Toggle buttons
        self.buy_sell = ToggleButton("Sell", "Buy", default=config["buy_sell"] if config and "buy_sell" in config else "Buy")
        self.buy_sell.toggled.connect(self.changed.emit)
        self.call_put = ToggleButton("Call", "Put", default=config["call_put"] if config and "call_put" in config else "Put")
        self.call_put.toggled.connect(self.changed.emit)
        
        row2.addWidget(self.buy_sell)
        row2.addSpacing(25)
        row2.addWidget(self.call_put)

        # Campos numéricos con labels al lado
        row2.addSpacing(25)
        self.qty_input = NumericInputWithLabel("QTY", config["qty"] if config and "qty" in config else 1, 1, 999)
        self.qty_input.valueChanged.connect(self.changed.emit)
        row2.addWidget(self.qty_input)

        row2.addSpacing(25)
        self.percent_input = NumericInputWithLabel("%", config["percent"] if config and "percent" in config else 15, 0, 100)
        self.percent_input.valueChanged.connect(self.changed.emit)
        row2.addWidget(self.percent_input)

        row2.addSpacing(25)
        self.dte_input = NumericInputWithLabel("DTE", config["dte"] if config and "dte" in config else 90, 0, 999)
        self.dte_input.valueChanged.connect(self.changed.emit)
        row2.addWidget(self.dte_input)

        # AGREGADO: Stretch final para centrar
        row2.addStretch(1)
        
        layout.addLayout(row2)

        # ARREGLADO: Tercera fila centrada como las anteriores
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(30)
        
        # AGREGADO: Stretch inicial para centrar
        row3.addStretch(1)
        
        # Containers horizontales para label + switch
        dte_container = QtWidgets.QHBoxLayout()
        dte_container.setSpacing(10)
        
        labelDTE = QtWidgets.QLabel("Use Extract DTE")
        labelDTE.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #ecf0f1;
        """)
        
        self.use_extract_dte = ToggleButton("No", "Yes", default=config["use_extract_dte"] if config and "use_extract_dte" in config else "No")
        self.use_extract_dte.toggled.connect(self.changed.emit)
        
        dte_container.addWidget(labelDTE)
        dte_container.addWidget(self.use_extract_dte)
        
        # Strike container
        strike_container = QtWidgets.QHBoxLayout()
        strike_container.setSpacing(10)
        
        labelStrike = QtWidgets.QLabel("Round Strike")
        labelStrike.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #ecf0f1;
        """)
        
        self.round_strike = ToggleButton("No", "Yes", default=config["round_strike"] if config and "round_strike" in config else "No")
        self.round_strike.toggled.connect(self.changed.emit)
        
        strike_container.addWidget(labelStrike)
        strike_container.addWidget(self.round_strike)
        
        # Wrappers para los containers
        dte_widget = QtWidgets.QWidget()
        dte_widget.setLayout(dte_container)
        
        strike_widget = QtWidgets.QWidget()
        strike_widget.setLayout(strike_container)
        
        row3.addWidget(dte_widget)
        row3.addSpacing(30)
        row3.addWidget(strike_widget)

        # Multiplicador por defecto 0
        row3.addSpacing(30)
        self.mult_input = NumericInputWithLabel("Multiplier", config["multiplier"] if config and "multiplier" in config else 0, 0, 100)
        self.mult_input.valueChanged.connect(self.changed.emit)
        row3.addWidget(self.mult_input)

        # AGREGADO: Stretch final para centrar
        row3.addStretch(1)
        
        layout.addLayout(row3)
        layout.addStretch()

        # Combos ocultos para compatibilidad
        self.strategy_combo = QtWidgets.QComboBox()
        self.strategy_combo.addItems(get_available_strategies())
        self.strategy_combo.hide()

        self.pct_type_combo = QtWidgets.QComboBox()
        self.pct_type_combo.addItems(get_pct_types())
        self.pct_type_combo.hide()

        self.buy_sell_combo = QtWidgets.QComboBox()
        self.buy_sell_combo.addItems(get_buy_sell_options())
        self.buy_sell_combo.hide()

        self.call_put_combo = QtWidgets.QComboBox()
        self.call_put_combo.addItems(get_call_put_options())
        self.call_put_combo.hide()

        self.extract_dte_combo = QtWidgets.QComboBox()
        self.extract_dte_combo.addItems(get_yes_no_options())
        self.extract_dte_combo.hide()

        self.round_strike_combo = QtWidgets.QComboBox()
        self.round_strike_combo.addItems(get_yes_no_options())
        self.round_strike_combo.hide()

    def get_config(self):
        return {
            "ticker": self.ticker_select.currentText(),
            "strategy": self.strat_select.currentText(),
            "pct_type": self.pct_select.currentText(),
            "buy_sell": self.buy_sell.value(),
            "call_put": self.call_put.value(),
            "qty": self.qty_input.value(),
            "percent": self.percent_input.value(),
            "dte": self.dte_input.value(),
            # ARREGLADO: Convertir correctamente a "Yes"/"No"
            "use_extract_dte": self.use_extract_dte.value(),  # Ya devuelve "Yes" o "No"
            "round_strike": self.round_strike.value(),        # Ya devuelve "Yes" o "No"
            "multiplier": self.mult_input.value()
        }

    def set_config(self, config):
        """Cargar configuración en los widgets"""
        if "ticker" in config:
            self.ticker_select.setCurrentText(config["ticker"])
        if "strategy" in config:
            self.strat_select.setCurrentText(config["strategy"])
        if "pct_type" in config:
            self.pct_select.setCurrentText(config["pct_type"])
        if "buy_sell" in config:
            self.buy_sell.setValue(config["buy_sell"])
        if "call_put" in config:
            self.call_put.setValue(config["call_put"])
        if "qty" in config:
            self.qty_input.setValue(config["qty"])
        if "percent" in config:
            self.percent_input.setValue(config["percent"])
        if "dte" in config:
            self.dte_input.setValue(config["dte"])
        if "use_extract_dte" in config:
            # ARREGLADO: Cargar valor correcto desde config
            self.use_extract_dte.setValue(config["use_extract_dte"])
        if "round_strike" in config:
            # ARREGLADO: Cargar valor correcto desde config
            self.round_strike.setValue(config["round_strike"])
        if "multiplier" in config:
            self.mult_input.setValue(config["multiplier"])

class ModernSwitch(QtWidgets.QWidget):
    toggled = QtCore.pyqtSignal(bool)
    
    def __init__(self, label_text, default=False, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.is_on = default
        
        # Hacer el widget más grande para que se vea bien
        self.setFixedHeight(50)
        self.setMinimumWidth(200)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Label
        self.label = QtWidgets.QLabel(label_text)
        self.label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        # Container para el switch
        self.switch_container = QtWidgets.QWidget()
        self.switch_container.setFixedSize(60, 30)
        self.switch_container.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.switch_container)
        
        # Estilo del widget principal
        self.setStyleSheet("""
            ModernSwitch {
                background-color: #34495e;
                border: 2px solid #5d6d7e;
                border-radius: 15px;
                padding: 5px;
            }
            ModernSwitch:hover {
                border-color: #3498db;
                background-color: #3c4c5f;
            }
        """)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Pintar solo el switch
        painter = QtGui.QPainter(self.switch_container)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.switch_container.rect()
        
        # Fondo del switch
        bg_color = QtGui.QColor("#27ae60" if self.is_on else "#e74c3c")
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.setPen(QtGui.QPen(bg_color.darker(120), 2))
        painter.drawRoundedRect(rect, 15, 15)
        
        # Círculo del switch
        circle_size = 22
        margin = 4
        circle_x = rect.width() - circle_size - margin if self.is_on else margin
        circle_y = (rect.height() - circle_size) // 2
        
        # Sombra del círculo
        shadow_color = QtGui.QColor(0, 0, 0, 60)
        painter.setBrush(QtGui.QBrush(shadow_color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(circle_x + 2, circle_y + 2, circle_size, circle_size)
        
        # Círculo principal
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.setPen(QtGui.QPen(QtGui.QColor("#bdc3c7"), 1))
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)
        
        # Texto ON/OFF en el switch
        painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff"), 2))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        
        if self.is_on:
            text_rect = QtCore.QRect(5, 0, 25, rect.height())
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, "ON")
        else:
            text_rect = QtCore.QRect(rect.width() - 30, 0, 25, rect.height())
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, "OFF")
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.toggle()
    
    def toggle(self):
        self.is_on = not self.is_on
        self.update()
        self.toggled.emit(self.is_on)
    
    def setValue(self, value):
        self.is_on = bool(value)
        self.update()
    
    def value(self):
        return self.is_on