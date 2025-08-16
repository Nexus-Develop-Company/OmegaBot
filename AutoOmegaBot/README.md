# AutoOmegaBot 🤖

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)](https://pypi.org/project/PyQt5/)
[![Playwright](https://img.shields.io/badge/Playwright-Web%20Automation-orange.svg)](https://playwright.dev/)

AutoOmegaBot es una aplicación de escritorio avanzada para automatizar el análisis de backtesting financiero en plataformas web. Diseñada específicamente para trabajar con datos de opciones financieras, permite procesar múltiples análisis de forma automatizada y generar reportes detallados en Excel.

## 🎯 Características Principales

- **🚀 Automatización Web**: Control completo del navegador con Playwright
- **📊 Análisis de Backtesting**: Procesamiento automatizado de estrategias de opciones
- **📁 Gestión de Archivos**: Lectura de URLs desde Excel y generación de reportes
- **🎨 Interfaz Moderna**: GUI elegante con tema oscuro y métricas en tiempo real
- **⚙️ Configuración Avanzada**: Sistema completo de configuración persistente
- **📝 Logs Detallados**: Sistema de logging completo con exportación
- **🌍 Multiplataforma**: Soporte para Windows, Linux y macOS

## 🏗️ Arquitectura del Sistema

```
AutoOmegaBot/
├── src/
│   ├── main.py                 # Punto de entrada principal
│   ├── Bot/
│   │   └── bot.py             # Lógica de automatización web
│   ├── Ui/
│   │   ├── gui.py             # Interfaz principal
│   │   └── Settings_Ui/       # Paneles de configuración
│   │       ├── General/       # Configuración general
│   │       ├── Fecha/         # Configuración de fechas
│   │       ├── Estrategia/    # Configuración de estrategias
│   │       └── Fondos/        # Configuración de fondos
│   └── Utiles/
│       ├── utils.py           # Utilidades centrales
│       └── assets.py          # Recursos gráficos (SVG)
├── requirements.txt           # Dependencias del proyecto
└── docs/                     # Documentación completa
```

## 🚀 Inicio Rápido

### Instalación
```bash
git clone <repository-url>
cd AutoOmegaBot
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
playwright install
```

### Ejecutar
```bash
cd src
python main.py
```

## 📋 Configuración Inicial

### 1. Configuración de Fechas
- **Fecha Inicial**: Desde cuándo analizar (formato DD/MM/YYYY o MM/DD/YYYY)
- **Fecha Final**: Hasta cuándo analizar
- **Validación automática** de rangos de fechas

### 2. Configuración de Fondos
- **Capital Inicial**: Monto base para análisis ($100,000 por defecto)
- **Asignación de Margen**: Porcentaje de capital por operación (10% por defecto)
- **Contratos Máximos**: Límite de contratos por trade
- **Configuraciones Avanzadas**: Max trades abiertos, límites de asignación

### 3. Configuración de Estrategia
- **Tipo de Estrategia**: Selección de estrategia de opciones
- **Parámetros**: Buy/Sell, Call/Put, Quantity, Percentage
- **DTE (Days to Expiration)**: Días hasta vencimiento
- **Tipo de Porcentaje**: Delta, Gamma, etc.

### 4. Configuración General
- **Carpeta de Salida**: Ubicación para archivos Excel generados
- **Estructura Automática**: Creación de carpetas Config/Logs en Documents

## 🎮 Uso de la Aplicación

### Panel Principal
- **📊 Métricas del Sistema**: Estado en tiempo real
- **📁 Selector de Archivos**: Carga de Excel con URLs
- **🚀 Control del Bot**: Botones de inicio/parada
- **📝 Logs en Vivo**: Seguimiento detallado del proceso

### Flujo de Trabajo
1. **Cargar archivo Excel** con URLs en columna A
2. **Configurar parámetros** de análisis
3. **Verificar conexión** a internet
4. **Iniciar análisis** automatizado
5. **Revisar resultados** en carpeta de salida

### Sistema de Validación
- ✅ **Conexión a Internet**: Verificación automática
- ✅ **Archivo válido**: Validación de formato Excel
- ✅ **Fechas configuradas**: Rango válido de fechas
- ✅ **Fondos configurados**: Parámetros financieros completos

## 🛠️ Tecnologías Utilizadas

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| **Python** | Lenguaje principal | 3.8+ |
| **PyQt5** | Interfaz gráfica | 5.15+ |
| **Playwright** | Automatización web | 1.30+ |
| **Pandas** | Manipulación de datos | 1.5+ |
| **OpenPyXL** | Manejo de Excel | 3.0+ |

## 📁 Estructura de Datos

### Archivos de Entrada
```
Excel con URLs:
Columna A: URLs para analizar
- https://example.com/analysis1
- https://example.com/analysis2
- ...
```

### Archivos de Salida
```
~/Documents/AutoOmega Bot/
├── Output/
│   ├── analysis_2024_01_15_10:30:45.xlsx
│   └── summary_report.xlsx
├── Config/
│   └── config.json
└── Logs/
    └── omega_bot_session_2024_01_15_10:30:45.log
```

## 🎨 Características de la Interfaz

### Tema Oscuro Moderno
- **Colores principales**: #2c3e50, #34495e, #3498db
- **Iconos SVG**: Gráficos vectoriales escalables
- **Métricas en tiempo real**: Widgets de estado dinámicos
- **Logs con colores**: Diferenciación por nivel de severidad

### Widgets Personalizados
- **StatusWidget**: Métricas del sistema con colores dinámicos
- **ActionButton**: Botones con efectos hover y animaciones
- **LogWidget**: Logs avanzados con formato y exportación
- **FileUploadButton**: Selector de archivos especializado

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
export OMEGA_DEBUG=1          # Modo debug
export OMEGA_TIMEOUT=30       # Timeout web (segundos)
export OMEGA_HEADLESS=false   # Mostrar navegador
```

### Configuración JSON
```json
{
  "ticker": "SPY",
  "strategy": "Iron Condor",
  "starting_funds": "100000",
  "margin_allocation_percent": "10",
  "start_date": "01/01/2024",
  "end_date": "31/12/2024",
  "output_folder": "~/Documents/AutoOmega Bot/Output"
}
```

## 🚨 Solución de Problemas

### Problemas Comunes
1. **Error de Conexión**: Verificar internet y firewall
2. **Playwright no funciona**: Ejecutar `playwright install`
3. **Archivos no se guardan**: Verificar permisos en Documents
4. **PyQt5 no se instala**: Instalar dependencias del sistema

### Logs de Debug
```python
from Utiles.utils import test_documents_detection
test_documents_detection()  # Verificar estructura de carpetas
```

## 🤝 Contribución

### Para Desarrolladores
1. **Fork** el repositorio
2. **Crear rama** para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. **Commit** cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. **Push** a la rama: `git push origin feature/nueva-funcionalidad`
5. **Crear Pull Request**

### Estándares de Código
- **PEP 8** para estilo de Python
- **Docstrings** para todas las funciones
- **Type hints** cuando sea posible
- **Comentarios** en código complejo

## 📊 Métricas y Rendimiento

- **Velocidad**: ~2-5 análisis por minuto (dependiendo de la web)
- **Memoria**: ~100-300MB RAM durante ejecución
- **CPU**: Bajo uso, principalmente I/O y red
- **Compatibilidad**: 99% de sitios web modernos

## 🔒 Seguridad y Privacidad

- **Sin datos sensibles** almacenados en código
- **Configuración local** únicamente
- **Respeto a robots.txt** y términos de servicio
- **Rate limiting** automático para evitar sobrecarga

## 📈 Roadmap

### Versión 2.0
- [ ] Soporte para múltiples exchanges
- [ ] Análisis en paralelo
- [ ] Dashboard web opcional
- [ ] API REST integrada
- [ ] Plugins personalizables

### Versión 1.5
- [ ] Análisis de riesgo avanzado
- [ ] Exportación a múltiples formatos
- [ ] Notificaciones push
- [ ] Modo batch automatizado

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Issues**: Reporta bugs en GitHub Issues
- **Documentación**: Ver `DOCUMENTACION.md`
- **Email**: [tu-email@empresa.com]
- **Discord**: [servidor-de-soporte]

---

**⚠️ Disclaimer**: Este software es para fines educativos y de investigación. Los usuarios son responsables de cumplir con los términos de servicio de las plataformas web que automaticen.

**💡 Tip**: Visita la [documentación completa](DOCUMENTACION.md) para guías detalladas y casos de uso avanzados.