import json
from datetime import datetime
from .predictor import EmotionPredictor
from .responses import ResponseGenerator
from src.data.data_manager import DataManager
from src.utils.logger import get_logger

class EmotionChatbot:
    def __init__(self):
        self.logger = get_logger()
        self.predictor = EmotionPredictor()
        self.response_gen = ResponseGenerator()
        self.data_manager = DataManager()
        self.conversation_history = []
        
        self.logger.info("Chatbot de Emociones inicializado (K-means No Supervisado)")
        
    def process_message(self, user_message):
        """Procesa un mensaje del usuario y genera respuesta usando K-means"""
        try:
            # Validar entrada
            if not user_message or len(user_message.strip()) == 0:
                return self._get_empty_message_response()
            
            # Predecir emoción usando K-means (no supervisado)
            emotion, confidence, cluster_info = self.predictor.predict(user_message)
            
            # Generar respuesta contextual
            bot_response = self.response_gen.get_response(emotion, user_message)
            
            # Guardar en historial
            self._save_conversation(user_message, emotion, bot_response, cluster_info)
            
            return {
                'response': bot_response,
                'emotion': emotion,
                'confidence': confidence,
                'cluster': cluster_info.get('cluster_id', -1),
                'top_words': cluster_info.get('top_words', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {e}")
            return self._get_error_response()
    
    def _save_conversation(self, user_msg, emotion, bot_response, cluster_info):
        """Guarda la conversación en JSON"""
        conversation_entry = {
            'user_message': user_msg,
            'detected_emotion': emotion,
            'bot_response': bot_response,
            'cluster_id': cluster_info.get('cluster_id'),
            'cluster_words': cluster_info.get('top_words', []),
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_history.append(conversation_entry)
        self.data_manager.save_conversation(conversation_entry)
        
        self.logger.info(f"Emoción detectada: {emotion} (Cluster: {cluster_info.get('cluster_id')})")
    
    def _get_empty_message_response(self):
        return {
            'response': "Por favor escribe un mensaje para poder analizar tus emociones.",
            'emotion': 'neutral',
            'confidence': 0.0,
            'cluster': -1,
            'top_words': []
        }
    
    def _get_error_response(self):
        return {
            'response': "Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo.",
            'emotion': 'neutral',
            'confidence': 0.0,
            'cluster': -1,
            'top_words': []
        }
    
    def run_chat_interface(self):
        """Interfaz de línea de comandos para chatear"""
        print("\n" + "="*50)
        print("CHATBOT DE EMOCIONES - APRENDIZAJE NO SUPERVISADO")
        print("="*50)
        print("Sistema basado en K-means y TF-IDF")
        print("Emociones: Positivo | Negativo | Neutral")
        print("Escribe 'salir' para terminar")
        print("="*50)
        
        while True:
            try:
                user_input = input("\nTú: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit', 'adios']:
                    print("\n¡Hasta luego! Gracias por chatear.")
                    break
                    
                if not user_input:
                    print("Por favor escribe un mensaje")
                    continue
                
                # Procesar mensaje
                result = self.process_message(user_input)
                
                # Mostrar resultado con información del cluster
                print(f"Bot [{result['emotion'].upper()}]: {result['response']}")
                print(f"   Cluster: {result['cluster']} | Confianza: {result['confidence']:.2f}")
                if result['top_words']:
                    print(f"  Palabras clave: {', '.join(result['top_words'][:3])}")
                    
            except KeyboardInterrupt:
                print("\n\n¡Chat terminado! Hasta pronto.")
                break
            except Exception as e:
                print(f" Error: {e}")
                self.logger.error(f"Error en interfaz: {e}")