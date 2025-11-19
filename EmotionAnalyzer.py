import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

# Descargar recursos de NLTK si no están presentes
try:
    stopwords.words('spanish')
except LookupError:
    print("Descargando recursos de NLTK ('stopwords')...")
    nltk.download('stopwords')


class EmotionAnalyzer:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=stopwords.words('spanish'))
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.stemmer = SnowballStemmer('spanish')
        self.is_fitted = False
        self.cluster_emotions = {}
        
    def preprocess_text(self, text):
        """Limpia y preprocesa el texto"""
        # Convertir a minúsculas
        text = text.lower()
        # Eliminar caracteres especiales y números
        text = re.sub(r'[^a-zA-Záéíóúñ\s]', '', text)
        # Tokenizar y eliminar stopwords
        words = text.split()
        words = [word for word in words if word not in stopwords.words('spanish')]
        # Aplicar stemming
        words = [self.stemmer.stem(word) for word in words]
        return ' '.join(words)
    
    def fit(self, texts):
        """Entrena el modelo con textos no etiquetados"""
        print("Preprocesando textos...")
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        print("Vectorizando con TF-IDF...")
        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        
        print("Aplicando K-means...")
        self.kmeans.fit(tfidf_matrix)
        
        # Asignar emociones a los clusters basado en palabras más representativas
        self._assign_emotions_to_clusters(tfidf_matrix)
        
        self.is_fitted = True
        print("Modelo entrenado exitosamente!")
        
    def _assign_emotions_to_clusters(self, tfidf_matrix):
        """Asigna nombres de emociones a los clusters basado en palabras clave"""
        feature_names = self.vectorizer.get_feature_names_out()
        
        for cluster_id in range(self.n_clusters):
            # Obtener los centroides del cluster
            centroid = self.kmeans.cluster_centers_[cluster_id]
            
            # Obtener las palabras más importantes del cluster
            top_indices = centroid.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            
            # Asignar emoción basado en palabras clave
            emotion = self._classify_emotion_from_words(top_words)
            self.cluster_emotions[cluster_id] = emotion
            
            print(f"Cluster {cluster_id}: {emotion}")
            print(f"Palabras clave: {top_words}\n")
    
    def _classify_emotion_from_words(self, words):
        """Clasifica la emoción basada en palabras clave"""
        emotion_keywords = {
            'positivo': ['feliz', 'alegr', 'genial', 'excelent', 'maravill', 'fantástic', 'content', 'encant'],
            'negativo': ['trist', 'mal', 'horribl', 'terribl', 'desanim'],
            'enojo': ['rabi', 'furios', 'odi', 'asco', 'hart', 'fastidi', 'enoj', 'molest'],
            'miedo': ['mied', 'tem', 'sust', 'asust', 'preocup', 'ansied'],
        }
        
        scores = {emotion: 0 for emotion in emotion_keywords}
        
        for word in words:
            for emotion, keywords in emotion_keywords.items():
                if word in keywords:
                    scores[emotion] += 1
        
        # Filtrar emociones con puntuación > 0
        detected_emotions = {emotion: score for emotion, score in scores.items() if score > 0}
        
        if not detected_emotions:
            return 'neutral'
        
        # Devolver la emoción con la puntuación más alta
        predominant_emotion = max(detected_emotions, key=detected_emotions.get)
        return predominant_emotion
    
    def predict_emotion(self, text):
        """Predice la emoción de un nuevo texto"""
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")
        
        processed_text = self.preprocess_text(text)
        tfidf_vector = self.vectorizer.transform([processed_text])
        cluster = self.kmeans.predict(tfidf_vector)[0]
        
        return self.cluster_emotions.get(cluster, 'neutral')
    
    def get_emotion_probability(self, text):
        """Obtiene la probabilidad de pertenencia a cada cluster"""
        processed_text = self.preprocess_text(text)
        tfidf_vector = self.vectorizer.transform([processed_text])
        distances = pairwise_distances(tfidf_vector, self.kmeans.cluster_centers_)
        probabilities = 1 / (1 + distances.flatten())
        probabilities = probabilities / probabilities.sum()
        
        return {self.cluster_emotions.get(i, f'cluster_{i}'): prob 
                for i, prob in enumerate(probabilities)}