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
        self.emotion_names_cache = {}  # Cache para nombres de emociones
        
        self._load_model()
        # Construir nombres de emociones después de cargar el modelo
        if self.model is not None:
            self._build_emotion_names()
    
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
            
            # Vectorizar con TF-IDF
            text_vector_tfidf = self.vectorizer.transform([cleaned_text])
            
            # K-means trabaja directamente con la matriz TF-IDF (sparse matrix)
            # No necesitamos PCA para K-means, pero si existe lo aplicamos
            if self.pca:
                text_vector_for_prediction = self.pca.transform(text_vector_tfidf.toarray())
            else:
                # K-means puede trabajar con sparse matrices directamente
                text_vector_for_prediction = text_vector_tfidf

            # Predecir cluster
            # Convertir a array denso para predicción si es sparse
            if hasattr(text_vector_for_prediction, 'toarray'):
                text_vector_dense = text_vector_for_prediction.toarray()
            else:
                text_vector_dense = text_vector_for_prediction
            
            cluster_id = self.model.predict(text_vector_dense)[0]
            
            # Analizar el texto del usuario directamente para determinar la emoción
            # Esto es más preciso que solo usar el cluster
            emotion_name = self._detect_emotion_from_text(text, cleaned_text)
            
            # Si no se detectó una emoción clara, usar el nombre del cluster como fallback
            if not emotion_name or emotion_name.startswith("emoción_"):
                emotion = self.cluster_emotions.get(cluster_id, f"emoción_{cluster_id}")
                emotion_name = self._get_emotion_name(cluster_id, emotion)
            
            # Calcular confianza (usar el vector denso)
            confidence = self._calculate_confidence(text_vector_dense, cluster_id)
            
            # Obtener palabras características del texto del usuario (no solo del cluster)
            top_words = self._get_user_text_words(text, text_vector_tfidf)
            
            cluster_info = {
                'cluster_id': int(cluster_id),
                'top_words': top_words,
                'distance_to_center': confidence,
                'emotion_name': emotion_name
            }
            
            return emotion_name, confidence, cluster_info
            
        except Exception as e:
            self.logger.error(f"Error en predicción: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return "neutral", 0.5, {'cluster_id': -1, 'top_words': []}
    
    def _calculate_confidence(self, text_vector, cluster_id):
        """Calcula confianza basada en distancia al centroide"""
        try:
            # Asegurar que sea un array numpy
            if not isinstance(text_vector, np.ndarray):
                text_vector = np.array(text_vector)
            
            # Calcular distancias a todos los centroides
            distances = self.model.transform(text_vector)[0]
            distance_to_cluster = distances[cluster_id]
            
            # La confianza es inversamente proporcional a la distancia
            # Normalizar basado en la distancia mínima y máxima
            min_dist = distances.min()
            max_dist = distances.max()
            
            if max_dist > min_dist:
                # Normalizar distancia (0 = muy cerca, 1 = muy lejos)
                normalized_dist = (distance_to_cluster - min_dist) / (max_dist - min_dist)
                confidence = 1.0 - normalized_dist
            else:
                confidence = 0.5
            
            # Asegurar que esté en el rango [0, 1]
            return max(0.0, min(1.0, confidence))
        except Exception as e:
            self.logger.error(f"Error calculando confianza: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return 0.5
    
    def _build_emotion_names(self):
        """Construye un mapeo de nombres de emociones basado en palabras características"""
        try:
            # Diccionario de palabras clave a emociones
            emotion_keywords = {
                'alegría': ['alegría', 'feliz', 'contento', 'genial', 'maravilloso', 'increíble', 'alegre', 'fantástico', 'perfecto', 'excelente', 'bueno', 'entusiasmado', 'satisfecho', 'animado', 'optimista', 'inspirado', 'agradecido', 'paz', 'tranquilidad', 'éxito', 'logro', 'afortunado', 'divertido', 'encantado', 'espectacular', 'orgulloso', 'amor', 'energía', 'bien'],
                'tristeza': ['triste', 'tristeza', 'desanimado', 'mal', 'terrible', 'horrible', 'deprimido', 'fatal', 'desesperanzado', 'frustración', 'decepcionado', 'pena', 'exhausto', 'vacío', 'sin motivación', 'dolor', 'miedo', 'culpa', 'nostálgico', 'ansioso', 'harto', 'solo', 'fastidio', 'pésimo', 'traicionado', 'dolido', 'incomprendido', 'agotado', 'odio', 'error', 'falla', 'problema', 'complicado', 'difícil'],
                'enojo': ['enojado', 'molesto', 'furioso', 'indignado', 'cabreado', 'rabia', 'injusticia', 'preocupa', 'asco', 'inaceptable', 'irritado'],
                'neutral': ['normal', 'regular', 'aceptable', 'estándar', 'tranquilo', 'indiferente', 'neutral', 'sin opinión', 'informativo', 'conciso', 'adecuado', 'irrelevante', 'usual', 'común', 'sin novedades', 'equilibrado', 'razonable'],
                'sorpresa': ['sorprendido', 'sorpresa', 'inesperado', 'sorpresa agradable'],
                'miedo': ['miedo', 'ansioso', 'preocupado', 'nervioso'],
                'confusión': ['confundido', 'no entiendo', 'no sé'],
                'satisfacción': ['satisfecho', 'satisfacción', 'lograr', 'terminar'],
                'motivación': ['motivado', 'ilusionado', 'proyecto', 'nuevo'],
                'orgullo': ['orgulloso', 'progreso', 'seguir'],
                'agradecimiento': ['agradecido', 'gracias'],
                'inspiración': ['inspirado', 'escuché'],
                'abrumado': ['abrumado', 'tantas', 'tareas'],
                'vacío': ['vacío', 'siento vacío', 'después']
            }
            
            # Para cada cluster, analizar sus palabras características
            if hasattr(self.vectorizer, 'get_feature_names_out'):
                features = self.vectorizer.get_feature_names_out()
                
                for cluster_id in range(len(self.model.cluster_centers_)):
                    # Obtener palabras más importantes del cluster
                    center = self.model.cluster_centers_[cluster_id]
                    top_indices = center.argsort()[-15:][::-1]
                    cluster_words = [features[i].lower() for i in top_indices]
                    
                    # Buscar coincidencias con emociones
                    emotion_scores = {}
                    for emotion, keywords in emotion_keywords.items():
                        score = sum(1 for word in cluster_words if any(kw in word or word in kw for kw in keywords))
                        if score > 0:
                            emotion_scores[emotion] = score
                    
                    # Asignar la emoción con mayor score
                    if emotion_scores:
                        best_emotion = max(emotion_scores, key=emotion_scores.get)
                        self.emotion_names_cache[cluster_id] = best_emotion
                    else:
                        # Si no hay coincidencias, usar el nombre del cluster
                        self.emotion_names_cache[cluster_id] = f"emoción_{cluster_id}"
                        
        except Exception as e:
            self.logger.error(f"Error construyendo nombres de emociones: {e}")
    
    def _detect_emotion_from_text(self, original_text, cleaned_text):
        """Detecta la emoción directamente del texto del usuario"""
        try:
            # Diccionario de palabras clave a emociones (más completo)
            emotion_keywords = {
                'alegría': ['alegría', 'feliz', 'contento', 'genial', 'maravilloso', 'increíble', 
                           'alegre', 'fantástico', 'perfecto', 'excelente', 'bueno', 'entusiasmado', 
                           'satisfecho', 'animado', 'optimista', 'inspirado', 'agradecido', 'paz', 
                           'tranquilidad', 'éxito', 'logro', 'afortunado', 'divertido', 'encantado', 
                           'espectacular', 'orgulloso', 'amor', 'energía', 'bien', 'gran día', 'gran'],
                'tristeza': ['triste', 'tristeza', 'desanimado', 'mal', 'terrible', 'horrible', 
                            'deprimido', 'fatal', 'desesperanzado', 'frustración', 'decepcionado', 
                            'pena', 'exhausto', 'vacío', 'sin motivación', 'dolor', 'miedo', 'culpa', 
                            'nostálgico', 'ansioso', 'harto', 'solo', 'fastidio', 'pésimo', 
                            'traicionado', 'dolido', 'incomprendido', 'agotado', 'odio', 'error', 
                            'falla', 'problema', 'complicado', 'difícil', 'me fue mal', 'fue mal'],
                'enojo': ['enojado', 'molesto', 'furioso', 'indignado', 'cabreado', 'rabia', 
                         'injusticia', 'preocupa', 'asco', 'inaceptable', 'irritado'],
                'neutral': ['normal', 'regular', 'aceptable', 'estándar', 'tranquilo', 'indiferente', 
                           'neutral', 'sin opinión', 'informativo', 'conciso', 'adecuado', 
                           'irrelevante', 'usual', 'común', 'sin novedades', 'equilibrado', 'razonable'],
                'sorpresa': ['sorprendido', 'sorpresa', 'inesperado', 'sorpresa agradable'],
                'miedo': ['miedo', 'ansioso', 'preocupado', 'nervioso'],
                'confusión': ['confundido', 'no entiendo', 'no sé'],
                'satisfacción': ['satisfecho', 'satisfacción', 'lograr', 'terminar'],
                'motivación': ['motivado', 'ilusionado', 'proyecto', 'nuevo'],
                'orgullo': ['orgulloso', 'progreso', 'seguir'],
                'agradecimiento': ['agradecido', 'gracias'],
                'inspiración': ['inspirado', 'escuché'],
                'abrumado': ['abrumado', 'tantas', 'tareas'],
                'vacío': ['vacío', 'siento vacío', 'después']
            }
            
            # Convertir texto a minúsculas para comparación
            text_lower = cleaned_text.lower()
            original_lower = original_text.lower()
            
            # Dividir en palabras para búsqueda más precisa
            text_words = set(text_lower.split())
            original_words = set(original_lower.split())
            all_words = text_words | original_words
            
            # Contar coincidencias para cada emoción
            emotion_scores = {}
            for emotion, keywords in emotion_keywords.items():
                score = 0
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    # Buscar palabra completa en el texto
                    if keyword_lower in text_lower or keyword_lower in original_lower:
                        # Dar más peso a frases completas
                        if ' ' in keyword:
                            score += 20
                        else:
                            score += 10
                    
                    # Buscar palabras individuales
                    keyword_words = set(keyword_lower.split())
                    matches = len(keyword_words & all_words)
                    if matches > 0:
                        score += matches * 5
                
                if score > 0:
                    emotion_scores[emotion] = score
            
            # Retornar la emoción con mayor score
            if emotion_scores:
                best_emotion = max(emotion_scores, key=emotion_scores.get)
                # Solo retornar si el score es significativo (mayor a 3)
                if emotion_scores[best_emotion] >= 3:
                    self.logger.info(f"Emoción detectada del texto: {best_emotion} (score: {emotion_scores[best_emotion]})")
                    return best_emotion
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detectando emoción del texto: {e}")
            return None
    
    def _get_emotion_name(self, cluster_id, default_emotion):
        """Obtiene el nombre descriptivo de la emoción para un cluster"""
        return self.emotion_names_cache.get(cluster_id, default_emotion)
    
    def _get_user_text_words(self, original_text, text_vector_tfidf, top_n=5):
        """Obtiene las palabras más relevantes del texto del usuario"""
        try:
            # Preprocesar texto original
            cleaned_text = self.preprocessor.clean_text(original_text)
            words = cleaned_text.split()
            
            # Obtener índices de palabras con mayor peso TF-IDF en el texto
            if hasattr(text_vector_tfidf, 'toarray'):
                vector_array = text_vector_tfidf.toarray()[0]
            else:
                vector_array = text_vector_tfidf[0] if hasattr(text_vector_tfidf, '__getitem__') else text_vector_tfidf
            
            # Obtener features del vectorizador
            if hasattr(self.vectorizer, 'get_feature_names_out'):
                features = self.vectorizer.get_feature_names_out()
                
                # Obtener top índices con mayor peso
                top_indices = vector_array.argsort()[-top_n*2:][::-1]  # Obtener más para filtrar
                
                # Filtrar palabras que realmente están en el texto del usuario
                relevant_words = []
                for idx in top_indices:
                    feature = features[idx]
                    # Verificar si la palabra está en el texto original
                    if any(word in feature or feature in word for word in words):
                        relevant_words.append(feature)
                        if len(relevant_words) >= top_n:
                            break
                
                # Si no encontramos suficientes, usar las palabras del texto directamente
                if len(relevant_words) < top_n:
                    # Agregar palabras del texto que sean significativas
                    for word in words:
                        if len(word) > 3 and word not in relevant_words:
                            relevant_words.append(word)
                            if len(relevant_words) >= top_n:
                                break
                
                return relevant_words[:top_n] if relevant_words else words[:top_n]
            else:
                # Fallback: usar palabras del texto preprocesado
                return [w for w in words if len(w) > 3][:top_n]
                
        except Exception as e:
            self.logger.error(f"Error obteniendo palabras del usuario: {e}")
            # Fallback: palabras del texto
            cleaned = self.preprocessor.clean_text(original_text)
            words = [w for w in cleaned.split() if len(w) > 3]
            return words[:top_n] if words else []