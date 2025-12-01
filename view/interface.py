import sys
import os
import subprocess
import threading
from pathlib import Path

# Cambiar al directorio raíz del proyecto
project_root = Path(__file__).parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk, scrolledtext
import logging

# Importa la lógica ya existente
from src.chat.core import EmotionChatbot
from src.utils.logger import setup_logger

# Paleta de colores NEON moderna y femenina ✨
COLORS = {
    'bg_main': '#1A0F1E',            # Fondo principal oscuro elegante
    'bg_chat': '#2A1F2E',           # Fondo del chat oscuro con tinte púrpura
    'bg_panel': '#1F1523',          # Fondo del panel oscuro
    'bg_header': '#FF6EC7',         # Header neon rosa vibrante
    'bg_bubble_user': '#FF6EC7',    # Burbuja usuario (neon rosa)
    'bg_bubble_bot': '#9D4EDD',     # Burbuja bot (neon púrpura)
    'text_dark': '#FFFFFF',          # Texto claro (blanco)
    'text_light': '#E0B0FF',        # Texto claro (púrpura claro)
    'accent': '#FF6EC7',             # Color de acento (neon rosa)
    'accent_dark': '#FF4DB8',       # Acento oscuro (rosa más intenso)
    'border': '#9D4EDD',             # Bordes (púrpura neon)
    'success': '#00FF88',            # Verde neon suave
    'warning': '#FFB84D',            # Naranja neon
    'error': '#FF4D6D',              # Rojo neon rosa
    'log_bg': '#1F1523',             # Fondo de logs oscuro
    'neon_pink': '#FF6EC7',          # Rosa neon
    'neon_purple': '#9D4EDD',        # Púrpura neon
    'neon_cyan': '#00D9FF',          # Cyan neon
    'neon_green': '#00FF88',         # Verde neon
    'gradient_start': '#FF6EC7',     # Inicio gradiente
    'gradient_end': '#9D4EDD',       # Fin gradiente
}

class TkinterHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        if self.widget is None:
            return
        self.widget.config(state="normal")
        # Formato similar a la terminal: mostrar nivel y mensaje
        # Similar a: "2025-12-01 00:18:12,327 - EmotionChatbot - INFO - mensaje"
        # Pero simplificado para la interfaz: "INFO - mensaje"
        log_msg = f"{record.levelname} - {record.getMessage()}"
        self.widget.insert("end", f"• {log_msg}\n")
        self.widget.config(state="disabled")
        self.widget.see("end")

class ChatUI:

    def __init__(self, root):
        self.root = root
        self.logger = setup_logger()
        self.chatbot = None
        self.is_training = False

        # Configurar handler para logs en la interfaz
        tk_handler = TkinterHandler(None)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        tk_handler.setFormatter(formatter)

        self.logger.handlers = []
        self.logger.addHandler(tk_handler)

        # Configurar ventana principal
        root.configure(bg=COLORS['bg_main'])
        root.title("✨ Chatbot de Emociones - IA Neon ✨")
        root.geometry("1400x800")
        root.minsize(1200, 700)

        # Configurar grid - Panel de control más ancho
        root.grid_columnconfigure(0, weight=2, minsize=600)  # Chat más ancho
        root.grid_columnconfigure(1, weight=1, minsize=400)  # Panel más ancho
        root.grid_rowconfigure(0, weight=1)

        # ========== ÁREA DE CHAT ==========
        chat_container = tk.Frame(root, bg=COLORS['bg_chat'], relief=tk.FLAT)
        chat_container.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        # Header del chat con efecto neon
        chat_header = tk.Frame(chat_container, bg=COLORS['neon_pink'], height=70)
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)

        title_label = tk.Label(
            chat_header,
            text="💬 Conversación",
            bg=COLORS['neon_pink'],
            fg="white",
            font=("Segoe UI", 18, "bold"),
            pady=18
        )
        title_label.pack()

        # Frame para mensajes con scrollbar
        messages_container = tk.Frame(chat_container, bg=COLORS['bg_chat'])
        messages_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Canvas y scrollbar para mensajes
        self.chat_canvas = tk.Canvas(messages_container, bg=COLORS['bg_chat'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(messages_container, orient="vertical", command=self.chat_canvas.yview)
        self.messages_frame = tk.Frame(self.chat_canvas, bg=COLORS['bg_chat'])

        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        
        def configure_scroll_region(event):
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.chat_canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.messages_frame.bind("<Configure>", configure_scroll_region)
        self.chat_canvas.bind("<Configure>", configure_canvas_width)
        self.chat_canvas.bind_all("<MouseWheel>", lambda e: self.chat_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Área de entrada
        input_frame = tk.Frame(chat_container, bg=COLORS['bg_chat'], height=70)
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        input_frame.pack_propagate(False)

        input_container = tk.Frame(input_frame, bg=COLORS['neon_purple'], relief=tk.FLAT, bd=2)
        input_container.pack(fill="both", expand=True, padx=0, pady=10)

        self.entry = tk.Entry(
            input_container,
            font=("Segoe UI", 11),
            bg=COLORS['bg_chat'],
            fg=COLORS['text_dark'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=COLORS['neon_pink']
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        self.entry.bind("<Return>", lambda e: self.send_message())

        send_btn = tk.Button(
            input_container,
            text="✨ Enviar",
            command=self.send_message,
            bg=COLORS['neon_pink'],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            activebackground=COLORS['accent_dark'],
            activeforeground="white"
        )
        send_btn.pack(side="right", padx=(0, 10), pady=10)

        # ========== PANEL DE CONTROL ==========
        panel_container = tk.Frame(root, bg=COLORS['bg_panel'], relief=tk.FLAT)
        panel_container.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        # Header del panel con efecto neon
        panel_header = tk.Frame(panel_container, bg=COLORS['neon_purple'], height=70)
        panel_header.pack(fill="x")
        panel_header.pack_propagate(False)

        panel_title = tk.Label(
            panel_header,
            text="⚙️ Panel de Control",
            bg=COLORS['neon_purple'],
            fg="white",
            font=("Segoe UI", 16, "bold"),
            pady=18
        )
        panel_title.pack()

        # Botón de entrenar
        button_frame = tk.Frame(panel_container, bg=COLORS['bg_panel'])
        button_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.train_btn = tk.Button(
            button_frame,
            text="🚀 Entrenar Modelo",
            command=self.train_model,
            bg=COLORS['neon_pink'],
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            bd=0,
            pady=15,
            cursor="hand2",
            activebackground=COLORS['accent_dark'],
            activeforeground="white"
        )
        self.train_btn.pack(fill="x")

        # Área de logs con scrollbar
        log_label = tk.Label(
            panel_container,
            text="📊 Actividad del Sistema",
            bg=COLORS['bg_panel'],
            fg=COLORS['neon_cyan'],
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        log_label.pack(fill="x", padx=15, pady=(10, 5))

        log_container = tk.Frame(panel_container, bg=COLORS['neon_purple'], relief=tk.FLAT, bd=2)
        log_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.log_box = scrolledtext.ScrolledText(
            log_container,
            width=35,
            height=30,
            state="disabled",
            bg=COLORS['log_bg'],
            fg=COLORS['text_light'],
            font=("Consolas", 9),
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            padx=12,
            pady=12,
            insertbackground=COLORS['neon_pink']
        )
        self.log_box.pack(fill="both", expand=True)

        tk_handler.widget = self.log_box

        # Inicializar chatbot después de crear log_box
        self._initialize_chatbot()

    def log(self, msg, level="INFO"):
        """Agrega un mensaje al log con formato similar a la terminal"""
        # Verificar que log_box existe antes de usarlo
        if not hasattr(self, 'log_box') or self.log_box is None:
            return
        
        # Colores neon según el nivel
        color_map = {
            "INFO": COLORS['neon_cyan'],
            "WARNING": COLORS['warning'],
            "ERROR": COLORS['error'],
            "SUCCESS": COLORS['success']
        }
        color = color_map.get(level, COLORS['neon_cyan'])
        
        self.log_box.config(state="normal")
        
        # Insertar con formato de color neon
        self.log_box.insert("end", "✨ ", "bullet")
        self.log_box.insert("end", f"{level} - ", level)
        self.log_box.insert("end", f"{msg}\n", "message")
        
        # Configurar tags de color neon
        self.log_box.tag_config("bullet", foreground=COLORS['neon_pink'], font=("Consolas", 9, "bold"))
        self.log_box.tag_config(level, foreground=color, font=("Consolas", 9, "bold"))
        self.log_box.tag_config("message", foreground=COLORS['text_light'], font=("Consolas", 9))
        
        self.log_box.config(state="disabled")
        self.log_box.see("end")
    
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

    def add_message(self, text, sender="user"):
        # Colores neon según el remitente
        if sender == "user":
            bubble_color = COLORS['neon_pink']
            text_color = "white"
            anchor_pos = "e"
        else:
            bubble_color = COLORS['neon_purple']
            text_color = "white"
            anchor_pos = "w"

        # Frame contenedor del mensaje
        msg_container = tk.Frame(self.messages_frame, bg=COLORS['bg_chat'])
        msg_container.pack(anchor=anchor_pos, pady=8, padx=10, fill="x")

        # Burbuja del mensaje con estilo neon
        bubble_frame = tk.Frame(
            msg_container,
            bg=bubble_color,
            relief=tk.FLAT,
            bd=2,
            highlightbackground=bubble_color,
            highlightthickness=1
        )
        bubble_frame.pack(anchor=anchor_pos, padx=(20, 0) if sender == "user" else (0, 20))

        msg_label = tk.Label(
            bubble_frame,
            text=text,
            bg=bubble_color,
            fg=text_color,
            wraplength=450,
            justify="left",
            font=("Segoe UI", 10),
            padx=18,
            pady=12,
            relief=tk.FLAT,
            bd=0
        )
        msg_label.pack(anchor=anchor_pos)

        # Auto-scroll al final
        self.messages_frame.update_idletasks()
        if hasattr(self, 'chat_canvas'):
            self.chat_canvas.update_idletasks()
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
            self.chat_canvas.yview_moveto(1.0)

    # CHAT

    def send_message(self):
        text = self.entry.get().strip()
        if not text:
            return

        # Validar que el chatbot esté inicializado
        if self.chatbot is None:
            self.log("Chatbot aún no está listo. Por favor espera...", "WARNING")
            return

        self.add_message("Tú: " + text, sender="user")
        self.entry.delete(0, "end")

        try:
            output = self.chatbot.process_message(text)
            response = output.get("response", "Sin respuesta")
            emotion = output.get("emotion", "neutral")
            cluster = output.get("cluster", -1)
            confidence = output.get("confidence", 0.0)
            top_words = output.get("top_words", [])
            
            # Mostrar solo la respuesta del bot en el chat
            self.add_message(f"Bot [{emotion.upper()}]: {response}", sender="bot")
            
            # Mostrar detalles técnicos en el panel de control (log_box)
            self.log(f"Emoción detectada: {emotion} (Cluster: {cluster})", "INFO")
            self.log(f"Confianza: {confidence:.2f}", "INFO")
            if top_words:
                words_str = ", ".join(top_words[:3])
                self.log(f"Palabras clave: {words_str}", "INFO")

        except Exception as e:
            self.log(f"Error procesando mensaje: {e}", "ERROR")
            self.add_message("Bot: Lo siento, hubo un error procesando tu mensaje.", sender="bot")

    # ENTRENAMIENTO

    def train_model(self):
        """Ejecuta train_model.py como subproceso"""
        if self.is_training:
            self.log("El entrenamiento ya está en curso. Por favor espera...", "WARNING")
            return
        
        self.is_training = True
        self.train_btn.config(state="disabled", text="⏳ Entrenando...")
        self.log("═══════════════════════════════════════", "INFO")
        self.log("INICIANDO ENTRENAMIENTO NO SUPERVISADO", "INFO")
        self.log("═══════════════════════════════════════", "INFO")
        
        def run_training():
            try:
                # Ejecutar train_model.py usando subprocess
                process = subprocess.Popen(
                    [sys.executable, "train_model.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=project_root
                )
                
                # Leer salida línea por línea
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        # Filtrar y mostrar solo los mensajes de log relevantes
                        if "INFO" in line or "ERROR" in line or "WARNING" in line:
                            # Extraer el mensaje después del nivel de log
                            if " - " in line:
                                parts = line.split(" - ", 2)
                                if len(parts) >= 3:
                                    level = parts[1]
                                    message = parts[2]
                                    # Usar función auxiliar para capturar correctamente las variables
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
                            # Mostrar líneas importantes
                            def log_important(m=line):
                                self.log(m, "INFO")
                            self.root.after(0, log_important)
                
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self.log("═══════════════════════════════════════", "INFO"))
                    self.root.after(0, lambda: self.log("ENTRENAMIENTO COMPLETADO EXITOSAMENTE", "SUCCESS"))
                    self.root.after(0, lambda: self.log("═══════════════════════════════════════", "INFO"))
                    # Reinicializar chatbot para cargar el nuevo modelo
                    self.root.after(0, self._reload_chatbot)
                    self.root.after(0, lambda: self.train_btn.config(state="normal", text="Entrenar Modelo"))
                else:
                    self.root.after(0, lambda: self.log(f"Error en entrenamiento (código: {process.returncode})", "ERROR"))
                    self.root.after(0, lambda: self.train_btn.config(state="normal", text="Entrenar Modelo"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error ejecutando entrenamiento: {e}", "ERROR"))
                self.root.after(0, lambda: self.train_btn.config(state="normal", text="Entrenar Modelo"))
            finally:
                self.is_training = False
        
        # Ejecutar en hilo separado para no bloquear la UI
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

if __name__ == "__main__":
    root = tk.Tk()
    ChatUI(root)
    root.mainloop()
