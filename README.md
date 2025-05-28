# ♻️ Clasificador de Residuos con Arduino y Visión Artificial

Un sistema inteligente que combina **visión por computadora** y **Arduino** para identificar residuos en tiempo real y activar LEDs según su tipo. Este proyecto busca contribuir con la **gestión responsable de residuos** y la protección del medio ambiente.

---

## 🧠 ¿Qué hace este proyecto?

- Detecta y clasifica 4 tipos de residuos: **Metal**, **Plástico**, **Papel** y **Orgánico**
- Captura imágenes en tiempo real mediante cámara
- Usa un modelo de Machine Learning con TensorFlow (formato `.keras`)
- Envía comandos al **Arduino Uno** para activar un **LED específico**
- Se controla con teclado:  
  `[ESPACIO]` para clasificar | `[ESC]` para salir

---

## 🏗️ Estructura del Proyecto
```
waste_classifier/
├── waste_classifier_model.keras   # Modelo entrenado
├── class_names.json               # Clases del modelo
├── requirements.txt               # Dependencias de Python
├── README.md                      # Este archivo
└── src/
    ├── main.py                    # Punto de entrada
    ├── camera.py                  # Captura de imágenes
    ├── gui.py                     # Interfaz y control serial
    └── classifier_stub.py         # Modelo y predicción
```

🚀 Características

✅ Clasificación en tiempo real con modelo TensorFlow Keras
✅ Alta precisión con umbral de confianza del 85%
✅ Comunicación serial con Arduino
✅ Control por eventos (procesa solo al presionar teclas)
✅ 4 categorías de residuos: Metal, Plástico, Papel, Orgánico
✅ Indicadores LED físicos para cada categoría
✅ Interfaz limpia con OpenCV

🛠️ Componentes de Hardware
Arduino
Microcontrolador: Arduino UnoR3
Puerto serial: COM12 (configurable)
Baudrate: 9600

LEDs y Conexiones
Categoría   PIN     LED     Comando
Metal        2      🟡       'M'
Plástico     3      🔴       'P'
Papel        4      🟢       'L'
Orgánico     5      ⚪       'O'

Resistencias

4x resistencias de 220Ω (una por cada LED)

📦 Instalación
1. Clonar el repositorio
git clone <url-del-repositorio>
cd waste_classifier
2. Instalar dependencias de Python
pip install -r requirements.txt
3. Cargar código en Arduino
Abre el Arduino IDE y carga el siguiente código:

```arduino
void setup() {
  pinMode(2, OUTPUT); // Metal
  pinMode(3, OUTPUT); // Plástico
  pinMode(4, OUTPUT); // Papel
  pinMode(5, OUTPUT); // Orgánico
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char input = Serial.read();
    apagarTodos();
    if (input == 'M') digitalWrite(2, HIGH);
    else if (input == 'P') digitalWrite(3, HIGH);
    else if (input == 'L') digitalWrite(4, HIGH);
    else if (input == 'O') digitalWrite(5, HIGH);
    delay(2000);
    apagarTodos();
  }
}

void apagarTodos() {
  digitalWrite(2, LOW);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
}
```

4. Verificar puerto serial

Asegúrate de que Arduino esté conectado al puerto correcto
En Windows: generalmente COM12, COM3, etc.
Puedes verificarlo en el Arduino IDE: Herramientas → Puerto

🎮 Uso
1. Ejecutar la aplicación
python src/main.py
2. Controles

[ESPACIO]: Capturar y clasificar el objeto actual
[ESC]: Salir de la aplicación
[X]: Cerrar ventana (también funciona)

3. Funcionamiento

Se abre una ventana mostrando la cámara en tiempo real
Coloca un residuo frente a la cámara
Presiona ESPACIO para clasificar
Si la confianza es ≥85%, se enciende el LED correspondiente
El LED se apaga automáticamente después de 2 segundos

🔧 Configuración
Cambiar puerto serial
En src/gui.py, línea 8:
arduino = serial.Serial('COM12', 9600, timeout=1)
Ajustar umbral de confianza
En src/gui.py, función display_feed():
if confidence >= 0.85:  # Cambiar 0.85 por el valor deseado
Modificar tiempo de LED encendido
En el código de Arduino:
delay(2000);  // 2000 = 2 segundos

🧪 Pruebas
Probar comunicación con Arduino
¡IMPORTANTE!
Antes de usar la aplicación principal, ejecuta este script independiente para verificar que los LEDs y la comunicación serial funcionen correctamente:
Crea un archivo llamado test_arduino.py y ejecuta:
```python
import serial
import time

arduino = serial.Serial('COM12', 9600, timeout=1)
time.sleep(2)

for letra in ['M', 'P', 'L', 'O']:
    arduino.write(letra.encode())
    print("Enviado:", letra)
    time.sleep(2)
```
¿Qué debe pasar?

LED Amarillo (Metal) se enciende 2 segundos → se apaga
LED Rojo (Plástico) se enciende 2 segundos → se apaga
LED Verde (Papel) se enciende 2 segundos → se apaga
LED Blanco (Orgánico) se enciende 2 segundos → se apaga

Si este test funciona correctamente, entonces el problema no está en las conexiones de hardware sino en la integración con la aplicación principal.

Verificar modelo
El modelo debe estar en la ruta: waste_classifier_model.keras
Las clases deben estar definidas en: class_names.json

📋 Dependencias
tensorflow>=2.10.0
opencv-python>=4.6.0
pyserial>=3.5
numpy>=1.21.0

🐛 Solución de Problemas
Los LEDs no se encienden
1.Verificar puerto: Asegúrate de que COM12 sea el correcto
2.Probar script de prueba: Ejecuta el código de prueba independiente
3.Revisar conexiones: Verifica que los LEDs estén bien conectados
4.Reiniciar Arduino: Desconecta y vuelve a conectar

La cámara no se abre
# Verificar que no esté siendo usada por otra aplicación
# Cambiar el índice de cámara en camera.py si es necesario
cap = cv2.VideoCapture(1)  # Probar con 1, 2, etc.

Error de comunicación serial
# Verificar puertos disponibles
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device)

🔄 Flujo de Funcionamiento
[Inicio] → [Abrir Cámara] → [Mostrar Video en Tiempo Real]
    ↓
[Usuario presiona ESPACIO] → [Capturar Frame Actual]
    ↓
[Procesar con Modelo] → [¿Confianza ≥ 85%?]
    ↓ (Sí)                     ↓ (No)
[Enviar comando Arduino] → [Mostrar "Baja confianza"]
    ↓
[Encender LED correspondiente] → [Esperar 3s] → [Apagar LED]

👥 Contribuciones
Las contribuciones son bienvenidas. Por favor:

Fork el proyecto
Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
Commit tus cambios (git commit -m 'Add some AmazingFeature')
Push a la rama (git push origin feature/AmazingFeature)
Abre un Pull Request

📝 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

📞 Contacto
Si tienes preguntas o sugerencias, no dudes en contactar.

¡Ayuda al medio ambiente clasificando residuos de forma inteligente! 🌱