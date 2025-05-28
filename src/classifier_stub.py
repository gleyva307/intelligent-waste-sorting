import tensorflow as tf
import numpy as np
import json
import os
import cv2
import serial

# 📌 Ruta y carga del modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "waste_classifier_model.keras")
model = tf.keras.models.load_model(MODEL_PATH)

# 📌 Cargar nombres de clases
CLASS_NAMES_PATH = os.path.join(os.path.dirname(__file__), "..", "class_names.json")
with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)

# 📌 Tamaño esperado por el modelo
IMG_SIZE = (180, 180)


def preprocess_frame_opencv(frame):
    """
    Preprocesamiento avanzado con OpenCV:
    - Conversión a RGB
    - Reducción de ruido
    - Corrección de iluminación
    - Redimensionado
    """
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l_eq = cv2.equalizeHist(l)
    lab_eq = cv2.merge((l_eq, a, b))
    frame_eq = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)

    resized = cv2.resize(frame_eq, IMG_SIZE)
    normalized = resized / 255.0
    input_tensor = np.expand_dims(normalized, axis=0)

    return input_tensor


def classify_frame_opencv(frame):
    """
    Clasifica un frame usando el modelo cargado.
    Devuelve la clase y el porcentaje de confianza.
    """
    processed = preprocess_frame_opencv(frame)
    predictions = model.predict(processed, verbose=0)
    predicted_index = np.argmax(predictions[0])
    predicted_class = class_names[predicted_index]
    confidence = float(np.max(predictions[0]))
    return predicted_class, confidence


def predict_image(img_path):
    """
    Clasifica una imagen desde su ruta en disco.
    Útil para pruebas sin cámara.
    """
    from tensorflow.keras.preprocessing import image
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    predictions = model.predict(img_array, verbose=0)
    predicted_index = np.argmax(predictions[0])
    predicted_class = class_names[predicted_index]
    confidence = float(np.max(predictions[0]))

    return predicted_class, confidence
