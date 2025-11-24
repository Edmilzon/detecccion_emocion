from .data_manager import DataManager
from src.utils.logger import get_logger

class ConfigLoader:
    def __init__(self):
        self.logger = get_logger()
        self.data_manager = DataManager()
    
    def load_emotions_config(self):
        """Carga la configuración de emociones"""
        return self.data_manager.load_json('config/emociones.json')
    
    def load_responses_config(self):
        """Carga la configuración de respuestas"""
        return self.data_manager.load_json('config/respuestas.json')
    
    def load_parameters_config(self):
        """Carga la configuración de parámetros"""
        return self.data_manager.load_json('config/parametros.json')