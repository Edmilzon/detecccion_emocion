import tkinter as tk
from tkinter import scrolledtext
from ..theme import COLORS

class ControlPanel(tk.Frame):
    def __init__(self, parent, train_command):
        super().__init__(parent, bg=COLORS['bg_panel'], relief=tk.FLAT)
        self.train_command = train_command

        self._setup_widgets()
    
    def _setup_widgets(self):
        # Header del panel con efecto neon
        panel_header = tk.Frame(self, bg=COLORS['neon_purple'], height=70)
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
        button_frame = tk.Frame(self, bg=COLORS['bg_panel'])
        button_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.train_btn = tk.Button(
            button_frame,
            text="🚀 Entrenar Modelo",
            command=self.train_command,
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
            self,
            text="📊 Actividad del Sistema",
            bg=COLORS['bg_panel'],
            fg=COLORS['neon_cyan'],
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        log_label.pack(fill="x", padx=15, pady=(10, 5))

        log_container = tk.Frame(self, bg=COLORS['neon_purple'], relief=tk.FLAT, bd=2)
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

    def log(self, msg, level="INFO"):
        """Agrega un mensaje al log con formato similar a la terminal"""
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
