"""
Utilidades centrales de OmegaBot
================================

Este módulo contiene todas las funciones de lógica de negocio y validación
que son utilizadas por la interfaz de usuario. Mantiene separada la lógica
de la presentación visual.

Funciones principales:
- Configuración: cargar/guardar/validar configuración
- Validación: fechas, archivos, conexión, sistema
- Logs: guardar registros de sesión
- Archivos: manejo de archivos y carpetas
- Conexión: verificar estado de internet
"""

import json
import os
from datetime import datetime, timedelta
import socket
import urllib.request
import platform

# =============================================================================
# FUNCIONES DE RUTAS Y DIRECTORIOS
# =============================================================================

def get_system_documents_folder():
    """
    NUEVO: Detectar automáticamente la carpeta Documents del sistema sin importar el idioma
    """
    import platform
    import os
    
    try:
        system = platform.system()
        home = os.path.expanduser("~")
        
        if system == "Windows":
            # En Windows, usar la API del sistema para obtener la carpeta Documents real
            try:
                import ctypes
                from ctypes import wintypes, windll
                
                # Usar SHGetFolderPath para obtener CSIDL_MYDOCUMENTS
                CSIDL_MYDOCUMENTS = 5
                SHGFP_TYPE_CURRENT = 0
                
                buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
                windll.shell32.SHGetFolderPathW(None, CSIDL_MYDOCUMENTS, None, SHGFP_TYPE_CURRENT, buf)
                documents_path = buf.value
                
                if documents_path and os.path.exists(documents_path):
                    return documents_path
                    
            except Exception:
                # Fallback: Intentar con registro de Windows
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                      r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                        documents_path = winreg.QueryValueEx(key, "Personal")[0]
                        if os.path.exists(documents_path):
                            return documents_path
                except Exception:
                    pass
        
        elif system == "Darwin":  # macOS
            # En macOS, la carpeta Documents siempre está en inglés
            documents_path = os.path.join(home, "Documents")
            if os.path.exists(documents_path):
                return documents_path
        
        elif system == "Linux":
            # En Linux, usar xdg-user-dirs para obtener la carpeta real
            try:
                import subprocess
                result = subprocess.run(['xdg-user-dir', 'DOCUMENTS'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    documents_path = result.stdout.strip()
                    if documents_path and os.path.exists(documents_path):
                        return documents_path
            except Exception:
                pass
            
            # Fallback: Buscar carpetas comunes en Linux
            possible_docs = [
                os.path.join(home, "Documents"),
                os.path.join(home, "Documentos"),
                os.path.join(home, "Dokumente"),
                os.path.join(home, "Documenti"),
                os.path.join(home, "文档"),  # Chino
                os.path.join(home, "書類"),  # Japonés
                os.path.join(home, "문서"),  # Coreano
            ]
            
            for path in possible_docs:
                if os.path.exists(path):
                    return path
        
        # Fallback universal: Buscar carpetas que contengan "doc" en su nombre
        for item in os.listdir(home):
            item_path = os.path.join(home, item)
            if os.path.isdir(item_path):
                item_lower = item.lower()
                # Buscar patrones comunes de "Documents" en diferentes idiomas
                if any(pattern in item_lower for pattern in [
                    'doc', 'dokumenty', 'документы', 'dokumen', 'belge',
                    '文档', '書類', '문서', 'asiakirjat', 'documenten'
                ]):
                    return item_path
        
        # Último fallback: Crear Documents en inglés
        fallback_path = os.path.join(home, "Documents")
        os.makedirs(fallback_path, exist_ok=True)
        return fallback_path
        
    except Exception as e:
        print(f"Error detectando carpeta Documents: {e}")
        # Fallback final
        fallback_path = os.path.join(os.path.expanduser("~"), "Documents")
        os.makedirs(fallback_path, exist_ok=True)
        return fallback_path

def get_output_folder():
    """
    MODIFICADO: Output por defecto en Documents (puede cambiar después)
    """
    try:
        documents_path = get_system_documents_folder()
        output_folder = os.path.join(documents_path, "AutoOmega Bot", "Output")
        os.makedirs(output_folder, exist_ok=True)
        return output_folder
    except Exception:
        fallback_path = os.path.join(os.path.expanduser("~"), "Documents", "AutoOmega Bot", "Output")
        os.makedirs(fallback_path, exist_ok=True)
        return fallback_path
      
def get_documents_folder():
    """
    AGREGADO: Función auxiliar para obtener solo la carpeta Documents
    """
    try:
        import locale
        import platform
        
        system_lang = locale.getdefaultlocale()[0] or 'en_US'
        home = os.path.expanduser("~")
        
        if platform.system() == "Windows":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    return winreg.QueryValueEx(key, "Personal")[0]
            except:
                pass
        
        # Detectar nombre de carpeta Documents según idioma
        if 'es' in system_lang.lower():
            docs_folder = "Documentos"
        elif 'pt' in system_lang.lower():
            docs_folder = "Documentos"
        elif 'fr' in system_lang.lower():
            docs_folder = "Documents"
        elif 'de' in system_lang.lower():
            docs_folder = "Dokumente"
        elif 'it' in system_lang.lower():
            docs_folder = "Documenti"
        else:
            docs_folder = "Documents"
        
        documents_path = os.path.join(home, docs_folder)
        
        # Verificar que existe, sino usar Documents por defecto
        if not os.path.exists(documents_path):
            documents_path = os.path.join(home, "Documents")
        
        return documents_path
        
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Documents")

def get_autobot_folder():
    """
    Crear y obtener la carpeta AutoOmegaBot en Documents
    
    Returns:
        str: Ruta a la carpeta AutoOmegaBot
    """
    documents = get_documents_folder()
    autobot_folder = os.path.join(documents, "AutoOmegaBot")
    
    if not os.path.exists(autobot_folder):
        os.makedirs(autobot_folder)
    
    return autobot_folder

def get_config_folder():
    """
    MODIFICADO: Config SIEMPRE en Documents, no cambia con output_path
    """
    try:
        documents_path = get_system_documents_folder()
        config_folder = os.path.join(documents_path, "AutoOmega Bot", "Config")
        os.makedirs(config_folder, exist_ok=True)
        return config_folder
    except Exception:
        fallback_path = os.path.join(os.path.expanduser("~"), "Documents", "AutoOmega Bot", "Config")
        os.makedirs(fallback_path, exist_ok=True)
        return fallback_path
      
def get_logs_folder():
    """
    MODIFICADO: Logs SIEMPRE en Documents, no cambia con output_path
    """
    try:
        documents_path = get_system_documents_folder()
        logs_folder = os.path.join(documents_path, "AutoOmega Bot", "Logs")
        os.makedirs(logs_folder, exist_ok=True)
        return logs_folder
    except Exception:
        fallback_path = os.path.join(os.path.expanduser("~"), "Documents", "AutoOmega Bot", "Logs")
        os.makedirs(fallback_path, exist_ok=True)
        return fallback_path
      
# FUNCIÓN DE PRUEBA para verificar que funciona
def test_documents_detection():
    """
    NUEVO: Función para probar la detección de Documents
    """
    print("🔍 Detectando carpeta Documents del sistema...")
    
    docs_path = get_system_documents_folder()
    print(f"📁 Carpeta Documents detectada: {docs_path}")
    
    output_path = get_output_folder()
    print(f"📁 Carpeta Output creada: {output_path}")
    
    config_path = get_config_folder()
    print(f"📁 Carpeta Config creada: {config_path}")
    
    logs_path = get_logs_folder()
    print(f"📁 Carpeta Logs creada: {logs_path}")
    
    return {
        'documents': docs_path,
        'output': output_path,
        'config': config_path,
        'logs': logs_path
    }

# =============================================================================
# FUNCIONES DE CONFIGURACIÓN
# =============================================================================

def load_config():
    """
    Cargar configuración desde archivo JSON en Documents/AutoOmegaBot/Config
    
    Utilizada por: gui.py, setting_gui.py, general.py
    Propósito: Obtener configuración persistente del sistema
    
    Returns:
        dict: Configuración completa con valores por defecto
    """
    config_folder = get_config_folder()
    config_path = os.path.join(config_folder, 'config.json')
    default_config = {
        "ticker": "SPY",
        "strategy": "Select strategy", 
        "pct_type": "Delta",
        "buy_sell": "Buy",
        "call_put": "Put",
        "qty": 1,
        "percent": 15,
        "dte": 90,
        "use_extract_dte": "No",
        "round_strike": "No",
        "multiplier": 0,
        "start_date": "",
        "end_date": "",
        "output_folder": "",
        "starting_funds":	"100000",
        "margin_allocation_percent":	"10",
        "max_contracts_per_trade":	"1",
        "max_open_trades":	"",
        "max_allocation_amount":	"",
        "prune_oldest_trades": False,
        "ignore_margin_requirements":	True,
    }
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Actualizar con valores por defecto si faltan claves
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config   
    except Exception as e:
        print(f"Error cargando configuración: {e}")
    
    return default_config

def ensure_autobot_structure(base_path):
    """
    NUEVO: Asegurar que exista la estructura AutoOmega Bot/Output en cualquier ruta
    """
    try:
        # Crear la estructura completa AutoOmega Bot/Output
        autobot_path = os.path.join(base_path, "AutoOmega Bot")
        output_path = os.path.join(autobot_path, "Output")
        
        # Crear carpetas si no existen
        os.makedirs(output_path, exist_ok=True)
        
        # También crear otras carpetas útiles
        config_path = os.path.join(autobot_path, "Config")
        logs_path = os.path.join(autobot_path, "Logs")
        
        os.makedirs(config_path, exist_ok=True)
        os.makedirs(logs_path, exist_ok=True)
        
        return output_path
        
    except Exception as e:
        print(f"Error creando estructura AutoOmega Bot: {e}")
        return base_path

def ensure_output_structure(base_path):
    """
      MODIFICADO: Solo crear carpeta Output en la ruta seleccionada por el usuario
    """
    try:
        # Solo crear la carpeta Output en la ubicación seleccionada
        output_path = os.path.join(base_path, "Output")
        os.makedirs(output_path, exist_ok=True)
        return output_path
        
    except Exception as e:
        print(f"Error creando carpeta Output: {e}")
        return base_path

def validate_and_create_output_path(path):
    """
    MODIFICADO: Solo validar y crear Output, no toda la estructura AutoOmega Bot
    """
    try:
        if not path:
            # Si no hay ruta, usar la por defecto
            return get_output_folder()
        
        # Verificar si ya termina en Output
        if path.endswith("Output"):
            # Ya tiene Output, solo asegurar que existe
            os.makedirs(path, exist_ok=True)
            return path
        else:
            # No tiene Output, agregarlo
            return ensure_output_structure(path)
            
    except Exception as e:
        print(f"Error validando ruta de salida: {e}")
        return get_output_folder()

def save_config(config):
    """
    MODIFICADO: Config siempre en Documents, solo validar output_path
    """
    config_folder = get_config_folder()  # SIEMPRE en Documents
    config_path = os.path.join(config_folder, 'config.json')
    
    try:
        # AGREGADO: Solo validar output_path (no afecta config)
        if 'output_path' in config and config['output_path']:
            validated_path = validate_and_create_output_path(config['output_path'])
            config['output_path'] = validated_path
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False
      
def get_default_output():
    """
    Obtener la carpeta de salida por defecto en AutoOmegaBot
    
    Utilizada por: general.py
    Propósito: Crear y obtener ruta de carpeta Output
    
    Returns:
        str: Ruta absoluta de la carpeta Output
    """
    try:
        autobot_folder = get_autobot_folder()
        output_dir = os.path.join(autobot_folder, 'Output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return os.path.abspath(output_dir)
    except Exception as e:
        print(f"Error creando carpeta de salida: {e}")
        import tempfile
        return tempfile.gettempdir()

# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def validate_date_format(date_string):
    """
    MODIFICADO: Validar formato MM/DD/AAAA en lugar de DD/MM/AAAA
    """
    if not date_string:
        return False
    
    try:
        # CAMBIADO: De "%d/%m/%Y" a "%m/%d/%Y"
        datetime.strptime(date_string, "%m/%d/%Y")
        return True
    except ValueError:
        return False

def validate_date_range(start_date, end_date):
    """
    ARREGLADO: Validar fechas aceptando formato dd/mm/yyyy correctamente
    """
    try:
        if not start_date or not end_date:
            return False, "Ambas fechas son requeridas"
        
        # Función para parsear fechas en múltiples formatos
        def parse_date(date_str):
            date_str = date_str.strip()
            
            # ARREGLADO: Primero intentar formato dd/mm/yyyy (formato preferido)
            if '/' in date_str:
                try:
                    # Verificar que tenga el formato correcto mm/dd/yyyy
                    parts = date_str.split('/')
                    if len(parts) == 3:
                        day, month, year = parts
                        if len(day) <= 2 and len(month) <= 2 and len(year) == 4:
                            return datetime.strptime(date_str, "%m/%d/%Y")
                except ValueError:
                    pass
            
            # Si ningún formato funciona
            raise ValueError("Formato de fecha inválido")
        
        try:
            start_obj = parse_date(start_date)
            end_obj = parse_date(end_date)
        except ValueError:
            return False, "Formato de fecha inválido. Use MM/DD/YYYY (ejemplo: 08/10/2025)"
        
        # Validar que la fecha de inicio sea anterior a la de fin
        if start_obj >= end_obj:
            return False, "La fecha de inicio debe ser anterior a la fecha de fin"
        
        # Validar que las fechas no sean futuras (permitir hasta 1 año futuro)
        max_date = datetime.now()
        if end_obj > max_date:
            return False, "La fecha de fin no puede ser en el futuro"
        
        return True, "Fechas válidas"
        
    except Exception as e:
        return False, f"Error validando fechas: {str(e)}"

def validate_file_path(file_path):
    """
    Validar archivo seleccionado
    
    Utilizada por: gui.py
    Propósito: Verificar que el archivo existe y tiene formato válido
    
    Args:
        file_path (str): Ruta del archivo
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file_path:
        return False, "Debe seleccionar un archivo de links"
    
    if not os.path.exists(file_path):
        return False, "El archivo seleccionado no existe"
    
    valid_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in valid_extensions:
        return False, "Formato de archivo no válido. Use CSV o Excel"
    
    return True, "Archivo válido"

def validate_strategy_selection(strategy):
    """
    Validar selección de estrategia
    
    Utilizada por: gui.py, estrategia.py
    Propósito: Verificar que se haya seleccionado una estrategia válida
    
    Args:
        strategy (str): Estrategia seleccionada
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not strategy or strategy == "Select strategy" or strategy.strip() == "":
        return False, "Debe seleccionar una estrategia"
    
    return True, "Estrategia válida"

def validate_system_ready(config, selected_file):
    """
    MODIFICADO: Sin validación de estrategia
    """
    try:
        status = get_validation_status(config, selected_file)
        
        if status['overall_valid']:
            return True, "Sistema listo para iniciar análisis"
        
        # Mensajes específicos según lo que falta (SIN estrategia)
        missing = []
        if not status['internet']:
            missing.append("conexión a internet")
        if not status['file_valid']:
            missing.append("archivo válido")
        if not status['dates_valid']:
            missing.append("configuración de fechas")
        
        error_msg = f"Faltan: {', '.join(missing)}"
        return False, error_msg
        
    except Exception as e:
        return False, f"Error validando sistema: {str(e)}"

def get_validation_status(config, selected_file):
    """
    MODIFICADO: Sin validación de estrategia - solo internet, archivo y fechas
    """
    try:
        errors = []
        
        # Verificar conexión
        internet = check_internet_connection()
        if not internet:
            errors.append("Sin conexión a internet")
        
        # Verificar archivo
        file_valid = bool(selected_file and os.path.exists(selected_file))
        if not file_valid:
            errors.append("Archivo no seleccionado o no válido")
        
        # Verificar fechas
        dates_valid = bool(
            config.get("start_date") and 
            config.get("end_date") and
            config.get("start_date") != "" and
            config.get("end_date") != ""
        )
        if not dates_valid:
            errors.append("Fechas no configuradas")
            
       # AGREGADO: Verificar fondos
        funds_valid = bool(
            config.get("starting_funds") and
            config.get("margin_allocation_percent") and
            config.get("max_contracts_per_trade")
        )
        if not funds_valid:
            errors.append("Configuración de fondos incompleta")
        
        # Estado general CON fondos
        overall_valid = internet and file_valid and dates_valid and funds_valid
        
        return {
            'internet': internet,
            'file_valid': file_valid,
            'dates_valid': dates_valid,
            'funds_valid': funds_valid,
            'overall_valid': overall_valid,
            'errors': errors
        }
        
    except Exception as e:
        return {
            'internet': False,
            'file_valid': False,
            'dates_valid': False,
            'funds_valid': False,
            'overall_valid': False,
            'errors': [f"Error en validación: {str(e)}"]
        }

def get_debug_info_complete(config, selected_file):
    """
    MODIFICADO: Las fechas ya están en MM/DD/YYYY, no convertir
    """
    try:
        status = get_validation_status(config, selected_file)
        
        # Información detallada del archivo
        file_info = ""
        if selected_file:
            file_data = get_file_info(selected_file)
            if file_data:
                file_info = f" - {file_data['name']} ({file_data['size']})"
            else:
                file_info = f" - {os.path.basename(selected_file)}"
        
        # CAMBIADO: Las fechas ya están en MM/DD/YYYY, usar directamente
        dates_info = ""
        if config.get("start_date") and config.get("end_date"):
            # NO CONVERTIR - ya están en MM/DD/YYYY
            start_date = config['start_date']
            end_date = config['end_date']
            dates_info = f" - Desde {start_date} hasta {end_date}"
        
        #Informacion de Estrategia
        strategy_info = ""
        if config:  # Si hay configuración
            # Obtener valores directamente del JSON plano
            buy_sell = config.get("buy_sell", "Buy")
            call_put = config.get("call_put", "Put") 
            qty = config.get("qty", 1)
            percent = config.get("percent", 15)
            dte = config.get("dte", 90)
            strategy = config.get("strategy", "Select strategy")
            pct_type = config.get("pct_type", "Delta")
            
            # Verificar si tiene valores configurados (no por defecto)
            has_custom_strategy = (
                strategy != "Select strategy" or
                buy_sell != "Buy" or
                call_put != "Put" or
                qty != 1 or
                percent != 15 or
                dte != 90 or
                pct_type != "Delta"
            )
            
            if has_custom_strategy:
                strategy_parts = []
                strategy_parts.append(f"Estrategia: {strategy}")
                strategy_parts.append(f"{buy_sell} {call_put}")
                strategy_parts.append(f"QTY: {qty}")
                strategy_parts.append(f"%: {percent} ({pct_type})")
                strategy_parts.append(f"DTE: {dte}")
                
                strategy_info = f" - {' | '.join(strategy_parts)}"
            else:
                strategy_info = " - Valores por defecto (Select strategy | Buy Put | QTY: 1 | %: 15 (Delta) | DTE: 90)"
        else:
            strategy_info = " - Sin configuración"
        
        #Informacion de Fondos
        funds_info = ""
        if config:  # Si hay configuración
            # Obtener valores directamente del JSON plano
            starting_funds = config.get("starting_funds", "100000")
            margin_allocation = config.get("margin_allocation_percent", "10")
            max_contracts = config.get("max_contracts_per_trade", "1")
            max_open_trades = config.get("max_open_trades", "")
            max_allocation = config.get("max_allocation_amount", "")
            prune_oldest = config.get("prune_oldest_trades", False)
            ignore_margin = config.get("ignore_margin_requirements", True)
            
            # Verificar si tiene valores configurados (no por defecto)
            has_custom_funds = (
                starting_funds != "100000" or
                margin_allocation != "10" or
                max_contracts != "1" or
                max_open_trades != "" or
                max_allocation != "" or
                prune_oldest != False or
                ignore_margin != True
            )
            
            if has_custom_funds or True:  # Siempre mostrar fondos
                funds_parts = []
                funds_parts.append(f"Capital: ${starting_funds}")
                funds_parts.append(f"Margen: {margin_allocation}%")
                funds_parts.append(f"Contratos: {max_contracts}")
                
                if max_open_trades:
                    funds_parts.append(f"Max Trades: {max_open_trades}")
                    if prune_oldest:
                        funds_parts.append("Prune: ON")
                
                if ignore_margin:
                    funds_parts.append("Sin Margen")
                
                if max_allocation:
                    funds_parts.append(f"Max: ${max_allocation}")
                
                funds_info = f" - {' | '.join(funds_parts)}"
            else:
                funds_info = " - Valores por defecto (Capital: $100000 | Margen: 10% | Contratos: 1 | Sin Margen)"
        else:
            funds_info = " - Sin configuración"
        
        connection_info = "Estable y rápida 🚀" if status['internet'] else "Desconectado 😢"
        
        general_info = ""
        output_path = config.get("output_path", "") or get_output_folder()
        if output_path:
            general_info = f" - {output_path}"
        
        config_path = get_config_folder()
        logs_path = get_logs_folder()
        
        return {
            'status': status,
            'file_info': file_info,
            'dates_info': dates_info,
            'strategy_info': strategy_info,
            'funds_info': funds_info,
            'connection_info': connection_info,
            'general_info': general_info,
            'config_path': config_path,
            'logs_path': logs_path
        }
        
    except Exception as e:
        return {
            'status': get_validation_status(config, selected_file),
            'file_info': " - Error obteniendo info",
            'dates_info': " - Error obteniendo fechas",
            'strategy_info': " - Error obteniendo estrategia",
            'funds_info': " - Error obteniendo fondos",
            'connection_info': "Error de conexión",
            'general_info': f" - Error: {str(e)}",
            'config_path': get_config_folder(),
            'logs_path': get_logs_folder()
        }

def validate_funds_config(config):
    """
    NUEVA: Validar configuración de fondos
    
    Args:
        config (dict): Configuración a validar
        
    Returns:
        tuple: (bool, str) - (es_válido, mensaje)
    """
    try:
        # Validar Starting Funds
        starting_funds = config.get('starting_funds', '')
        if starting_funds:
            try:
                funds_value = float(starting_funds)
                if funds_value <= 0:
                    return False, "Starting Funds debe ser mayor a 0"
            except ValueError:
                return False, "Starting Funds debe ser un número válido"
        
        # Validar Margin Allocation
        margin_percent = config.get('margin_allocation_percent', '')
        if margin_percent:
            try:
                margin_value = float(margin_percent)
                if margin_value <= 0 or margin_value > 100:
                    return False, "Margin Allocation debe estar entre 1% y 100%"
            except ValueError:
                return False, "Margin Allocation debe ser un porcentaje válido"
        
        # Validar Max Open Trades
        max_trades = config.get('max_open_trades', '')
        if max_trades:
            try:
                trades_value = int(max_trades)
                if trades_value <= 0:
                    return False, "Max Open Trades debe ser mayor a 0"
            except ValueError:
                return False, "Max Open Trades debe ser un número entero válido"
        
        # Validar Max Contracts Per Trade
        max_contracts = config.get('max_contracts_per_trade', '')
        if max_contracts:
            try:
                contracts_value = int(max_contracts)
                if contracts_value <= 0:
                    return False, "Max Contracts Per Trade debe ser mayor a 0"
            except ValueError:
                return False, "Max Contracts Per Trade debe ser un número entero válido"
        
        # Validar Max Allocation Amount
        max_allocation = config.get('max_allocation_amount', '')
        if max_allocation:
            try:
                allocation_value = float(max_allocation)
                if allocation_value <= 0:
                    return False, "Max Allocation Amount debe ser mayor a 0"
            except ValueError:
                return False, "Max Allocation Amount debe ser un número válido"
        
        return True, "Configuración de fondos válida"
        
    except Exception as e:
        return False, f"Error validando configuración de fondos: {str(e)}"

# =============================================================================
# FUNCIONES DE CONEXIÓN
# =============================================================================

def check_internet_connection():
    """
    Verificar conexión a internet
    
    Utilizada por: gui.py (timer cada 5s)
    Propósito: Monitorear estado de conexión para habilitar/deshabilitar funciones
    
    Returns:
        bool: True si hay conexión
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        try:
            urllib.request.urlopen('http://www.google.com', timeout=3)
            return True
        except:
            return False

def get_connection_status():
    """
    Obtener estado de conexión con mensaje descriptivo
    
    Utilizada por: gui.py (actualizar status bar)
    Propósito: Obtener estado formateado para mostrar en UI
    
    Returns:
        tuple: (is_connected, status_message)
    """
    if check_internet_connection():
        return True, "Conectado"
    else:
        return False, "Sin conexión"

# =============================================================================
# FUNCIONES DE ARCHIVOS Y LOGS
# =============================================================================

def get_system_info_for_logs(config, selected_file):
    """
    Obtener información relevante del sistema y configuración para logs.
    Args:
        config (dict): Configuración actual.
        selected_file (str): Archivo seleccionado.
    Returns:
        list: Líneas de información del sistema para escribir en el log.
    """
    import platform
    info_lines = []
    info_lines.append(f"Sistema operativo: {platform.system()} {platform.release()} ({platform.version()})")
    info_lines.append(f"Usuario: {os.environ.get('USERNAME') or os.environ.get('USER') or 'N/A'}")
    info_lines.append(f"Carpeta de trabajo: {os.getcwd()}")
    info_lines.append(f"Archivo seleccionado: {selected_file if selected_file else 'Ninguno'}")
    if config:
        info_lines.append(f"Configuración:")
        for k, v in config.items():
            info_lines.append(f"  - {k}: {v}")
    return info_lines

def save_logs(log_content, config=None, selected_file=None):
    """
    ACTUALIZADO: Guardar logs con información del sistema incluida
    
    Utilizada por: gui.py (al cerrar ventana)
    Propósito: Persistir logs de sesión con información completa del sistema
    
    Args:
        log_content (str): Contenido de logs a guardar
        config (dict): Configuración actual (opcional)
        selected_file (str): Archivo seleccionado (opcional)
        
    Returns:
        tuple: (success, log_file_path)
    """
    try:
        logs_dir = get_logs_folder()
        
        now = datetime.now()
        filename = now.strftime("omega_bot_session_%Y_%m_%d_%H:%M:%S.log")
        log_path = os.path.join(logs_dir, filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            # Header del log
            f.write(f"=== OMEGABOT SESSION LOG ===\n")
            f.write(f"Fecha y hora de inicio: {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            
            # AGREGADO: Información del sistema al inicio
            if config is not None and selected_file is not None:
                system_info = get_system_info_for_logs(config, selected_file)
                for line in system_info:
                    f.write(f"{line}\n")
                f.write(f"\n{'='*60}\n\n")
            
            # Logs de la sesión
            f.write("LOGS DE LA SESIÓN\n")
            f.write("="*60 + "\n")
            f.write(log_content)
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Sesión finalizada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        return True, log_path
    except Exception as e:
        print(f"Error guardando logs: {e}")
        return False, None

def get_file_info(file_path):
    """
    Obtener información de archivo seleccionado
    
    Utilizada por: gui.py (mostrar info de archivo)
    Propósito: Obtener metadatos del archivo para mostrar en UI
    
    Args:
        file_path (str): Ruta del archivo
        
    Returns:
        dict: Información del archivo o None si error
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        size_bytes = stat.st_size
        
        # Formatear tamaño
        if size_bytes == 0:
            size_str = "0 B"
        else:
            size_names = ["B", "KB", "MB", "GB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            if i >= len(size_names):
                i = len(size_names) - 1
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            size_str = f"{s} {size_names[i]}"
        
        return {
            'name': os.path.basename(file_path),
            'size': size_str,
            'size_bytes': size_bytes,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M:%S'),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception as e:
        print(f"Error obteniendo info del archivo: {e}")
        return None

# =============================================================================
# FUNCIONES DE UTILIDAD PARA ESTRATEGIAS
# =============================================================================

def get_available_strategies():
    """
    Obtener lista de estrategias disponibles
    
    Utilizada por: estrategia.py
    Propósito: Cargar opciones de estrategia en combobox
    
    Returns:
        list: Lista de estrategias disponibles
    """
    return [
        "Select strategy",
        "Long Call",
        "Long Put", 
        "Short Call",
        "Short Put",
        "Bull Call Spread",
        "Bear Put Spread",
        "Iron Condor",
        "Butterfly Spread",
        "Straddle",
        "Strangle"
    ]

def get_pct_types():
    """
    Obtener tipos de porcentaje disponibles
    
    Utilizada por: estrategia.py
    Propósito: Cargar opciones de tipo de porcentaje
    
    Returns:
        list: Lista de tipos de porcentaje
    """
    return ["Delta", "Percentage", "Strike"]

def get_buy_sell_options():
    """
    Obtener opciones de compra/venta
    
    Utilizada por: estrategia.py
    Propósito: Cargar opciones de dirección
    
    Returns:
        list: Lista de opciones buy/sell
    """
    return ["Buy", "Sell"]

def get_call_put_options():
    """
    Obtener opciones de call/put
    
    Utilizada por: estrategia.py
    Propósito: Cargar opciones de tipo de opción
    
    Returns:
        list: Lista de opciones call/put
    """
    return ["Call", "Put"]

def get_yes_no_options():
    """
    Obtener opciones sí/no
    
    Utilizada por: estrategia.py, general.py
    Propósito: Cargar opciones booleanas
    
    Returns:
        list: Lista de opciones Yes/No
    """
    return ["Yes", "No"]

# =============================================================================
# FUNCIONES DE CONEXIÓN
# =============================================================================

def check_internet_connection():
    """
    Verificar conexión a internet
    
    Utilizada por: gui.py (timer cada 5s)
    Propósito: Monitorear estado de conexión para habilitar/deshabilitar funciones
    
    Returns:
        bool: True si hay conexión
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        try:
            urllib.request.urlopen('http://www.google.com', timeout=3)
            return True
        except:
            return False

def get_connection_status():
    """
    Obtener estado de conexión con mensaje descriptivo
    
    Utilizada por: gui.py (actualizar status bar)
    Propósito: Obtener estado formateado para mostrar en UI
    
    Returns:
        tuple: (is_connected, status_message)
    """
    if check_internet_connection():
        return True, "Conectado"
    else:
        return False, "Sin conexión"

# =============================================================================
# FUNCIONES DE ARCHIVOS Y LOGS
# =============================================================================

def get_system_info_for_logs(config, selected_file):
    """
    Obtener información relevante del sistema y configuración para logs.
    Args:
        config (dict): Configuración actual.
        selected_file (str): Archivo seleccionado.
    Returns:
        list: Líneas de información del sistema para escribir en el log.
    """
    import platform
    info_lines = []
    info_lines.append(f"Sistema operativo: {platform.system()} {platform.release()} ({platform.version()})")
    info_lines.append(f"Usuario: {os.environ.get('USERNAME') or os.environ.get('USER') or 'N/A'}")
    info_lines.append(f"Carpeta de trabajo: {os.getcwd()}")
    info_lines.append(f"Archivo seleccionado: {selected_file if selected_file else 'Ninguno'}")
    if config:
        info_lines.append(f"Configuración:")
        for k, v in config.items():
            info_lines.append(f"  - {k}: {v}")
    return info_lines

def save_logs(log_content, config=None, selected_file=None):
    """
    ACTUALIZADO: Guardar logs con información del sistema incluida
    
    Utilizada por: gui.py (al cerrar ventana)
    Propósito: Persistir logs de sesión con información completa del sistema
    
    Args:
        log_content (str): Contenido de logs a guardar
        config (dict): Configuración actual (opcional)
        selected_file (str): Archivo seleccionado (opcional)
        
    Returns:
        tuple: (success, log_file_path)
    """
    try:
        logs_dir = get_logs_folder()
        
        now = datetime.now()
        filename = now.strftime("omega_bot_session_%Y_%m_%d_%H:%M:%S.log")
        log_path = os.path.join(logs_dir, filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            # Header del log
            f.write(f"=== OMEGABOT SESSION LOG ===\n")
            f.write(f"Fecha y hora de inicio: {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            
            # AGREGADO: Información del sistema al inicio
            if config is not None and selected_file is not None:
                system_info = get_system_info_for_logs(config, selected_file)
                for line in system_info:
                    f.write(f"{line}\n")
                f.write(f"\n{'='*60}\n\n")
            
            # Logs de la sesión
            f.write("LOGS DE LA SESIÓN\n")
            f.write("="*60 + "\n")
            f.write(log_content)
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Sesión finalizada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        return True, log_path
    except Exception as e:
        print(f"Error guardando logs: {e}")
        return False, None

def get_file_info(file_path):
    """
    Obtener información de archivo seleccionado
    
    Utilizada por: gui.py (mostrar info de archivo)
    Propósito: Obtener metadatos del archivo para mostrar en UI
    
    Args:
        file_path (str): Ruta del archivo
        
    Returns:
        dict: Información del archivo o None si error
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        size_bytes = stat.st_size
        
        # Formatear tamaño
        if size_bytes == 0:
            size_str = "0 B"
        else:
            size_names = ["B", "KB", "MB", "GB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            if i >= len(size_names):
                i = len(size_names) - 1
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            size_str = f"{s} {size_names[i]}"
        
        return {
            'name': os.path.basename(file_path),
            'size': size_str,
            'size_bytes': size_bytes,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M:%S'),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception as e:
        print(f"Error obteniendo info del archivo: {e}")
        return None

# =============================================================================
# FUNCIONES DE DEBUG Y DIAGNÓSTICO
# =============================================================================

def get_debug_lines_for_ui(status):
    """
    MODIFICADO: Sin línea de estrategia en el debug simplificado
    """
    try:
        debug_lines = []
        
        # Estado de componentes individuales (SIN estrategia)
        debug_lines.append(f"🌐 Internet: {'✓ Conectado' if status['internet'] else '✗ Sin conexión'}")
        debug_lines.append(f"📄 Archivo: {'✓ Válido' if status['file_valid'] else '✗ No seleccionado/inválido'}")
        debug_lines.append(f"📅 Fechas: {'✓ Configuradas' if status['dates_valid'] else '✗ No configuradas'}")
        debug_lines.append(f"💰 Fondos: {'✓ Configurados' if status['funds_valid'] else '✗ No configurados'}")
        debug_lines.append("")  # Línea vacía para separar
        debug_lines.append(f"🎯 Estado General: {'✓ LISTO PARA INICIAR' if status['overall_valid'] else '✗ NO LISTO'}")
        
        # Agregar errores si existen
        if not status['overall_valid'] and status['errors']:
            debug_lines.append("")  # Línea vacía
            debug_lines.append("❌ Errores encontrados:")
            for error in status['errors']:
                debug_lines.append(f"  • {error}")
        
        return debug_lines
        
    except Exception as e:
        return [f"Error generando debug para UI: {str(e)}"]

def get_current_timestamp():
    """
    NUEVO: Obtener timestamp actual para tracking de tiempo
    """
    return datetime.now()

def format_execution_summary(start_time, end_time, analysis_count):
    """
    NUEVO: Formatear resumen de ejecución con tiempo y estadísticas
    """
    try:
        # Calcular duración
        duration = end_time - start_time
        
        # Formatear duración en formato legible
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Calcular análisis por minuto si hay análisis
        if analysis_count > 0 and total_seconds > 0:
            rate = (analysis_count / total_seconds) * 60  # análisis por minuto
            rate_str = f" - Velocidad: {rate:.1f} análisis/min"
        else:
            rate_str = ""
        
        # Generar mensaje completo
        summary = (
            f"📊 RESUMEN DE EJECUCIÓN - "
            f"Duración: {duration_str} - "
            f"Enlaces procesados: {analysis_count}{rate_str}"
        )
        
        return summary
        
    except Exception as e:
        return f"Error generando resumen de ejecución: {str(e)}"

def log_debug_lines(self, debug_lines):
    """
    NUEVO: Loggear líneas de debug con formato apropiado
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
    NUEVO: Actualizar display de tiempo de ejecución cada segundo
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

def get_system_status_summary(config, selected_file):
    """
    Obtener resumen del estado del sistema para mostrar en UI (SIN ICONOS)
    
    Utilizada por: gui.py (logs), setting_gui.py (widget de estado)
    Propósito: Mostrar estado actual en tiempo real
    
    Args:
        config (dict): Configuración actual
        selected_file (str): Archivo seleccionado
        
    Returns:
        dict: Resumen del estado con mensajes para UI
    """
    status = get_validation_status(config, selected_file)
    
    summary = {
        "ready": status["overall_valid"],
        "items": [],
        "missing_count": 0
    }
    
    # Solo mostrar elementos obligatorios
    if status["internet"]:
        summary["items"].append("Conexión a internet")
    else:
        summary["items"].append("Sin conexión a internet")
        summary["missing_count"] += 1
    
    if status["file_valid"]:
        summary["items"].append("Archivo válido seleccionado")
    else:
        summary["items"].append("Archivo no seleccionado o inválido")
        summary["missing_count"] += 1
    
    if status["dates_valid"]:
        summary["items"].append("Fechas configuradas correctamente")
    else:
        summary["items"].append("Fechas no configuradas o inválidas")
        summary["missing_count"] += 1
    
    # Mensaje principal (solo requisitos obligatorios)
    if summary["ready"]:
        summary["main_message"] = "Sistema listo para análisis"
        summary["status_color"] = "#27ae60"
    else:
        summary["main_message"] = f"Faltan {summary['missing_count']} requisitos"
        summary["status_color"] = "#e74c3c"
    
    return summary

def get_funds_config_summary(config):
    """
    ARREGLADO: Leer configuración de fondos directamente del JSON plano
    """
    try:
        # ARREGLADO: Obtener valores directamente del config (JSON plano)
        starting_funds = config.get('starting_funds', '100000')
        margin_allocation = config.get('margin_allocation_percent', '10')
        max_open_trades = config.get('max_open_trades', '')
        prune_oldest = config.get('prune_oldest_trades', False)
        max_contracts = config.get('max_contracts_per_trade', '1')
        ignore_margin = config.get('ignore_margin_requirements', False)
        max_allocation = config.get('max_allocation_amount', '')
        
        # Formatear para mostrar
        summary_parts = []
        
        # Capital inicial
        summary_parts.append(f"Capital: ${starting_funds}")
        
        # Asignación de margen
        summary_parts.append(f"Margen: {margin_allocation}%")
        
        # Trades máximos
        if max_open_trades:
            summary_parts.append(f"Max Trades: {max_open_trades}")
            if prune_oldest:
                summary_parts.append("Prune: ON")
        
        # Contratos
        summary_parts.append(f"Contratos: {max_contracts}")
        
        # Ignorar margen
        if ignore_margin:
            summary_parts.append("Sin Margen")
        
        # Asignación máxima
        if max_allocation:
            summary_parts.append(f"Max: ${max_allocation}")
        
        return " | ".join(summary_parts)
        
    except Exception as e:
        return f"Error obteniendo resumen de fondos: {str(e)}"

