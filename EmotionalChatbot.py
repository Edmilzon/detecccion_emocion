from EmotionAnalyzer import EmotionAnalyzer
import pandas as pd
import random


class EmotionalChatbot:
    def __init__(self):
        self.analyzer = EmotionAnalyzer(n_clusters=5)
        self.conversation_history = []
        
    def train_with_sample_data(self):
        """Entrena con datos de ejemplo (en un caso real, usarías datos reales)"""
        sample_texts = [
            "Estoy muy feliz hoy, todo me sale bien",
            "Me siento genial con los resultados",
            "Qué día tan maravilloso",
            "Estoy contento con el progreso",
            "Estoy triste y desanimado",
            "Qué mal me siento hoy",
            "Todo sale terrible",
            "No tengo ganas de nada",
            "Estoy enojado con esta situación",
            "Qué rabia me da esto",
            "Me tiene furioso",
            "Estoy muy molesto",
            "Tengo miedo de lo que pueda pasar",
            "Me siento preocupado",
            "Qué susto me dio",
            "Hoy es un día normal",
            "Todo está bien, sin novedades",
            "Voy a trabajar como siempre"
        ]
        self.analyzer.fit(sample_texts)
    
    def get_emotional_response(self, emotion, user_message):
        """Genera respuesta basada en la emoción detectada"""
        responses = {
            'positivo': [
                "¡Me alegra mucho saber que te sientes así!",
                "¡Qué genial! Sigue con esa energía positiva",
                "Me encanta verte tan motivado, ¡así se hace!"
            ],
            'negativo': [
                "Lamento escuchar que no te sientes bien. ¿Quieres hablar de ello?",
                "Entiendo que puedas sentirte así. Recuerda que los malos momentos pasan",
                "Estoy aquí para escucharte. Cuéntame más sobre cómo te sientes"
            ],
            'enojo': [
                "Parece que estás molesto. Respirar profundo puede ayudar",
                "Entiendo tu frustración. A veces es bueno expresar lo que sentimos",
                "Tomemos un momento para calmarnos. Estoy aquí para ayudarte"
            ],
            'miedo': [
                "Entiendo que puedas sentir temor. ¿Qué es lo que más te preocupa?",
                "No estás solo. Juntos podemos enfrentar lo que te preocupa",
                "Es normal sentir miedo a veces. Hablemos de qué te inquieta"
            ],
            'neutral': [
                "Entiendo. ¿Hay algo específico en lo que te pueda ayudar hoy?",
                "Gracias por compartir. ¿En qué más puedo asistirte?",
                "Perfecto. Estoy aquí para lo que necesites"
            ]
        }
        
        # Seleccionar respuesta aleatoria para la emoción
        return random.choice(responses.get(emotion, responses['neutral']))
    
    def chat(self):
        """Inicia el chat interactivo"""
        print(" Chatbot Emocional: ¡Hola! Escribe 'salir' para terminar la conversación.")
        print("Puedes contarme cómo te sientes o lo que piensas.\n")
        
        if not self.analyzer.is_fitted:
            print("Entrenando el modelo con datos de ejemplo...")
            self.train_with_sample_data()
            print("Modelo listo!\n")
        
        while True:
            user_input = input("Tú: ")
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print(" ¡Ha sido un gusto conversar contigo! Hasta pronto ")
                break
            
            if not user_input.strip():
                print(" Por favor, escribe algo para poder ayudarte mejor.")
                continue
            
            # Analizar emoción
            try:
                emotion = self.analyzer.predict_emotion(user_input)
                probabilities = self.analyzer.get_emotion_probability(user_input)
                
                # Guardar en historial
                self.conversation_history.append({
                    'message': user_input,
                    'emotion': emotion,
                    'probabilities': probabilities
                })
                
                # Obtener respuesta emocional
                response = self.get_emotional_response(emotion, user_input)
                
                print(f" {response}")
                print(f"   [Emoción detectada: {emotion.upper()}]")
                
                # Mostrar análisis detallado ocasionalmente
                if len(self.conversation_history) % 3 == 0:
                    self.show_emotional_analysis()
                    
            except Exception as e:
                print(f"Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo.")
    
    def show_emotional_analysis(self):
        """Muestra análisis del patrón emocional de la conversación"""
        if len(self.conversation_history) >= 2:
            emotions = [entry['emotion'] for entry in self.conversation_history[-5:]]
            emotion_counts = pd.Series(emotions).value_counts()
            
            print("\n Análisis de tu estado emocional reciente:")
            for emotion, count in emotion_counts.items():
                print(f"   {emotion}: {count} mensajes")
            print()
    
    def generate_conversation_report(self):
        """Genera un reporte de la conversación"""
        if not self.conversation_history:
            print("No hay historial de conversación para analizar.")
            return
        
        df = pd.DataFrame(self.conversation_history)
        print("\n" + "="*50)
        print("REPORTE FINAL DE LA CONVERSACIÓN")
        print("="*50)
        
        # Estadísticas de emociones
        emotion_stats = df['emotion'].value_counts()
        print("\nDistribución de emociones:")
        for emotion, count in emotion_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {emotion}: {count} veces ({percentage:.1f}%)")
        
        # Emoción predominante
        predominant_emotion = emotion_stats.index[0]
        print(f"\nEmoción predominante: {predominant_emotion.upper()}")
        
        # Recomendación basada en el análisis
        recommendations = {
            'positivo': "¡Mantén esa actitud positiva! Sigue haciendo lo que te hace feliz.",
            'negativo': "Te recomiendo practicar ejercicios de gratitud y mindfulness.",
            'enojo': "La respiración profunda y el ejercicio pueden ayudar a manejar la frustración.",
            'miedo': "Hablar sobre tus preocupaciones y dividirlas en pasos pequeños puede ayudar.",
            'neutral': "Mantén el equilibrio. Explora nuevas actividades para añadir emoción."
        }
        
        print(f"Recomendación: {recommendations.get(predominant_emotion, 'Continúa expresando tus emociones.')}")