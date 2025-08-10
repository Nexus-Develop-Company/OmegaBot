# AutoOmegaBot

Este proyecto es un bot automatizado diseñado para interactuar con páginas web y procesar datos desde archivos Excel. Utiliza Playwright para la automatización del navegador y PyQt/PySide para la interfaz gráfica de usuario.

## Estructura del Proyecto

- **src/main.py**: Punto de entrada de la aplicación. Inicializa la interfaz gráfica y gestiona la interacción entre la GUI y el bot.
- **src/gui.py**: Contiene la clase `MainWindow`, que define la interfaz gráfica. Incluye campos de entrada y un botón de inicio, así como contadores para los enlaces.
- **src/bot.py**: Implementa la lógica del bot. Lee el archivo Excel con las URLs, abre cada URL en un navegador, realiza las acciones necesarias y guarda los resultados en un archivo Excel.
- **src/utils.py**: Contiene funciones auxiliares para la lectura y escritura de archivos Excel y la validación de entradas.
- **requirements.txt**: Lista las dependencias necesarias para el proyecto, incluyendo Playwright, PyQt/PySide y Pandas.
- **.vscode/settings.json**: Configuración específica para el entorno de desarrollo en Visual Studio Code.

## Herramientas y Tecnologías

1. **Playwright**: Para la automatización del navegador.
2. **PyQt/PySide**: Para crear la interfaz gráfica de usuario.
3. **Pandas**: Para manejar la lectura y escritura de archivos Excel.
4. **Visual Studio Code**: Como IDE para el desarrollo.
5. **Python**: Como lenguaje de programación.

## Preparación del Entorno de Desarrollo

1. **Instalar Python**: Asegúrate de tener Python instalado en tu sistema Zorin.
2. **Crear un entorno virtual**: Utiliza `python -m venv venv` para crear un entorno virtual.
3. **Activar el entorno virtual**: Ejecuta `source venv/bin/activate`.
4. **Instalar dependencias**: Ejecuta `pip install -r requirements.txt` para instalar las bibliotecas necesarias.
5. **Configurar Visual Studio Code**: Instala las extensiones recomendadas para Python, como "Python" y "Pylance".

## Protocolo HTTPS vs Aplicación de Escritorio

- **Aplicación de Escritorio**: Es más adecuada para este caso, ya que permite una interacción directa con el sistema de archivos y la interfaz gráfica. Además, puedes empaquetar el bot junto con la aplicación.
- **Protocolo HTTPS**: Sería más adecuado si quisieras que el bot funcionara como un servicio web, pero en este caso, una aplicación de escritorio es más conveniente.

## Plugins y Addons Recomendados para Visual Studio Code

- **Python**: Para soporte de Python.
- **Pylance**: Para autocompletado y análisis de código.
- **Jupyter**: Si necesitas trabajar con notebooks.
- **Excel Viewer**: Para visualizar archivos Excel directamente en el IDE.

## Estructura de la Aplicación de Escritorio

La aplicación debe incluir los siguientes campos:
- **Año anterior** (Obligatorio)
- **Dirección de salida de Excel** (Opcional)
- **Excel plantilla** (Opcional)
- **Excel de URLs** (Obligatorio)
- **Botón de iniciar** (que solo funcione cuando los campos obligatorios estén llenos)

Los contadores deben mostrar:
- **Total de enlaces detectados**.
- **Total de enlaces procesados**.

La lectura del Excel debe ser sencilla, iterando sobre las filas hasta encontrar una celda vacía.