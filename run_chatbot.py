from src.chat.core import EmotionChatbot
from src.utils.logger import setup_logger

if __name__ == "__main__":
    logger = setup_logger()
    
    try:
        logger.info("Iniciando Chatbot de Emociones...")
        chatbot = EmotionChatbot()
        chatbot.run_chat_interface()
        
    except Exception as e:
        logger.error(f"Error ejecutando chatbot: {e}")
        print(f"Error: {e}")
        print("Asegúrate de haber entrenado el modelo primero: python train_model.py")