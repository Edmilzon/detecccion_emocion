import joblib
import os
from src.utils.logger import get_logger

class ModelLoader:
    def __init__(self):
        self.logger = get_logger()
    
    def load_trained_model(self, model_path='models/current/modelo_entrenado.pkl'):
        """Carga un modelo entrenado"""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Modelo no encontrado en {model_path}")
            
            model_data = joblib.load(model_path)
            self.logger.info("Modelo cargado exitosamente")
            return model_data
            
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
            raise