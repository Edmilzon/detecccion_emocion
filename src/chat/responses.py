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
        """Carga las respuestas desde JSON"""
        try:
            return self.data_manager.load_json('config/respuestas.json')
        except:
            # Respuestas por defecto
            return {
                "positivo": [
                    "¡Me alegra mucho escuchar tu entusiasmo!",
                    "¡Qué energía tan positiva! Sigue así ",
                    "Me encanta tu actitud positiva "
                ],
                "negativo": [
                    "Lamento que estés pasando por esto",
                    "Es válido sentirse así. Estoy aquí para escucharte",
                    "Los momentos difíciles pasan. Cuenta conmigo"
                ],
                "neutral": [
                    "Gracias por compartir. ¿Quieres contarme más?",
                    "Entiendo. ¿Hay algo específico en lo que pueda ayudarte?",
                    "Gracias por tu mensaje. ¿Cómo te sientes al respecto?"
                ],
                "error": [
                    "Lo siento, no pude procesar tu mensaje correctamente",
                    "Hubo un error entendiendo tu mensaje. ¿Puedes reformularlo?"
                ]
            }
    
    def get_response(self, emotion, user_message):
        """Obtiene una respuesta contextual basada en la emoción"""
        try:
            emotion_responses = self.responses.get(emotion, self.responses["neutral"])
            
            # Seleccionar respuesta aleatoria para variedad
            response = random.choice(emotion_responses)
            
            self.logger.info(f"Respuesta generada para emoción: {emotion}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return "Gracias por tu mensaje. ¿En qué más puedo ayudarte?"