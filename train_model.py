from src.ml.unsupervised_trainer import UnsupervisedTrainer
from src.utils.logger import setup_logger
from src.data.data_manager import DataManager

def main():
    logger = setup_logger()
    data_manager = DataManager()
    
    try:
        # Cargar parámetros
        params = data_manager.load_json('config/parametros.json')
        n_clusters = params.get('modelo', {}).get('n_clusters', 30)
        
        logger.info("INICIANDO ENTRENAMIENTO NO SUPERVISADO")
        logger.info("Algoritmo: K-means con TF-IDF")
        logger.info(f"Clusters: {n_clusters} (completamente no supervisado - sin palabras clave)")
        logger.info("El modelo detectará emociones automáticamente sin etiquetas")
        
        # Entrenar modelo (sin especificar n_clusters, lo carga de parámetros)
        trainer = UnsupervisedTrainer(n_clusters=n_clusters)
        evaluation = trainer.train()
        
        logger.info("ENTRENAMIENTO COMPLETADO")
        logger.info(f"Resultados:")
        logger.info(f"   - Silhouette Score: {evaluation['silhouette_score']}")
        logger.info(f"   - Inercia: {evaluation['inertia']}")
        logger.info(f"   - Muestras: {evaluation['n_samples']}")
        logger.info(f"   - Clusters detectados: {evaluation['n_clusters']}")
        
        print("\n" + "="*50)
        print("MODELO ENTRENADO EXITOSAMENTE")
        print("="*50)
        print(f"Algoritmo: K-means NO SUPERVISADO")
        print(f"Clusters detectados: {evaluation['n_clusters']}")
        print(f"Silhouette Score: {evaluation['silhouette_score']}")
        print(f"Muestras entrenadas: {evaluation['n_samples']}")
        print("="*50)
        print("NOTA: Los clusters se nombran automáticamente (emoción_0, emoción_1, etc.)")
        print("      Sin uso de palabras clave - completamente no supervisado")
        print("="*50)
        print("Ahora puedes ejecutar: python run_chatbot.py")
        
    except Exception as e:
        logger.error(f"Error en entrenamiento: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error entrenando modelo: {e}")

if __name__ == "__main__":
    main()