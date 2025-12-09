# view/components/chat_area.py
import tkinter as tk
from tkinter import ttk
from ..theme import COLORS

class ChatArea(tk.Frame):
    def __init__(self, parent, send_command, record_command):
        super().__init__(parent, bg=COLORS['bg_chat'], relief=tk.FLAT)
        self.send_command = send_command
        self.record_command = record_command
        
        self._setup_widgets()

    def _setup_widgets(self):
        # Header del chat con efecto neon
        chat_header = tk.Frame(self, bg=COLORS['neon_pink'], height=70)
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
        messages_container = tk.Frame(self, bg=COLORS['bg_chat'])
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
        input_frame = tk.Frame(self, bg=COLORS['bg_chat'], height=70)
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
        self.entry.bind("<Return>", lambda e: self.send_command())

        send_btn = tk.Button(
            input_container,
            text="✨ Enviar",
            command=self.send_command,
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

        self.record_btn = tk.Button(
            input_container,
            text="🎤",
            command=self.record_command,
            bg=COLORS['neon_cyan'],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground=COLORS['accent_dark'],
            activeforeground="white"
        )
        self.record_btn.pack(side="right", padx=(0, 5), pady=10)

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
    
    def get_text(self):
        return self.entry.get().strip()

    def clear_input(self):
        self.entry.delete(0, "end")