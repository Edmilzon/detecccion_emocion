from src.chat.core import EmotionChatbot
from src.utils.logger import setup_logger

def main(): 
    looger = setup_logger()
    looger.info("iniciando chatbot de emociones")

    try: 
        chatbot = EmotionChatbot()
        chatbot.run_chat_interface()

    except Exception as e:
        looger.error(f"Error al iniciar chatboot: {e}")
        print("Error al iniciar el chatbot: ", e)

if __name__ == "__main__":
    main()