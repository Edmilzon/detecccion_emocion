import logging

class TkinterHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        if self.widget is None:
            return
        self.widget.config(state="normal")
        log_msg = f"{record.levelname} - {record.getMessage()}"
        self.widget.insert("end", f"• {log_msg}\n")
        self.widget.config(state="disabled")
        self.widget.see("end")
