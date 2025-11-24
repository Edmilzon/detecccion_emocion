import pandas as pd
import json
import os
from datetime import datetime
from src.utils.logger import get_logger

class DataManager:
    def __init__(self):
        self.logger = get_logger()
    
    def load_csv(self, file_path):
        """Carga un archivo CSV"""
        try:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                self.logger.info(f"CSV cargado: {file_path} - {len(df)} registros")
                return df
            else:
                self.logger.warning(f"Archivo no encontrado: {file_path}")
                return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error cargando CSV {file_path}: {e}")
            return pd.DataFrame()
    
    def save_csv(self, df, file_path):
        """Guarda un DataFrame en CSV"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path, index=False, encoding='utf-8')
            self.logger.info(f"CSV guardado: {file_path}")
        except Exception as e:
            self.logger.error(f"Error guardando CSV {file_path}: {e}")
    
    def load_json(self, file_path):
        """Carga un archivo JSON"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.info(f"JSON cargado: {file_path}")
                return data
            else:
                self.logger.warning(f"Archivo JSON no encontrado: {file_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Error cargando JSON {file_path}: {e}")
            return {}
    
    def save_json(self, data, file_path):
        """Guarda datos en JSON"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"JSON guardado: {file_path}")
        except Exception as e:
            self.logger.error(f"Error guardando JSON {file_path}: {e}")
    
    def save_conversation(self, conversation_data):
        """Guarda una conversación en el historial"""
        try:
            history_file = 'data/history/conversaciones.json'
            history = self.load_json(history_file)
            
            if 'conversations' not in history:
                history['conversations'] = []
            
            history['conversations'].append(conversation_data)
            
            # Mantener solo las últimas 100 conversaciones
            if len(history['conversations']) > 100:
                history['conversations'] = history['conversations'][-100:]
            
            self.save_json(history, history_file)
            self.logger.info("Conversación guardada en historial")
            
        except Exception as e:
            self.logger.error(f"Error guardando conversación: {e}")