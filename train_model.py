from src.ml.unsupervised_trainer import UnsupervisedTrainer
from src.utils.logger import setup_logger

def main():
    logger = setup_logger()
    
    try:
        logger.info("INICIANDO ENTRENAMIENTO NO SUPERVISADO")
        logger.info("Algoritmo: K-means con TF-IDF")
        logger.info("Clusters: 3 (Positivo, Negativo, Neutral)")
        
        # Entrenar modelo
        trainer = UnsupervisedTrainer(n_clusters=3)
        evaluation = trainer.train()
        
        logger.info("ENTRENAMIENTO COMPLETADO")
        logger.info(f"Resultados:")
        logger.info(f"   - Silhouette Score: {evaluation['silhouette_score']}")
        logger.info(f"   - Inercia: {evaluation['inertia']}")
        logger.info(f"   - Muestras: {evaluation['n_samples']}")
        
        print("\n" + "="*50)
        print("MODELO ENTRENADO EXITOSAMENTE")
        print("="*50)
        print(f"Silhouette Score: {evaluation['silhouette_score']}")
        print(f"Clusters: {evaluation['n_clusters']}")
        print(f"Muestras entrenadas: {evaluation['n_samples']}")
        print("="*50)
        print("Ahora puedes ejecutar: python run_chatbot.py")
        
    except Exception as e:
        logger.error(f"Error en entrenamiento: {e}")
        print(f"Error entrenando modelo: {e}")

if __name__ == "__main__":
    main()