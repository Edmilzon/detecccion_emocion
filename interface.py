from EmotionalChatbot import EmotionalChatbot


def run_chatbot():
    """Función principal para ejecutar el chatbot"""
    chatbot = EmotionalChatbot()
    
    print("Iniciando Sistema de Análisis Emocional")
    print("="*55)
    
    # Entrenamiento inicial
    print("Fase de Exploración: Entrenando el modelo...")
    chatbot.train_with_sample_data()
    print("Modelo entrenado y listo para la Fase de Explotación\n")
    
    # Iniciar chat
    chatbot.chat()
    
    # Generar reporte final
    chatbot.generate_conversation_report()

# Ejecutar el chatbot
if __name__ == "__main__":
    run_chatbot()