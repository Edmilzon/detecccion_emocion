import joblib
import os
import numpy as np
from src.ml.preprocessor import TextPreprocessor
from src.utils.logger import get_logger

class EmotionPredictor:
    def __init__(self):
        self.logger = get_logger()
        self.preprocessor = TextPreprocessor()
        self.model = None
        self.vectorizer = None
        self.pca = None
        self.cluster_emotions = {}
        
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo entrenado y el mapeo de clusters"""
        try:
            model_path = 'models/current/modelo_entrenado.pkl'
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['kmeans']
                self.vectorizer = model_data['vectorizer']
                self.pca = model_data.get('pca')
                self.cluster_emotions = model_data['cluster_emotions']
                self.logger.info("Modelo K-means cargado exitosamente")
            else:
                raise FileNotFoundError("Modelo no encontrado. Ejecuta train_model.py primero")
                
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
            raise
    
    def predict(self, text):
        """Predice la emoción usando K-means (no supervisado)"""
        try:
            # Preprocesar texto
            cleaned_text = self.preprocessor.clean_text(text)
            
            # Vectorizar
            text_vector_tfidf = self.vectorizer.transform([cleaned_text])
            
            # Aplicar PCA si existe
            if self.pca:
                text_vector_transformed = self.pca.transform(text_vector_tfidf.toarray())
            else:
                text_vector_transformed = text_vector_tfidf

            # Predecir cluster
            cluster_id = self.model.predict(text_vector_transformed)[0]
            
            # Obtener emoción del cluster
            emotion = self.cluster_emotions.get(cluster_id, "neutral")
            
            # Calcular confianza
            confidence = self._calculate_confidence(text_vector_transformed, cluster_id)
            
            # Obtener palabras características
            top_words = self._get_cluster_words(cluster_id)
            
            cluster_info = {
                'cluster_id': int(cluster_id),
                'top_words': top_words,
                'distance_to_center': confidence
            }
            
            return emotion, confidence, cluster_info
            
        except Exception as e:
            self.logger.error(f"Error en predicción: {e}")
            return "neutral", 0.5, {'cluster_id': -1, 'top_words': []}
    
    def _calculate_confidence(self, text_vector, cluster_id):
        """Calcula confianza basada en distancia al centroide"""
        try:
            distance = self.model.transform(text_vector)[0][cluster_id]
            confidence = 1.0 / (1.0 + (distance**2))
            return min(confidence * 1.2, 1.0)
        except:
            return 0.5
    
    def _get_cluster_words(self, cluster_id, top_n=5):
        """Obtiene las palabras más representativas del cluster"""
        try:
            if hasattr(self.vectorizer, 'get_feature_names_out'):
                features = self.vectorizer.get_feature_names_out()
                
                if self.pca:
                    center_pca = self.model.cluster_centers_[cluster_id].reshape(1, -1)
                    original_center = self.pca.inverse_transform(center_pca)
                    top_indices = original_center[0].argsort()[-top_n:][::-1]
                else:
                    center = self.model.cluster_centers_[cluster_id]
                    top_indices = center.argsort()[-top_n:][::-1]

                return [features[i] for i in top_indices]
        except Exception as e:
            self.logger.error(f"Error obteniendo palabras: {e}")
        return []