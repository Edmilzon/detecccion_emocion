import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk
import logging

# Importa la lógica ya existente
from src.chat.core import EmotionChatbot
from src.ml.unsupervised_trainer import UnsupervisedTrainer
from src.utils.logger import setup_logger


# =========================================================
# Handler para mostrar logs del chatbot dentro del panel UI
# =========================================================
class TkinterHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.config(state="normal")
        self.widget.insert("end", msg + "\n")
        self.widget.config(state="disabled")
        self.widget.see("end")


# =========================================================
# INTERFAZ CHAT
# =========================================================
class ChatUI:

    def __init__(self, root):

        # ------------------------ LOGGER ------------------------
        self.logger = setup_logger()

        # Chatbot
        self.chatbot = EmotionChatbot()

        # CONECTAR EL LOGGER DEL CHATBOT A LA INTERFAZ
        tk_handler = TkinterHandler(None)  # widget se asignará luego
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        tk_handler.setFormatter(formatter)

        # Reset handlers
        self.logger.handlers = []
        self.logger.addHandler(tk_handler)
        self.chatbot.logger = self.logger

        # ----------------- DISEÑO (UI) -----------------

        root.configure(bg="#FBE9E7")

        # Usamos grid para manejar el layout y permitir redimensionar el panel de control
        root.grid_columnconfigure(0, weight=1)  # columna de mensajes a la izquierda (expandible)
        root.grid_columnconfigure(1, weight=0, minsize=240)  # columna de panel de control a la derecha (redimensionable)

        # ---- Panel derecho: CHAT (ahora en columna 0, a la izquierda) ----
        right = tk.Frame(root, bg="#FFF3E0")
        right.grid(row=0, column=0, sticky="nsew")

        self.messages_frame = tk.Frame(right, bg="#FFF3E0")
        self.messages_frame.pack(fill="both", expand=True)

        bottom = tk.Frame(right, bg="#FFE0B2")
        bottom.pack(fill="x")

        self.entry = ttk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        send_btn = ttk.Button(bottom, text="Enviar", command=self.send_message)
        send_btn.pack(side="right", padx=5, pady=5)

        # ---- Panel izquierdo: LOG (ahora en columna 1, a la derecha) ----
        left = tk.Frame(root, bg="#FFCCBC")
        left.grid(row=0, column=1, sticky="ns")

        tk.Label(
            left, text="Panel de control",
            bg="#FFAB91", fg="black",
            font=("Arial", 12, "bold")
        ).pack(fill="x")

        self.log_box = tk.Text(left, width=25, height=25,
                               state="disabled", bg="#FFECE6")
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Ahora asignamos el widget al handler
        tk_handler.widget = self.log_box

        train_btn = ttk.Button(left, text="Entrenar modelo", command=self.train_model)
        train_btn.pack(pady=10)

        self.log("Chatbot listo.")

    # =========================================================
    # FUNCIONES DE LA INTERFAZ
    # =========================================================

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.config(state="disabled")
        self.log_box.see("end")

    def add_message(self, text, sender="user"):
        bubble_color = "#FFD180" if sender == "user" else "#FFF59D"
        text_color = "#4E342E"

        frame = tk.Frame(self.messages_frame, bg="#FFF3E0")
        frame.pack(anchor="e" if sender == "user" else "w", pady=3, padx=5, fill="x")

        msg = tk.Label(
            frame, text=text,
            bg=bubble_color, fg=text_color,
            wraplength=480, justify="left",
            font=("Arial", 11), padx=10, pady=5,
        )
        msg.pack(anchor="e" if sender == "user" else "w")

    # =========================================================
    # CHAT
    # =========================================================

    def send_message(self):
        text = self.entry.get().strip()
        if not text:
            return

        self.add_message("Tú: " + text, sender="user")
        self.entry.delete(0, "end")

        try:
            output = self.chatbot.process_message(text)
            response = output.get("response", "Sin respuesta")
            self.add_message("Bot: " + response, sender="bot")

        except Exception as e:
            self.log(f"Error procesando mensaje: {e}")

    # =========================================================
    # ENTRENAMIENTO
    # =========================================================

    def train_model(self):
        self.log("Iniciando entrenamiento...")

        try:
            trainer = UnsupervisedTrainer(n_clusters=3)
            evaluation = trainer.train()

            self.log("Entrenamiento completado")
            self.log(f"Silhouette score: {evaluation['silhouette_score']}")
            self.log(f"Inercia: {evaluation['inertia']}")
            self.log(f"Muestras: {evaluation['n_samples']}")
            self.log(f"Clusters: {evaluation['n_clusters']}")

        except Exception as e:
            self.log(f"Error en el entrenamiento: {e}")


# =========================================================
# EJECUCIÓN
# =========================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chatsito Emocional")
    root.geometry("900x500")
    ChatUI(root)
    root.mainloop()