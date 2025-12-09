# Detección de Emociones en Texto

Este proyecto es un chatbot capaz de detectar el estado emocional del usuario a través de sus mensajes de texto.

# Chatbot de Emociones - Aprendizaje No Supervisado

Sistema de chatbot que detecta emociones en textos usando **K-means** y **TF-IDF** (Aprendizaje No Supervisado).

## Características

- **Aprendizaje No Supervisado** (K-means con 30 clusters)
- **Procesamiento de Lenguaje Natural** (TF-IDF + limpieza de texto)
- **Respuestas contextuales** según emoción detectada
- **Interfaz de chat** en tiempo real
- **Registro de conversaciones** en archivos JSON


## Configuración del Entorno

Sigue estos pasos para configurar y ejecutar el proyecto.

### 1. Crear el Entorno Virtual

Un entorno virtual aísla las dependencias de tu proyecto. Abre una terminal (`cmd`, `PowerShell` o `Git Bash`) y navega a la carpeta del proyecto.

```bash
cd ruta/a/tu/proyecto/detecccion_emocion
```

Para crear el entorno, usa uno de los siguientes comandos. En Windows, es común que `python` no funcione pero `py` sí.

```bash
# Iniciar entorno de desarrolo : Usando el lanzador de Python
py -m venv venv

### 2. Activar el Entorno Virtual

**En Windows, macOS, Linux:**
```bash
#Opcion 1
source .venv/Scripts/activate

#Opcion 2
source venv/Scripts/activate
```

**instalacion de dependencias**
```bash
pip install -r requirements.txt
```

**Iniciar proyecto con interfaz**
```bash
#Opcion 1
python -m view.main_app
#Opcion 1
py view/main_app
```





**Para desarrolladores**
```bash
#generar lista de librerias instaladas 
pip freeze > requirements.txt
```


**Estructura del proyecto**
/deteccion_emocion/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── predictor.py
│   │   └── responses.py
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── unsupervised_trainer.py
│   │   ├── cluster_interpreter.py
│   │   ├── preprocessor.py
│   │   └── model_loader.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_manager.py
│   │   └── config_loader.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py
│
├── data/
│   ├── training/
│   │   ├── textos_sin_etiquetar.csv
│   │   └── palabras_referencia.json
│   │
│   └── history/
│       ├── conversaciones.json
│       └── metricas_entrenamiento.json
│
├── config/
│   ├── emociones.json
│   ├── respuestas.json
│   ├── parametros.json
│   └── palabras_clave.json
│
├── models/
│   ├── current/
│   │   ├── modelo_entrenado.pkl
│   │   ├── info_modelo.json
│   │   └── version_actual.txt
│   │
│   └── backups/
│
├── logs/
│   ├── errores.json
│   ├── entrenamiento.json
│   └── uso_chatbot.json
├── view/
│   ├──interface.py
│
├── requirements.txt
├── train_model.py
├── run_chatbot.py
└── README.md

**Problema a resolver**
Área: Aprendizaje no supervisado
Subárea: Procesamiento de Lenguaje Natural
Problema: Detección del estado emocional a
través del texto