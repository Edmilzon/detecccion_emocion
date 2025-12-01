import json
import random
from src.data.data_manager import DataManager
from src.utils.logger import get_logger

class ResponseGenerator:
    def __init__(self):
        self.logger = get_logger()
        self.data_manager = DataManager()
        self.responses = self._load_responses()
    
    def _load_responses(self):
        """Carga las respuestas desde JSON (lista simple sin etiquetas)"""
        try:
            responses = self.data_manager.load_json('config/respuestas.json')
            # Verificar que sea una lista
            if not responses or not isinstance(responses, list):
                raise ValueError("Respuestas deben ser una lista")
            if len(responses) == 0:
                raise ValueError("Lista de respuestas vacía")
            return responses
        except Exception as e:
            self.logger.warning(f"Error cargando respuestas: {e}, usando respuestas por defecto")
            # Respuestas por defecto (lista simple)
            return [
                "¡Me alegra mucho escuchar tu entusiasmo!",
                "¡Qué energía tan positiva! Sigue así",
                "Me encanta tu actitud positiva",
                "Lamento que estés pasando por esto",
                "Es válido sentirse así. Estoy aquí para escucharte",
                "Los momentos difíciles pasan. Cuenta conmigo",
                "Entiendo tu frustración. Es válido sentirse así",
                "Gracias por compartir. ¿Quieres contarme más?",
                "Entiendo. ¿Hay algo específico en lo que pueda ayudarte?",
                "Gracias por tu mensaje. ¿Cómo te sientes al respecto?",
                "Lo siento, no pude procesar tu mensaje correctamente"
            ]
    
    def get_response(self, emotion, user_message):
        """Obtiene una respuesta aleatoria de la lista (sin etiquetas)"""
        try:
            # Como ahora es una lista simple sin etiquetas, seleccionamos aleatoriamente
            if not self.responses or len(self.responses) == 0:
                return "Gracias por tu mensaje. ¿En qué más puedo ayudarte?"
            
            # Seleccionar respuesta aleatoria de la lista
            response = random.choice(self.responses)
            
            self.logger.info(f"Respuesta generada para emoción detectada: {emotion}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return "Gracias por tu mensaje. ¿En qué más puedo ayudarte?"