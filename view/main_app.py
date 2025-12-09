# view/main_app.py
import sys
import os
import subprocess
import threading
import logging
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr

# Cambiar al directorio raíz del proyecto
project_root = Path(__file__).parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importa la lógica ya existente
from src.chat.core import EmotionChatbot
from src.utils.logger import setup_logger

from .theme import COLORS
from .components.tkinter_handler import TkinterHandler
from .components.chat_area import ChatArea
from .components.control_panel import ControlPanel

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.logger = setup_logger()
        self.chatbot = None
        self.is_training = False
        
        self.project_root = Path(__file__).parent.parent

        # Configurar ventana principal
        root.configure(bg=COLORS['bg_main'])
        root.title("✨ Chatbot de Emociones - IA Neon ✨")
        root.geometry("1400x800")
        root.minsize(1200, 700)

        # Configurar grid
        root.grid_columnconfigure(0, weight=2, minsize=600)
        root.grid_columnconfigure(1, weight=1, minsize=400)
        root.grid_rowconfigure(0, weight=1)

        # Crear y posicionar los componentes de la UI
        self.chat_area = ChatArea(root, self.send_message, self.record_message)
        self.chat_area.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        self.control_panel = ControlPanel(root, self.train_model)
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Configurar handler para logs en la interfaz
        tk_handler = TkinterHandler(self.control_panel.log_box)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        tk_handler.setFormatter(formatter)

        self.logger.handlers = []
        self.logger.addHandler(tk_handler)

        # Inicializar chatbot después de crear log_box
        self._initialize_chatbot()

    def log(self, msg, level="INFO"):
        self.control_panel.log(msg, level)
    
    def _initialize_chatbot(self):
        """Inicializa el chatbot en un hilo separado para no bloquear la UI"""
        def init():
            try:
                self.log("Iniciando Chatbot de Emociones...", "INFO")
                self.chatbot = EmotionChatbot()
                self.chatbot.logger = self.logger
                self.log("Chatbot de Emociones inicializado (K-means No Supervisado)", "INFO")
            except Exception as e:
                self.log(f"Error inicializando chatbot: {e}", "ERROR")
        
        thread = threading.Thread(target=init, daemon=True)
        thread.start()

    # CHAT
    def send_message(self, text=None):
        if text is None:
            text = self.chat_area.get_text()
        
        if not text:
            return

        if self.chatbot is None:
            self.log("Chatbot aún no está listo. Por favor espera...", "WARNING")
            return

        self.chat_area.add_message("Tú: " + text, sender="user")
        self.chat_area.clear_input()

        try:
            output = self.chatbot.process_message(text)
            response = output.get("response", "Sin respuesta")
            emotion = output.get("emotion", "neutral")
            cluster = output.get("cluster", -1)
            confidence = output.get("confidence", 0.0)
            top_words = output.get("top_words", [])
            
            self.chat_area.add_message(f"Bot [{emotion.upper()}]: {response}", sender="bot")
            
            self.log(f"Emoción detectada: {emotion} (Cluster: {cluster})", "INFO")
            self.log(f"Confianza: {confidence:.2f}", "INFO")
            if top_words:
                words_str = ", ".join(top_words[:3])
                self.log(f"Palabras clave: {words_str}", "INFO")

        except Exception as e:
            self.log(f"Error procesando mensaje: {e}", "ERROR")
            self.chat_area.add_message("Bot: Lo siento, hubo un error procesando tu mensaje.", sender="bot")

    def record_message(self):
        """Inicia la grabación de audio en un hilo separado"""
        thread = threading.Thread(target=self._record_thread, daemon=True)
        thread.start()

    def _record_thread(self):
        """Graba audio del micrófono, lo transcribe y lo envía al chat"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.root.after(0, lambda: self.log("🎤 Di algo...", "INFO"))
            self.root.after(0, lambda: self.control_panel.record_btn.config(state="disabled", text="🎤 Escuchando..."))
            
            try:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                
                self.root.after(0, lambda: self.log("🔄 Procesando audio...", "INFO"))
                
                text = r.recognize_google(audio, language='es-ES')
                self.root.after(0, lambda: self.log(f"Texto reconocido: '{text}'", "SUCCESS"))
                
                # Enviar al hilo principal para actualizar la UI
                self.root.after(0, lambda: self.send_message(text))
                
            except sr.WaitTimeoutError:
                self.root.after(0, lambda: self.log("No se detectó audio. Inténtalo de nuevo.", "WARNING"))
                self.root.after(0, lambda: messagebox.showwarning("Sin audio", "No se detectó audio. Asegúrate de hablar claro."))
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.log("No se pudo entender el audio.", "ERROR"))
                self.root.after(0, lambda: messagebox.showerror("Error de Reconocimiento", "No se pudo entender lo que dijiste. Intenta de nuevo."))
            except sr.RequestError as e:
                self.root.after(0, lambda: self.log(f"Error con el servicio de Google: {e}", "ERROR"))
                self.root.after(0, lambda: messagebox.showerror("Error de API", f"No se pudo conectar con el servicio de reconocimiento de voz: {e}"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error inesperado al grabar: {e}", "ERROR"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}"))
            finally:
                # Restaurar botón en el hilo principal
                self.root.after(0, lambda: self.control_panel.record_btn.config(state="normal", text="🎤 Grabar Voz"))


    # ENTRENAMIENTO
    def train_model(self):
        """Ejecuta train_model.py como subproceso"""
        if self.is_training:
            self.log("El entrenamiento ya está en curso. Por favor espera...", "WARNING")
            return
        
        self.is_training = True
        self.control_panel.train_btn.config(state="disabled", text="⏳ Entrenando...")
        self.log("═══════════════════════════════════════", "INFO")
        self.log("INICIANDO ENTRENAMIENTO NO SUPERVISADO", "INFO")
        self.log("═══════════════════════════════════════", "INFO")
        
        def run_training():
            try:
                process = subprocess.Popen(
                    [sys.executable, "train_model.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=self.project_root
                )
                
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        if "INFO" in line or "ERROR" in line or "WARNING" in line:
                            if " - " in line:
                                parts = line.split(" - ", 2)
                                if len(parts) >= 3:
                                    level = parts[1]
                                    message = parts[2]
                                    def log_message(m=message, l=level):
                                        self.log(m, l)
                                    self.root.after(0, log_message)
                                else:
                                    def log_line(m=line):
                                        self.log(m, "INFO")
                                    self.root.after(0, log_line)
                            else:
                                def log_line2(m=line):
                                    self.log(m, "INFO")
                                self.root.after(0, log_line2)
                        elif "MODELO ENTRENADO" in line or "=" in line:
                            def log_important(m=line):
                                self.log(m, "INFO")
                            self.root.after(0, log_important)
                
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self.log("═══════════════════════════════════════", "INFO"))
                    self.root.after(0, lambda: self.log("ENTRENAMIENTO COMPLETADO EXITOSAMENTE", "SUCCESS"))
                    self.root.after(0, lambda: self.log("═══════════════════════════════════════", "INFO"))
                    self.root.after(0, self._reload_chatbot)
                    self.root.after(0, lambda: self.control_panel.train_btn.config(state="normal", text="Entrenar Modelo"))
                else:
                    self.root.after(0, lambda: self.log(f"Error en entrenamiento (código: {process.returncode})", "ERROR"))
                    self.root.after(0, lambda: self.control_panel.train_btn.config(state="normal", text="Entrenar Modelo"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error ejecutando entrenamiento: {e}", "ERROR"))
                self.root.after(0, lambda: self.control_panel.train_btn.config(state="normal", text="Entrenar Modelo"))
            finally:
                self.is_training = False
        
        thread = threading.Thread(target=run_training, daemon=True)
        thread.start()
    
    def _reload_chatbot(self):
        """Recarga el chatbot después del entrenamiento"""
        try:
            self.log("Recargando chatbot con nuevo modelo...", "INFO")
            self.chatbot = EmotionChatbot()
            self.chatbot.logger = self.logger
            self.log("Chatbot recargado exitosamente", "INFO")
        except Exception as e:
            self.log(f"Error recargando chatbot: {e}", "ERROR")

def main():
    root = tk.Tk()
    ChatUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
