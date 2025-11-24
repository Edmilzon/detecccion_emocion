import logging
import json
import os
from datetime import datetime

def setup_logger():
    """Configura el sistema de logging"""
    logger = logging.getLogger('EmotionChatbot')
    logger.setLevel(logging.INFO)
    
    # Evitar logs duplicados
    if not logger.handlers:
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/chatbot.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger():
    """Obtiene el logger configurado"""
    return logging.getLogger('EmotionChatbot')

def log_error(error_type, message):
    """Guarda un error en el archivo de errores JSON"""
    try:
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message
        }
        
        # Cargar errores existentes
        errors_file = 'logs/errores.json'
        errors = []
        if os.path.exists(errors_file):
            with open(errors_file, 'r', encoding='utf-8') as f:
                errors = json.load(f)
        
        # Agregar nuevo error
        errors.append(error_log)
        
        # Guardar (mantener últimos 50 errores)
        if len(errors) > 50:
            errors = errors[-50:]
        
        with open(errors_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error guardando log: {e}")