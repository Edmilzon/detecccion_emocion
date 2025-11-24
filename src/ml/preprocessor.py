import re
import nltk
from nltk.corpus import stopwords
from src.utils.logger import get_logger

class TextPreprocessor:
    def __init__(self):
        self.logger = get_logger()
        self.stop_words = self._setup_stopwords()
    
    def _setup_stopwords(self):
        """Configura las stopwords en español"""
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        return set(stopwords.words('spanish'))
    
    def clean_text(self, text):
        """Limpia y preprocesa el texto para análisis"""
        if not isinstance(text, str):
            return ""
        
        try:
            # Convertir a minúsculas
            text = text.lower()
            
            # Eliminar caracteres especiales pero mantener letras y acentos
            text = re.sub(r'[^a-zA-Záéíóúñü\s]', ' ', text)
            
            # Eliminar espacios extras
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Eliminar stopwords
            words = text.split()
            words = [word for word in words if word not in self.stop_words and len(word) > 2]
            
            return ' '.join(words)
            
        except Exception as e:
            self.logger.error(f"Error limpiando texto: {e}")
            return text.lower() if isinstance(text, str) else ""