# Guía de Instalación - AutoOmegaBot

Esta guía te ayudará a instalar y configurar AutoOmegaBot en tu sistema.

## Requisitos del Sistema

### Sistemas Operativos Soportados
- **Windows 10/11** (64-bit)
- **Linux** (Ubuntu 18.04+, Zorin OS, Debian, etc.)
- **macOS 10.14+** (Mojave o superior)

### Requisitos de Software
- **Python 3.8+** (Recomendado: Python 3.10)
- **Conexión a Internet** (para automatización web)
- **4GB RAM mínimo** (8GB recomendado)
- **500MB espacio libre** en disco

## Instalación Paso a Paso

### 1. Instalar Python

#### Windows:
```bash
# Descargar desde python.org o usar Chocolatey
choco install python
```

#### Linux (Ubuntu/Zorin):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### macOS:
```bash
# Usando Homebrew
brew install python
```

### 2. Verificar Instalación de Python
```bash
python --version
# o
python3 --version
```

### 3. Clonar o Descargar el Proyecto
```bash
git clone <repository-url> AutoOmegaBot
cd AutoOmegaBot
```

### 4. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 5. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 6. Instalar Playwright Browsers
```bash
playwright install
```

## Configuración Inicial

### 1. Verificar Estructura de Carpetas
Al ejecutar por primera vez, el sistema creará automáticamente:
```
~/Documents/AutoOmega Bot/
├── Output/          # Archivos Excel generados
├── Config/          # Configuraciones guardadas
└── Logs/           # Registros del sistema
```

### 2. Ejecutar la Aplicación
```bash
cd src
python main.py
```

## Configuración del Entorno de Desarrollo (Opcional)

### Visual Studio Code
Si planeas modificar el código:

1. **Instalar VSCode**: https://code.visualstudio.com/
2. **Extensiones recomendadas**:
   ```
   - Python (Microsoft)
   - Pylance (Microsoft)
   - Python Docstring Generator
   - GitLens
   - Excel Viewer
   ```

3. **Configurar VSCode**:
   ```bash
   code AutoOmegaBot
   ```

### PyQt Designer (Opcional)
Para editar interfaces gráficas:
```bash
pip install pyqt5-tools
```

## Verificación de la Instalación

### 1. Test Básico
```bash
cd src
python -c "from Utiles.utils import test_documents_detection; test_documents_detection()"
```

### 2. Test de Conexión
Abre la aplicación y verifica:
- ✅ Internet conectado
- ✅ Estructura de carpetas creada
- ✅ Interfaz se carga correctamente

## Solución de Problemas Comunes

### Error: ModuleNotFoundError
```bash
# Asegúrate de tener el entorno virtual activado
pip install -r requirements.txt
```

### Error: playwright no encontrado
```bash
playwright install chromium
```

### Error: PyQt5 no se instala
#### Ubuntu/Linux:
```bash
sudo apt install python3-pyqt5 python3-pyqt5-dev
```

#### Windows:
```bash
pip install --upgrade pip
pip install PyQt5
```

### Error: Permisos en Documents
Verifica que tu usuario tenga permisos de escritura en Documents.

### Error: Conexión a Internet
- Verifica tu conexión
- Desactiva temporalmente antivirus/firewall
- Usa VPN si hay restricciones

## Distribución de la Aplicación

### Crear Ejecutable (Opcional)
Para crear un .exe/.app distributable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

### Empaquetado Avanzado
```bash
# Windows
pyinstaller --name="AutoOmegaBot" --icon="assets/icon.ico" --onefile --windowed src/main.py

# Linux
pyinstaller --name="AutoOmegaBot" --onefile --windowed src/main.py
```

## Actualizaciones

### Actualizar Dependencias
```bash
pip install --upgrade -r requirements.txt
playwright install
```

### Actualizar Código
```bash
git pull origin main
pip install -r requirements.txt
```

## Soporte

- **Issues**: Reporta problemas en el repositorio
- **Documentación**: Ver `DOCUMENTACION.md`
- **Email**: [contacto del soporte]

---

**Nota**: Este software está diseñado para uso educativo y de investigación. Asegúrate de cumplir con los términos de servicio de los sitios web que automatices.