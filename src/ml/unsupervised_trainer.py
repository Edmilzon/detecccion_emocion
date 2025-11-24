import pandas as pd
import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from .preprocessor import TextPreprocessor
from src.data.data_manager import DataManager
from src.utils.logger import get_logger

class UnsupervisedTrainer:
    def __init__(self, n_clusters=3):
        self.logger = get_logger()
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2), min_df=2, max_df=0.9)
        self.preprocessor = TextPreprocessor()
        self.data_manager = DataManager()
        
    def load_training_data(self):
        """Carga datos sin etiquetas para aprendizaje no supervisado"""
        try:
            # Cargar textos sin etiquetar
            base_data = self.data_manager.load_csv('data/training/textos_sin_etiquetar.csv')
            if base_data.empty:
                raise ValueError("No se encontraron datos de entrenamiento")
            
            self.logger.info(f"Cargados {len(base_data)} textos para entrenamiento no supervisado")
            return base_data['texto'].tolist()
            
        except Exception as e:
            self.logger.error(f"Error cargando datos: {e}")
            # Datos de ejemplo si no hay archivo
            return [
                "Estoy muy feliz y contento hoy",
                "Me siento terrible y mal",
                "Es un día normal y regular",
                "Qué enojo tengo ahora mismo",
                "Increíble maravilloso día",
                "Horrible situación deprimente",
                "Todo bien sin problemas",
                "Furioso indignado molesto"
            ]
    
    def train(self):
        """Entrena el modelo K-means no supervisado"""
        self.logger.info("Iniciando entrenamiento NO SUPERVISADO con K-means")
        
        # Cargar datos
        texts = self.load_training_data()
        
        # Preprocesar
        self.logger.info("Preprocesando textos...")
        cleaned_texts = [self.preprocessor.clean_text(text) for text in texts]
        
        # Vectorizar con TF-IDF
        self.logger.info("Vectorizando con TF-IDF...")
        X = self.vectorizer.fit_transform(cleaned_texts)
        
        # Entrenar K-means
        self.logger.info(f"Entrenando K-means con {self.n_clusters} clusters...")
        self.kmeans.fit(X)
        clusters = self.kmeans.predict(X)
        
        # Interpretar clusters
        self.logger.info("Interpretando clusters...")
        cluster_emotions = self.interpret_clusters(X, clusters)
        
        # Evaluar modelo
        evaluation = self.evaluate_model(X, clusters)
        
        # Guardar modelo
        self.save_model(cluster_emotions, evaluation)
        
        return evaluation
    
    def interpret_clusters(self, X, clusters):
        """Interpreta automáticamente qué emoción representa cada cluster"""
        try:
            # Cargar y procesar palabras de referencia para que coincidan con el preprocesamiento del texto
            raw_reference_words = self.data_manager.load_json('config/palabras_clave.json')
            cleaned_reference_words = {}
            for emotion, words_list in raw_reference_words.items():
                processed_words = [self.preprocessor.clean_text(word) for word in words_list]
                # Usar un set para búsquedas eficientes y eliminar duplicados o vacíos
                cleaned_reference_words[emotion] = {word for word in processed_words if word}

            cluster_emotions = {}
            features = self.vectorizer.get_feature_names_out()
            
            for cluster_id in range(self.n_clusters):
                # Obtener palabras más importantes del cluster
                center = self.kmeans.cluster_centers_[cluster_id]
                top_indices = center.argsort()[-10:][::-1]
                top_words = [features[i] for i in top_indices]
                
                # Asignar emoción basada en palabras de referencia limpias
                emotion_scores = {}
                for emotion, words_set in cleaned_reference_words.items():
                    score = sum(1 for top_word in top_words if top_word in words_set)
                    emotion_scores[emotion] = score
                
                # Asignar la emoción con mayor score, con fallback a neutral
                max_score = max(emotion_scores.values())
                if max_score > 0:
                    assigned_emotion = max(emotion_scores, key=emotion_scores.get)
                else:
                    assigned_emotion = 'neutral'
                cluster_emotions[cluster_id] = assigned_emotion
                
                self.logger.info(f"Cluster {cluster_id}: {assigned_emotion} - Palabras: {top_words[:5]}")
            
            return cluster_emotions
            
        except Exception as e:
            self.logger.error(f"Error interpretando clusters: {e}")
            # Asignación por defecto
            return {0: "positivo", 1: "negativo", 2: "neutral"}
    
    def evaluate_model(self, X, clusters):
        """Evalúa la calidad del clustering"""
        try:
            silhouette_avg = silhouette_score(X, clusters)
            inertia = self.kmeans.inertia_
            
            evaluation = {
                'silhouette_score': round(silhouette_avg, 4),
                'inertia': round(inertia, 2),
                'n_clusters': self.n_clusters,
                'n_samples': X.shape[0],
                'n_features': X.shape[1]
            }
            
            self.logger.info(f"Evaluación - Silhouette: {silhouette_avg:.4f}, Inercia: {inertia:.2f}")
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error en evaluación: {e}")
            return {'silhouette_score': 0.0, 'inertia': 0.0}
    
    def save_model(self, cluster_emotions, evaluation):
        """Guarda el modelo entrenado y metadatos"""
        try:
            model_data = {
                'kmeans': self.kmeans,
                'vectorizer': self.vectorizer,
                'preprocessor': self.preprocessor,
                'cluster_emotions': cluster_emotions,
                'evaluation': evaluation
            }
            
            # Guardar modelo
            joblib.dump(model_data, 'models/current/modelo_entrenado.pkl')
            
            # Guardar metadatos
            metadata = {
                'model_type': 'KMeans_Unsupervised',
                'n_clusters': self.n_clusters,
                'cluster_emotions': cluster_emotions,
                'evaluation': evaluation,
                'features_used': self.vectorizer.get_feature_names_out().tolist()[:20],
                'version': '1.0'
            }
            
            self.data_manager.save_json(metadata, 'models/current/info_modelo.json')
            self.data_manager.save_json(evaluation, 'data/history/metricas_entrenamiento.json')
            
            self.logger.info("Modelo K-means guardado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error guardando modelo: {e}")
            raise