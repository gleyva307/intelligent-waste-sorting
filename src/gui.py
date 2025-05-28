import cv2
import numpy as np
import serial
import time
from classifier_stub import classify_frame_opencv
import unicodedata

# 📌 Intentar conectar con el Arduino
try:
    arduino = serial.Serial('COM12', 9600, timeout=1)
    time.sleep(2)
    print("✅ Conexión con Arduino establecida.")
except serial.SerialException:
    arduino = None
    print("❌ No se pudo conectar con Arduino.")

# 📌 Enviar señal al Arduino según la clase detectada
def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.lower()

def enviar_a_arduino(predicted_class):
    if arduino is None:
        return

    clase = normalizar(predicted_class)

    if clase == "metal":
        arduino.write(b'M')
    elif clase == "plastico":
        arduino.write(b'P')
    elif clase == "papel":
        arduino.write(b'L')
    elif clase == "organico":
        arduino.write(b'O')

# 📌 Mostrar la cámara y procesar por tecla
# 📌 Mostrar la cámara y procesar por tecla
def display_feed(cap):
    print("▶️ Presiona [ESPACIO] para clasificar. Presiona [ESC] para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clasificador de Residuos", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == 32:  # ESPACIO
            predicted_class, confidence = classify_frame_opencv(frame)
            text = f"{predicted_class} ({confidence*100:.1f}%)"
            print(f"🔍 Detectado: {text}")

            # 🖍️ Dibujar el texto directamente sobre el frame
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)

            # Mostrar el frame con el texto por 1 segundo
            cv2.imshow("Clasificador de Residuos", frame)
            cv2.waitKey(1000)

            if confidence >= 0.85:
                enviar_a_arduino(predicted_class)

    cap.release()
    cv2.destroyAllWindows()
