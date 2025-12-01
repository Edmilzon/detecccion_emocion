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
    def __init__(self, n_clusters=None):
        self.logger = get_logger()
        self.data_manager = DataManager()
        
        # Cargar número de clusters desde parámetros si no se especifica
        if n_clusters is None:
            params = self.data_manager.load_json('config/parametros.json')
            n_clusters = params.get('modelo', {}).get('n_clusters', 30)
        
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True)
        self.preprocessor = TextPreprocessor()
        
    def load_training_data(self):
        """Carga datos sin etiquetas para aprendizaje no supervisado"""
        try:
            # Cargar textos sin etiquetar
            base_data = self.data_manager.load_csv('data/training/textos_sin_etiquetar.csv')
            if base_data.empty:
                raise ValueError("No se encontraron datos de entrenamiento")
            
            self.logger.info(f"Cargados {len(base_data)} textos para entrenamiento")
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
        """Asigna nombres automáticos a los clusters (completamente no supervisado)"""
        try:
            cluster_emotions = {}
            features = self.vectorizer.get_feature_names_out()
            
            # Obtener textos originales para análisis
            texts = self.load_training_data()
            cleaned_texts = [self.preprocessor.clean_text(text) for text in texts]
            
            for cluster_id in range(self.n_clusters):
                # Obtener palabras más importantes del centroide
                center = self.kmeans.cluster_centers_[cluster_id]
                top_indices = center.argsort()[-10:][::-1]
                top_words = [features[i] for i in top_indices]
                
                # Obtener textos que pertenecen a este cluster
                cluster_texts = [cleaned_texts[i] for i, c in enumerate(clusters) if c == cluster_id]
                
                # Asignar nombre automático: "emoción_{cluster_id}"
                # Esto es completamente no supervisado - no usa palabras clave
                assigned_emotion = f"emoción_{cluster_id}"
                cluster_emotions[cluster_id] = assigned_emotion
                
                self.logger.info(f"Cluster {cluster_id}: {assigned_emotion}")
                self.logger.info(f"  Palabras características: {', '.join(top_words[:5])}")
                self.logger.info(f"  Textos en cluster: {len(cluster_texts)}")
            
            return cluster_emotions
            
        except Exception as e:
            self.logger.error(f"Error asignando nombres a clusters: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Asignación automática por defecto
            return {i: f"emoción_{i}" for i in range(self.n_clusters)}
    
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